import boto3
import json
import os

# initialization
# session = boto3.session.Session()
# client = session.client("events")
region = os.environ["AWS_REGION"]

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
    # output = build_response(200, json.dumps(event))
    output = {
        "region": region,
        "event": event
    }
    print(json.dumps(output))
    return output
