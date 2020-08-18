import logging
import os
import json
from GeneratePDF import GeneratePDF
from s3tasks import s3tasks
from util import unquie_uuid
from APIExceptions import S3WriteFailure, DynamoDBWriteFailure
from dynamodbtasks import dynamodbtasks
from RestfulEndpoint import Endpoint

class CreatePDF(Endpoint):
    def __init__(self, event, context):
        logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s')
        self.logger = logging.getLogger('Demo/CreatePDF')
        self.logger.setLevel(os.environ.get('Logging', logging.DEBUG))
        self.bucket = os.environ.get('Bucket', None)
        self.kmskey = os.environ.get('KMSKey', None)
        self.table = os.environ.get('Table', None)
        self.s3tasks = s3tasks(bucket=self.bucket, kmskey=self.kmskey)
        self.dynamodbtasks = dynamodbtasks()
        self.event = event
        self.endpoint_path = "/create_pdf"
        self.context = context
        self.query_parameters = {
        }
        self.header_parameters = {
        }
        self.data = json.loads(self.event.get('body', "[]"))
        super().__init__(self.event, self.context)

    def response(self):
        try:
            pdf = GeneratePDF(self.data).build_pdf()
            doc_key = unquie_uuid
            self.s3tasks.write_file(body=pdf, key=doc_key)
            self.dynamodbtasks.write_item(key=doc_key, payload=self.data)
        except ValueError as err:
            self.status = 400
            response_payload = {
                'message': repr(err)
            }
        except S3WriteFailure as err:
            self.status = 500
            response_payload = [repr(err)]
        except DynamoDBWriteFailure as err:
            self.status = 500
            response_payload = [repr(err)]
        else:
            self.status = 200
            response_payload = ['Successfully creation']
        finally:
            return self.build_response(self.status, response_payload)

def lambda_handler(event, context):
    return CreatePDF(event, context).response()
