# # pdf_generation.py
# import os  # Add this line
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
# from reportlab.lib.pagesizes import LETTER
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
# from io import BytesIO
# from flask_cors import CORS
# from flask import Flask


# # app = Flask(__name__)
# # CORS(app)

# def generate_invoice(driver_name, data):
#     buffer = BytesIO()
#     doc = SimpleDocTemplate(
#         buffer,
#         pagesize=LETTER,
#         rightMargin=30,
#         leftMargin=30,
#         topMargin=30,
#         bottomMargin=18,
#     )
#     elements = create_invoice_elements(driver_name, data)
#     doc.build(elements)
#     pdf_value = buffer.getvalue()
#     buffer.close()
#     return pdf_value

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

#     # Define Table Style with Alternating Row Colors
#     table_style = TableStyle(
#         [
#             ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F618D")),
#             ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
#             ("ALIGN", (0, 0), (-1, -1), "CENTER"),
#             ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
#             ("FONTSIZE", (0, 0), (-1, -1), 9),
#             ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
#             ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
#         ]
#     )

#     # Apply Alternating Row Background Colors
#     for i in range(1, len(table_data)):
#         if i % 2 == 0:
#             bg_color = colors.HexColor("#FFFFFF")  # White
#         else:
#             bg_color = colors.HexColor("#F2F2F2")  # Light grey
#         table_style.add('BACKGROUND', (0, i), (-1, i), bg_color)

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





# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
# from reportlab.lib.pagesizes import LETTER
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
# from io import BytesIO
# import pandas as pd

# def generate_invoice(driver_name, data):
#     buffer = BytesIO()
#     doc = SimpleDocTemplate(
#         buffer,
#         pagesize=LETTER,
#         rightMargin=30,
#         leftMargin=30,
#         topMargin=30,
#         bottomMargin=18,
#     )
#     elements = create_invoice_elements(driver_name, data)
#     doc.build(elements)
#     pdf_value = buffer.getvalue()
#     buffer.close()
#     return pdf_value

# def create_invoice_elements(driver_name, data):
#     elements = []
    
#     # Define styles
#     styles = getSampleStyleSheet()
#     styles.add(ParagraphStyle(
#         name="CompanyName",
#         fontSize=16,
#         leading=20,
#         alignment=1,
#         spaceAfter=0,
#         spaceBefore=0
#     ))
#     styles.add(ParagraphStyle(
#         name="SubTitle",
#         fontSize=14,
#         leading=16,
#         alignment=1,
#         spaceAfter=20
#     ))
#     styles.add(ParagraphStyle(
#         name="NormalText",
#         fontSize=10,
#         leading=12
#     ))

#     # Add header
#     elements.append(Paragraph("Giant Transport Group LLC", styles["CompanyName"]))
    
#     # Add date range
#     date_range = f"Cashiering date {data['DATE'].min().strftime('%m/%d/%Y')} - {data['DATE'].max().strftime('%m/%d/%Y')}"
#     elements.append(Paragraph(date_range, styles["SubTitle"]))
    
#     # Create summary table
#     summary_data = [
#         ["Active", "Between Days", "Run Miles", "Gross", "SF", "InTel", "Net Pay"],
#         [
#             str(len(data)),
#             str((data['DATE'].max() - data['DATE'].min()).days + 1),
#             str(data['MILES'].sum()),
#             f"${data['GROSS PAY'].sum():.2f}",
#             f"${data['SPIFF'].sum():.2f}",
#             "$0.00",  # Placeholder for InTel
#             f"${data['NET PAY'].sum():.2f}"
#         ]
#     ]
    
#     summary_style = TableStyle([
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('FONTSIZE', (0, 0), (-1, -1), 9),
#         ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
#     ])
    
#     summary_table = Table(summary_data, style=summary_style)
#     elements.append(summary_table)
#     elements.append(Spacer(1, 20))
    
#     # Create daily details table
#     daily_data = [["Date", "Key", "Miles", "Gross", "NetPay"]]
    
#     for _, row in data.iterrows():
#         daily_data.append([
#             row['DATE'].strftime('%m/%d/%Y'),
#             str(row['TRIP CODE']),
#             str(row['MILES']),
#             f"${row['GROSS PAY']:.2f}",
#             f"${row['NET PAY']:.2f}"
#         ])
    
#     # Add totals row
#     daily_data.append([
#         "",
#         "",
#         str(data['MILES'].sum()),
#         f"${data['GROSS PAY'].sum():.2f}",
#         f"${data['NET PAY'].sum():.2f}"
#     ])
    
#     daily_style = TableStyle([
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('FONTSIZE', (0, 0), (-1, -1), 9),
#         ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
#         ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
#     ])
    
#     daily_table = Table(daily_data, style=daily_style)
#     elements.append(daily_table)
#     elements.append(Spacer(1, 10))
    
#     # Add average price per mile
#     total_miles = data['MILES'].sum()
#     total_gross = data['GROSS PAY'].sum()
#     avg_price = total_gross / total_miles if total_miles > 0 else 0
#     elements.append(Paragraph(f"Average Price per Miles ${avg_price:.2f}", styles["NormalText"]))
    
#     # Add driver details
#     elements.append(Spacer(1, 20))
#     elements.append(Paragraph("Details", styles["SubTitle"]))
#     elements.append(Paragraph("Person Name", styles["NormalText"]))
#     for _ in range(4):  # Repeat driver info 4 times as in example
#         elements.append(Paragraph(
#             f"{driver_name} 466 53 OCA Satellite (Milliones) PRG IB 02",
#             styles["NormalText"]
#         ))
    
#     # Add final summary
#     elements.append(Spacer(1, 20))
#     elements.append(Paragraph("Summary", styles["SubTitle"]))
#     elements.append(Paragraph("Person", styles["NormalText"]))
#     elements.append(Paragraph(
#         f"{driver_name} {data['DATE'].min().strftime('%m/%d/%Y')} - {data['DATE'].max().strftime('%m/%d/%Y')}",
#         styles["NormalText"]
#     ))
    
#     return elements

# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
# from reportlab.lib.pagesizes import LETTER
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
# from io import BytesIO
# import os

# def generate_invoice(driver_name, data):
#     buffer = BytesIO()
#     doc = SimpleDocTemplate(
#         buffer,
#         pagesize=LETTER,
#         rightMargin=30,
#         leftMargin=30,
#         topMargin=30,
#         bottomMargin=18,
#     )
#     elements = create_invoice_elements(driver_name, data)
#     doc.build(elements)
#     pdf_value = buffer.getvalue()
#     buffer.close()
#     return pdf_value

# def create_invoice_elements(driver_name, data):
#     elements = []
    
#     # Define colors
#     header_blue = colors.HexColor('#B8CCE4')  # Light blue for table headers
#     row_green = colors.HexColor('#93C47D')   # Green for certain rows
    
#     # Define styles
#     styles = getSampleStyleSheet()
#     styles.add(ParagraphStyle(
#         name="Header",
#         fontSize=14,
#         leading=16,
#         textColor=colors.HexColor('#0000CD'),  # Royal blue for header text
#         spaceBefore=0,
#         spaceAfter=0
#     ))
    
#     # Add logo and header in a table for proper alignment
#     logo_path = "logo.png"  # Update with your logo path
#     if os.path.exists(logo_path):
#         logo = Image(logo_path, 1.5*inch, 1.5*inch)
#         header_text = [
#             Paragraph("Cashiering Receipt", styles["Header"]),
#             Paragraph("Giant Transport Group LLC", styles["Header"]),
#             Paragraph(f"Cashiering date {data['DATE'].min().strftime('%m/%d/%Y')} - {data['DATE'].max().strftime('%m/%d/%Y')}", styles["Header"])
#         ]
#         header_table = Table(
#             [[logo, header_text]],
#             colWidths=[2*inch, 4*inch]
#         )
#         header_table.setStyle(TableStyle([
#             ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ]))
#         elements.append(header_table)
    
#     elements.append(Spacer(1, 20))
#     elements.append(Paragraph("Giant Transport Group LLC", styles["Header"]))
#     elements.append(Spacer(1, 20))
    
#     # Create summary table
#     summary_data = [
#         ["Summary"],
#         ["Person", "Active Between", "Days", "Run", "Miles", "Gross", "SF", "InTel", "Net Pay"],
#         [
#             driver_name,
#             f"{data['DATE'].min().strftime('%m/%d/%Y')} - {data['DATE'].max().strftime('%m/%d/%Y')}",
#             "4",
#             "14",
#             str(data['MILES'].sum()),
#             f"${data['GROSS PAY'].sum():.2f}",
#             f"${data['SPIFF'].sum():.2f}",
#             "$0.00",
#             f"${data['NET PAY'].sum():.2f}"
#         ]
#     ]
    
#     summary_style = TableStyle([
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('SPAN', (0, 0), (-1, 0)),  # Span the "Summary" cell across all columns
#         ('BACKGROUND', (0, 0), (-1, 0), header_blue),
#         ('BACKGROUND', (0, 1), (-1, 1), row_green),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#         ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#     ])
    
#     summary_table = Table(summary_data, colWidths=[1.2*inch]*9)
#     summary_table.setStyle(summary_style)
#     elements.append(summary_table)
#     elements.append(Spacer(1, 20))
    
#     # Create details table
#     details_data = [
#         ["Details"],
#         ["Person", "Date", "Key", "Name", "Milles", "Gross", "NetPay"]
#     ]
    
#     for _, row in data.iterrows():
#         details_data.append([
#             driver_name,
#             row['DATE'].strftime('%m/%d/%Y'),
#             "",  # Key column
#             "466 53 OCA Satellite (Milliones) PRG IB 02",
#             str(row['MILES']),
#             f"${row['GROSS PAY']:.2f}",
#             f"${row['NET PAY']:.2f}"
#         ])
    
#     # Add empty row
#     details_data.append([""] * 7)
    
#     # Add average and total rows
#     avg_price = data['GROSS PAY'].sum() / data['MILES'].sum() if data['MILES'].sum() > 0 else 0
#     details_data.append(["Average Price per Miles", "", "", "", "", "", f"${avg_price:.2f}"])
#     details_data.append(["Total NET", "", "", "", str(data['MILES'].sum()), f"${data['GROSS PAY'].sum():.2f}", f"${data['NET PAY'].sum():.2f}"])
    
#     details_style = TableStyle([
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('SPAN', (0, 0), (-1, 0)),  # Span the "Details" cell across all columns
#         ('BACKGROUND', (0, 0), (-1, 0), header_blue),
#         ('BACKGROUND', (0, 1), (-1, 1), row_green),
#         ('BACKGROUND', (0, -1), (-1, -1), row_green),
#         ('BACKGROUND', (0, -2), (-1, -2), row_green),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#         ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#     ])
    
#     col_widths = [1.2*inch, 1*inch, 0.8*inch, 3*inch, 0.8*inch, 1*inch, 1*inch]
#     details_table = Table(details_data, colWidths=col_widths)
#     details_table.setStyle(details_style)
#     elements.append(details_table)
    
#     return elements





# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
# from reportlab.lib.pagesizes import LETTER, landscape
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
# from io import BytesIO
# import os

# def generate_invoice(driver_name, data):
#     buffer = BytesIO()
#     doc = SimpleDocTemplate(
#         buffer,
#         pagesize=LETTER,
#         rightMargin=30,
#         leftMargin=30,
#         topMargin=30,
#         bottomMargin=18,
#     )
#     elements = create_invoice_elements(driver_name, data)
#     doc.build(elements)
#     pdf_value = buffer.getvalue()
#     buffer.close()
#     return pdf_value

# def create_invoice_elements(driver_name, data):
#     elements = []
    
#     # Define colors
#     header_blue = colors.HexColor('#B8CCE4')  # Light blue for table headers
#     row_green = colors.HexColor('#93C47D')   # Green for certain rows
    
#     # Define styles
#     styles = getSampleStyleSheet()
#     styles.add(ParagraphStyle(
#         name="Header",
#         fontSize=14,
#         leading=16,
#         textColor=colors.HexColor('#0000CD'),
#         spaceBefore=0,
#         spaceAfter=0
#     ))
    
#     # Add logo and header in a table
#     logo_path = "logo.png"
#     if os.path.exists(logo_path):
#         logo = Image(logo_path, 1.5*inch, 1.5*inch)
#         header_text = [
#             Paragraph("Cashiering Receipt", styles["Header"]),
#             Paragraph("Giant Transport Group LLC", styles["Header"]),
#             Paragraph(f"Cashiering date {data['DATE'].min().strftime('%m/%d/%Y')} - {data['DATE'].max().strftime('%m/%d/%Y')}", styles["Header"])
#         ]
#         header_table = Table(
#             [[logo, header_text]],
#             colWidths=[2*inch, 4*inch]
#         )
#         header_table.setStyle(TableStyle([
#             ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ]))
#         elements.append(header_table)
    
#     elements.append(Spacer(1, 20))
#     elements.append(Paragraph("Giant Transport Group LLC", styles["Header"]))
#     elements.append(Spacer(1, 20))
    
#     # Calculate active days
#     active_days = (data['DATE'].max() - data['DATE'].min()).days + 1
    
#     # Create summary table with simplified columns
#     summary_data = [
#         ["Summary"],
#         ["Person", "Active Between", "Days", "Run", "Miles", "SF", "InTel", "Net Pay"],
#         [
#             driver_name,
#             f"{data['DATE'].min().strftime('%m/%d/%Y')} - {data['DATE'].max().strftime('%m/%d/%Y')}",
#             str(active_days),
#             str(len(data)),
#             str(data['MILES'].sum()),
#             f"${data['SPIFF'].sum():.2f}",
#             "$0.00",
#             f"${data['GROSS PAY'].sum() * 0.75:.2f}"  # Net Pay is 75% of Gross
#         ]
#     ]
    
#     summary_style = TableStyle([
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('SPAN', (0, 0), (-1, 0)),
#         ('BACKGROUND', (0, 0), (-1, 0), header_blue),
#         ('BACKGROUND', (0, 1), (-1, 1), row_green),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#         ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#     ])
    
#     # Adjust column widths for better fit
#     summary_table = Table(summary_data, colWidths=[1.5*inch, 2*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 1*inch])
#     summary_table.setStyle(summary_style)
#     elements.append(summary_table)
#     elements.append(Spacer(1, 20))
    
#     # Create details table with simplified columns
#     details_data = [
#         ["Details"],
#         ["Person", "Date", "Name", "Miles", "NetPay"]
#     ]
    
#     # Add rows with calculated Net Pay
#     for _, row in data.iterrows():
#         net_pay = row['GROSS PAY'] * 0.75  # Calculate Net Pay as 75% of Gross
#         details_data.append([
#             driver_name,
#             row['DATE'].strftime('%m/%d/%Y'),
#             "466 53 OCA Satellite (Milliones) PRG IB 02",
#             str(row['MILES']),
#             f"${net_pay:.2f}"
#         ])
    
#     # Add empty row
#     details_data.append([""] * 5)
    
#     # Add average and total rows
#     total_miles = data['MILES'].sum()
#     total_gross = data['GROSS PAY'].sum()
#     avg_price = total_gross / total_miles if total_miles > 0 else 0
    
#     details_data.append(["Average Price per Miles", "", "", "", f"${avg_price:.2f}"])
#     details_data.append(["Total NET", "", "", str(total_miles), f"${total_gross * 0.75:.2f}"])
    
#     details_style = TableStyle([
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('ALIGN', (2, 2), (2, -3), 'LEFT'),  # Left align the Name column
#         ('SPAN', (0, 0), (-1, 0)),
#         ('BACKGROUND', (0, 0), (-1, 0), header_blue),
#         ('BACKGROUND', (0, 1), (-1, 1), row_green),
#         ('BACKGROUND', (0, -1), (-1, -1), row_green),
#         ('BACKGROUND', (0, -2), (-1, -2), row_green),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#         ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#     ])
    
#     # Adjust column widths for better fit
#     col_widths = [1.5*inch, 1*inch, 4*inch, 1*inch, 1*inch]
#     details_table = Table(details_data, colWidths=col_widths)
#     details_table.setStyle(details_style)
#     elements.append(details_table)
    
#     return elements



# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
# from reportlab.lib.pagesizes import LETTER
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
# from io import BytesIO
# import os

# def create_paragraph_cell(text, style_name="Normal"):
#     styles = getSampleStyleSheet()
#     return Paragraph(text, styles[style_name])

# def generate_invoice(driver_name, data):
#     buffer = BytesIO()
#     doc = SimpleDocTemplate(
#         buffer,
#         pagesize=LETTER,
#         rightMargin=30,
#         leftMargin=30,
#         topMargin=30,
#         bottomMargin=18,
#     )
#     elements = create_invoice_elements(driver_name, data)
#     doc.build(elements)
#     pdf_value = buffer.getvalue()
#     buffer.close()
#     return pdf_value

# def create_invoice_elements(driver_name, data):
#     elements = []
    
#     # Define colors
#     header_blue = colors.HexColor('#B8CCE4')
#     row_green = colors.HexColor('#93C47D')
    
#     # Define styles
#     styles = getSampleStyleSheet()
#     styles.add(ParagraphStyle(
#         name="Header",
#         fontSize=14,
#         leading=16,
#         textColor=colors.HexColor('#0000CD'),
#         spaceBefore=0,
#         spaceAfter=0
#     ))
    
#     # Add header with logo
#     header_content = [
#         [
#             Image("logo.png", 1.5*inch, 1.5*inch) if os.path.exists("logo.png") else "",
#             [
#                 Paragraph('<font color="blue">Cashiering Receipt</font>', styles["Header"]),
#                 Paragraph('<font color="blue">Giant Transport Group LLC</font>', styles["Header"]),
#                 Paragraph(f'<font color="blue">Cashiering date {data["DATE"].min().strftime("%m/%d/%Y")} - {data["DATE"].max().strftime("%m/%d/%Y")}</font>', styles["Header"])
#             ]
#         ]
#     ]
    
#     header_table = Table(header_content, colWidths=[2*inch, 4*inch])
#     header_table.setStyle(TableStyle([
#         ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#     ]))
#     elements.append(header_table)
#     elements.append(Spacer(1, 20))
    
#     # Add company name
#     elements.append(Paragraph('<font color="blue">Giant Transport Group LLC</font>', styles["Header"]))
#     elements.append(Spacer(1, 20))
    
#     # Calculate active days
#     active_days = (data['DATE'].max() - data['DATE'].min()).days + 1
    
#     # Create summary table with wrapped text
#     summary_data = [
#         [Paragraph("Summary", styles["Normal"])],
#         [
#             Paragraph("Person", styles["Normal"]),
#             Paragraph("Active Between", styles["Normal"]),
#             Paragraph("Days", styles["Normal"]),
#             Paragraph("Run", styles["Normal"]),
#             Paragraph("Miles", styles["Normal"]),
#             Paragraph("SF", styles["Normal"]),
#             Paragraph("InTel", styles["Normal"]),
#             Paragraph("Net Pay", styles["Normal"])
#         ],
#         [
#             Paragraph(driver_name, styles["Normal"]),
#             Paragraph(f"{data['DATE'].min().strftime('%m/%d/%Y')} - {data['DATE'].max().strftime('%m/%d/%Y')}", styles["Normal"]),
#             str(active_days),
#             str(len(data)),
#             str(data['MILES'].sum()),
#             f"${data['SPIFF'].sum():.2f}",
#             "$0.00",
#             f"${data['GROSS PAY'].sum() * 0.75:.2f}"
#         ]
#     ]
    
#     summary_style = TableStyle([
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('SPAN', (0, 0), (-1, 0)),
#         ('BACKGROUND', (0, 0), (-1, 0), header_blue),
#         ('BACKGROUND', (0, 1), (-1, 1), row_green),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#         ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('LEFTPADDING', (0, 0), (-1, -1), 5),
#         ('RIGHTPADDING', (0, 0), (-1, -1), 5),
#     ])
    
#     summary_table = Table(summary_data, colWidths=[1.5*inch, 1.7*inch, 0.6*inch, 0.6*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.9*inch])
#     summary_table.setStyle(summary_style)
#     elements.append(summary_table)
#     elements.append(Spacer(1, 20))
    
#     # Create details table with wrapped text
#     details_data = [
#         [Paragraph("Details", styles["Normal"])],
#         [
#             Paragraph("Person", styles["Normal"]),
#             Paragraph("Date", styles["Normal"]),
#             Paragraph("Name", styles["Normal"]),
#             Paragraph("Miles", styles["Normal"]),
#             Paragraph("NetPay", styles["Normal"])
#         ]
#     ]
    
#     # Add rows with wrapped text
#     for _, row in data.iterrows():
#         net_pay = row['GROSS PAY'] * 0.75
#         details_data.append([
#             Paragraph(driver_name, styles["Normal"]),
#             row['DATE'].strftime('%m/%d/%Y'),
#             Paragraph("466 53 OCA Satellite (Milliones) PRG IB 02", styles["Normal"]),
#             str(row['MILES']),
#             f"${net_pay:.2f}"
#         ])
    
#     # Add empty row
#     details_data.append([""] * 5)
    
#     # Add average and total rows
#     total_miles = data['MILES'].sum()
#     total_gross = data['GROSS PAY'].sum()
#     avg_price = total_gross / total_miles if total_miles > 0 else 0
    
#     details_data.append([Paragraph("Average Price per Miles", styles["Normal"]), "", "", "", f"${avg_price:.2f}"])
#     details_data.append([Paragraph("Total NET", styles["Normal"]), "", "", str(total_miles), f"${total_gross * 0.75:.2f}"])
    
#     details_style = TableStyle([
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('ALIGN', (2, 2), (2, -3), 'LEFT'),
#         ('SPAN', (0, 0), (-1, 0)),
#         ('BACKGROUND', (0, 0), (-1, 0), header_blue),
#         ('BACKGROUND', (0, 1), (-1, 1), row_green),
#         ('BACKGROUND', (0, -1), (-1, -1), row_green),
#         ('BACKGROUND', (0, -2), (-1, -2), row_green),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#         ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('LEFTPADDING', (0, 0), (-1, -1), 5),
#         ('RIGHTPADDING', (0, 0), (-1, -1), 5),
#     ])
    
#     col_widths = [1.5*inch, 1*inch, 3.5*inch, 0.8*inch, 0.8*inch]
#     details_table = Table(details_data, colWidths=col_widths)
#     details_table.setStyle(details_style)
#     elements.append(details_table)
    
#     return elements




# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
# from reportlab.lib.pagesizes import LETTER
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
# from io import BytesIO
# import os

# def calculate_net_pay(driver_name: str, gross_pay: float) -> float:
#     """Calculate net pay based on driver-specific rules"""
#     if driver_name == "Azzedine  Boumeraou":
#         return gross_pay  # 100% of income
#     elif driver_name == "Djebar  Kacimi":
#         return gross_pay + 600  # All income plus $600
#     elif driver_name == "Bilal  Bouhssane":
#         return gross_pay * 0.8  # 80% of income
#     else:
#         return gross_pay * 0.75  # Default 75% of income

# def create_paragraph_cell(text, style_name="Normal"):
#     styles = getSampleStyleSheet()
#     return Paragraph(text, styles[style_name])

# def generate_invoice(driver_name, data):
#     buffer = BytesIO()
#     doc = SimpleDocTemplate(
#         buffer,
#         pagesize=LETTER,
#         rightMargin=30,
#         leftMargin=30,
#         topMargin=30,
#         bottomMargin=18,
#     )
#     elements = create_invoice_elements(driver_name, data)
#     doc.build(elements)
#     pdf_value = buffer.getvalue()
#     buffer.close()
#     return pdf_value

# def create_invoice_elements(driver_name, data):
#     elements = []
    
#     # Define colors
#     header_blue = colors.HexColor('#B8CCE4')
#     row_green = colors.HexColor('#93C47D')
    
#     # Define styles
#     styles = getSampleStyleSheet()
#     styles.add(ParagraphStyle(
#         name="Header",
#         fontSize=14,
#         leading=16,
#         textColor=colors.HexColor('#0000CD'),
#         spaceBefore=0,
#         spaceAfter=0
#     ))
    
#     # Add header with logo
#     header_content = [
#         [
#             Image("logo.png", 1.5*inch, 1.5*inch) if os.path.exists("logo.png") else "",
#             [
#                 Paragraph('<font color="blue">Cashiering Receipt</font>', styles["Header"]),
#                 Paragraph('<font color="blue">Giant Transport Group LLC</font>', styles["Header"]),
#                 Paragraph(f'<font color="blue">Cashiering date {data["DATE"].min().strftime("%m/%d/%Y")} - {data["DATE"].max().strftime("%m/%d/%Y")}</font>', styles["Header"])
#             ]
#         ]
#     ]
    
#     header_table = Table(header_content, colWidths=[2*inch, 4*inch])
#     header_table.setStyle(TableStyle([
#         ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#     ]))
#     elements.append(header_table)
#     elements.append(Spacer(1, 20))
    
#     # Add company name
#     elements.append(Paragraph('<font color="blue">Giant Transport Group LLC</font>', styles["Header"]))
#     elements.append(Spacer(1, 20))
    
#     # Calculate active days
#     active_days = (data['DATE'].max() - data['DATE'].min()).days + 1
    
#     # Calculate total net pay for summary
#     total_gross = data['GROSS PAY'].sum()
#     print(driver_name)
#     total_net = calculate_net_pay(driver_name, total_gross)
    
#     # Create summary table with wrapped text
#     summary_data = [
#         [Paragraph("Summary", styles["Normal"])],
#         [
#             Paragraph("Person", styles["Normal"]),
#             Paragraph("Active Between", styles["Normal"]),
#             Paragraph("Days", styles["Normal"]),
#             Paragraph("Run", styles["Normal"]),
#             Paragraph("Miles", styles["Normal"]),
#             Paragraph("SF", styles["Normal"]),
#             Paragraph("InTel", styles["Normal"]),
#             Paragraph("Net Pay", styles["Normal"])
#         ],
#         [
#             Paragraph(driver_name, styles["Normal"]),
#             Paragraph(f"{data['DATE'].min().strftime('%m/%d/%Y')} - {data['DATE'].max().strftime('%m/%d/%Y')}", styles["Normal"]),
#             str(active_days),
#             str(len(data)),
#             str(data['MILES'].sum()),
#             f"${data['SPIFF'].sum():.2f}",
#             "$0.00",
#             f"${total_net:.2f}"
#         ]
#     ]
    
#     summary_style = TableStyle([
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('SPAN', (0, 0), (-1, 0)),
#         ('BACKGROUND', (0, 0), (-1, 0), header_blue),
#         ('BACKGROUND', (0, 1), (-1, 1), row_green),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#         ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('LEFTPADDING', (0, 0), (-1, -1), 5),
#         ('RIGHTPADDING', (0, 0), (-1, -1), 5),
#     ])
    
#     summary_table = Table(summary_data, colWidths=[1.5*inch, 1.7*inch, 0.6*inch, 0.6*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.9*inch])
#     summary_table.setStyle(summary_style)
#     elements.append(summary_table)
#     elements.append(Spacer(1, 20))
    
#     # Create details table with wrapped text
#     details_data = [
#         [Paragraph("Details", styles["Normal"])],
#         [
#             Paragraph("Person", styles["Normal"]),
#             Paragraph("Date", styles["Normal"]),
#             Paragraph("Name", styles["Normal"]),
#             Paragraph("Miles", styles["Normal"]),
#             Paragraph("NetPay", styles["Normal"])
#         ]
#     ]
    
#     # Add rows with wrapped text and custom net pay calculations
#     for _, row in data.iterrows():
#         net_pay = calculate_net_pay(driver_name, row['GROSS PAY'])
#         details_data.append([
#             Paragraph(driver_name, styles["Normal"]),
#             row['DATE'].strftime('%m/%d/%Y'),
#             Paragraph("466 53 OCA Satellite (Milliones) PRG IB 02", styles["Normal"]),
#             str(row['MILES']),
#             f"${net_pay:.2f}"
#         ])
    
#     # Add empty row
#     details_data.append([""] * 5)
    
#     # Add average and total rows
#     total_miles = data['MILES'].sum()
#     avg_price = total_gross / total_miles if total_miles > 0 else 0
    
#     details_data.append([Paragraph("Average Price per Miles", styles["Normal"]), "", "", "", f"${avg_price:.2f}"])
#     details_data.append([Paragraph("Total NET", styles["Normal"]), "", "", str(total_miles), f"${total_net:.2f}"])
    
#     details_style = TableStyle([
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('ALIGN', (2, 2), (2, -3), 'LEFT'),
#         ('SPAN', (0, 0), (-1, 0)),
#         ('BACKGROUND', (0, 0), (-1, 0), header_blue),
#         ('BACKGROUND', (0, 1), (-1, 1), row_green),
#         ('BACKGROUND', (0, -1), (-1, -1), row_green),
#         ('BACKGROUND', (0, -2), (-1, -2), row_green),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#         ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('LEFTPADDING', (0, 0), (-1, -1), 5),
#         ('RIGHTPADDING', (0, 0), (-1, -1), 5),
#     ])
    
#     col_widths = [1.5*inch, 1*inch, 3.5*inch, 0.8*inch, 0.8*inch]
#     details_table = Table(details_data, colWidths=col_widths)
#     details_table.setStyle(details_style)
#     elements.append(details_table)
    
#     return elements



from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
import os

def calculate_net_pay(driver_name: str, gross_pay: float, is_final_total: bool = False) -> float:
    """Calculate net pay based on driver-specific rules"""
    if driver_name == "Azzedine  Boumeraou":
        return gross_pay  # 100% of income
    elif driver_name == "Djebar  Kacimi":
        base_pay = gross_pay  # Regular calculation for individual rows
        return base_pay + 600 if is_final_total else base_pay  # Only add $600 to final total
    elif driver_name == "Bilal  Bouhssane":
        return gross_pay * 0.8  # 80% of income
    else:
        return gross_pay * 0.75  # Default 75% of income

def create_paragraph_cell(text, style_name="Normal"):
    styles = getSampleStyleSheet()
    return Paragraph(text, styles[style_name])

def generate_invoice(driver_name, data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=18,
    )
    elements = create_invoice_elements(driver_name, data)
    doc.build(elements)
    pdf_value = buffer.getvalue()
    buffer.close()
    return pdf_value

def create_invoice_elements(driver_name, data):
    elements = []
    
    # Define colors
    header_blue = colors.HexColor('#B8CCE4')
    row_green = colors.HexColor('#93C47D')
    
    # Define styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="Header",
        fontSize=14,
        leading=16,
        textColor=colors.HexColor('#0000CD'),
        spaceBefore=0,
        spaceAfter=0
    ))
    
    # Add header with logo
    header_content = [
        [
            Image("logo.png", 1.5*inch, 1.5*inch) if os.path.exists("logo.png") else "",
            [
                Paragraph('<font color="blue">Cashiering Receipt</font>', styles["Header"]),
                Paragraph('<font color="blue">Giant Transport Group LLC</font>', styles["Header"]),
                Paragraph(f'<font color="blue">Cashiering date {data["DATE"].min().strftime("%m/%d/%Y")} - {data["DATE"].max().strftime("%m/%d/%Y")}</font>', styles["Header"])
            ]
        ]
    ]
    
    header_table = Table(header_content, colWidths=[2*inch, 4*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))
    
    # Add company name
    elements.append(Paragraph('<font color="blue">Giant Transport Group LLC</font>', styles["Header"]))
    elements.append(Spacer(1, 20))
    
    # Calculate active days
    active_days = (data['DATE'].max() - data['DATE'].min()).days + 1
    
    # Calculate total net pay for summary
    total_gross = data['GROSS PAY'].sum()
    total_net = calculate_net_pay(driver_name, total_gross, is_final_total=True)
    
    # Create summary table with wrapped text
    summary_data = [
        [Paragraph("Summary", styles["Normal"])],
        [
            Paragraph("Person", styles["Normal"]),
            Paragraph("Active Between", styles["Normal"]),
            Paragraph("Days", styles["Normal"]),
            Paragraph("Run", styles["Normal"]),
            Paragraph("Miles", styles["Normal"]),
            Paragraph("SF", styles["Normal"]),
            Paragraph("InTel", styles["Normal"]),
            Paragraph("Net Pay", styles["Normal"])
        ],
        [
            Paragraph(driver_name, styles["Normal"]),
            Paragraph(f"{data['DATE'].min().strftime('%m/%d/%Y')} - {data['DATE'].max().strftime('%m/%d/%Y')}", styles["Normal"]),
            str(active_days),
            str(len(data)),
            str(data['MILES'].sum()),
            f"${data['SPIFF'].sum():.2f}",
            "$0.00",
            f"${total_net:.2f}"
        ]
    ]
    
    summary_style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('SPAN', (0, 0), (-1, 0)),
        ('BACKGROUND', (0, 0), (-1, 0), header_blue),
        ('BACKGROUND', (0, 1), (-1, 1), row_green),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ])
    
    summary_table = Table(summary_data, colWidths=[1.5*inch, 1.7*inch, 0.6*inch, 0.6*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.9*inch])
    summary_table.setStyle(summary_style)
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Create details table with wrapped text
    details_data = [
        [Paragraph("Details", styles["Normal"])],
        [
            Paragraph("Person", styles["Normal"]),
            Paragraph("Date", styles["Normal"]),
            Paragraph("Name", styles["Normal"]),
            Paragraph("Miles", styles["Normal"]),
            Paragraph("NetPay", styles["Normal"])
        ]
    ]
    
    # Add rows with wrapped text and regular net pay calculations
    total_miles = 0
    regular_total_net = 0
    
    for _, row in data.iterrows():
        # Calculate regular net pay without bonus
        net_pay = calculate_net_pay(driver_name, row['GROSS PAY'], is_final_total=False)
        regular_total_net += net_pay
        total_miles += row['MILES']
        
        details_data.append([
            Paragraph(driver_name, styles["Normal"]),
            row['DATE'].strftime('%m/%d/%Y'),
            Paragraph("466 53 OCA Satellite (Milliones) PRG IB 02", styles["Normal"]),
            str(row['MILES']),
            f"${net_pay:.2f}"
        ])
    
    # Add empty row
    details_data.append([""] * 5)
    
    # Add average and total rows
    avg_price = total_gross / total_miles if total_miles > 0 else 0
    
    details_data.append([Paragraph("Average Price per Miles", styles["Normal"]), "", "", "", f"${avg_price:.2f}"])
    details_data.append([Paragraph("Total NET", styles["Normal"]), "", "", str(total_miles), f"${total_net:.2f}"])
    
    details_style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (2, 2), (2, -3), 'LEFT'),
        ('SPAN', (0, 0), (-1, 0)),
        ('BACKGROUND', (0, 0), (-1, 0), header_blue),
        ('BACKGROUND', (0, 1), (-1, 1), row_green),
        ('BACKGROUND', (0, -1), (-1, -1), row_green),
        ('BACKGROUND', (0, -2), (-1, -2), row_green),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ])
    
    col_widths = [1.5*inch, 1*inch, 3.5*inch, 0.8*inch, 0.8*inch]
    details_table = Table(details_data, colWidths=col_widths)
    details_table.setStyle(details_style)
    elements.append(details_table)
    
    return elements