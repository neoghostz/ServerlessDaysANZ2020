import logging
import os
import traceback
from dynamodbtasks import dynamodbtasks
from RestfulEndpoint import Endpoint
from APIExceptions import DynamoDBReadFailure


class ListPDF(Endpoint):
    def __init__(self, event, context):
        logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s')
        self.logger = logging.getLogger('Demo/ListPDF')
        self.logger.setLevel(os.environ.get('Logging', logging.DEBUG))
        self.event = event
        self.context = context
        super().__init__(self.event, self.context)
        self.endpoint_path = "/list_pdf"
        self.status = None
        self.response_payload = None
        self.table = os.environ.get('Table', None)
        self.dynamodbtasks = dynamodbtasks(table_name=self.table)

    def response(self):
        try:
            list_pdf = self.dynamodbtasks.list_items()
        except (ValueError, AttributeError) as err:
            self.status = 400
            self.logger.error(repr(traceback.print_exc()))
            self.response_payload = {
                'message': repr(err)
            }
        except DynamoDBReadFailure as err:
            self.status = 400
            self.response_payload = {
                'message': repr(err)
            }
        except Exception as err:
            self.status = 500
            self.logger.error(repr(traceback.print_exc()))
            self.response_payload = {
                'message': repr(err)
            }
        else:
            self.status = 200
            self.response_payload = {
                'Documents': [item['DocID'] for item in list_pdf]
            }
        finally:
            return self.build_response(self.status, self.response_payload)


def lambda_handler(event, context):
    return ListPDF(event, context).response()
