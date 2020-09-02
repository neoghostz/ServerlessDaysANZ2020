import logging
import os
import traceback
import json
from datetime import datetime
from fpdf import FPDF
import boto3
from botocore.exceptions import ClientError
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

## Util Functions

def unquie_uuid():
    return str(uuid.uuid4())

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


##Exceptions

class DynamoDBWriteFailure(Exception):
    pass


class S3WriteFailure(Exception):
    pass


## Generate PDF

class PDF(FPDF):
    def header(self):
        self.creation_date = self.zero_creation_date()
        self.image('https://res.cloudinary.com/serverlessdays/image/upload/c_scale,w_150/v1560783574/Mascots/unicorn_mascot.png', type="png", w=150, h=196)
        self.set_font('Arial', 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'Demo PDF Generation', 0, 0, 'C')
        self.ln(20)

    def zero_creation_date(self):
        time_tuple = (1969, 12, 31, 19, 00, 00)
        zero = datetime(*time_tuple)

        return zero

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')


class GeneratePDF:
    def __init__(self, data):
        logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s')
        self.logger = logging.getLogger('Demo/GeneratePDF')
        self.logger.setLevel(os.environ.get('Logging', logging.DEBUG))
        self.pdf = None
        self.data = self.validate_payload(data)
        self.logger.debug(f"PDF Data: {self.data}")

    def validate_payload(self, data):
        self.logger.debug('GeneratePDF Validation')
        self.logger.debug(type(data))
        self.logger.debug(isinstance(data, dict))
        if not isinstance(data, dict):
            raise ValueError("Submitted data is not a dict")
        else:
            return data

    def build_pdf(self, spacing=1):
        self.pdf = PDF()
        self.pdf.alias_nb_pages()
        self.pdf.add_page()
        self.pdf.set_font('Arial', '', size=12)
        col_width = self.pdf.w / 4.5
        row_height = self.pdf.font_size

        for row in self.data.get('table_data', []):
            for item in row:
                self.pdf.cell(col_width, row_height * spacing, txt=item, border=1)
            self.pdf.ln(row_height * spacing)

        return self.pdf.output(dest='S')


class CreatePDF:
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
        self.s3_client = boto3.client('s3')
        self.dynamodb_resource = boto3.resource('dynamodb')
        self.table = self.dynamodb_resource.Table(self.table)
        self.endpoint_path = "/create_pdf"
        self.status = None
        self.response_payload = None
        self.data = json.loads(self.event.get('body', "{}"))
        self.endpoint_path = None
        self.required_fields = []

    def response(self):
        try:
            pdf = GeneratePDF(self.data).build_pdf()
            doc_key = unquie_uuid()
            self.s3tasks.write_file(body=pdf, key=doc_key)
            self.dynamodbtasks.write_item(key=doc_key, payload=self.data)
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

## DynamoDB Functions

    def put_item(self, item):
        response = self.table.put_item(
            Item=item
        )

        return response

    def write_item(self, key, payload):
        self.logger.info('Starting DynamoDB Tasks Write Item')
        item = {
            'DocID': key,
            'Payload': payload
        }
        try:
            response = self.put_item(
                item=item
            )
        except ClientError as err:
            self.logger.error(f'Error when attempting to write {key} to {self.table_name} with error: {err}')
            raise DynamoDBWriteFailure(f'Error when attempt to write {key} to {self.table_name} with error: {err}')
        else:
            self.logger.info(f'Successfully wrote {key} to {self.table_name}')
            self.logger.debug(json.dumps(response, default=json_serial, sort_keys=True, indent=4, separators=(',', ': ')))
            return response

## S3 Functions

    def put_object(self, ACL, Body, Bucket, Key, SSEKMSKeyId, ServerSideEncryption='aws:kms'):
        response = self.s3_client.put_object(
            ACL=ACL,
            Body=Body,
            Bucket=Bucket,
            Key=Key,
            ServerSideEncryption=ServerSideEncryption,
            SSEKMSKeyId=SSEKMSKeyId
        )

        return response

    def write_file(self, body, key, acl='private'):
        self.logger.debug(f'Starting S3Tasks write_file for {key} in bucket {self.bucket}')
        try:
            response = self.put_object(
                ACL=self.build_acl(acl),
                Body=body,
                Bucket=self.bucket,
                Key=key,
                SSEKMSKeyId=self.kmskey
            )
        except ClientError as err:
            self.logger.error(f'Error when attempting to write {key} to {self.bucket} with error: {err}')
            raise S3WriteFailure(f'Error when attempt to write {key} to {self.bucket} with error: {err}')
        else:
            self.logger.info(f'Successfully wrote {key} to {self.bucket}')
            self.logger.debug(json.dumps(response, default=json_serial, sort_keys=True, indent=4, separators=(',', ': ')))
            return response

## Restful Endpoint

    def build_headers(self, payload, content_type):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': content_type,
            'Cache-Control:': 'private',
            'Content-Length': self.calc_content_length(payload),
            'Date': self.calc_date(),
        }

        return headers

    def calc_content_length(self, payload):
        return sys.getsizeof(payload)

    def calc_etag(self, payload):
        return hashlib.md5(str(payload)).hexdigest()

    def calc_date(self):
        return datetime.now(tz=tz.gettz('Australia/Sydney')).strftime('%A, %d. %B %Y %I:%M%p')

    def build_response(self, status_code=200, payload={}, content_type='application/json', error_type=None):
        if status_code in [200, 304]:
            response = {
                'statusCode': status_code,
                'headers': self.build_headers(payload, content_type),
                'body': json.dumps(payload),
            }
        else:
            response = {
                'httpStatus': status_code,
                'errorMessage': payload,
                'requestId': self.context.aws_request_id
            }
        self.logger.debug(json.dumps(response))
        return response

    def validate_response(self, response):
        if response.get('statusCode') == 200:
            if any(x for x in self.required_fields not in response):
                raise MissingReponseFields(f'Missing key fields: {any(x for x in self.required_fields not in response)}')

    def validate_headers(self, headers):
        if headers.get('Content-Type', None) not in ["application/json"]:
            raise ValueError('Content-Type header is invalid')
        if headers.get('Accept', None) not in ["application/json", "application/pdf"]:
            raise ValueError('Accept header is invalid')

    def validate_request(self):
        return True if self.endpoint_path == self.event.get('path') else False

def lambda_handler(event, context):
    return CreatePDF(event, context).response()
