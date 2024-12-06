#!/bin/bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y tinyproxy jq curl unzip
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
rm -rf awscliv2.zip aws

# Fetch credentials from SSM
TINYPROXY_USERNAME=$(aws ssm get-parameter --name /tinyproxy/username --with-decryption --query "Parameter.Value" --output text)
TINYPROXY_PASSWORD=$(aws ssm get-parameter --name /tinyproxy/password --with-decryption --query "Parameter.Value" --output text)

# Fetch IP list from SSM
IP_LIST=$(aws ssm get-parameter --name /tinyproxy/ip_list --with-decryption --query "Parameter.Value" --output text)

# Set Tinyproxy credentials
sudo sed -i "s|^#BasicAuth .*|BasicAuth $TINYPROXY_USERNAME $TINYPROXY_PASSWORD|" /etc/tinyproxy/tinyproxy.conf

# Add IPs to Allow list
sudo sed -i '/^Allow /d' /etc/tinyproxy/tinyproxy.conf
echo "Allow 127.0.0.1" | sudo tee -a /etc/tinyproxy/tinyproxy.conf

IFS=',' read -ra IP_ARRAY <<< "$IP_LIST"
for ip in "${IP_ARRAY[@]}"; do
  echo "Allow $ip" | sudo tee -a /etc/tinyproxy/tinyproxy.conf
done

sudo systemctl restart tinyproxy
sudo systemctl enable tinyproxy