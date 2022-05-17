import argparse
import boto3
import json
from lib.eventbridge import AdptEventBridge

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", help="endpoint id for global endpoints")
    ap.add_argument("--bus", required=True, help="event bus")
    ap.add_argument("--message", required=True, help="message to send to the bus")
    args = ap.parse_args()

    debugging = {
        "endpoint": args.endpoint,
        "bus": args.bus,
        "message": args.message
    }
    print(json.dumps(debugging))

    session = boto3.session.Session()
    eb = AdptEventBridge(session, args.bus, args.endpoint)
    source = "put_event.py"
    response = eb.put_event(source, args.message)
    print(json.dumps(response))

if __name__ == "__main__":
    main()
