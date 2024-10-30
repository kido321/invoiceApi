
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