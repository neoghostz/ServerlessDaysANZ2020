import logging
import os
import traceback
from s3tasks import s3tasks
from dynamodbtasks import dynamodbtasks
from RestfulEndpoint import Endpoint
from APIExceptions import S3DeleteFailure, DynamoDBDeleteFailure


class DeletePDF(Endpoint):
    def __init__(self, event, context):
        logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s')
        self.logger = logging.getLogger('Demo/DeletePDF')
        self.logger.setLevel(os.environ.get('Logging', logging.DEBUG))
        self.event = event
        self.context = context
        super().__init__(self.event, self.context)
        self.endpoint_path = "/delete_pdf"
        self.DocId = self.event.get('pathParameters', {}).get('DocId', '')
        self.status = None
        self.response_payload = None
        self.bucket = os.environ.get('Bucket', None)
        self.kmskey = os.environ.get('KMSKey', None)
        self.table = os.environ.get('Table', None)
        self.s3tasks = s3tasks(bucket=self.bucket, kmskey=self.kmskey)
        self.dynamodbtasks = dynamodbtasks(table_name=self.table)

    def response(self):
        try:
            self.s3tasks.delete_file(self.DocId)
            self.dynamodbtasks.delete_item(self.DocId)
        except (ValueError, AttributeError) as err:
            self.status = 400
            self.logger.error(repr(traceback.print_exc()))
            self.response_payload = {
                'message': repr(err)
            }
        except (S3DeleteFailure, DynamoDBDeleteFailure) as err:
            self.status = 400
            self.logger.error(repr(traceback.print_exc()))
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
                'message': 'Success'
            }
        finally:
            return self.build_response(self.status, self.response_payload)


def lambda_handler(event, context):
    return DeletePDF(event, context).response()
