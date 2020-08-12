import json
import logging
import os
import sys
import jsonschema
from APIExceptions import MissingReponseFields, InvalidateSchema
from datetime import datetime
from dateutil import tz


class Endpoint:
    def __init__(self, event, context):
        self.event = event
        self.context = context
        self.data = None
        self.endpoint_path = None
        self.required_fields = []
        self.logger = logging.getLogger(self.event.get('resource', 'Generic'))
        self.logger.setLevel(os.environ.get('Logging', logging.DEBUG))

    def build_headers(self, payload):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json',
            'x-v': '',
            'x-fapi-interaction-id': '',
            'Cache-Control:': 'private',
            'Content-Length': self.calc_content_length(payload),
            'Date': self.calc_date()
        }

        return headers

    def calc_content_length(self, payload):
        return sys.getsizeof(payload)

    def calc_date(self):
        return datetime.now(tz=tz.gettz('Australia/Sydney')).strftime('%A, %d. %B %Y %I:%M%p')

    def build_response(self, status_code=200, payload={}):
        response = {
            'statusCode': status_code,
            'headers': self.build_headers(payload),
            'body': json.dumps(payload),
        }
        self.logger.debug(json.dumps(response))
        return response

    def validate_response(self, response):
        if response.get('statusCode') == 200:
            if any(x for x in self.required_fields not in response):
                raise MissingReponseFields(f'Missing key fields: {any(x for x in ["data", "links"] not in response)}')

    def validate_headers(self, headers):
        if headers.get('Content-Type', None):
            if headers['Content-Type'] != "application/json":
                raise ValueError('Content-Type header is invalid')
        if headers.get('Accept', None):
            if headers['Accept'] != "application/json":
                raise ValueError('Accept header is invalid')

    def validate_request(self):
        valid_request_object = True
        if self.endpoint_path == self.event.get('path'):
            valid_request_object = False
        
        return valid_request_object
