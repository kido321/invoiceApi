#app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from io import BytesIO
import base64
from pdf_generation import generate_invoice
import os
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from supabase import create_client, Client
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional  # Added Dict import here
import traceback
import asyncio
import aiosmtplib 

app = Flask(__name__)
# CORS(app, resources={r"/process_csv/*": {"origins": "http://localhost:3000"}})
CORS(app, resources={r"/*": {"origins": "*"}})

# Load environment variables (you can keep this if you have other env variables)
load_dotenv()
supabase: Client = create_client(
    os.environ.get('SUPABASE_URL'),
    os.environ.get('SUPABASE_KEY')
)

class AsyncEmailSender:
    def __init__(self, sender_email: str, sender_password: str, max_concurrent: int = 5):
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def send_single_email(self, driver_name: str, recipient_email: str, pdf_buffer: bytes) -> Dict:
        async with self.semaphore:
            try:
                msg = MIMEMultipart()
                msg['From'] = self.sender_email
                msg['To'] = recipient_email
                msg['Subject'] = f'Paystub for {driver_name}'

                body = f'Dear {driver_name},\n\nPlease find attached your paystub.\n\nBest regards,\nGiant Transport Group LLC'
                msg.attach(MIMEText(body, 'plain'))

                pdf_attachment = MIMEApplication(pdf_buffer, _subtype='pdf')
                pdf_attachment.add_header('Content-Disposition', 'attachment', filename=f'{driver_name}-paystub.pdf')
                msg.attach(pdf_attachment)

                # Use start_tls=True to handle TLS negotiation automatically
                smtp = aiosmtplib.SMTP(hostname='smtp.gmail.com', port=587, start_tls=True)
                try:
                    await smtp.connect()
                    await smtp.login(self.sender_email, self.sender_password)
                    await smtp.send_message(msg)
                finally:
                    await smtp.quit()

                print(f"✓ Successfully sent email to {driver_name} ({recipient_email})")
                return {
                    'name': driver_name,
                    'email': recipient_email,
                    'status': 'sent'
                }

            except Exception as e:
                error_msg = str(e)
                print(f"✗ Failed to send email to {driver_name} ({recipient_email}): {error_msg}")
                return {
                    'name': driver_name,
                    'email': recipient_email,
                    'status': 'failed',
                    'error': error_msg
                }

    async def send_emails_batch(self, email_tasks: List[Dict]) -> Dict:
        print(f"\n=== Starting Batch Email Processing ===")
        print(f"Total emails to send: {len(email_tasks)}")

        # Adjust batch size as needed
        batch_size = self.max_concurrent
        all_results = []

        # Create tasks for all emails
        tasks = [
            self.send_single_email(
                task['driver_name'],
                task['email'],
                task['pdf_buffer']
            )
            for task in email_tasks
        ]

        # Process emails in batches
        for i in range(0, len(tasks), batch_size):
            current_batch = tasks[i:i + batch_size]
            batch_results = await asyncio.gather(*current_batch, return_exceptions=True)
            all_results.extend(batch_results)

            # Optional: Add a delay between batches if needed
            # await asyncio.sleep(1)

        # Collect results
        emails_sent = []
        failed_emails = []

        for result in all_results:
            if isinstance(result, dict):
                if result['status'] == 'sent':
                    emails_sent.append(result)
                else:
                    failed_emails.append(result)
            else:
                # Handle exceptions
                failed_emails.append({
                    'status': 'failed',
                    'error': str(result)
                })

        print("\n=== Email Sending Summary ===")
        print(f"Successfully sent: {len(emails_sent)}")
        print(f"Failed to send: {len(failed_emails)}")

        if failed_emails:
            print("\nFailed emails:")
            for fail in failed_emails:
                print(f"- {fail.get('name', 'Unknown')} ({fail.get('email', 'Unknown')}): {fail.get('error', 'Unknown error')}")

        return {
            'summary': {
                'total_emails': len(email_tasks),
                'emails_sent': len(emails_sent),
                'emails_failed': len(failed_emails)
            },
            'emails_sent': emails_sent,
            'failed_emails': failed_emails
        }

def run_async_email_sender(email_tasks: List[Dict]) -> Dict:
    """Helper function to run the async email sender in a separate thread"""
    try:
        sender = AsyncEmailSender(
            sender_email=os.environ.get('SENDER_EMAIL'),
            sender_password=os.environ.get('SENDER_PASSWORD'),
            max_concurrent=5  # Adjust the concurrency level as needed
        )

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(sender.send_emails_batch(email_tasks))
        finally:
            loop.close()

        return result
    except Exception as e:
        print(f"Error in run_async_email_sender: {str(e)}")
        traceback.print_exc()
        raise

@app.route('/send_email/', methods=['POST'])
def send_email_route():
    try:
        data = request.get_json()
        pdfs = data.get('pdfs')
        if not pdfs:
            return jsonify({'error': 'No PDFs provided'}), 400

        # Fetch all drivers from Supabase
        response = supabase.table('drivers').select('*').execute()

        # Create normalized dictionary for email lookup
        drivers_db = {}
        for driver in response.data:
            normalized_name = normalize_name(driver['name'])
            drivers_db[normalized_name] = {
                'email': driver['email'],
                'original_name': driver['name']
            }

        # Prepare email tasks and track unmatched drivers
        email_tasks = []
        not_found_drivers = []
        email_mapping = []

        print("\n=== Preparing Email Tasks ===")
        for driver_name, pdf_base64 in pdfs.items():
            normalized_name = normalize_name(driver_name)
            driver_info = drivers_db.get(normalized_name)

            mapping_info = {
                'original_name': driver_name,
                'normalized_name': normalized_name
            }

            if driver_info and driver_info['email']:
                mapping_info.update({
                    'email': driver_info['email'],
                    'status': 'found'
                })
                email_mapping.append(mapping_info)

                email_tasks.append({
                    'driver_name': driver_name,
                    'email': driver_info['email'],
                    'pdf_buffer': base64.b64decode(pdf_base64)
                })
                print(f"✓ Prepared email task for {driver_name} ({driver_info['email']})")
            else:
                mapping_info['status'] = 'not_found'
                not_found_drivers.append(driver_name)
                email_mapping.append(mapping_info)
                print(f"✗ No email found for {driver_name}")

        if not_found_drivers:
            return jsonify({
                'error': 'Some drivers do not have email mappings',
                'not_found_drivers': not_found_drivers,
                'email_mapping': email_mapping
            }), 400

        # Use ThreadPoolExecutor to run async code in a separate thread
        with ThreadPoolExecutor() as executor:
            future = executor.submit(run_async_email_sender, email_tasks)
            try:
                result = future.result(timeout=25)  # Adjust timeout as needed
            except TimeoutError:
                return jsonify({
                    'error': 'Operation timed out. Some emails may have been sent.',
                    'timeout_occurred': True
                }), 504

        return jsonify({
            'message': 'Email process completed',
            **result,
            'email_mapping': email_mapping
        }), 200

    except Exception as e:
        print(f"Error in send_email_route: {e}")
        traceback.print_exc()
        return jsonify({'error': f'An error occurred while sending emails: {str(e)}'}), 500

# The rest of your code remains unchanged
# print(DATABASE_URL)
@app.route('/')
def hello():
    return "Hello, World!"

@app.route('/favicon.ico')
def favicon():
    return '', 204

def normalize_name(name) -> str:
    """
    Normalize a name by:
    1. Converting to string
    2. Converting to title case
    3. Removing extra spaces
    4. Removing trailing/leading spaces
    """
    try:
        # Convert input to string, handling various types
        if name is None:
            return ""
        # Convert to string, handling float/int cases
        if isinstance(name, (float, int)):
            name = str(int(name))
        else:
            name = str(name)
        
        # Remove extra spaces and trim
        normalized = " ".join(name.split())
        
        # print(f"Normalized name: '{name}' -> '{normalized}'")  # Debugging
        return normalized
    except Exception as e:
        print(f"Error normalizing name '{name}' (type: {type(name)}): {str(e)}")
        return str(name)

def send_email(driver_name, recipient_email, pdf_buffer):
    """Send email with PDF attachment to driver"""
    try:
        sender_email = os.environ.get('SENDER_EMAIL')
        sender_password = os.environ.get('SENDER_PASSWORD')

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f'Paystub for {driver_name}'
        
        body = f'Dear {driver_name},\n\nPlease find attached your paystub.\n\nBest regards,\nGiant Transport Group LLC'
        msg.attach(MIMEText(body, 'plain'))

        pdf_attachment = MIMEApplication(pdf_buffer, _subtype='pdf')
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename=f'{driver_name}-paystub.pdf')
        msg.attach(pdf_attachment)
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            
        return True
    except Exception as e:
        raise Exception(f"Failed to send email: {str(e)}")
    # print('driver' , driver_name ,  '  ' , recipient_email , pdf_buffer)


@app.route('/process_excel/', methods=['POST'])
def process_excel():
    try:
        file = request.files['file']
        if not file:
            return jsonify({'error': 'No file provided'}), 400
        
        # Fetch drivers from Supabase with their pay multipliers
        response = supabase.table('drivers').select('*').execute()
        
        # Create a normalized dictionary for driver lookup with debug logging
        drivers = {}
        for driver in response.data:
            original_name = driver['name']
            normalized_name = normalize_name(original_name)
            drivers[normalized_name] = {
                'email': driver['email'],
                'pay_multiplier': float(driver['pay_multiplier']),
                'original_name': original_name
            }
            # print(f"Loaded driver: '{original_name}' -> '{normalized_name}'")

        file_contents = file.read()
        excel_file = BytesIO(file_contents)

        try:
            # Read Excel file with explicit string type for DRIVER NAME
            df = pd.read_excel(
                excel_file, 
                sheet_name=1, 
                dtype={"DRIVER NAME": str},
                engine='openpyxl'
            )
            
            # Debug print column types
            # print("DataFrame column types:", df.dtypes)
            # print("Sample of DRIVER NAME column:", df["DRIVER NAME"].head())
            
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return jsonify({'error': f'Error reading Excel file: {str(e)}'}), 500

        # Normalize the DRIVER NAME column with error handling
        df['DRIVER NAME'] = df['DRIVER NAME'].apply(lambda x: normalize_name(x))
        
        # Debug print unique driver names
        print("Unique driver names in Excel:", df['DRIVER NAME'].unique())
        
        df = process_data(df)
        df = df[df["DRIVER NAME"].notna()]
        grouped_data = df.groupby("DRIVER NAME")

        driver_pdfs = {}
        unmatched_drivers = []
        processed_drivers = []

        for driver_name, group in grouped_data:
            normalized_name = normalize_name(driver_name)
            print(f"Processing group for driver: '{driver_name}' (normalized: '{normalized_name}')")
            
            # Get driver info with default pay multiplier if not found
            driver_info = drivers.get(normalized_name, {
                'pay_multiplier': 0.75,
                'email': None,
                'original_name': driver_name
            })
            
            pay_multiplier = float(driver_info['pay_multiplier'])
            
            if normalized_name not in drivers:
                unmatched_drivers.append({
                    'name': driver_name,
                    'normalized_name': normalized_name
                })
                print(f"Warning: No matching driver found for '{driver_name}' (normalized: '{normalized_name}')")
            else:
                processed_drivers.append({
                    'name': driver_name,
                    'normalized_name': normalized_name,
                    'pay_multiplier': pay_multiplier
                })
            
            try:
                # Generate PDF with pay multiplier
                pdf_buffer = generate_invoice(driver_name, group, pay_multiplier)
                pdf_base64 = base64.b64encode(pdf_buffer).decode('utf-8')
                driver_pdfs[driver_name] = pdf_base64
            except Exception as e:
                print(f"Error generating PDF for {driver_name}: {e}")
                continue

        # Print summary
        print("\nProcessing Summary:")
        print(f"Total drivers processed: {len(processed_drivers)}")
        print(f"Unmatched drivers: {len(unmatched_drivers)}")
        
        if unmatched_drivers:
            print("\nUnmatched drivers details:")
            for driver in unmatched_drivers:
                print(f"- {driver['name']} (normalized: {driver['normalized_name']})")

        return jsonify({
            'message': 'PDFs generated successfully.',
            'pdfs': driver_pdfs,
            'unmatched_drivers': unmatched_drivers,
            'processed_drivers': processed_drivers
        }), 200

    except Exception as e:
        print(f"General error: {e}")
        traceback.print_exc()  # Print full traceback for debugging
        return jsonify({'error': f'An error occurred while processing the Excel file: {str(e)}'}), 500







@app.route('/validate_emails/', methods=['POST'])
def validate_emails():
    try:
        data = request.get_json()
        pdfs = data.get('pdfs', {})
        
        if not pdfs:
            return jsonify({'error': 'No PDFs provided'}), 400

        # Fetch all drivers from Supabase
        response = supabase.table('drivers').select('*').execute()
        
        # Create normalized dictionary for email lookup with debug info
        drivers_db = {}
        print("\n=== Loaded Driver Database ===")
        for driver in response.data:
            normalized_name = normalize_name(driver['name'])
            drivers_db[normalized_name] = {
                'email': driver['email'],
                'original_name': driver['name'],
                'pay_multiplier': driver['pay_multiplier']
            }
            print(f"✓ {driver['name']} -> {driver['email']} (multiplier: {driver['pay_multiplier']})")

        # Validate mappings
        email_mappings = []
        not_found = []
        found = []

        print("\n=== Checking PDF Driver Mappings ===")
        for driver_name in pdfs.keys():
            normalized_name = normalize_name(driver_name)
            driver_info = drivers_db.get(normalized_name)
            
            mapping_status = {
                'original_name': driver_name,
                'normalized_name': normalized_name,
            }

            if driver_info:
                mapping_status.update({
                    'email': driver_info['email'],
                    'pay_multiplier': driver_info['pay_multiplier'],
                    'status': 'found'
                })
                found.append(mapping_status)
                print(f"✓ Found: {driver_name} -> {driver_info['email']}")
            else:
                mapping_status.update({
                    'status': 'not_found',
                    'error': 'No matching driver in database'
                })
                not_found.append(mapping_status)
                print(f"✗ Not Found: {driver_name}")

        # Print summary statistics
        print("\n=== Validation Summary ===")
        print(f"Total drivers in database: {len(drivers_db)}")
        print(f"Total PDFs to process: {len(pdfs)}")
        print(f"Matched drivers: {len(found)}")
        print(f"Unmatched drivers: {len(not_found)}")

        # Print detailed unmatched drivers if any
        if not_found:
            print("\n=== Unmatched Drivers ===")
            print("The following drivers from the Excel file were not found in the database:")
            for driver in not_found:
                print(f"- {driver['original_name']} (normalized: {driver['normalized_name']})")
            
            print("\nPossible matches in database:")
            for unmatched in not_found:
                normalized_unmatched = unmatched['normalized_name'].lower()
                possible_matches = [
                    f"{name} -> {info['email']}"
                    for name, info in drivers_db.items()
                    if normalized_unmatched in name.lower() or name.lower() in normalized_unmatched
                ]
                if possible_matches:
                    print(f"\nPossible matches for {unmatched['original_name']}:")
                    for match in possible_matches:
                        print(f"  - {match}")

        # Detailed validation response
        validation_response = {
            'summary': {
                'total_pdfs': len(pdfs),
                'total_drivers_in_db': len(drivers_db),
                'matched_drivers': len(found),
                'unmatched_drivers': len(not_found)
            },
            'matched_drivers': found,
            'unmatched_drivers': not_found,
            'ready_to_send': len(not_found) == 0
        }

        return jsonify(validation_response), 200

    except Exception as e:
        print(f"Error in validate_emails: {e}")
        traceback.print_exc()
        return jsonify({
            'error': f'An error occurred while validating emails: {str(e)}'
        }), 500


def process_data(df):
    # Convert DATE column to datetime
    df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")

    numeric_columns = ["GROSS PAY", "DEDUCTION", "SPIFF", "NET PAY", "MILES"]
    
    # Clean and convert numeric columns
    def clean_numeric(series):
        # Convert to string first, then clean
        series = series.astype(str)
        series = series.replace('[\$,]', '', regex=True)
        return pd.to_numeric(series, errors='coerce')

    # Process numeric columns
    for col in numeric_columns:
        if col in df.columns:
            df[col] = clean_numeric(df[col])
            df[col] = df[col].fillna(0)

    # Debug print
    print("\nProcessed DataFrame Info:")
    print(df.info())
    print("\nSample of processed data:")
    print(df.head())
    
    return df


def process_data_totals(df):
    """
    Clean and convert numeric columns needed for totals,
    without attempting to parse or handle a 'DATE' column.
    """
    # List only the columns you actually need to process numerically.
    numeric_columns = ["GROSS PAY", "DEDUCTION", "SPIFF", "NET PAY", "MILES"]

    def clean_numeric(series):
        # Convert to string first, remove $, commas, etc.
        series = series.astype(str)
        series = series.replace('[\\$,]', '', regex=True)
        return pd.to_numeric(series, errors='coerce')

    for col in numeric_columns:
        if col in df.columns:
            df[col] = clean_numeric(df[col])
            df[col] = df[col].fillna(0)

    print("\nProcessed Totals DataFrame Info:")
    print(df.info())
    print("\nSample of totals data:")
    print(df.head())

    return df



@app.route('/process_excels_totals/', methods=['POST'])
def process_excels_totals():
    try:
        # Fetch drivers from Supabase (like you do now)
        response = supabase.table('drivers').select('*').execute()

        # Create a dictionary for driver lookup
        drivers_db = {}
        for driver in response.data:
            normalized_name = normalize_name(driver['name'])
            drivers_db[normalized_name] = {
                'email': driver['email'],
                'pay_multiplier': float(driver['pay_multiplier']),
                'original_name': driver['name']
            }

        # 1) Get multiple files from the request
        files = request.files.getlist('files')
        if not files or len(files) == 0:
            return jsonify({'error': 'No files provided'}), 400

        all_data_frames = []

        # 2) Loop through each file
        for f in files:
            file_contents = f.read()
            excel_file = BytesIO(file_contents)

            # 3) Read each Excel or CSV into a DataFrame
            try:
                # If you have CSV files, you can do a check:
                #   if f.filename.endswith('.csv'):
                #       df = pd.read_csv(...)
                #   else:
                #       df = pd.read_excel(...)
                # For simplicity, assume .xlsx
                df = pd.read_excel(
                    excel_file,
                    sheet_name=0,
                    dtype={"DRIVER NAME": str},
                    engine='openpyxl'
                )
            except Exception as e:
                print(f"Error reading Excel file: {e}")
                return jsonify({'error': f'Error reading file {f.filename}: {str(e)}'}), 500

            # Normalize the DRIVER NAME column
            df['DRIVER NAME'] = df['DRIVER NAME'].apply(lambda x: normalize_name(x))

            # Process numeric columns, ignoring 'DATE'
            df = process_data_totals(df)

            # Store in a list so we can combine them later
            all_data_frames.append(df)

        # 4) Concatenate all DataFrames into one
        if not all_data_frames:
            return jsonify({'error': 'No valid data found in files'}), 400

        combined_df = pd.concat(all_data_frames, ignore_index=True)
        # Remove any rows without a DRIVER NAME
        combined_df = combined_df[combined_df["DRIVER NAME"].notna()]

        # 5) Group the combined data by DRIVER NAME
        grouped_data = combined_df.groupby("DRIVER NAME")

        unmatched_drivers = []
        processed_drivers = []
        driver_totals = []

        # 6) For each driver, compute totals
        for driver_name, group in grouped_data:
            normalized_name = normalize_name(driver_name)

            # If the driver doesn’t exist in the DB, mark unmatched
            driver_info = drivers_db.get(normalized_name, {
                'pay_multiplier': 0.75,
                'email': None,
                'original_name': driver_name
            })

            pay_multiplier = float(driver_info['pay_multiplier'])

            if normalized_name not in drivers_db:
                unmatched_drivers.append({
                    'name': driver_name,
                    'normalized_name': normalized_name
                })
            else:
                processed_drivers.append({
                    'name': driver_name,
                    'normalized_name': normalized_name,
                    'pay_multiplier': pay_multiplier
                })

            # Example: Summation of NET PAY, then apply pay_multiplier
            # You can do your own formula if needed:
            net_sum = group['NET PAY'].sum()
            # final earning = net_sum * pay_multiplier (change if your logic is different)
            final_earning = net_sum * pay_multiplier

            # Collect results in a list/dict
            driver_totals.append({
                'driver_name': driver_name,
                'pay_multiplier': pay_multiplier,
                'total_net': float(net_sum),
                'total_earning_after_multiplier': float(final_earning)
            })

        # 7) Return JSON response with the totals
        return jsonify({
            'message': 'Driver totals calculated successfully (no PDF).',
            'driver_totals': driver_totals,           # The list of totals
            'unmatched_drivers': unmatched_drivers,   # Anyone not in DB
            'processed_drivers': processed_drivers,   # Everyone matched in DB
        }), 200

    except Exception as e:
        print(f"General error: {e}")
        traceback.print_exc()
        return jsonify({
            'error': f'An error occurred while processing the files: {str(e)}'
        }), 500



if __name__ == '__main__': # For compatibility across platforms
    app.run(debug=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)











    








# @app.route('/send_email/', methods=['POST'])
# def send_email_route():
#     try:
#         data = request.get_json()
#         pdfs = data.get('pdfs')
#         if not pdfs:
#             return jsonify({'error': 'No PDFs provided'}), 400

#         # Fetch all drivers from Supabase
#         response = supabase.table('drivers').select('*').execute()
        
#         # Create normalized dictionary for email lookup with debug info
#         drivers_db = {}
#         for driver in response.data:
#             normalized_name = normalize_name(driver['name'])
#             drivers_db[normalized_name] = {
#                 'email': driver['email'],
#                 'original_name': driver['name']
#             }
#             print(f"Loaded driver email mapping: '{driver['name']}' -> '{driver['email']}'")

#         emails_sent = []
#         failed_emails = []
#         not_found_drivers = []
#         email_mapping = []

#         print("\n=== Starting Email Processing ===")
#         print(f"Total PDFs to process: {len(pdfs)}")
#         print("Checking email mappings...")

#         # First, check all mappings
#         for driver_name in pdfs.keys():
#             normalized_name = normalize_name(driver_name)
#             driver_info = drivers_db.get(normalized_name)
            
#             mapping_info = {
#                 'original_name': driver_name,
#                 'normalized_name': normalized_name
#             }

#             if driver_info:
#                 mapping_info['email'] = driver_info['email']
#                 mapping_info['status'] = 'found'
#                 email_mapping.append(mapping_info)
#             else:
#                 mapping_info['status'] = 'not_found'
#                 not_found_drivers.append(driver_name)
#                 email_mapping.append(mapping_info)

#         # Print mapping summary
#         print("\n=== Email Mapping Summary ===")
#         print(f"Total drivers in database: {len(drivers_db)}")
#         print(f"Total PDFs to send: {len(pdfs)}")
#         print(f"Drivers with email mappings: {len(email_mapping) - len(not_found_drivers)}")
#         print(f"Drivers without email mappings: {len(not_found_drivers)}")

#         if not_found_drivers:
#             print("\nDrivers without email mappings:")
#             for driver in not_found_drivers:
#                 print(f"- {driver}")
        
#         # Only proceed if all drivers have email mappings
#         if not_found_drivers:
#             return jsonify({
#                 'error': 'Some drivers do not have email mappings',
#                 'not_found_drivers': not_found_drivers,
#                 'email_mapping': email_mapping
#             }), 400

#         print("\n=== Starting Email Sending ===")
#         # Send emails if all mappings are found
#         for driver_name, pdf_base64 in pdfs.items():
#             normalized_name = normalize_name(driver_name)
#             driver_info = drivers_db.get(normalized_name)
            
#             if driver_info:  # This check should always pass since we validated above
#                 try:
#                     print(f"Sending email to {driver_name} ({driver_info['email']})")
#                     pdf_buffer = base64.b64decode(pdf_base64)
#                     send_email(driver_name, driver_info['email'], pdf_buffer)
#                     emails_sent.append({
#                         'name': driver_name,
#                         'email': driver_info['email'],
#                         'status': 'sent'
#                     })
#                     print(f"✓ Successfully sent email to {driver_name}")
#                 except Exception as e:
#                     error_msg = str(e)
#                     failed_emails.append({
#                         'name': driver_name,
#                         'email': driver_info['email'],
#                         'error': error_msg
#                     })
#                     print(f"✗ Failed to send email to {driver_name}: {error_msg}")

#         # Print final summary
#         print("\n=== Email Sending Summary ===")
#         print(f"Successfully sent: {len(emails_sent)}")
#         print(f"Failed to send: {len(failed_emails)}")

#         if failed_emails:
#             print("\nFailed emails:")
#             for fail in failed_emails:
#                 print(f"- {fail['name']} ({fail['email']}): {fail['error']}")

#         return jsonify({
#             'message': 'Email process completed',
#             'summary': {
#                 'total_pdfs': len(pdfs),
#                 'emails_sent': len(emails_sent),
#                 'emails_failed': len(failed_emails)
#             },
#             'emails_sent': emails_sent,
#             'failed_emails': failed_emails,
#             'email_mapping': email_mapping
#         }), 200

#     except Exception as e:
#         print(f"Error in send_email_route: {e}")
#         traceback.print_exc()  # Print full traceback for debugging
#         return jsonify({'error': f'An error occurred while sending emails: {str(e)}'}), 500


# @app.route('/send_email/', methods=['POST'])
# def send_email_route():
#     try:
#         data = request.get_json()
#         pdfs = data.get('pdfs')
#         if not pdfs:
#             return jsonify({'error': 'No PDFs provided'}), 400

#         # Fetch all drivers from Supabase
#         response = supabase.table('drivers').select('*').execute()
        
#         # Create normalized dictionary for email lookup
#         drivers_db = {}
#         for driver in response.data:
#             normalized_name = normalize_name(driver['name'])
#             drivers_db[normalized_name] = {
#                 'email': driver['email'],
#                 'original_name': driver['name']
#             }
#             print(f"Loaded driver email mapping: '{driver['name']}' -> '{driver['email']}'")

#         # Prepare email tasks and track unmatched drivers
#         email_tasks = []
#         not_found_drivers = []
#         email_mapping = []

#         print("\n=== Preparing Email Tasks ===")
#         for driver_name, pdf_base64 in pdfs.items():
#             normalized_name = normalize_name(driver_name)
#             driver_info = drivers_db.get(normalized_name)
            
#             mapping_info = {
#                 'original_name': driver_name,
#                 'normalized_name': normalized_name
#             }

#             if driver_info and driver_info['email']:
#                 mapping_info.update({
#                     'email': driver_info['email'],
#                     'status': 'found'
#                 })
#                 email_mapping.append(mapping_info)
                
#                 # Add to email tasks
#                 email_tasks.append({
#                     'driver_name': driver_name,
#                     'email': driver_info['email'],
#                     'pdf_buffer': base64.b64decode(pdf_base64)
#                 })
#                 print(f"✓ Prepared email task for {driver_name} ({driver_info['email']})")
#             else:
#                 mapping_info['status'] = 'not_found'
#                 not_found_drivers.append(driver_name)
#                 email_mapping.append(mapping_info)
#                 print(f"✗ No email found for {driver_name}")

#         if not_found_drivers:
#             return jsonify({
#                 'error': 'Some drivers do not have email mappings',
#                 'not_found_drivers': not_found_drivers,
#                 'email_mapping': email_mapping
#             }), 400

#         # Use ThreadPoolExecutor to run async code in a separate thread
#         with ThreadPoolExecutor() as executor:
#             future = executor.submit(run_async_email_sender, email_tasks)
#             try:
#                 result = future.result(timeout=25)  # Set timeout to 25 seconds for Heroku's 30-second limit
#             except TimeoutError:
#                 return jsonify({
#                     'error': 'Operation timed out. Some emails may have been sent.',
#                     'timeout_occurred': True
#                 }), 504

#         return jsonify({
#             'message': 'Email process completed',
#             **result,
#             'email_mapping': email_mapping
#         }), 200

#     except Exception as e:
#         print(f"Error in send_email_route: {e}")
#         traceback.print_exc()
#         return jsonify({'error': f'An error occurred while sending emails: {str(e)}'}), 500


