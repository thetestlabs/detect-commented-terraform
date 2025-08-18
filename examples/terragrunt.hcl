# Terragrunt configuration example
# This demonstrates commented Terragrunt blocks

# include {
#   path = find_in_parent_folders()
# }

# dependency "vpc" {
#   config_path = "../vpc"
#
#   mock_outputs = {
#     vpc_id = "vpc-fake-12345"
#   }
# }

# dependency "security_groups" {
#   config_path = "../security-groups"
# }

terraform {
  source = "github.com/terraform-aws-modules/terraform-aws-ec2-instance?ref=v4.3.0"
}

# inputs = {
#   name = "example-instance"
#
#   instance_type          = "t3.micro"
#   monitoring             = true
#   vpc_security_group_ids = dependency.security_groups.outputs.security_group_ids
#   subnet_id              = dependency.vpc.outputs.private_subnets[0]
# }

# generate "provider" {
#   path      = "provider.tf"
#   if_exists = "overwrite_terragrunt"
#   contents  = <<EOF
# provider "aws" {
#   region = "us-east-1"
# }
# EOF
# }
