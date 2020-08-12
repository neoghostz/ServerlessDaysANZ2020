class DynamoDB:
    
    def __init__(self, session, table_name):
        self.client = session.client('s3')
        self.resource = session.resource('dynamodb')
        self.table = self.resource.Table(table_name)

    def delete_item(self):
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

