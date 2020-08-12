import logging
import os
from RestfulEndpoint import Endpoint

class CreatePDF(Endpoint):
    def __init__(self, event, context):
        logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s')
        self.logger = logging.getLogger('Demo/CreatePDF')
        self.logger.setLevel(os.environ.get('Logging', logging.DEBUG))
        self.event = event
        self.endpoint_path = "/create_pdf"
        self.context = context
        self.query_parameters = {
        }
        self.header_parameters = {
        }
        super().__init__(self.event, self.context)

    def build_mock_response(self):
        if self.validate_request():
            if self.event.get('httpMethod') == 'GET':
                mock_response = mock_response_get
            else:
                mock_response = {}

            return mock_response

    def response(self):
        return self.build_response(200, {})

def lambda_handler(event, context):
    return CreatePDF(event, context).response()
