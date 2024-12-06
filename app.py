#!/usr/bin/env python3
import os

import aws_cdk as cdk
from dotenv import load_dotenv

from aws_proxy_server.aws_proxy_server_stack import AwsProxyServerStack

# Load environment variables from .env file
load_dotenv()

app = cdk.App()

# Fetch account and region from env variable
account_id = os.getenv("ACCOUNT_ID")
region = os.getenv("REGION")

if not account_id or not region:
    raise ValueError("ACCOUNT_ID and REGION must be set in the .env file.")

env = cdk.Environment(
    account= account_id,  # Replace with your AWS account ID
    region= region       # Replace with your desired AWS region
)

AwsProxyServerStack(app, "AwsProxyServerStack", env=env)

app.synth()
