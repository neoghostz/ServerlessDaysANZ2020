import logging
import os
import traceback
from S3Tasks import S3Tasks
from DynamoDBTasks import DynamoDBTasks
from RestfulEndpoint import Endpoint
from APIExceptions import S3DeleteFailure, DynamoDBDeleteFailure
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()


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
        self.S3Tasks = S3Tasks(bucket=self.bucket, kmskey=self.kmskey)
        self.DynamoDBTasks = DynamoDBTasks(table_name=self.table)

    def response(self):
        try:
            self.S3Tasks.delete_file(self.DocId)
            self.DynamoDBTasks.delete_item(self.DocId)
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
