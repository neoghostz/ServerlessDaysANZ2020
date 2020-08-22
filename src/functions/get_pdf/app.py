import logging
import os
import traceback
from s3tasks import s3tasks
from RestfulEndpoint import Endpoint
from APIExceptions import DynamoDBReadFailure

logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s')
logger = logging.getLogger('Demo/GetPDF')
logger.setLevel(os.environ.get('Logging', logging.DEBUG))


class GetPDF(Endpoint):
    def __init__(self, event, context):
        logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s')
        self.logger = logging.getLogger('Demo/GetPDF')
        self.logger.setLevel(os.environ.get('Logging', logging.DEBUG))
        self.event = event
        self.context = context
        super().__init__(self.event, self.context)
        self.endpoint_path = "/create_pdf"
        self.DocId = self.event.get('pathParameters', {}).get('DocId', '')
        self.status = None
        self.response_payload = None
        self.bucket = os.environ.get('Bucket', None)
        self.kmskey = os.environ.get('KMSKey', None)
        self.s3tasks = s3tasks(bucket=self.bucket, kmskey=self.kmskey)

    def response(self):
        try:
            document = self.s3tasks.get_file(self.DocId)
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
            self.response_payload = document
        finally:
            return self.build_response(self.status, self.response_payload)

    def build_response(self, status, payload):
        self.logger.debug(f"Payload Type: {type(payload)}")
        if status in [200, 304]:
            response = {
                'statusCode': status,
                'headers': self.build_headers(payload),
                'body': payload.decode("latin-1").encode('utf8'),
                'isBase64Encoded': False
            }
        else:
            response = {
                'httpStatus': status,
                'errorMessage': payload,
                'requestId': self.context.aws_request_id
            }

        self.logger.debug(response)
        return response

    def build_headers(self, payload):
        headers = {
            'Content-Type': 'application/pdf',
            'content-disposition': f'attachment; filename={self.DocId}.pdf',
            'Cache-Control': 'private',
            'Content-Length': self.calc_content_length(payload),
            'Date': self.calc_date()
        }

        return headers


def lambda_handler(event, context):
    return GetPDF(event, context).response()
