from strands import tool
import boto3
import json
import os
from typing import Dict, Any, Optional
import time
import random

@tool
def lambda_aws_cli_executor(
    bash_command: str,
    region: str,
    aws_access_key_id: str,
    aws_secret_access_key: str,
    aws_session_token: Optional[str] = None,
    debug_mode: bool = False
) -> str:
    """
    Execute AWS CLI commands via Lambda function.
    Note: this tool requires valid AWS credentials to connect to a target account where this tool is executed,
    these execution credentials come from the environment.
    
    Required environment variables:
    - AWS_PROFILE_LAMBDA_AWS_CLI_EXECUTOR: AWS profile to use for Lambda invocation
    - LAMBDA_FUNCTION_NAME: Name of the Lambda function to invoke (e.g., strands-agents-aws-executor-{env})

    Args:
        bash_command (str): The AWS CLI command to execute. Ideally ask for text as output.
        region (str): AWS region to use for the command.
        aws_access_key_id (str): AWS access key ID to use for executing the command.
        aws_secret_access_key (str): AWS secret access key to use for executing the command.
        aws_session_token (Optional[str]): AWS session token to use for executing the command: this is optional.
        debug_mode (bool): Enable debug logging.

    Returns:
        str: The command output
    """
    if debug_mode:
        print(f"Executing Lambda with command: {bash_command}")

    profile_name = os.getenv('AWS_PROFILE_LAMBDA_AWS_CLI_EXECUTOR')
    if not profile_name or not profile_name.strip():
        raise ValueError("AWS_PROFILE_LAMBDA_AWS_CLI_EXECUTOR environment variable must be set to a valid profile name")
    print(f"Using AWS profile: {profile_name}")
    session = boto3.Session(profile_name=profile_name)

    # Create Lambda client
    lambda_client = session.client(
        'lambda'
    )

    # Create payload
    payload = {
        "messageVersion": "1.0",
        "function": "aws",
        "parameters": [
            {
                "name": "AWS_SESSION_TOKEN",
                "type": "string",
                "value": aws_session_token or ""
            },
            {
                "name": "AWS_ACCESS_KEY_ID",
                "type": "string",
                "value": aws_access_key_id
            },
            {
                "name": "AWS_SECRET_ACCESS_KEY",
                "type": "string",
                "value": aws_secret_access_key
            },
            {
                "name": "bash_command",
                "type": "string",
                "value": bash_command
            },
            {
                "name": "REGION",
                "type": "string",
                "value": region
            }
        ],
        "sessionId": f"session-{int(time.time() * 1000)}-{random.randint(100, 999)}"
    }

    # Get Lambda function name from environment variable
    lambda_function_name = os.getenv('LAMBDA_FUNCTION_NAME')
    if not lambda_function_name or not lambda_function_name.strip():
        raise ValueError("LAMBDA_FUNCTION_NAME environment variable must be set")
    
    if debug_mode:
        print(f"Using Lambda function: {lambda_function_name}")

    try:
        # Invoke Lambda function
        response = lambda_client.invoke(
            FunctionName=lambda_function_name,
            Payload=json.dumps(payload),
            InvocationType="RequestResponse"
        )

        # Parse response
        payload_response = response['Payload'].read().decode('utf-8')
        result = json.loads(payload_response)

        if debug_mode:
            print(f"Lambda response: {json.dumps(result, indent=2)}")

        command_result = result['response']['functionResponse']['responseBody']['TEXT']['body']
        print("\n\n\n" + "-"*50)
        print(f"Lambda Command: {bash_command}")
        print(f"Lambda result: {command_result}")
        print("-"*50 + "\n\n\n")

        return command_result

    except KeyError as error:
        print(f"Lambda response parsing error: {error}")
        raise ValueError(f"Unexpected Lambda response format: {error}") from error
    except json.JSONDecodeError as error:
        print(f"Lambda response JSON decode error: {error}")
        raise ValueError(f"Invalid JSON in Lambda response: {error}") from error
    except boto3.exceptions.Boto3Error as error:
        print(f"AWS/Boto3 error: {error}")
        raise RuntimeError(f"AWS Lambda invocation failed: {error}") from error
