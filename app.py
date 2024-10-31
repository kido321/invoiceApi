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

app = Flask(__name__)
# CORS(app, resources={r"/process_csv/*": {"origins": "http://localhost:3000"}})
CORS(app, resources={r"/*": {"origins": "*"}})

# Load environment variables (you can keep this if you have other env variables)
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


print(DATABASE_URL)
@app.route('/')
def hello():
    return "Hello, World!"

@app.route('/favicon.ico')
def favicon():
    return '', 204


@app.route('/process_excel/', methods=['POST'])
def process_excel():
    try:
        file = request.files['file']
        if not file:
            return jsonify({'error': 'No file provided'}), 400

        # Read file contents into memory
        file_contents = file.read()
        excel_file = BytesIO(file_contents)

        # Optionally, reset file pointer
        # file.seek(0)

        # Read the second sheet from the Excel file
        try:
            df = pd.read_excel(excel_file, sheet_name=1, dtype={"DRIVER NAME": str}, engine='openpyxl')
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return jsonify({'error': f'Error reading Excel file: {str(e)}'}), 500

         # For debugging purposes

        # Proceed with data processing
        df = process_data(df)

        # Remove rows where DRIVER NAME is missing
        df = df[df["DRIVER NAME"].notna()]

        # Group data by DRIVER NAME
        grouped_data = df.groupby("DRIVER NAME")

        driver_pdfs = {}

        for driver_name, group in grouped_data:
            # Generate PDF invoice
            pdf_buffer = generate_invoice(driver_name, group)
            # Encode PDF to base64 string for transmission
            pdf_base64 = base64.b64encode(pdf_buffer).decode('utf-8')
            driver_pdfs[driver_name] = pdf_base64

        return jsonify({'message': 'PDFs generated successfully.', 'pdfs': driver_pdfs}), 200

    except Exception as e:
        print(f"General error: {e}")
        return jsonify({'error': f'An error occurred while processing the Excel file: {str(e)}'}), 500




@app.route('/send_email/', methods=['POST'])
def send_email_route():
    try:
        data = request.get_json()
        pdfs = data.get('pdfs')
        # print(pdfs)
        if not pdfs:
            return jsonify({'error': 'No PDFs provided'}), 400

        # Iterate over the PDFs and send emails
        for driver_name, pdf_base64 in pdfs.items():
            pdf_buffer = base64.b64decode(pdf_base64)
            send_email(driver_name, pdf_buffer)

        return jsonify({'message': 'Emails sent successfully.'}), 200

    except Exception as e:
        print(f"Error in send_email_route: {e}")
        return jsonify({'error': f'An error occurred while sending emails: {str(e)}'}), 500

def send_email(driver_name, pdf_buffer):
    try:
        # Define email parameters
        sender_email = os.environ.get('SENDER_EMAIL')
        sender_password = os.environ.get('SENDER_PASSWORD')
        recipient_email = get_driver_email(driver_name)  # Implement this function
        subject = f'Paystub for {driver_name}'
        body = f'Dear {driver_name},\n\nPlease find attached your paystub.\n\nBest regards,\nYour Company'

        if not recipient_email:
            print(f"No email address found for {driver_name}. Skipping.")
            return

        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Attach the body text
        msg.attach(MIMEText(body, 'plain'))

        # Attach the PDF
        pdf_attachment = MIMEApplication(pdf_buffer, _subtype='pdf')
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename=f'{driver_name}-paystub.pdf')
        msg.attach(pdf_attachment)

        # Send the email via SMTP
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(f"Email sent to {recipient_email} for {driver_name}")

    except Exception as e:
        print(f'Error sending email to {driver_name}: {e}')
        # Handle the error as needed

def get_driver_email(driver_name):
    # Implement logic to retrieve the driver's email address
    driver_emails = {
        'Said  Bouza': 'kiduswork2@gmail.com',
        'Rouzbeh  Shure': 'kiduswork2@gmail.com',
        # Add more driver emails as needed
    }
    return driver_emails.get(driver_name)



def process_data(df):
    # Implement your data processing and cleaning logic
    df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")

    numeric_columns = ["GROSS PAY", "DEDUCTION", "SPIFF", "NET PAY", "MILES"]

    # Clean and convert numeric columns
    def clean_numeric(series):
        series = series.replace('[\$,]', '', regex=True)
        return pd.to_numeric(series, errors='coerce')

    df[numeric_columns] = df[numeric_columns].apply(clean_numeric)
    df[numeric_columns] = df[numeric_columns].fillna(0)

    return df

if __name__ == '__main__': # For compatibility across platforms
    app.run(debug=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)