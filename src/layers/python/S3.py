import boto3


class S3:

    def __init__(self):
        self.client = boto3.client('s3')
        self.resource = boto3.resource('s3')

    def delete_object(self, Bucket, Key):
        response = self.client.delete_object(
            Bucket=Bucket,
            Key=Key,
        )

        return response

    def get_object(self, Bucket, Key):
        response = self.resource.Object(Bucket, Key)

        return response

    def put_object(self, ACL, Body, Bucket, Key, SSEKMSKeyId, ServerSideEncryption='aws:kms'):
        response = self.client.put_object(
            ACL=ACL,
            Body=Body,
            Bucket=Bucket,
            Key=Key,
            ServerSideEncryption=ServerSideEncryption,
            SSEKMSKeyId=SSEKMSKeyId
        )

        return response
