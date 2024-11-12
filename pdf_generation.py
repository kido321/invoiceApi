#pdf_generation
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
import os
import pandas as pd

def calculate_net_pay(driver_name: str, gross_pay: float, is_final_total: bool = False) -> float:
    """Calculate net pay based on driver-specific rules"""
    if driver_name == "Azzedine  Boumeraou":
        return gross_pay  # 100% of income
    elif driver_name == "Djebar  Kacimi":
        base_pay = gross_pay  # Regular calculation for individual rows
        return base_pay + 600 if is_final_total else base_pay  # Only add $600 to final total
    elif driver_name == "Bilal  Bouhssane":
        return gross_pay * 0.8  # 80% of income
    elif driver_name == "Abdul Latif Hassani":
        print(gross_pay, 'gross_pay' , driver_name)
        return gross_pay * 0.73
    elif driver_name == "Chadi  Tebah":
        return gross_pay * 0.73
    elif driver_name == "Fatsah  Kennouche ":
        print(gross_pay, 'gross_pay')
        return gross_pay * 0.73
    elif driver_name == "Ghulam  Sarwar Safi":
        return gross_pay * 0.73
    elif driver_name == "Inamullah  Hamraz":
        return gross_pay * 0.73
    elif driver_name == "LWABOSH B PUKA":
        return gross_pay * 0.73
    elif driver_name == "Mustapa  Quraishi":
        return gross_pay * 0.73
    elif driver_name == "Najibullah  Halimi":
        return gross_pay * 0.73
    elif driver_name == "Samuel Suzi":
        return gross_pay * 0.73
    elif driver_name == "Sheraqa Shoresh":
        return gross_pay * 0.73
    elif driver_name == "Tarun Vachani":
        return gross_pay * 0.73
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
    row_green = colors.HexColor('#6AA84F')
    title_blue = colors.HexColor('#000066')
    
    # Define styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="Header",
        fontSize=12,
        leading=14,
        textColor=title_blue,
        spaceBefore=0,
        spaceAfter=0,
        fontName='Helvetica-Bold'
    ))
    
    # Add a bold style for section headers
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontSize=9,
        leading=11,
        alignment=1,  # Center alignment
        fontName='Helvetica-Bold'
    ))
    
    # Add header with logo
    header_content = [
        [
            Image("logo.png", 1.5*inch, 1.5*inch) if os.path.exists("logo.png") else "",
            [
                Paragraph('Cashiering Receipt', styles["Header"]),
                Paragraph('Giant Transport Group LLC', styles["Header"]),
                Paragraph(f'Cashiering date {data["DATE"].min().strftime("%m/%d/%Y")} - {data["DATE"].max().strftime("%m/%d/%Y")}', styles["Header"])
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
    elements.append(Paragraph('Giant Transport Group LLC', styles["Header"]))
    elements.append(Spacer(1, 20))
    
    # Calculate active days
    active_days = (data['DATE'].max() - data['DATE'].min()).days + 1
    
    # Calculate total net pay and average price per mile for summary
    total_gross = data['GROSS PAY'].sum()
    total_net = calculate_net_pay(driver_name, total_gross, is_final_total=True)
    total_miles = data['MILES'].sum()
    avg_price = total_gross / total_miles if total_miles > 0 else 0
    
    # Modified normal style for smaller text
    styles["Normal"].fontSize = 9
    
    # Create summary table with wrapped text
    summary_data = [
        [Paragraph("Summary", styles["SectionHeader"])],  # Using bold centered style
        [
            Paragraph("Person", styles["Normal"]),
            Paragraph("Active Between", styles["Normal"]),
            Paragraph("Days", styles["Normal"]),
            Paragraph("Run", styles["Normal"]),
            Paragraph("Miles", styles["Normal"]),
            Paragraph("Average Price Per Mile", styles["Normal"]),
            Paragraph("Net Pay", styles["Normal"])
            
        ],
        [
            Paragraph(driver_name, styles["Normal"]),
            Paragraph(f"{data['DATE'].min().strftime('%m/%d/%Y')} - {data['DATE'].max().strftime('%m/%d/%Y')}", styles["Normal"]),
            str(active_days),
            str(len(data)),
            str(int(total_miles)),
            f"${avg_price:.2f}",
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
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ])
    
    summary_table = Table(summary_data, colWidths=[1.83*inch, 1.5*inch, 0.5*inch, 0.5*inch, 0.6*inch, 1.8*inch,0.85*inch])
    summary_table.setStyle(summary_style)
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Group data by date and calculate aggregates
    grouped_data = data.groupby('DATE').agg({
        'MILES': 'sum',
        'GROSS PAY': 'sum'
    }).reset_index()
    
    # Create details table with wrapped text
    details_data = [
        [Paragraph("Details", styles["SectionHeader"])],  # Using bold centered style
        [
            Paragraph("Person", styles["Normal"]),
            Paragraph("Date", styles["Normal"]),
            Paragraph("Name", styles["Normal"]),
            Paragraph("Miles", styles["Normal"]),
            Paragraph("NetPay", styles["Normal"])
        ]
    ]
    
    # Add rows with wrapped text and regular net pay calculations
    running_total_miles = 0
    regular_total_net = 0
    
    for _, row in grouped_data.iterrows():
        net_pay = calculate_net_pay(driver_name, row['GROSS PAY'], is_final_total=False)
        regular_total_net += net_pay
        running_total_miles += row['MILES']
        
        details_data.append([
            Paragraph(driver_name, styles["Normal"]),
            row['DATE'].strftime('%m/%d/%Y'),
            Paragraph("466 53 OCA Satellite (Milliones) PRG IB 02", styles["Normal"]),
            str(int(row['MILES'])),
            f"${net_pay:.2f}"
        ])
    
    # Add empty row
    details_data.append([""] * 5)
    
    # Add total NET
    details_data.append([Paragraph("Total NET", styles["Normal"]), "", "", str(int(running_total_miles)), f"${total_net:.2f}"])
    
    details_style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (2, 2), (2, -3), 'LEFT'),
        ('SPAN', (0, 0), (-1, 0)),
        ('BACKGROUND', (0, 0), (-1, 0), header_blue),
        ('BACKGROUND', (0, 1), (-1, 1), row_green),
        ('BACKGROUND', (0, -1), (-1, -1), row_green),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ])
    
    col_widths = [1.5*inch, 1*inch, 3.5*inch, 0.8*inch, 0.8*inch]
    details_table = Table(details_data, colWidths=col_widths)
    details_table.setStyle(details_style)
    elements.append(details_table)
    
    return elements