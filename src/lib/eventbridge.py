import boto3
import botocore
import json
from datetime import datetime

class AdptEventBridge:
    def __init__(self, session, bus, endpoint=None):
        self.session = session
        self.client = self.session.client("events")
        self.bus = bus
        self.endpoint=endpoint

    def put_event(self, source, event):
        if self.endpoint is not None:
            response = self.client.put_events(
                EndpointId=self.endpoint,
                Entries=[
                    {
                        "Time": datetime.now(),
                        "Source": source,
                        "Resources": [],
                        "DetailType": "boto3.client.put_events()",
                        "Detail": event,
                        "EventBusName": self.bus
                    }
                ]
            )
        else:
            response = self.client.put_events(
                Entries=[
                    {
                        "Time": datetime.now(),
                        "Source": source,
                        "Resources": [],
                        "DetailType": "boto3.client.put_events()",
                        "Detail": event,
                        "EventBusName": self.bus
                    }
                ]
            )
        return response
