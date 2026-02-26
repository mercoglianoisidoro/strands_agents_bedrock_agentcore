terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.18.0"
    }
    http = {
      source  = "hashicorp/http"
      version = "~> 3.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Docker provider - will use ECR credentials when building
provider "docker" {
  registry_auth {
    address  = data.aws_ecr_authorization_token.token.proxy_endpoint
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}

# Get current AWS account ID
data "aws_caller_identity" "current" {}

# Get current AWS region
data "aws_region" "current" {}

# Get current public IP automatically (IPv4 only)
data "http" "my_ip" {
  url = "https://ipv4.icanhazip.com"
}

# Default tags applied to all resources
locals {
  default_tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
  
  # Use provided admin IP or auto-detect current IP
  admin_ip = var.admin_ip_cidr != "" ? var.admin_ip_cidr : "${chomp(data.http.my_ip.response_body)}/32"
  
  # Naming convention: environment_project_resource
  name_prefix = "${var.environment}_${var.project_name}"
}
