# OpenTofu example (same syntax as Terraform)
# This demonstrates commented OpenTofu blocks

# resource "aws_instance" "opentofu_example" {
#   ami           = "ami-0c7217cdde317cfec"
#   instance_type = "t2.micro"
#
#   tags = {
#     Name = "OpenTofu-Instance"
#     Tool = "OpenTofu"
#   }
# }

# variable "environment" {
#   description = "Environment name"
#   type        = string
#   default     = "development"
# }

# output "instance_id" {
#   description = "ID of the EC2 instance"
#   value       = aws_instance.opentofu_example.id
# }

# data "aws_availability_zones" "available" {
#   state = "available"
# }

# locals {
#   common_tags = {
#     Environment = var.environment
#     ManagedBy   = "OpenTofu"
#   }
# }
