import logging
import os
from RestfulEndpoint import Endpoint

logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s')
logger = logging.getLogger('Demo/GetPDF')
logger.setLevel(os.environ.get('Logging', logging.DEBUG))


class GetPDF(Endpoint):
    def __init__(self, event, context):
        self.event = event
        self.endpoint_path = "/create_pdf"
        self.context = context
        self.query_parameters = {
        }
        self.header_parameters = {
        }
        super().__init__(self.event, self.context)
        self.mock = os.environ.get('Mocking', True)

    def build_mock_response(self):
        if self.validate_request():
            if self.event.get('httpMethod') == 'GET':
                mock_response = mock_response_get
            else:
                mock_response = {}

            return mock_response

    def validate_payload(self):
        if not isinstance(self.data, list):
            raise ValueError("Submitted data is not a list")

    def response(self):
        self.vali
        return self.build_response(200, {})

    def build_response(self):
        response = {
            'statusCode': self.status,
            'headers': self.build_headers(self.pdf.output(dest='S').encode('latin-1')),
            'body': str(self.pdf.output(dest='S').encode('latin-1'), 'latin-1', errors='ignore'),
            'isBase64Encoded': True
        }
        self.logger.debug(response)
        return response

def lambda_handler(event, context):
    return GetPDF(event, context).response()
