from aws_cdk import (
    # Duration,
    RemovalPolicy,
    Stack,
    # aws_sqs as sqs,
    aws_s3 as s3,
    aws_kms as kms,
    aws_iam as iam,
    aws_sns as sns,
    aws_sqs as sqs,
    aws_lambda as _lambda,
    aws_sns_subscriptions as sns_subscriptions,
    aws_lambda_event_sources as lambda_event_sources,
    aws_s3_notifications as s3_notifications
)
from constructs import Construct

class PubSubStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        account_id = self.node.try_get_context('ACCOUNT_ID')
        app_name = self.node.try_get_context('APP_NAME')

        # Kms key
        key = kms.Key(self, f'{app_name}Key',
                      alias= f'{app_name}KeyAlias',
                      description='Key for PubSub')
        
        key.grant_encrypt_decrypt(iam.AccountRootPrincipal())

        # s3 bucket       
        s3_bucket = s3.Bucket(self, 
                              f'{app_name}Bucket',
                              bucket_name=f'{account_id}-ap-south-1-pubsub-bucket',
                              encryption_key=key,
                              removal_policy=RemovalPolicy.DESTROY,
                              auto_delete_objects=True
                              )
        # sns topic
        sns_topic = sns.Topic(self, f'{app_name}Topic',
                              topic_name=f'{app_name}Topic')
        
        # sqs queue
        sqs_queue = sqs.Queue(self, f'{app_name}Queue',
                              queue_name=f'{app_name}Queue')
        
        # lambda layer for external libraries used in lambda
        lambda_layer = _lambda.LayerVersion(self, f'{app_name}LambdaLayer',
            code=_lambda.Code.from_asset("./assets/lambda_layer"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="A layer to include requests package"
        )
        
        # lambda function
        lambda_function = _lambda.Function(self, f'{app_name}LambdaFunction',
            function_name=f'{app_name}LambdaFunction',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.main",
            code=_lambda.Code.from_asset("./assets/lambda"),
            layers=[lambda_layer],
            environment={
                'SLACK_WEBHOOK_URL': self.node.try_get_context('SLACK_WEBHOOK_URL')  # Slack Webhook URL as environment variable
            }
        )

        # Add sqs subscription to sns topic
        sns_topic.add_subscription(sns_subscriptions.SqsSubscription(sqs_queue))

        # Add sqs as event source for lambda function
        sqs_queue.grant_consume_messages(lambda_function)
        lambda_function.add_event_source(lambda_event_sources.SqsEventSource(sqs_queue))

        # Add s3 event notification to sns topic
        s3_bucket.add_event_notification(s3.EventType.OBJECT_CREATED, s3_notifications.SnsDestination(sns_topic))

