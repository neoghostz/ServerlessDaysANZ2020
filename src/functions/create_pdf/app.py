import logging
import os
import json
from s3tasks import s3tasks
from dynamodbtasks import dynamodbtasks
from RestfulEndpoint import Endpoint

class CreatePDF(Endpoint):
    def __init__(self, event, context):
        logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s')
        self.logger = logging.getLogger('Demo/CreatePDF')
        self.logger.setLevel(os.environ.get('Logging', logging.DEBUG))
        self.s3tasks = s3tasks(session)
        self.event = event
        self.endpoint_path = "/create_pdf"
        self.context = context
        self.query_parameters = {
        }
        self.header_parameters = {
        }
        self.data = json.loads(self.event.get('body', "[]"))
        super().__init__(self.event, self.context)

    def generate_pdf(self):
        pass



    def response(self):
        return self.build_response(200, {})

def lambda_handler(event, context):
    return CreatePDF(event, context).response()
