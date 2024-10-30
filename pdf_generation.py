# pdf_generation.py
import os  # Add this line
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from flask_cors import CORS
from flask import Flask


# app = Flask(__name__)
# CORS(app)

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

    # Define styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="InvoiceTitle", fontSize=24, leading=28, alignment=1, textColor=colors.HexColor("#2E4053")))
    styles.add(ParagraphStyle(name="SectionHeading", fontSize=16, leading=20, alignment=1, textColor=colors.HexColor("#1F618D")))
    styles.add(ParagraphStyle(name="NormalText", fontSize=12, leading=14))
    styles.add(ParagraphStyle(name="TableHeader", fontSize=10, leading=12, alignment=1, textColor=colors.white, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="TableBody", fontSize=10, leading=12))

    # Add Company Logo (Optional)
    logo_path = "logo.png"  # Update with your logo file path
    if os.path.exists(logo_path):
        logo = Image(logo_path, 2 * inch, inch)
        elements.append(logo)
        elements.append(Spacer(1, 12))

    # Add Invoice Title
    elements.append(Paragraph("Giant Transport Group LLC", styles["InvoiceTitle"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Cashiering Receipt", styles["InvoiceTitle"]))
    elements.append(Spacer(1, 24))

    # Add Driver and Date Information
    date_range = f"{data['DATE'].min().strftime('%m/%d/%Y')} - {data['DATE'].max().strftime('%m/%d/%Y')}"
    elements.append(Paragraph(f"Driver Name: <b>{driver_name}</b>", styles["NormalText"]))
    elements.append(Paragraph(f"Date Range: <b>{date_range}</b>", styles["NormalText"]))
    elements.append(Spacer(1, 12))

    # Add Section Heading for Trip Details
    elements.append(Paragraph("Trip Details", styles["SectionHeading"]))
    elements.append(Spacer(1, 12))

    # Create Trip Details Table
    trip_data = data[
        [
            "DATE",
            "TRIP CODE",
            "TRIP NAME",
            "MILES",
            "GROSS PAY",
            "DEDUCTION",
            "SPIFF",
            "NET PAY",
        ]
    ].copy()
    trip_data["DATE"] = trip_data["DATE"].dt.strftime("%m/%d/%Y")

    # Format Currency Fields
    currency_fields = ["GROSS PAY", "DEDUCTION", "SPIFF", "NET PAY"]
    for field in currency_fields:
        trip_data[field] = trip_data[field].apply(lambda x: f"${x:,.2f}")

    # Convert DataFrame to list of lists
    table_data = [trip_data.columns.tolist()] + trip_data.values.tolist()

    # Define Table Style with Alternating Row Colors
    table_style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F618D")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]
    )

    # Apply Alternating Row Background Colors
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            bg_color = colors.HexColor("#FFFFFF")  # White
        else:
            bg_color = colors.HexColor("#F2F2F2")  # Light grey
        table_style.add('BACKGROUND', (0, i), (-1, i), bg_color)

    # Create Table
    trip_table = Table(table_data, style=table_style, hAlign="CENTER")
    elements.append(trip_table)

    # Add Section Heading for Totals
    elements.append(Spacer(1, 24))
    elements.append(Paragraph("Summary", styles["SectionHeading"]))
    elements.append(Spacer(1, 12))

    # Calculate Totals
    total_miles = data["MILES"].sum()
    total_gross_pay = data["GROSS PAY"].sum()
    total_deduction = data["DEDUCTION"].sum()
    total_spiff = data["SPIFF"].sum()
    total_net_pay = data["NET PAY"].sum()

    # Prepare Data for Totals Table
    totals_data = [
        ["Total Miles", total_miles],
        ["Total Gross Pay", f"${total_gross_pay:,.2f}"],
        ["Total Deductions", f"${total_deduction:,.2f}"],
        ["Total SPIFF", f"${total_spiff:,.2f}"],
        ["Total Net Pay", f"${total_net_pay:,.2f}"],
    ]

    # Create Totals Table
    totals_table = Table(totals_data, colWidths=[200, 100])
    totals_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F618D")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F2F2F2")),
            ]
        )
    )

    elements.append(totals_table)
    elements.append(Spacer(1, 24))

    # Add Footer
    elements.append(Paragraph("Thank you for your hard work!", styles["NormalText"]))

    return elements
