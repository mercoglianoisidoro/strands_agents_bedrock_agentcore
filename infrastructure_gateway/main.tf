terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.18"
    }
  }
}

provider "aws" {
  region  = var.region
  profile = var.profile
}

data "aws_caller_identity" "current" {}
data "aws_partition" "current" {}

locals {
  default_tags = {
    env = var.environment
  }
  gateway_name = "strands-agents-gateway-${var.environment}"
}
