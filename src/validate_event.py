import argparse
import boto3
import json
import time
import uuid
from lib.ddb import AdptDynamoDB
from lib.eventbridge import AdptEventBridge

# global variables
session = boto3.session.Session()

def main():
    try:
        ap = argparse.ArgumentParser()
        ap.add_argument("--table", required=True, help="global table name")
        ap.add_argument("--idempotence_token", required=True, help="optional idempotence token, if not specified, one will be generated")
        args = ap.parse_args()

        ddb = AdptDynamoDB(session, args.table)
        response = ddb.get({"uuid": {"S": args.idempotence_token}})
        output = {k: v["S"] for (k, v) in response.items()}
        print(json.dumps(output))
    except KeyboardInterrupt as e:
        print("interrupted")

if __name__ == "__main__":
    main()
