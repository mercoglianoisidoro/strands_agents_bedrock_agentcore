variable "region" {
  description = "AWS region"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "profile" {
  description = "AWS profile to use"
  type        = string
}

variable "lambda_arn" {
  description = "ARN of the Lambda function to use as target"
  type        = string
}
