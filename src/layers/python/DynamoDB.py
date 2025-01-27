import boto3


class DynamoDB:

    def __init__(self, table_name):
        self.resource = boto3.resource('dynamodb')
        self.table = self.resource.Table(table_name)

    def delete_item(self, Key):
        response = self.table.delete_item(
            Key=Key,
            ReturnValues='NONE',
            ReturnConsumedCapacity='TOTAL'
        )

        return response

    def get_item(self, Key, ConsistentRead=True):
        response = self.table.get_item(
            Key=Key,
            ConsistentRead=ConsistentRead,
            ReturnConsumedCapacity='NONE'
        )

        return response

    def put_item(self, item):
        response = self.table.put_item(
            Item=item
        )

        return response

    def scan(self):
        items = []
        response = self.table.scan()
        items.extend(response.get('Items', []))
        while 'LastEvaluatedKey' in response:
            response = self.table.scan(
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items.extend(response.get('Items', []))

        return items
