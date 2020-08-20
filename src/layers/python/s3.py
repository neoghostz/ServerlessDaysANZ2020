import boto3


class s3:

    def __init__(self):
        self.client = boto3.client('s3')
        self.resource = boto3.resource('s3')

    def create_multipart_upload(self, ACL, Bucket, ContentType, Key, ServerSideEncryption, SSEKMSKeyId, Metadata={}):
        response = self.client.create_multipart_upload(
            ACL=ACL,
            Bucket=Bucket,
            ContentType=ContentType,
            Key=Key,
            Metadata=Metadata,
            ServerSideEncryption='aws:kms',
            SSEKMSKeyId=SSEKMSKeyId,
        )

        return response

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
