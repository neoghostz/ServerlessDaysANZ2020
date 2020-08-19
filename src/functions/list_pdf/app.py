import logging
import os
from RestfulEndpoint import Endpoint
from APIExceptions import DynamoDBReadFailure

logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s')
logger = logging.getLogger('Demo/ListPDF')
logger.setLevel(os.environ.get('Logging', logging.DEBUG))


class ListPDF(Endpoint):
    def __init__(self, event, context):
        self.event = event
        self.endpoint_path = "/create_pdf"
        self.context = context
        self.table = os.environ.get('Table', None)
        self.dynamodbtasks = dynamodbtasks(table_name=self.table)
        super().__init__(self.event, self.context)

    def response(self):
        try:
            list_pdf = self.dynamodbtasks.list_items()
        except DynamoDBReadFailure as err:
            self.status = 400
            response_payload = [repr(err)]
            error_type = 'ReadError'
        else:
            self.status = 200
            response_payload = list_pdf
            error_type = None
        finally:
            return self.build_response(self.status, response_payload, error_type=error_type)

def lambda_handler(event, context):
    return ListPDF(event, context).response()
