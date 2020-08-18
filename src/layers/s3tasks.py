import os
from s3 import s3
from botocore.exceptions import ClientError

class s3tasks:

    def __init__(self):
        logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s')
        self.logger = logging.getLogger('Demo/S3Tasks')
        self.logger.setLevel(os.environ.get('Logging', logging.DEBUG))
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

