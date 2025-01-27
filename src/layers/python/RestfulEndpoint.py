import json
import logging
import os
import sys
import hashlib
from APIExceptions import MissingReponseFields
from datetime import datetime
from dateutil import tz


class Endpoint:
    def __init__(self, event, context):
        self.event = event
        self.context = context
        self.endpoint_path = None
        self.required_fields = []
        self.logger = logging.getLogger(self.event.get('resource', 'Generic'))
        self.logger.setLevel(os.environ.get('Logging', logging.DEBUG))

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
