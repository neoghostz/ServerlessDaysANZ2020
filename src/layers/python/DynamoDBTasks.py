import os
import logging
import json
from DynamoDB import DynamoDB
from util import json_serial
from botocore.exceptions import ClientError
from APIExceptions import DynamoDBWriteFailure, DynamoDBReadFailure, DynamoDBDeleteFailure


class DynamoDBTasks:

    def __init__(self, table_name):
        logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s')
        self.logger = logging.getLogger('Demo/DynamoDBTasks')
        self.logger.setLevel(os.environ.get('Logging', logging.DEBUG))
        self.table_name = table_name
        self.DynamoDB = DynamoDB(table_name=self.table_name)

    def write_item(self, key, payload):
        self.logger.info('Starting DynamoDB Tasks Write Item')
        item = {
            'DocID': key,
            'Payload': payload
        }
        try:
            response = self.DynamoDB.put_item(
                item=item
            )
        except ClientError as err:
            self.logger.error(f'Error when attempting to write {key} to {self.table_name} with error: {err}')
            raise DynamoDBWriteFailure(f'Error when attempt to write {key} to {self.table_name} with error: {err}')
        else:
            self.logger.info(f'Successfully wrote {key} to {self.table_name}')
            self.logger.debug(json.dumps(response, default=json_serial, sort_keys=True, indent=4, separators=(',', ': ')))
            return response

    def get_item(self, key):
        self.logger.info('Starting DynamoDB Tasks Get Item')
        try:
            response = self.DynamoDB.get_item(
                Key=key
            )
        except ClientError as err:
            self.logger.error(f'Error when attempting to read {key} from {self.table_name} with error: {err}')
            raise DynamoDBReadFailure(f'Error when attempt to read {key} from {self.table_name} with error: {err}')
        else:
            self.logger.info(f'Successfully read {key} from {self.table_name}')
            self.logger.debug(json.dumps(response, default=json_serial, sort_keys=True, indent=4, separators=(',', ': ')))
            return response

    def list_items(self):
        self.logger.info('Starting DynamoDB Tasks List Items')
        try:
            response = self.DynamoDB.scan()
        except ClientError as err:
            self.logger.error(f'Error when attempting to scan table {self.table_name} with error: {err}')
            raise DynamoDBReadFailure(f'Error when attempt to scan table {self.table_name} with error: {err}')
        else:
            self.logger.info(f'Successfully scanned {self.table_name}')
            self.logger.debug(json.dumps(response, default=json_serial, sort_keys=True, indent=4, separators=(',', ': ')))
            return response

    def delete_item(self, key):
        self.logger.info('Starting DynamoDB Tasks Delete Item')
        item = {
            'DocID': key,
        }
        try:
            response = self.DynamoDB.delete_item(
                Key=item
            )
        except ClientError as err:
            self.logger.error(f'Error when attempting to delete {key} from table {self.table_name} with error: {err}')
            raise DynamoDBDeleteFailure(f'Error when attempting to delete {key} from table {self.table_name} with error: {err}')
        else:
            self.logger.info(f'Successfully deleted {key} from {self.table_name}')
            self.logger.debug(json.dumps(response, default=json_serial, sort_keys=True, indent=4, separators=(',', ': ')))
            return response
