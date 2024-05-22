import aws_cdk as core
import aws_cdk.assertions as assertions

from pub_sub.pub_sub_stack import PubSubStack

# example tests. To run these tests, uncomment this file along with the example
# resource in pub_sub/pub_sub_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = PubSubStack(app, "pub-sub")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
