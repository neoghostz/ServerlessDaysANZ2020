import json
import logging
import os
import sys
import hashlib
import base64
from datetime import datetime
from dateutil import tz
from fpdf import FPDF


class PDF(FPDF):
    def header(self):
        self.creation_date = self.zero_creation_date()
        self.image('https://res.cloudinary.com/serverlessdays/image/upload/c_scale,w_150/v1560783574/Mascots/unicorn_mascot.png', type="png", w=150, h=196)
        self.set_font('Arial', 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'Demo PDF Generation', 0, 0, 'C')
        self.ln(20)
        

    def zero_creation_date(self):
        time_tuple = (1969, 12, 31, 19, 00, 00)
        zero = datetime(*time_tuple)
        
        return zero

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')


class GeneratePDF():
    def __init__(self, data):
        logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s')
        self.logger = logging.getLogger('Demo/GeneratePDF')
        self.logger.setLevel(os.environ.get('Logging', logging.DEBUG))
        self.pdf = None
        self.data = self.validate_payload(data)
        self.logger.debug(f"PDF Data: {self.data}")

    def validate_payload(self, data):
        self.logger.debug('GeneratePDF Validation')
        self.logger.debug(type(data))
        self.logger.debug(isinstance(data, dict))
        if not isinstance(data, dict):
            raise ValueError("Submitted data is not a dict")
        else:
            return data

    def build_pdf(self, spacing=1):
        self.pdf = PDF()
        self.pdf.alias_nb_pages()
        self.pdf.add_page()
        self.pdf.set_font('Arial', '', size=12)
        col_width = self.pdf.w / 4.5
        row_height = self.pdf.font_size

        for row in self.data.get('table_data', []):
            for item in row:
                self.pdf.cell(col_width, row_height * spacing, txt=item, border=1)
            self.pdf.ln(row_height * spacing)

        return self.pdf.output(dest='S')
