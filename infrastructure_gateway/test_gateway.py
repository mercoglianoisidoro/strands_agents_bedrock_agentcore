#!/usr/bin/env python3
import boto3
import json
import subprocess
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import requests
import sys

# Get gateway URL from Terraform output
def get_gateway_url():
    try:
        result = subprocess.run(
            ["terraform", "output", "-raw", "gateway_url"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print("Error: Could not get gateway_url from Terraform. Run 'terraform apply' first.")
        sys.exit(1)

GATEWAY_URL = get_gateway_url()
REGION = "us-west-2"

def sign_request(url, method, body, session):
    request = AWSRequest(method=method, url=url, data=body, headers={"Content-Type": "application/json"})
    SigV4Auth(session.get_credentials(), "bedrock-agentcore", REGION).add_auth(request)
    return dict(request.headers)

def list_tools():
    session = boto3.Session(region_name=REGION)
    payload = {
        "jsonrpc": "2.0",
        "id": "test-list-tools",
        "method": "tools/list"
    }
    body = json.dumps(payload)
    headers = sign_request(GATEWAY_URL, "POST", body, session)
    response = requests.post(GATEWAY_URL, headers=headers, data=body)
    print("Status:", response.status_code)
    print("Response:", json.dumps(response.json(), indent=2))

def call_tool(aws_access_key, aws_secret_key, region, command):
    session = boto3.Session(region_name=REGION)
    payload = {
        "jsonrpc": "2.0",
        "id": "test-call-tool",
        "method": "tools/call",
        "params": {
            "name": "LambdaAWSExecutor___AWS",
            "arguments": {
                "AWS_ACCESS_KEY_ID": aws_access_key,
                "AWS_SECRET_ACCESS_KEY": aws_secret_key,
                "REGION": region,
                "bash_command": command
            }
        }
    }
    body = json.dumps(payload)
    headers = sign_request(GATEWAY_URL, "POST", body, session)
    response = requests.post(GATEWAY_URL, headers=headers, data=body)
    print("Status:", response.status_code)
    print("Response:", json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("=== Listing tools ===")
    list_tools()
    
    if len(sys.argv) > 1 and sys.argv[1] == "call":
        if len(sys.argv) < 6:
            print("Usage: python test_gateway.py call <access_key> <secret_key> <region> <command>")
            sys.exit(1)
        print("\n=== Calling tool ===")
        call_tool(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
