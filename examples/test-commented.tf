# Example Terraform configuration for testing the GitHub Action

# This is a regular comment - should be ignored
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"

  tags = {
    Name = "HelloWorld"
  }
}

# resource "aws_instance" "commented_out" {
#   ami           = "ami-87654321"
#   instance_type = "t3.medium"
#
#   tags = {
#     Name = "CommentedOut"
#   }
# }

# Another regular comment explaining the variable below
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

# variable "commented_variable" {
#   description = "This variable is commented out"
#   type        = string
#   default     = "test"
# }
