# Pub/Sub Notification System with S3, SNS, SQS, and Lambda
## Overview
This project implements a Pub/Sub notification system using AWS services. The system is designed to send notifications to Slack whenever a new file is uploaded to an S3 bucket. The architecture includes S3, SNS, SQS, and Lambda functions to achieve a scalable and decoupled solution.

## Architecture
![alt text](PubSub.drawio.png "PubSub Architecture")
The architecture consists of the following components:

1. **S3 Bucket**: Acts as the source of events when new files are uploaded.
2. **SNS Topic**: Receives event notifications from S3 and fans out messages to SQS queues.
3. **SQS Queue**: Buffers the messages from the SNS topic, decoupling the event source from the processing logic.
4. **Lambda Function**: Processes messages from the SQS queue, formats the message into a Slack-compatible format, and sends it to Slack.

## Detailed Workflow
1. **S3 Event**: When a new file is uploaded to the S3 bucket, an event notification is sent to the SNS topic.
2. **SNS Topic**: The SNS topic fans out the event notification to the SQS queue.
3. **SQS Queue**: Buffers the incoming messages.
4. **Notification Lambda**: Triggered by the SQS queue. It formats the message into a Slack notification with a card containing details and a button linking to the S3 bucket, then sends it to the Slack webhook URL.
5. **Slack Notification**: The Slack message is sent to the specified Slack channel, providing a detailed and formatted notification about the new file upload.


## Prerequisites
1. AWS account with appropriate permissions.
2. AWS CLI installed and configured.
3. AWS CDK (Cloud Development Kit) installed.
4. A Slack workspace and an incoming webhook URL.
5. Node Installed.
6. Python

## Setup and Deployment

### Clone the repository:

```sh
git clone https://github.com/your-repo/aws-pubsub-notification-system.git
cd aws-pubsub-notification-system
```
### Install dependencies:

```sh
pip install -r requirements.txt
```
### Set up environment variables:

Create a .env file in the project root directory and add the Slack webhook URL:
```sh
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/slack/webhook
```

### Deploy the CDK stack:

```sh
cdk deploy
```
### CDK Stack
Here is the CDK stack definition (in Python):

```python
from aws_cdk import (
    aws_s3 as s3,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_sqs as sqs,
    aws_lambda as _lambda,
    aws_iam as iam,
    core,
)

class PubSubNotificationStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # S3 bucket
        bucket = s3.Bucket(self, "MyBucket")

        # SNS topic
        topic = sns.Topic(self, "MyTopic")

        # S3 event notification to SNS
        bucket.add_event_notification(s3.EventType.OBJECT_CREATED, s3_notifications.SnsDestination(topic))

        # SQS queue
        queue = sqs.Queue(self, "MyQueue")

        # Subscribe SQS to SNS topic
        topic.add_subscription(subs.SqsSubscription(queue))

        # Lambda function for processing SQS messages and sending to Slack
        lambda_role = iam.Role(self, "LambdaRole", 
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )

        function = _lambda.Function(self, "MyFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "SLACK_WEBHOOK_URL": os.environ['SLACK_WEBHOOK_URL']
            },
            role=lambda_role
        )

        # Grant the Lambda function permission to read from the SQS queue
        queue.grant_consume_messages(function)

        # Trigger Lambda function on new SQS messages
        function.add_event_source(_lambda_event_sources.SqsEventSource(queue))

app = core.App()
PubSubNotificationStack(app, "PubSubNotificationStack")
app.synth()

```

### Lambda Function Code
Create a lambda directory and add a handler.py file with the following code:

```python
import json
import os
import requests

def lambda_handler(event, context):
    slack_webhook_url = os.environ['SLACK_WEBHOOK_URL']
    
    for record in event['Records']:
        sns_message = json.loads(record['body'])
        s3_event = json.loads(sns_message['Message'])
        
        bucket_name = s3_event['Records'][0]['s3']['bucket']['name']
        file_name = s3_event['Records'][0]['s3']['object']['key']
        
        slack_message = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*New file uploaded*\nBucket: `{bucket_name}`\nFile: `{file_name}`"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "View in S3"
                            },
                            "url": f"https://s3.console.aws.amazon.com/s3/buckets/{bucket_name}"
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(slack_webhook_url, json=slack_message)
        if response.status_code != 200:
            raise ValueError(f"Request to Slack returned an error {response.status_code}, the response is:\n{response.text}")

    return {
        'statusCode': 200,
        'body': json.dumps('Slack notification sent successfully!')
    }
```

### Testing
1. Upload a file to the configured S3 bucket.
2. Check the specified Slack channel for a notification about the new file upload.

### Conclusion
This project demonstrates how to build a scalable and decoupled Pub/Sub notification system using AWS services. By leveraging S3, SNS, SQS, Lambda, and Slack, we can efficiently handle file upload events and notify stakeholders in real-time.