# # # import csv
# # # from collections import defaultdict
# # # from datetime import datetime
# # # import os
# # # from reportlab.lib import colors
# # # from reportlab.lib.pagesizes import letter
# # # from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
# # # from reportlab.lib.styles import getSampleStyleSheet

# # # def parse_csv_data(csv_content):
# # #     # Parse CSV content
# # #     reader = csv.DictReader(csv_content.splitlines())
    
# # #     # Organize data by driver and date
# # #     driver_data = defaultdict(lambda: defaultdict(list))
    
# # #     for row in reader:
# # #         driver_name = row['DRIVER NAME']
# # #         date_str = row['DATE'].strip()  # Remove any leading/trailing whitespace
        
# # #         # Try to parse the date, skip the row if it fails
# # #         try:
# # #             if date_str:
# # #                 date = datetime.strptime(date_str, "%b %d, %Y").date()
# # #             else:
# # #                 print(f"Skipping row for {driver_name} due to empty date.")
# # #                 continue
# # #         except ValueError:
# # #             print(f"Skipping row for {driver_name} due to invalid date format: {date_str}")
# # #             continue
        
# # #         # Parse numeric values, defaulting to 0.0 if empty or invalid
# # #         def parse_float(value):
# # #             try:
# # #                 return float(value.replace('$', '').strip() or '0')
# # #             except ValueError:
# # #                 print(f"Invalid numeric value: {value}. Defaulting to 0.")
# # #                 return 0.0

# # #         driver_data[driver_name][date].append({
# # #             'trip_code': row['TRIP CODE'],
# # #             'trip_name': row['TRIP NAME'],
# # #             'miles': parse_float(row['MILES']),
# # #             'gross_pay': parse_float(row['GROSS PAY']),
# # #             'deduction': parse_float(row['DEDUCTION']),
# # #             'spiff': parse_float(row['SPIFF']),
# # #             'net_pay': parse_float(row['NET PAY'])
# # #         })
    
# # #     return driver_data

# # # def generate_pdf_invoice(driver_name, date, trips, output_filename):
# # #     doc = SimpleDocTemplate(output_filename, pagesize=letter)
# # #     elements = []

# # #     # Add title
# # #     styles = getSampleStyleSheet()
# # #     elements.append(Paragraph(f"Invoice for {driver_name}", styles['Title']))
# # #     elements.append(Paragraph(f"Date: {date}", styles['Normal']))
# # #     elements.append(Spacer(1, 12))

# # #     # Create table for trip details
# # #     data = [['Trip Name', 'Miles', 'Gross Pay', 'Deduction', 'Spiff', 'Net Pay']]
# # #     for trip in trips:
# # #         data.append([
# # #             trip['trip_name'],
# # #             f"{trip['miles']:.2f}",
# # #             f"${trip['gross_pay']:.2f}",
# # #             f"${trip['deduction']:.2f}",
# # #             f"${trip['spiff']:.2f}",
# # #             f"${trip['net_pay']:.2f}"
# # #         ])

# # #     # Add totals row
# # #     totals = ['Total', sum(t['miles'] for t in trips), sum(t['gross_pay'] for t in trips),
# # #               sum(t['deduction'] for t in trips), sum(t['spiff'] for t in trips),
# # #               sum(t['net_pay'] for t in trips)]
# # #     data.append([totals[0], f"{totals[1]:.2f}"] + [f"${t:.2f}" for t in totals[2:]])

# # #     table = Table(data)
# # #     table.setStyle(TableStyle([
# # #         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
# # #         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
# # #         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
# # #         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
# # #         ('FONTSIZE', (0, 0), (-1, 0), 14),
# # #         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
# # #         ('BACKGROUND', (0, -1), (-1, -1), colors.beige),
# # #         ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
# # #         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
# # #         ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
# # #         ('FONTSIZE', (0, 1), (-1, -1), 12),
# # #         ('TOPPADDING', (0, 1), (-1, -1), 6),
# # #         ('BOTTOMPADDING', (0, -1), (-1, -1), 6),
# # #         ('GRID', (0, 0), (-1, -1), 1, colors.black)
# # #     ]))

# # #     elements.append(table)
# # #     doc.build(elements)

# # # def generate_all_invoices(driver_data, output_directory):
# # #     os.makedirs(output_directory, exist_ok=True)
    
# # #     for driver_name, dates in driver_data.items():
# # #         for date, trips in dates.items():
# # #             output_filename = os.path.join(output_directory, f"{driver_name}_{date}_invoice.pdf")
# # #             generate_pdf_invoice(driver_name, date, trips, output_filename)
# # #             print(f"Generated invoice: {output_filename}")

# # # # Main execution
# # # if __name__ == "__main__":
# # #     # Read CSV file
# # #     csv_filename = 'data.csv'  # Make sure this file exists in the same directory as the script
# # #     try:
# # #         with open(csv_filename, 'r') as f:
# # #             csv_content = f.read()
# # #     except FileNotFoundError:
# # #         print(f"Error: The file '{csv_filename}' was not found.")
# # #         exit(1)
    
# # #     # Parse CSV data
# # #     driver_data = parse_csv_data(csv_content)
    
# # #     if not driver_data:
# # #         print("No valid data was found in the CSV file. Please check the file contents and format.")
# # #         exit(1)
    
# # #     # Generate invoices
# # #     output_directory = "invoices"
# # #     generate_all_invoices(driver_data, output_directory)
    
# # #     print(f"All invoices have been generated in the '{output_directory}' folder.")


# # import csv
# # from collections import defaultdict
# # from datetime import datetime, timedelta
# # import os
# # from reportlab.lib import colors
# # from reportlab.lib.pagesizes import letter
# # from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
# # from reportlab.lib.styles import getSampleStyleSheet

# # def parse_csv_data(csv_content):
# #     reader = csv.DictReader(csv_content.splitlines())
# #     driver_data = defaultdict(lambda: defaultdict(list))
    
# #     for row in reader:
# #         driver_name = row['DRIVER NAME']
# #         date_str = row['DATE'].strip()
        
# #         try:
# #             if date_str:
# #                 date = datetime.strptime(date_str, "%b %d, %Y").date()
# #             else:
# #                 print(f"Skipping row for {driver_name} due to empty date.")
# #                 continue
# #         except ValueError:
# #             print(f"Skipping row for {driver_name} due to invalid date format: {date_str}")
# #             continue
        
# #         def parse_float(value):
# #             try:
# #                 return float(value.replace('$', '').strip() or '0')
# #             except ValueError:
# #                 print(f"Invalid numeric value: {value}. Defaulting to 0.")
# #                 return 0.0

# #         driver_data[driver_name][date].append({
# #             'trip_code': row['TRIP CODE'],
# #             'trip_name': row['TRIP NAME'],
# #             'miles': parse_float(row['MILES']),
# #             'gross_pay': parse_float(row['GROSS PAY']),
# #             'deduction': parse_float(row['DEDUCTION']),
# #             'spiff': parse_float(row['SPIFF']),
# #             'net_pay': parse_float(row['NET PAY'])
# #         })
    
# #     return driver_data

# # def generate_pdf_invoice(driver_name, week_start, week_end, daily_trips, output_filename):
# #     doc = SimpleDocTemplate(output_filename, pagesize=letter)
# #     elements = []

# #     styles = getSampleStyleSheet()
# #     elements.append(Paragraph(f"Weekly Invoice for {driver_name}", styles['Title']))
# #     elements.append(Paragraph(f"Week: {week_start.strftime('%b %d, %Y')} - {week_end.strftime('%b %d, %Y')}", styles['Normal']))
# #     elements.append(Spacer(1, 12))

# #     # Create table for daily summaries
# #     data = [['Date', 'Active', 'Run', 'Miles', 'Gross', 'SF', 'InTel', 'Net Pay']]
    
# #     total_active = total_run = total_miles = total_gross = total_sf = total_intel = total_net = 0
    
# #     for date, trips in sorted(daily_trips.items()):
# #         active = len(set(trip['trip_code'] for trip in trips))  # Unique trip codes
# #         run = len(trips)
# #         miles = sum(trip['miles'] for trip in trips)
# #         gross = sum(trip['gross_pay'] for trip in trips)
# #         sf = sum(trip['spiff'] for trip in trips)
# #         intel = sum(trip['deduction'] for trip in trips)
# #         net = sum(trip['net_pay'] for trip in trips)
        
# #         data.append([
# #             date.strftime("%b %d, %Y"),
# #             str(active),
# #             str(run),
# #             f"{miles:.2f}",
# #             f"${gross:.2f}",
# #             f"${sf:.2f}",
# #             f"${intel:.2f}",
# #             f"${net:.2f}"
# #         ])
        
# #         total_active += active
# #         total_run += run
# #         total_miles += miles
# #         total_gross += gross
# #         total_sf += sf
# #         total_intel += intel
# #         total_net += net
    
# #     # Add totals row
# #     data.append([
# #         'Total',
# #         str(total_active),
# #         str(total_run),
# #         f"{total_miles:.2f}",
# #         f"${total_gross:.2f}",
# #         f"${total_sf:.2f}",
# #         f"${total_intel:.2f}",
# #         f"${total_net:.2f}"
# #     ])

# #     table = Table(data)
# #     table.setStyle(TableStyle([
# #         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
# #         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
# #         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
# #         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
# #         ('FONTSIZE', (0, 0), (-1, 0), 12),
# #         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
# #         ('BACKGROUND', (0, -1), (-1, -1), colors.beige),
# #         ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
# #         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
# #         ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
# #         ('FONTSIZE', (0, 1), (-1, -1), 10),
# #         ('TOPPADDING', (0, 1), (-1, -1), 6),
# #         ('BOTTOMPADDING', (0, -1), (-1, -1), 6),
# #         ('GRID', (0, 0), (-1, -1), 1, colors.black)
# #     ]))

# #     elements.append(table)
    
# #     # Add summary
# #     elements.append(Spacer(1, 12))
# #     elements.append(Paragraph("Summary", styles['Heading2']))
# #     elements.append(Paragraph(f"Average Price per Mile: ${total_gross / total_miles:.2f}", styles['Normal']))
# #     elements.append(Paragraph(f"Total NET: ${total_net:.2f}", styles['Normal']))

# #     doc.build(elements)

# # def generate_all_invoices(driver_data, output_directory):
# #     os.makedirs(output_directory, exist_ok=True)
    
# #     for driver_name, dates in driver_data.items():
# #         if not dates:
# #             print(f"No data for driver: {driver_name}")
# #             continue
        
# #         # Find the start of the week (Monday) for the first date
# #         first_date = min(dates.keys())
# #         week_start = first_date - timedelta(days=first_date.weekday())
# #         week_end = week_start + timedelta(days=6)
        
# #         output_filename = os.path.join(output_directory, f"{driver_name}_{week_start.strftime('%Y%m%d')}_weekly_invoice.pdf")
# #         generate_pdf_invoice(driver_name, week_start, week_end, dates, output_filename)
# #         print(f"Generated invoice: {output_filename}")

# # # Main execution
# # if __name__ == "__main__":
# #     csv_filename = 'data.csv'
# #     try:
# #         with open(csv_filename, 'r') as f:
# #             csv_content = f.read()
# #     except FileNotFoundError:
# #         print(f"Error: The file '{csv_filename}' was not found.")
# #         exit(1)
    
# #     driver_data = parse_csv_data(csv_content)
    
# #     if not driver_data:
# #         print("No valid data was found in the CSV file. Please check the file contents and format.")
# #         exit(1)
    
# #     output_directory = "invoices"
# #     generate_all_invoices(driver_data, output_directory)
    
# #     print(f"All weekly invoices have been generated in the '{output_directory}' folder.")





# # invoice_generator.py

# import pandas as pd
# import os
# from reportlab.platypus import (
#     SimpleDocTemplate,
#     Table,
#     TableStyle,
#     Paragraph,
#     Spacer,
#     Image,
# )
# from reportlab.lib.pagesizes import LETTER
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
# from reportlab.pdfgen import canvas
# from reportlab.lib.units import mm

# # Define a custom canvas to add page numbers
# class NumberedCanvas(canvas.Canvas):
#     def __init__(self, *args, **kwargs):
#         canvas.Canvas.__init__(self, *args, **kwargs)
#         self._saved_page_states = []

#     def showPage(self):
#         self._saved_page_states.append(dict(self.__dict__))
#         self._startPage()

#     def save(self):
#         num_pages = len(self._saved_page_states)
#         for state in self._saved_page_states:
#             self.__dict__.update(state)
#             self.draw_page_number(num_pages)
#             canvas.Canvas.showPage(self)
#         canvas.Canvas.save(self)

#     def draw_page_number(self, page_count):
#         self.setFont("Helvetica", 9)
#         self.drawRightString(
#             200 * mm, 10 * mm, f"Page {self._pageNumber} of {page_count}"
#         )

# # Function to create invoice elements
# def create_invoice_elements(driver_name, data):
#     elements = []

#     # Define styles
#     styles = getSampleStyleSheet()
#     styles.add(
#         ParagraphStyle(name="InvoiceTitle", fontSize=18, leading=22, alignment=1)
#     )
#     styles.add(ParagraphStyle(name="InvoiceInfo", fontSize=12, leading=14))
#     styles.add(
#         ParagraphStyle(
#             name="TableHeader",
#             fontSize=12,
#             leading=14,
#             alignment=1,
#             fontName="Helvetica-Bold",
#         )
#     )
#     styles.add(ParagraphStyle(name="TableBody", fontSize=10, leading=12))

#     # Add Company Logo (Optional)
#     logo_path = "logo.png"  # Replace with your logo file path
#     if os.path.exists(logo_path):
#         logo = Image(logo_path, 2 * inch, inch)
#         elements.append(logo)
#         elements.append(Spacer(1, 12))

#     # Add Invoice Title
#     elements.append(Paragraph("Giant Transport Group LLC", styles["InvoiceTitle"]))
#     elements.append(Spacer(1, 12))
#     elements.append(Paragraph("Cashiering Receipt", styles["InvoiceTitle"]))
#     elements.append(Spacer(1, 24))

#     # Add Driver and Date Information
#     date_range = f"{data['DATE'].min().strftime('%m/%d/%Y')} - {data['DATE'].max().strftime('%m/%d/%Y')}"
#     elements.append(
#         Paragraph(f"Driver Name: <b>{driver_name}</b>", styles["InvoiceInfo"])
#     )
#     elements.append(
#         Paragraph(f"Date Range: <b>{date_range}</b>", styles["InvoiceInfo"])
#     )
#     elements.append(Spacer(1, 12))

#     # Create Trip Details Table
#     trip_data = data[
#         [
#             "DATE",
#             "TRIP CODE",
#             "TRIP NAME",
#             "MILES",
#             "GROSS PAY",
#             "DEDUCTION",
#             "SPIFF",
#             "NET PAY",
#         ]
#     ].copy()
#     trip_data["DATE"] = trip_data["DATE"].dt.strftime("%m/%d/%Y")

#     # Format Currency Fields
#     currency_fields = ["GROSS PAY", "DEDUCTION", "SPIFF", "NET PAY"]
#     for field in currency_fields:
#         trip_data[field] = trip_data[field].apply(lambda x: f"${x:,.2f}")

#     # Convert DataFrame to List of Lists
#     table_data = [trip_data.columns.tolist()] + trip_data.values.tolist()

#     # Define Table Style
#     table_style = TableStyle(
#         [
#             ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F2F2")),
#             ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
#             ("ALIGN", (0, 0), (-1, -1), "CENTER"),
#             ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
#             ("FONTSIZE", (0, 0), (-1, -1), 9),
#             ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
#             ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
#         ]
#     )

#     # Create Table
#     trip_table = Table(table_data, style=table_style, hAlign="CENTER")
#     elements.append(trip_table)
#     elements.append(Spacer(1, 12))

#     # Add Summary Information
#     total_miles = data["MILES"].sum()
#     total_gross_pay = data["GROSS PAY"].sum()
#     total_deduction = data["DEDUCTION"].sum()
#     total_spiff = data["SPIFF"].sum()
#     total_net_pay = data["NET PAY"].sum()

#     summary_data = [
#         ["Total Miles", total_miles],
#         ["Total Gross Pay", f"${total_gross_pay:,.2f}"],
#         ["Total Deductions", f"${total_deduction:,.2f}"],
#         ["Total SPIFF", f"${total_spiff:,.2f}"],
#         ["Total Net Pay", f"${total_net_pay:,.2f}"],
#     ]

#     # Create Summary Table
#     summary_table = Table(summary_data, hAlign="RIGHT", colWidths=[200, 100])
#     summary_table.setStyle(
#         TableStyle(
#             [
#                 ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
#                 ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
#             ]
#         )
#     )

#     elements.append(summary_table)
#     elements.append(Spacer(1, 24))

#     # Add Footer
#     elements.append(Paragraph("Thank you for your hard work!", styles["InvoiceInfo"]))

#     return elements

# # Function to generate the invoice PDF
# def generate_invoice(driver_name, data, output_dir):
#     # Ensure the output directory exists
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)

#     pdf_file = os.path.join(
#         output_dir, f"{driver_name.replace(' ', '_')}_invoice.pdf"
#     )
#     doc = SimpleDocTemplate(
#         pdf_file,
#         pagesize=LETTER,
#         rightMargin=30,
#         leftMargin=30,
#         topMargin=30,
#         bottomMargin=18,
#     )
#     elements = create_invoice_elements(driver_name, data)
#     doc.build(elements, canvasmaker=NumberedCanvas)
#     print(f"Generated invoice for {driver_name}")

# def main():
#     # Replace 'your_data.csv' with the path to your CSV file
#     csv_file = "data.csv"  # Update this to your CSV file name
#     output_dir = "invoices"  # Directory to save invoices

#     # Read CSV data
#     df = pd.read_csv(csv_file)

#     # Ensure correct data types
#     df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
#     df["GROSS PAY"] = pd.to_numeric(df["GROSS PAY"], errors="coerce")
#     df["DEDUCTION"] = pd.to_numeric(df["DEDUCTION"], errors="coerce")
#     df["SPIFF"] = pd.to_numeric(df["SPIFF"], errors="coerce")
#     df["NET PAY"] = pd.to_numeric(df["NET PAY"], errors="coerce")
#     df["MILES"] = pd.to_numeric(df["MILES"], errors="coerce")

#     # Handle missing values
#     df.fillna(0, inplace=True)

#     # Remove rows where DRIVER NAME is missing
#     df = df[df["DRIVER NAME"] != "-"]

#     # Group data by DRIVER NAME
#     grouped_data = df.groupby("DRIVER NAME")

#     for driver_name, group in grouped_data:
#         generate_invoice(driver_name, group, output_dir)

# if __name__ == "__main__":
#     main()




















# invoice_generator.py

import pandas as pd
import os
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image,
)
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, inch

# Custom canvas to add page numbers
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        self.drawRightString(
            200 * mm, 10 * mm, f"Page {self._pageNumber} of {page_count}"
        )

# Function to create invoice elements
# def create_invoice_elements(driver_name, data):
#     elements = []

#     # Define styles
#     styles = getSampleStyleSheet()
#     styles.add(
#         ParagraphStyle(name="InvoiceTitle", fontSize=18, leading=22, alignment=1)
#     )
#     styles.add(ParagraphStyle(name="InvoiceInfo", fontSize=12, leading=14))
#     styles.add(
#         ParagraphStyle(
#             name="TableHeader",
#             fontSize=12,
#             leading=14,
#             alignment=1,
#             fontName="Helvetica-Bold",
#         )
#     )
#     styles.add(ParagraphStyle(name="TableBody", fontSize=10, leading=12))

#     # Add Company Logo (Optional)
#     logo_path = "logo.png"  # Update with your logo file path
#     if os.path.exists(logo_path):
#         logo = Image(logo_path, 2 * inch, inch)
#         elements.append(logo)
#         elements.append(Spacer(1, 12))

#     # Add Invoice Title
#     elements.append(Paragraph("Giant Transport Group LLC", styles["InvoiceTitle"]))
#     elements.append(Spacer(1, 12))
#     elements.append(Paragraph("Cashiering Receipt", styles["InvoiceTitle"]))
#     elements.append(Spacer(1, 24))

#     # Add Driver and Date Information
#     date_range = f"{data['DATE'].min().strftime('%m/%d/%Y')} - " \
#                  f"{data['DATE'].max().strftime('%m/%d/%Y')}"
#     elements.append(
#         Paragraph(f"Driver Name: <b>{driver_name}</b>", styles["InvoiceInfo"])
#     )
#     elements.append(
#         Paragraph(f"Date Range: <b>{date_range}</b>", styles["InvoiceInfo"])
#     )
#     elements.append(Spacer(1, 12))

#     # Create Trip Details Table
#     trip_data = data[
#         [
#             "DATE",
#             "TRIP CODE",
#             "TRIP NAME",
#             "MILES",
#             "GROSS PAY",
#             "DEDUCTION",
#             "SPIFF",
#             "NET PAY",
#         ]
#     ].copy()
#     trip_data["DATE"] = trip_data["DATE"].dt.strftime("%m/%d/%Y")

#     # Format Currency Fields
#     currency_fields = ["GROSS PAY", "DEDUCTION", "SPIFF", "NET PAY"]
#     for field in currency_fields:
#         trip_data[field] = trip_data[field].apply(lambda x: f"${x:,.2f}")

#     # Convert DataFrame to list of lists
#     table_data = [trip_data.columns.tolist()] + trip_data.values.tolist()

#     # Define table style
#     table_style = TableStyle(
#         [
#             ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F2F2")),
#             ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
#             ("ALIGN", (0, 0), (-1, -1), "CENTER"),
#             ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
#             ("FONTSIZE", (0, 0), (-1, -1), 9),
#             ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
#             ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
#         ]
#     )

#     # Create table
#     trip_table = Table(table_data, style=table_style, hAlign="CENTER")
#     elements.append(trip_table)
#     elements.append(Spacer(1, 12))

#     # Add Summary Information
#     total_miles = data["MILES"].sum()
#     total_gross_pay = data["GROSS PAY"].sum()
#     total_deduction = data["DEDUCTION"].sum()
#     total_spiff = data["SPIFF"].sum()
#     total_net_pay = data["NET PAY"].sum()

#     summary_data = [
#         ["Total Miles", total_miles],
#         ["Total Gross Pay", f"${total_gross_pay:,.2f}"],
#         ["Total Deductions", f"${total_deduction:,.2f}"],
#         ["Total SPIFF", f"${total_spiff:,.2f}"],
#         ["Total Net Pay", f"${total_net_pay:,.2f}"],
#     ]

#     # Create summary table
#     summary_table = Table(summary_data, hAlign="RIGHT", colWidths=[200, 100])
#     summary_table.setStyle(
#         TableStyle(
#             [
#                 ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
#                 ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
#             ]
#         )
#     )

#     elements.append(summary_table)
#     elements.append(Spacer(1, 24))

#     # Add Footer
#     elements.append(Paragraph("Thank you for your hard work!", styles["InvoiceInfo"]))

#     return elements



# def create_invoice_elements(driver_name, data):
#     elements = []

#     # Define styles
#     styles = getSampleStyleSheet()
#     styles.add(ParagraphStyle(name="InvoiceTitle", fontSize=24, leading=28, alignment=1, textColor=colors.HexColor("#2E4053")))
#     styles.add(ParagraphStyle(name="SectionHeading", fontSize=16, leading=20, alignment=1, textColor=colors.HexColor("#1F618D")))
#     styles.add(ParagraphStyle(name="NormalText", fontSize=12, leading=14))
#     styles.add(ParagraphStyle(name="TableHeader", fontSize=10, leading=12, alignment=1, textColor=colors.white, fontName="Helvetica-Bold"))
#     styles.add(ParagraphStyle(name="TableBody", fontSize=10, leading=12))

#     # Add Company Logo (Optional)
#     logo_path = "logo.png"  # Update with your logo file path
#     if os.path.exists(logo_path):
#         logo = Image(logo_path, 2 * inch, inch)
#         elements.append(logo)
#         elements.append(Spacer(1, 12))

#     # Add Invoice Title
#     elements.append(Paragraph("Giant Transport Group LLC", styles["InvoiceTitle"]))
#     elements.append(Spacer(1, 12))
#     elements.append(Paragraph("Cashiering Receipt", styles["InvoiceTitle"]))
#     elements.append(Spacer(1, 24))

#     # Add Driver and Date Information
#     date_range = f"{data['DATE'].min().strftime('%m/%d/%Y')} - {data['DATE'].max().strftime('%m/%d/%Y')}"
#     elements.append(Paragraph(f"Driver Name: <b>{driver_name}</b>", styles["NormalText"]))
#     elements.append(Paragraph(f"Date Range: <b>{date_range}</b>", styles["NormalText"]))
#     elements.append(Spacer(1, 12))

#     # Add Section Heading for Trip Details
#     elements.append(Paragraph("Trip Details", styles["SectionHeading"]))
#     elements.append(Spacer(1, 12))

#     # Create Trip Details Table
#     trip_data = data[
#         [
#             "DATE",
#             "TRIP CODE",
#             "TRIP NAME",
#             "MILES",
#             "GROSS PAY",
#             "DEDUCTION",
#             "SPIFF",
#             "NET PAY",
#         ]
#     ].copy()
#     trip_data["DATE"] = trip_data["DATE"].dt.strftime("%m/%d/%Y")

#     # Format Currency Fields
#     currency_fields = ["GROSS PAY", "DEDUCTION", "SPIFF", "NET PAY"]
#     for field in currency_fields:
#         trip_data[field] = trip_data[field].apply(lambda x: f"${x:,.2f}")

#     # Convert DataFrame to list of lists
#     table_data = [trip_data.columns.tolist()] + trip_data.values.tolist()

#     # Define Table Style
#     table_style = TableStyle(
#         [
#             ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F618D")),
#             ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
#             ("ALIGN", (0, 0), (-1, -1), "CENTER"),
#             ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
#             ("FONTSIZE", (0, 0), (-1, -1), 9),
#             ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
#             ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F2F2F2")),
#             ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
#         ]
#     )

#     # Create Table
#     trip_table = Table(table_data, style=table_style, hAlign="CENTER")
#     elements.append(trip_table)

#     # Add Section Heading for Totals
#     elements.append(Spacer(1, 24))
#     elements.append(Paragraph("Summary", styles["SectionHeading"]))
#     elements.append(Spacer(1, 12))

#     # Calculate Totals
#     total_miles = data["MILES"].sum()
#     total_gross_pay = data["GROSS PAY"].sum()
#     total_deduction = data["DEDUCTION"].sum()
#     total_spiff = data["SPIFF"].sum()
#     total_net_pay = data["NET PAY"].sum()

#     # Prepare Data for Totals Table
#     totals_data = [
#         ["Total Miles", total_miles],
#         ["Total Gross Pay", f"${total_gross_pay:,.2f}"],
#         ["Total Deductions", f"${total_deduction:,.2f}"],
#         ["Total SPIFF", f"${total_spiff:,.2f}"],
#         ["Total Net Pay", f"${total_net_pay:,.2f}"],
#     ]

#     # Create Totals Table
#     totals_table = Table(totals_data, colWidths=[200, 100])
#     totals_table.setStyle(
#         TableStyle(
#             [
#                 ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F618D")),
#                 ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
#                 ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
#                 ("ALIGN", (0, 0), (-1, -1), "LEFT"),
#                 ("FONTSIZE", (0, 0), (-1, -1), 10),
#                 ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
#                 ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
#                 ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F2F2F2")),
#             ]
#         )
#     )

#     elements.append(totals_table)
#     elements.append(Spacer(1, 24))

#     # Add Footer
#     elements.append(Paragraph("Thank you for your hard work!", styles["NormalText"]))

#     return elements


# # Function to generate the invoice PDF
# def generate_invoice(driver_name, data, output_dir):
#     # Ensure driver_name is a string
#     driver_name = str(driver_name)

#     # Ensure the output directory exists
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)

#     # Create the PDF file path
#     pdf_file = os.path.join(
#         output_dir, f"{driver_name.replace(' ', '_')}_invoice.pdf"
#     )

#     # Create the PDF document
#     doc = SimpleDocTemplate(
#         pdf_file,
#         pagesize=LETTER,
#         rightMargin=30,
#         leftMargin=30,
#         topMargin=30,
#         bottomMargin=18,
#     )

#     elements = create_invoice_elements(driver_name, data)
#     doc.build(elements, canvasmaker=NumberedCanvas)
#     print(f"Generated invoice for {driver_name}")

# def main():
#     # Update this to your CSV file name
#     csv_file = "data.csv"  # Replace with your CSV file path
#     output_dir = "invoices"  # Directory to save invoices

#     # Read CSV data, ensuring DRIVER NAME is read as string
#     df = pd.read_csv(csv_file, dtype={"DRIVER NAME": str})

#     # Ensure correct data types
#     df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")

#     numeric_columns = ["GROSS PAY", "DEDUCTION", "SPIFF", "NET PAY", "MILES"]

#     # Clean and convert numeric columns
#     def clean_numeric(series):
#         series = series.replace('[\$,]', '', regex=True)
#         return pd.to_numeric(series, errors='coerce')

#     df[numeric_columns] = df[numeric_columns].apply(clean_numeric)

#     # Handle missing values
#     df[numeric_columns] = df[numeric_columns].fillna(0)

#     # Remove rows where DRIVER NAME is missing
#     df = df[df["DRIVER NAME"].notna()]

#     # Group data by DRIVER NAME
#     grouped_data = df.groupby("DRIVER NAME")

#     for driver_name, group in grouped_data:
#         generate_invoice(driver_name, group, output_dir)

# if __name__ == "__main__":
#     main()



# app.py
# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from io import BytesIO
import base64
from pdf_generation import generate_invoice


app = Flask(__name__)
CORS(app)

# Load environment variables (you can keep this if you have other env variables)

@app.route('/process_csv/', methods=['POST'])
def process_csv():
    try:
        file = request.files['file']
        if not file:
            return jsonify({'error': 'No file provided'}), 400

        df = pd.read_csv(file, dtype={"DRIVER NAME": str})

        # Handle missing values and data cleaning
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
        return jsonify({'error': str(e)}), 500

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

if __name__ == '__main__':
    app.run(debug=True)