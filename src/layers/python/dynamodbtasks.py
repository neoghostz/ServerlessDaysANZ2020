import os
import logging
from dynamodb import dynamodb
from botocore.exceptions import ClientError
from APIExceptions import DynamoDBWriteFailure, DynamoDBReadFailure


class dynamodbtasks:
    
    def __init__(self, table_name):
        logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s')
        self.logger = logging.getLogger('Demo/DynamoDBTasks')
        self.logger.setLevel(os.environ.get('Logging', logging.DEBUG))
        self.table_name = table_name
        self.dynamodb = dynamodb(table_name=self.table_name)

    def write_item(self, key, payload):
        item = {
            'DocID': key,
            'Payload': payload
        }
        try:
            response = self.dynamodb.put_item(
                item=item
            )
        except ClientError as err:
            self.logger.error(f'Error when attempting to write {key} to {self.table_name} with error: {err}')
            raise DynamoDBWriteFailure(f'Error when attempt to write {key} to {self.table_name} with error: {err}')
        else:
            self.logger.debug(f'Successfully wrote {key} to {self.table_name}')
            return response

    def get_item(self, key):
        try:
            self.dynamodb.get_item(
                Key=key
            )
        except ClientError as err:
            self.logger.error(f'Error when attempting to read {key} from {self.table_name} with error: {err}')
            raise DynamoDBReadFailure(f'Error when attempt to read {key} from {self.table_name} with error: {err}')
        else:
            self.logger.debug(f'Successfully read {key} from {self.table_name}')
            return response

    def list_items(self):
        try:
            response = self.dynamodb.scan()
        except ClientError as err:
            self.logger.error(f'Error when attempting to scan table {self.table_name} with error: {err}')
            raise DynamoDBReadFailure(f'Error when attempt to scan table {self.table_name} with error: {err}')
        else:
            self.logger.debug(response)
            self.logger.info(f'Successfully scanned {self.table_name}')
            return response
