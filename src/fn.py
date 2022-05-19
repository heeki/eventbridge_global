import boto3
import json
import os
from lib.ddb import AdptDynamoDB

# initialization
session = boto3.session.Session()
region = os.environ["AWS_REGION"]
table = os.environ["TABLE"]
ddb = AdptDynamoDB(session, table)

# helper functions
def build_response(code, body):
    # headers for cors
    headers = {
        "Content-Type": "application/json"
    }
    # lambda proxy integration
    response = {
        "isBase64Encoded": False,
        "statusCode": code,
        "headers": headers,
        "body": body
    }
    return response

def handler(event, context):
    print(json.dumps(event))
    output = event["detail"]
    output["region"] = region
    item = {k: {"S": v} for (k, v) in output.items()}
    print(json.dumps(item))
    response = ddb.put(item)
    print(response)
    return output
