import os
from s3 import s3
from APIExceptions import S3ReadFailure, S3WriteFailure
from botocore.exceptions import ClientError


class s3tasks:

    def __init__(self, bucket, kmskey):
        logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s')
        self.logger = logging.getLogger('Demo/S3Tasks')
        self.logger.setLevel(os.environ.get('Logging', logging.DEBUG))
        self.bucket = bucket
        self.kmskey = kmskey
        self.s3 = s3()

    def build_acl(self, acl):
        valid_acl = {
            'private',
            'public-read',
            'public-read-write',
            'authenticated-read',
            'aws-exec-read',
            'bucket-owner-read',
            'bucket-owner-full-control'
        }

        return valid_acl.get(acl, 'private')

    def write_file(self, body, key, acl='private'):
        try:
            response = self.s3.put_object(
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
            self.logger.debug(f'Successfully wrote {key} to {self.bucket}')
            return response

    def get_file(self, key):
        try:
            response = self.s3.get_object(
                Bucket=self.bucket,
                Key=key
            )
        except ClientError as err:
            self.logger.error(f'Error when attempting to get {key} from {self.bucket} with error: {err}')
            raise S3ReadFailure(f'Error when attempting to get {key} from {self.bucket} with error: {err}')
        else:
            self.logger.debug(f'Successfully read {key} from {self.bucket}')
            return response