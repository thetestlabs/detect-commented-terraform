# This is a regular comment - should be ignored
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
}

# data "aws_region" "current" {}

data "aws_caller_identity" "current" {}

# This is a commented out resource block - should be detected
# resource "aws_instance" "web" {
#   ami           = "ami-12345678"
#   instance_type = "t2.micro"
#
#   tags = {
#     Name = "HelloWorld"
#   }
# }

resource "aws_s3_bucket" "example" {
  bucket = "my-terraform-bucket"
}

# Another commented out block - should be detected
# resource "aws_s3_bucket_versioning" "example" {
#   bucket = aws_s3_bucket.example.id
#   versioning_configuration {
#     status = "Enabled"
#   }
# }

# TODO: Add more resources later - should be ignored

# variable "instance_type" {
#   description = "EC2 instance type"
#   type        = string
#   default     = "t2.micro"
# }

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

output "bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.example.bucket
}
