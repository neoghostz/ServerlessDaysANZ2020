import os
import logging
import json
from S3 import S3
from util import json_serial
from APIExceptions import S3ReadFailure, S3WriteFailure, S3DeleteFailure
from botocore.exceptions import ClientError


class S3Tasks:

    def __init__(self, bucket, kmskey):
        logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s')
        self.logger = logging.getLogger('Demo/S3Tasks')
        self.logger.setLevel(os.environ.get('Logging', logging.DEBUG))
        self.bucket = bucket
        self.kmskey = kmskey
        self.S3 = S3()

    def build_acl(self, acl):
        valid_acl = [
            'private',
            'public-read',
            'public-read-write',
            'authenticated-read',
            'aws-exec-read',
            'bucket-owner-read',
            'bucket-owner-full-control'
        ]

        return acl if acl in valid_acl else 'private'

    def write_file(self, body, key, acl='private'):
        self.logger.debug(f'Starting S3Tasks write_file for {key} in bucket {self.bucket}')
        try:
            response = self.S3.put_object(
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

    def get_file(self, key):
        self.logger.debug(f'Starting S3Tasks get_file for {key} in bucket {self.bucket}')
        try:
            response = self.S3.get_object(
                Bucket=self.bucket,
                Key=key
            )
        except ClientError as err:
            self.logger.error(f'Error when attempting to get {key} from {self.bucket} with error: {err}')
            raise S3ReadFailure(f'Error when attempting to get {key} from {self.bucket} with error: {err}')
        else:
            self.logger.info(f'Successfully read {key} from {self.bucket}')
            self.logger.debug(json.dumps(response, default=json_serial, sort_keys=True, indent=4, separators=(',', ': ')))
            return response.get()['Body'].read()

    def delete_file(self, key):
        self.logger.debug(f'Starting S3Tasks delete_file for {key} in bucket {self.bucket}')
        try:
            response = self.S3.delete_object(
                Bucket=self.bucket,
                Key=key
            )
        except ClientError as err:
            self.logger.error(f'Error when attempting to delete {key} from {self.bucket} with error: {err}')
            raise S3DeleteFailure(f'Error when attempting to delete {key} from {self.bucket} with error: {err}')
        else:
            self.logger.info(f'Successfully deleted {key} from {self.bucket}')
            self.logger.debug(json.dumps(response, default=json_serial, sort_keys=True, indent=4, separators=(',', ': ')))
            return response
