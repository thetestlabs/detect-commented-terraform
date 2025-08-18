# Why Use This Tool?

## The Problem with Commented-Out Code

While commenting out code can be a useful technique during local development and testing, **commented-out code should never be committed to a shared repository**. This tool helps you identify and remove such code from your Terraform configurations.

### When Local Testing Goes Wrong

It's common during Terraform development to temporarily comment out resources or configurations:

```terraform
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"
}

# Temporarily disabled for testing
# resource "aws_s3_bucket" "logs" {
#   bucket = "my-app-logs"
#   versioning {
#     enabled = true
#   }
# }

resource "aws_security_group" "web" {
  name = "web-sg"
  # ... configuration
}
```

This practice is perfectly fine for **local experimentation**, but becomes problematic when accidentally committed to version control.

## Why Commented-Out Code is Harmful

### 🗑️ Dead Code Pollution

Commented-out code creates **"dead code"** that serves no functional purpose but pollutes your codebase:

- **Confusion for Team Members**: Other developers don't know if the code is intentionally disabled, temporarily commented, or forgotten
- **Maintenance Burden**: Dead code still needs to be updated when APIs change, even though it's not active
- **Code Review Overhead**: Reviewers waste time trying to understand the purpose of commented code

### 📚 Version Control Redundancy

One of the most compelling arguments against commented-out code is that **version control systems already serve this purpose**:

- **Git History**: Previous versions of your code are permanently stored in git history
- **Easy Recovery**: You can always retrieve deleted code using `git log`, `git show`, or `git checkout`
- **Better Documentation**: Commit messages provide context about why code was removed
- **Clean Current State**: The current branch represents the actual, working configuration

```bash
# Instead of commenting out code, delete it and use git to recover if needed
git log --oneline -- path/to/file.tf
git show <commit-hash>:path/to/file.tf
```

### 🏗️ Infrastructure Drift and Confusion

In Terraform specifically, commented-out code can lead to:

**State Management Issues**
: Commented infrastructure might still exist in your Terraform state, leading to confusion about what's actually deployed.

**Security Concerns**
: Commented-out security groups, IAM policies, or network configurations might contain sensitive or overly permissive settings that shouldn't be visible in the repository.

**Cost Management**
: Teams might be unclear about whether commented resources are actually running and incurring costs.

**Compliance Problems**
: Auditors and compliance tools may flag commented-out configurations as potential security risks.

### 🔧 Code Quality and Maintainability

Commented-out code degrades overall code quality:

- **Violates YAGNI Principle**: "You Aren't Gonna Need It" - if code isn't being used, it shouldn't be there
- **Reduces Readability**: Large blocks of commented code make it harder to focus on active configurations
- **Testing Complications**: It's unclear whether commented code should be tested or validated
- **Documentation Confusion**: Comments should explain *why*, not store unused *what*

### 👥 Team Collaboration Issues

In team environments, commented-out code creates communication problems:

- **Unclear Intent**: Team members can't determine if code is temporarily disabled or permanently removed
- **Merge Conflicts**: Commented blocks can cause unnecessary merge conflicts
- **Code Review Friction**: Reviewers must ask clarifying questions about commented code intent
- **Knowledge Transfer**: New team members may waste time trying to understand dead code

## When to Use This Tool

### 🚀 Perfect for CI/CD Pipelines

Integrate `detect-commented-terraform` into your continuous integration pipeline:

```yaml
# .github/workflows/terraform-quality.yml
- name: Check for commented Terraform code
  run: detect-commented-terraform scan .
```

### 🪝 As a Pre-commit Hook

Prevent commented code from ever reaching your repository:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/thetestlabs/detect-commented-terraform
    rev: v1.0.0 # Use the latest version
    hooks:
      - id: detect-commented-terraform
```

### 💻 Development Workflow Integration

Make it part of your standard development workflow:

```bash
# Before committing changes
detect-commented-terraform scan src/terraform/

# Automatically fix issues
detect-commented-terraform scan src/terraform/ --fix
```

## Best Practices Instead

Rather than commenting out code, consider these alternatives:

### 🎯 Use Feature Flags

For conditional infrastructure:

```terraform
variable "enable_monitoring" {
  description = "Enable monitoring infrastructure"
  type        = bool
  default     = true
}

resource "aws_cloudwatch_dashboard" "main" {
  count = var.enable_monitoring ? 1 : 0
  # ... configuration
}
```

### 🌍 Use Separate Environments

For testing different configurations:

```bash
# Different tfvars files for different scenarios
terraform plan -var-file="environments/testing.tfvars"
terraform plan -var-file="environments/production.tfvars"
```

### 🏢 Use Terraform Workspaces

For environment-specific variations:

```bash
terraform workspace new testing
terraform workspace select testing
```

### 📝 Document with TODO Comments

If you need to remember to implement something later:

```terraform
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  # TODO: Add monitoring configuration after monitoring module is ready
  # See: https://github.com/company/terraform-modules/issues/123
}
```

## The Bottom Line

**Commented-out code is a code smell** that indicates process problems in your development workflow. This tool helps you maintain clean, professional Terraform codebases by:

✅ **Detecting** commented-out Terraform configurations
✅ **Preventing** dead code from entering your repository
✅ **Maintaining** high code quality standards
✅ **Improving** team collaboration and code clarity
✅ **Reducing** maintenance overhead and confusion

> **Remember**: If you don't need the code right now, delete it. Git will remember it for you.

## Real-World Impact

### Before Using This Tool

```terraform
# This is a mess - what's active? What's not?
resource "aws_instance" "web" {
  ami = "ami-12345678"
  instance_type = "t3.micro"
}

# resource "aws_instance" "worker" {
#   ami = "ami-87654321"
#   instance_type = "t3.small"
# }

# TODO: maybe enable this later?
# resource "aws_s3_bucket" "logs" {
#   bucket = "app-logs"
# }

resource "aws_security_group" "web" {
  name = "web-sg"
}

# resource "aws_security_group" "worker" {
#   name = "worker-sg"
# }
```

### After Using This Tool

```terraform
# Clean, clear, and purposeful
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"
}

resource "aws_security_group" "web" {
  name = "web-sg"

  # TODO: Add worker security group after worker instances are implemented
  # See: https://github.com/company/infrastructure/issues/456
}
```

The difference is clear: **clean code that communicates intent effectively**.
