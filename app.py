#!/usr/bin/env python3
import os

import aws_cdk as cdk

from pub_sub.pub_sub_stack import PubSubStack


app = cdk.App(
    context= {
        'ACCOUNT_ID': os.getenv('AWS_ACCOUNT_ID'),
        'APP_NAME': 'PubSub',
        'SLACK_WEBHOOK_URL': os.getenv('SLACK_WEBHOOK_URL')
    }
)
stack = PubSubStack(app, "PubSubStack",
    env=cdk.Environment(account=os.getenv('AWS_ACCOUNT_ID'), region='ap-south-1'),
    )

app.synth()
