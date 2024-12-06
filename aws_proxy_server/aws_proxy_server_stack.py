import os
from aws_cdk import (
    Stack,
    CfnOutput,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_ssm as ssm
)
from constructs import Construct

class AwsProxyServerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Use the default VPC
        vpc = ec2.Vpc.from_lookup(self, "DefaultVpc", is_default=True)
        
        # Fetch credentials from environment variables
        tinyproxy_username = os.getenv("TINYPROXY_USERNAME")
        tinyproxy_password = os.getenv("TINYPROXY_PASSWORD")
        ec2_instance_ami = os.getenv("EC2_INSTANCE_AMI")
        ip_list = os.getenv("IP_LIST")
        instance_type = os.getenv("INSTANCE_TYPE")
        
        if not tinyproxy_username or not tinyproxy_password or not ec2_instance_ami or not ip_list or not instance_type:
            raise ValueError("TINYPROXY_USERNAME, TINYPROXY_PASSWORD, EC2_INSTANCE_AMI, IP_LIST and INSTANCE_TYPE must be set in the .env file.")
        
        # Create SSM Parameters
        ssm.StringParameter(
            self, "TinyproxyUsernameParameter",
            parameter_name="/tinyproxy/username",
            string_value=tinyproxy_username,
            description="Tinyproxy username for authentication"
        )

        ssm.StringParameter(
            self, "TinyproxyPasswordParameter",
            parameter_name="/tinyproxy/password",
            string_value=tinyproxy_password,
            description="Tinyproxy password for authentication"
        )
        
        ssm.StringParameter(
            self, "TinyproxyIpListParameter",
            parameter_name="/tinyproxy/ip_list",
            string_value=ip_list,
            description="Tinyproxy IP List for access"
        )

        # Define the IAM role for the EC2 instance
        proxy_ec2_instance_role = iam.Role(
            self, "ProxyEC2InstanceRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            inline_policies={
                "SSMAccessPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=["ssm:GetParameter"],
                            resources=[
                                f"arn:aws:ssm:{self.region}:{self.account}:parameter/tinyproxy/*"
                            ]
                        )
                    ]
                )
            }
        )
        
        # Define the EC2 instance profile
        proxy_ec2_instance_profile = iam.CfnInstanceProfile(
            self, "ProxyEC2InstanceProfile",
            roles=[proxy_ec2_instance_role.role_name]
        )
        
        # Define the EC2 instance
        proxy_security_group = ec2.SecurityGroup(
            self, "ProxyEC2SecurityGroup",
            vpc=vpc,
            description="Allow traffic for Tinyproxy and SSH",
            allow_all_outbound=True
        )

        # Allow Tinyproxy (port 8888) and SSH (port 22) access
        proxy_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(8888), "Allow proxy traffic"
        )
        proxy_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "Allow SSH access"
        )
        
        # Convert IP_LIST to a shell-friendly format
        formatted_ip_list = " ".join(ip_list.split(","))

        # Read user data from file and replace placeholder
        user_data_file_path = os.path.join(os.path.dirname(__file__), "../user_data.sh")
        with open(user_data_file_path, "r") as user_data_file:
            user_data_script = user_data_file.read()
        
        # Read user data from file
        with open("user_data.sh", "r") as user_data_file:
            user_data_script = user_data_file.read()

        proxy_ec2_instance = ec2.Instance(
            self, "ProxyEC2Instance",
            instance_type=ec2.InstanceType(instance_type),
            machine_image=ec2.MachineImage.generic_linux({
                self.region: ec2_instance_ami
            }),
            vpc=vpc,
            key_pair=ec2.KeyPair(self,"Key Pair",key_pair_name="ec2-key-pair"),
            security_group=proxy_security_group,
            role=proxy_ec2_instance_role,
            user_data=ec2.UserData.custom(user_data_script)
        )
        # Allocate an Elastic IP
        elastic_ip = ec2.CfnEIP(
            self, "ProxyElasticIP",
            domain="vpc"  # Ensures compatibility with EC2 in a VPC
        )

        # Associate the Elastic IP with the EC2 instance
        ec2.CfnEIPAssociation(
            self, "ProxyElasticIPAssociation",
            allocation_id=elastic_ip.attr_allocation_id,
            instance_id=proxy_ec2_instance.instance_id
        )
        
        # Outputs
        CfnOutput(
            self, "TinyproxyUsernameOutput",
            value=tinyproxy_username,
            description="Tinyproxy username for authentication",
            export_name="TinyproxyUsername"
        )

        CfnOutput(
            self, "TinyproxyPasswordOutput",
            value=tinyproxy_password,
            description="Tinyproxy password for authentication",
            export_name="TinyproxyPassword"
        )

        CfnOutput(
            self, "ElasticIPOutput",
            value=elastic_ip.ref,
            description="Elastic IP of the proxy server",
            export_name="ProxyElasticIP"
        )
