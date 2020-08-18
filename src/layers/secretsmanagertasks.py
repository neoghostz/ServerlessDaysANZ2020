import sys
import logging
import uuid
import os
import json
import base64
import logging
import botocore.errorfactory
from secretsmanager import secretsmanager
from botocore.exceptions import ClientError


class secretsmanagertasks:

    def __init__(self):
        logging.basicConfig(format='%(asctime)s [%(levelname)s] (%(funcName)s) %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        self.logger = logging.getLogger("Demo/SecretsManagerTasks")
        self.logger.setLevel(int(os.environ.get("Logging", logging.DEBUG)))
        self.sm = secretsmanager()

    def generate_password(self):
        password = self.sm.get_random_password()
        self.logger.info(password)

    def upsert_secret_string(self, name, secret, description, kmskey=None, tags=None, token=None):
        if token is None:
            token = self.generate_client_token()
        exists = self.get_secret_by_name(name)
        if exists:
            try:
                response = self.sm.update_secret_string(
                    SecretId=name,
                    SecretString=secret,
                    ClientRequestToken=token,
                    Description=description,
                    KmsKeyId=kmskey
                )
            except ClientError as err:
                self.logger.error("Failed to Update Secret {} with Error {}".format(name, err))
                sys.exit(1)
            else:
                self.logger.info("Successfully Updated Secret {}".format(name))
        else:
            try:
                response = self.sm.create_secret_string(
                    Name=name,
                    SecretString=secret,
                    ClientRequestToken=token,
                    Description=description,
                    KmsKeyId=kmskey,
                    Tags=tags
                )
            except ClientError as err:
                self.logger.error("Failed to Update Secret {} with Error {}".format(name, err))
                sys.exit(1)
            else:
                self.logger.info("Successfully Created Secret {}".format(name))

        self.logger.debug(json.dumps(response, default=str, sort_keys=True, indent=4, separators=(',', ': ')))

        return response

    def rotate_secret(self, name, token=None, rotationdays=60):
        if token is None:
            token = self.generate_client_token()
        exists = self.get_secret_by_name(name)
        if exists:
            try:
                response = self.sm.rotate_secret(
                    SecretId=name,
                    ClientRequestToken=token,
                    RotationRules=self.generate_rotation_rules(rotationdays)
                )
            except ClientError as err:
                self.logger.error("Failed to Rotate Secret {} with Error {}".format(name, err))
                sys.exit(1)
            else:
                self.logger.info("Successfully rotated Secret {}".format(name))
        else:
            self.logger.error("Secret {} does not exist.".format(name))
            sys.exit(1)

        self.logger.debug(json.dumps(response, default=str, sort_keys=True, indent=4, separators=(',', ': ')))

        return response

    def rotate_secret_by_lambda(self, name, lambdaarn, token=None, rotationdays=60):
        if token is None:
            token = self.generate_client_token()
        exists = self.get_secret_by_name(name)
        if exists:
            try:
                response = self.sm.rotate_secret_lambda(
                    SecretId=name,
                    ClientRequestToken=token,
                    RotationRules=self.generate_rotation_rules(rotationdays),
                    RotationLambdaARN=lambdaarn
                )
            except ClientError as err:
                self.logger.error("Failed to Rotate Secret {} by Lambda {} with Error {}".format(name, lambdaarn, err))
                sys.exit(1)
        else:
            self.logger.error(f"Secret {name} does not exist.")
            sys.exit(1)

        self.logger.debug(json.dumps(response, default=str, sort_keys=True, indent=4, separators=(',', ': ')))

        return response

    def get_secret(self, name, versionid=None):
        try:
            response = self.sm.get_secret_value(
                SecretId=name,
                VersionId=versionid
            )
        except ClientError as err:
            self.logger.error(f"Failed to retreive Secret {name}.")
            sys.exit(1)
        else:
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                if response.get('SecretString', False):
                    return response["SecretString"]
                else:
                    return response["SecretBinary"]

    def get_secret_by_name(self, name):
        secretslist = self.sm.list_secrets()
        for obj in secretslist:
            if name in obj["Name"]:
                return True
        else:
            return False

    def get_secret_by_arn(self, arn):
        secretslist = self.sm.list_secrets()
        for obj in secretslist:
            if arn in obj["ARN"]:
                return True
        else:
            return False

    def generate_client_token(self):
        token = uuid.uuid4()

        return str(token)

    def generate_rotation_rules(self, days=60):
        rules = {
            'AutomaticallyAfterDays': days
        }

        return rules
