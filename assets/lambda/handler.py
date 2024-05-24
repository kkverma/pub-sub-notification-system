import json
import os
import requests
from datetime import datetime

def main(event, context):
    slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')

    for record in event['Records']:
        # Process the SQS message
        sns_message = json.loads(record['body'])
        s3_event = json.loads(sns_message['Message'])
        print(s3_event)

        for s3_record in s3_event['Records']:
            s3_bucket_name = s3_record['s3']['bucket']['name']
            s3_object_key = s3_record['s3']['object']['key']
            event_time = s3_record['eventTime']

            # Convert eventTime to a Unix timestamp
            event_datetime = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            timestamp = int(event_datetime.timestamp())
            # Generate S3 object URL
            s3_object_url = f"https://s3.console.aws.amazon.com/s3/object/{s3_bucket_name}/{s3_object_key}?region=ap-south-1"


            # Format the Slack message
            slack_message = {
                "attachments": [
                    {
                        "fallback": f"New file uploaded to {s3_bucket_name}",
                        "color": "#36a64f",
                        "title": "New S3 Upload",
                        "fields": [
                            {
                                "title": "Bucket",
                                "value": s3_bucket_name,
                                "short": True
                            },
                            {
                                "title": "File",
                                "value": s3_object_key,
                                "short": True
                            }
                        ],
                        "footer": "AWS S3 Notification",
                        "ts": timestamp,
                        "actions": [
                            {
                                "type": "button",
                                "text": "View in S3",
                                "url": s3_object_url
                            }
                        ]
                    }
                ]
            }

            # Send message to Slack
            response = requests.post(slack_webhook_url, json=slack_message)

            if response.status_code != 200:
                raise ValueError(f"Request to slack returned an error {response.status_code}, the response is:\n{response.text}")

    return {"statusCode": 200, "body": json.dumps('Message processed')}
