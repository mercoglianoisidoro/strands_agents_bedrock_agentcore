

terraform {

  # backend "s3" {
  #   bucket = "isipilot-core-terraform-states"
  #   key    = var.environment
  #     region = var.region }

  /**

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::isidoro_terraform_states"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::isidoro_terraform_states/simple_ec2"
    }
  ]
}

to create the bucket:
aws s3api create-bucket --bucket isidoro-dev-terraform-states --region eu-west-1 --create-bucket-configuration LocationConstraint=eu-west-1

*/



}


provider "aws" {
  region  = var.region
  profile = var.profile
}


locals {
  default_tags = {
    env = var.environment
  }

  # S3 bucket for storing Lambda layers (jq, AWS CLI)
  bucket_name = "strands-agents-layers-${var.environment}"
  
  # Lambda function that executes AWS CLI commands
  lambda_function_name = "strands-agents-aws-executor-${var.environment}"
  
  # IAM Role: Identity that Lambda assumes to access AWS services
  iam_role_name = "strands-agents-lambda-exec-${var.environment}"
  
  # IAM Policy: Defines specific S3 permissions for the Lambda role
  iam_policy_name = "strands-agents-s3-access-${var.environment}"
  
  # CloudWatch Log Group for debugging Lambda executions
  debug_log_group_name = "strands-agents-debug-${var.environment}"
}


data "aws_partition" "current" {}
data "aws_caller_identity" "current" {}
