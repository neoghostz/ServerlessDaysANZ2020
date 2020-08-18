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

    def get_object(self, Bucket, Key, SSECustomerKey, SSECustomerAlgorithm="AES256"):
        reponse = self.client.get_object(
            Bucket=Bucket,
            Key=Key,
            SSECustomerAlgorithm=SSECustomerAlgorithm,
            SSECustomerKey=SSECustomerKey
        )

        return response

    def put_object(self, ACL, Body, BUcket, ContentLength, Key, ServerSideEncryption, SSECustomerKey, SSEKMSKeyId):
        response = self.client.put_object(
            ACL=ACL,
            Body=Body,
            Bucket=Bucket,
            ContentLength=ContentLength,
            Key=Key,
            ServerSideEncryption='aws:kms',
            SSECustomerAlgorithm="AES256",
            SSECustomerKey=SSECustomerKey,
            SSEKMSKeyId=SSEKMSKeyId
        )

        return response
