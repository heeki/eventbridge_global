import boto3
import botocore
import json

class AdptDynamoDB:
    def __init__(self, session, table, lsi=None):
        self.session = session
        self.client = self.session.client("dynamodb")
        self.table = table
        self.lsi = lsi

    def set_lsi(self, lsi):
        self.lsi = lsi

    def get(self, hkey):
        response = self.client.get_item(
            TableName=self.table,
            Key=hkey
        )
        if "Item" in response:
            return response["Item"]
        else:
            return {}

    def put(self, item):
        try:
            response = self.client.put_item(
                TableName=self.table,
                Item=item
            )
        except botocore.exceptions.ResourceNotFoundException as e:
            response = {
                "ResponseMetadata": {
                    "HTTPStatusCode": 404
                },
                "error": e
            }
        return response

    def update(self, item_key, update_expression, expression_names, expression_attributes):
        try:
            response = self.client.update_item(
                TableName=self.table,
                Key=item_key,
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_names,
                ExpressionAttributeValues=expression_attributes,
                ReturnValues="ALL_NEW"
            )
        except botocore.exceptions.ClientError as e:
            response = {
                "ResponseMetadata": {
                    "HTTPStatusCode": 400
                },
                "error": e
            }
            print(e)
        return response

    def increment(self, hkey, attr, incr=1):
        try:
            response = self.client.update_item(
                TableName=self.table,
                Key=hkey,
                ExpressionAttributeNames={
                    "#attr": attr
                },
                ExpressionAttributeValues={
                    ":increment": {"N": str(incr)},
                    ":zero": {"N": "0"}
                },
                UpdateExpression="SET #attr = if_not_exists(#attr, :zero) + :increment",
                ReturnValues="ALL_NEW"
            )
        except botocore.exceptions.ClientError as e:
            response = {
                "error": e
            }
        return response

    def _query(self, expression_values, key_condition, projection_expression, last_key=None):
        if last_key is None:
            if self.lsi is None:
                response = self.client.query(
                    TableName=self.table,
                    ExpressionAttributeValues=expression_values,
                    KeyConditionExpression=key_condition,
                    ProjectionExpression=projection_expression,
                )
            else:
                response = self.client.query(
                    TableName=self.table,
                    IndexName=self.lsi,
                    ExpressionAttributeValues=expression_values,
                    KeyConditionExpression=key_condition,
                    ProjectionExpression=projection_expression,
                )
        else:
            if self.lsi is None:
                response = self.client.query(
                    TableName=self.table,
                    ExpressionAttributeValues=expression_values,
                    KeyConditionExpression=key_condition,
                    ProjectionExpression=projection_expression,
                    ExclusiveStartKey=last_key
                )
            else:
                response = self.client.query(
                    TableName=self.table,
                    IndexName=self.lsi,
                    ExpressionAttributeValues=expression_values,
                    KeyConditionExpression=key_condition,
                    ProjectionExpression=projection_expression,
                    ExclusiveStartKey=last_key
                )
        return response

    def query(self, expression_values, key_condition, projection_expression):
        output = []
        response = self._query(expression_values, key_condition, projection_expression)
        output.extend(response["Items"])
        while "LastEvaluatedKey" in response:
            response = self._query(expression_values, key_condition, projection_expression, last_key=response['LastEvaluatedKey'])
            output.extend(response["Items"])
        return output

    def _generate_delete_requests(self, hkey, skey, items):
        output = []
        for item in items:
            output.append({
                "DeleteRequest": {
                    "Key": {
                        hkey: {"S": item["hval"]},
                        skey: {"S": item["sval"]}
                    }
                }
            })
        return output

    def batch_delete(self, hkey, skey, items):
        requests = self._generate_delete_requests(hkey, skey, items)
        response = self.client.batch_write_item(
            RequestItems={
                self.table: requests
            }
        )
        return response

    def scan(self):
        response = self.client.scan(
            TableName=self.table
        )
        return response["Items"]