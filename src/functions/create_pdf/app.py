import logging
import os
import traceback
import json
from GeneratePDF import GeneratePDF
from S3Tasks import S3Tasks
from util import unquie_uuid
from APIExceptions import S3WriteFailure, DynamoDBWriteFailure
from DynamoDBTasks import DynamoDBTasks
from RestfulEndpoint import Endpoint
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()


class CreatePDF(Endpoint):
    def __init__(self, event, context):
        logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s')
        self.logger = logging.getLogger('Demo/CreatePDF')
        self.logger.setLevel(os.environ.get('Logging', logging.DEBUG))
        self.event = event
        self.context = context
        super().__init__(self.event, self.context)
        self.bucket = os.environ.get('Bucket', None)
        self.kmskey = os.environ.get('KMSKey', None)
        self.table = os.environ.get('Table', None)
        self.S3Tasks = S3Tasks(bucket=self.bucket, kmskey=self.kmskey)
        self.DynamoDBTasks = DynamoDBTasks(table_name=self.table)
        self.endpoint_path = "/create_pdf"
        self.status = None
        self.response_payload = None
        self.data = json.loads(self.event.get('body', "{}"))

    def response(self):
        try:
            pdf = GeneratePDF(self.data).build_pdf()
            doc_key = unquie_uuid()
            self.S3Tasks.write_file(body=pdf, key=doc_key)
            self.DynamoDBTasks.write_item(key=doc_key, payload=self.data)
        except (ValueError, AttributeError) as err:
            self.status = 400
            self.logger.error(repr(traceback.print_exc()))
            self.response_payload = {
                'message': repr(err)
            }
        except (DynamoDBWriteFailure, S3WriteFailure) as err:
            self.status = 500
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
                'DocID': doc_key,
                'message': 'Success'
            }
        finally:
            return self.build_response(self.status, self.response_payload)


def lambda_handler(event, context):
    return CreatePDF(event, context).response()
