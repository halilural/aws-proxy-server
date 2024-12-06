import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_proxy_server.aws_proxy_server_stack import AwsProxyServerStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_proxy_server/aws_proxy_server_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwsProxyServerStack(app, "aws-proxy-server")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
