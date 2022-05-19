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
        ap.add_argument("--endpoint", help="endpoint id for global endpoints")
        ap.add_argument("--bus", required=True, help="event bus")
        ap.add_argument("--idempotence_token", help="optional idempotence token, if not specified, one will be generated")
        ap.add_argument("--type", required=True, help="attribute for rule filtering")
        ap.add_argument("--message", required=True, help="message to send to the bus")
        args = ap.parse_args()

        if args.idempotence_token is not None:
            idempotence_token = args.idempotence_token
        else:
            idempotence_token = str(uuid.uuid4())

        # debugging = {
        #     "endpoint": args.endpoint,
        #     "bus": args.bus,
        #     "idempotence_token": idempotence_token
        # }
        # print(json.dumps(debugging))

        eb_event = {
            "uuid": idempotence_token,
            "type": args.type,
            "message": args.message
        }
        print(json.dumps(eb_event))

        eb = AdptEventBridge(session, args.bus, args.endpoint)
        source = "put_event.py"
        response = eb.put_event(source, json.dumps(eb_event))
        print(json.dumps({k: response[k] for k in ["FailedEntryCount"] }))
    except KeyboardInterrupt as e:
        print("interrupted")

if __name__ == "__main__":
    main()
