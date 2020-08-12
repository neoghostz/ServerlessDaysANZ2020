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
        self.image('https://uploads-ssl.webflow.com/5ab350b53c0d5f3d6462a20a/5ab350b53c0d5fc17b62a24a_webclip.png', type="png", w=64, h=64)
        self.set_font('Arial', 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'Demo PDF Generation', 0, 0, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')


class GeneratePDF():
    def __init__(self, event, context):
        self.logger = logging.getLogger(event.get('resource', 'Generic'))
        self.logger.setLevel(os.environ.get('Logging', logging.DEBUG))
        self.event = event
        self.context = context
        self.status = None
        self.payload = None
        self.pdf = None
        self.data = json.loads(self.event.get('body', "[]"))

    def validate_payload(self):
        if not isinstance(self.data, list):
            raise ValueError("Submitted data is not a list")

    def build_headers(self, payload, filename="quote.pdf"):
        headers = {
            'Content-Type': 'application/pdf',
            'content-disposition': f'attachment; filename={filename}',
            'Cache-Control': 'private',
            'Content-Length': self.calc_content_length(payload),
            'Date': self.calc_date(),
            'ETag': self.calc_etag(payload)
        }

        return headers

    def build_pdf(self, spacing=1):
        self.pdf = PDF()
        self.pdf.alias_nb_pages()
        self.pdf.add_page()
        self.pdf.set_font('Arial', '', size=12)
        col_width = self.pdf.w / 4.5
        row_height = self.pdf.font_size

        for row in self.data:
            for item in row:
                self.pdf.cell(col_width, row_height * spacing, txt=item, border=1)
            self.pdf.ln(row_height * spacing)

    def calc_content_length(self, payload):
        return sys.getsizeof(payload)

    def calc_date(self):
        return datetime.now(tz=tz.gettz('Australia/Sydney')).strftime('%A, %d. %B %Y %I:%M%p')

    def calc_etag(self, payload):
        print(type(payload))
        print(dir(payload))
        return hashlib.md5(payload).hexdigest()

    def build_response(self):
        response = {
            'statusCode': self.status,
            'headers': self.build_headers(self.pdf.output(dest='S').encode('latin-1')),
            'body': str(self.pdf.output(dest='S').encode('latin-1'), 'latin-1', errors='ignore'),
            'isBase64Encoded': True
        }
        self.logger.debug(response)
        return response

    def response(self):
        try:
            self.validate_payload()
        except ValueError as e:
            self.status = 500
            self.data = [repr(e)]
        else:
            self.status = 200
        finally:
            self.build_pdf()
            self.logger.debug(self.pdf.output(dest='S').encode('latin-1'))
            return self.build_response()

    def build_file(self):
        try:
            self.validate_payload()
        except ValueError as e:
            self.status = 500
            self.data = [repr(e)]
        else:
            self.status = 200
        finally:
            self.build_pdf()
            print(type(self.pdf.output(dest='S').encode('latin-1')))
            self.pdf.output('quote.pdf')
