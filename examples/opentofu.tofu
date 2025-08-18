# OpenTofu configuration with .tofu extension
# This demonstrates commented OpenTofu blocks in a .tofu file

# resource "aws_instance" "tofu_example" {
#   ami           = "ami-0c7217cdde317cfec"
#   instance_type = "t2.micro"
#
#   tags = {
#     Name = "OpenTofu-Instance"
#     Tool = "OpenTofu"
#   }
# }

# variable "environment" {
#   description = "Environment name for OpenTofu"
#   type        = string
#   default     = "development"
# }

# output "instance_public_ip" {
#   description = "Public IP of the EC2 instance"
#   value       = aws_instance.tofu_example.public_ip
# }

# locals {
#   tofu_tags = {
#     Environment = var.environment
#     ManagedBy   = "OpenTofu"
#     FileType    = ".tofu"
#   }
# }
