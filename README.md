Here's the updated `README.md` reflecting that the **SSM Parameters are created by CDK**:

---

# **AWS EC2 Proxy Server**

This project provisions an EC2 instance as a proxy server using [Tinyproxy](https://tinyproxy.github.io/). The proxy server is configured dynamically using **AWS CDK** with user data scripts, and allows IP-based filtering managed through **AWS SSM Parameter Store**.

---

## **Features**

- **Proxy Server**: A lightweight proxy server using Tinyproxy.
- **Dynamic IP Management**: IPs allowed to use the proxy are retrieved dynamically from **AWS SSM Parameter Store**.
- **Secure Access**: Tinyproxy credentials (username and password) are securely stored and retrieved from **AWS SSM Parameter Store**.
- **Elastic IP**: The EC2 instance is assigned a static Elastic IP for consistent access.
- **Infrastructure as Code (IaC)**: All resources, including SSM parameters, are provisioned using **AWS CDK**.

---

## **Prerequisites**

1. **AWS Account**
   - Ensure you have access to an AWS account with permissions to create EC2 instances, SSM parameters, and related resources.

2. **AWS CLI**
   - Install and configure the AWS CLI with a profile that has required permissions.
   ```bash
   aws configure
   ```

3. **Node.js**
   - Install Node.js (v14 or higher) for AWS CDK.
   ```bash
   # Verify Node.js installation
   node -v
   ```

4. **AWS CDK**
   - Install AWS CDK globally:
   ```bash
   npm install -g aws-cdk
   ```

5. **Python Environment**
   - Set up a Python virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .\.venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

---

## **Environment Variables**

Create a `.env` file in the root directory with the following variables:

```env
TINYPROXY_USERNAME="your-proxy-username"
TINYPROXY_PASSWORD="your-proxy-password"
ACCOUNT_ID="your-account-id"
REGION="us-east-1"
EC2_INSTANCE_AMI="ami-0e2c8caa4b6378d8c"
IP_LIST="your-ip-lists"
INSTANCE_TYPE="t2.micro"
```

---

## **Deploy the Stack**

1. **Synthesize the CDK Stack:**
   ```bash
   cdk synth
   ```

2. **Deploy the Stack:**
   ```bash
   cdk deploy
   ```

3. **Outputs:**
   - After a successful deployment, the following details will be displayed:
     - **Tinyproxy Username**
     - **Tinyproxy Password**
     - **Elastic IP of the Proxy Server**

---

## **How the SSM Parameters Are Created**

During the CDK deployment, the stack creates the following **SSM Parameters**:

1. `/tinyproxy/username`: Stores the Tinyproxy username (from `.env`).
2. `/tinyproxy/password`: Stores the Tinyproxy password (from `.env`).
3. `/tinyproxy/ip_list`: Stores the list of IPs allowed to use the proxy (from `.env`).

You can view these parameters in the AWS SSM Parameter Store console.

---

## **Testing the Proxy Server**

### **1. Verify Configuration**
- SSH into the EC2 instance:
  ```bash
  ssh -i ec2-key-pair.pem ec2-user@<Elastic_IP>
  ```
- Check the Tinyproxy configuration:
  ```bash
  cat /etc/tinyproxy/tinyproxy.conf | grep Allow
  ```

### **2. Test Locally**
Use `curl` to test the proxy server:
```bash
curl -x http://proxy_user:proxy_password@<Elastic_IP>:8888 https://api.ipify.org
```

### **3. Configure Browser**
Set your browser's proxy settings to use the EC2 instance's Elastic IP on port `8888`.

---

## **Updating the IP List**

To update the allowed IP list:
1. Modify the `/tinyproxy/ip_list` parameter in SSM directly:
   ```bash
   aws ssm put-parameter \
     --name "/tinyproxy/ip_list" \
     --value "new.ip.1,new.ip.2" \
     --overwrite
   ```
2. Restart Tinyproxy on the EC2 instance:
   ```bash
   ssh -i ec2-key-pair.pem ec2-user@<Elastic_IP>
   sudo systemctl restart tinyproxy
   ```

Alternatively, redeploy the stack with a new `IP_LIST` in the `.env` file.

---

## **Cleanup**

To delete all resources created by the stack:
```bash
cdk destroy
```

---

## **Troubleshooting**

- **No Internet Access via Proxy:**
  - Check that the security group allows inbound traffic on port `8888`.
  - Verify the Tinyproxy configuration for `Allow` entries.

- **User Data Not Applied:**
  - Review the Cloud-Init logs:
    ```bash
    sudo cat /var/log/cloud-init-output.log
    ```

- **SSM Permission Issues:**
  - Ensure the EC2 instance role has the necessary `ssm:GetParameter` permission.

---

## **License**

This project is licensed under the MIT License.

---

This reflects that **SSM Parameters are dynamically created by CDK** and eliminates any manual intervention. Let me know if further adjustments are needed!