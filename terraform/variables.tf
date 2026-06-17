variable "aws_region" {
  description = "AWS region for the lab"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "iam-operational-serverless-lab"
}

variable "environment" {
  description = "Environment tag"
  type        = string
  default     = "lab"
}

variable "owner" {
  description = "Owner tag"
  type        = string
  default     = "mentoring"
}

variable "use_least_privilege_roles" {
  description = "Use dedicated least privilege roles instead of the shared role"
  type        = bool
  default     = false
}

variable "bucket_prefix" {
  description = "Bucket name prefix"
  type        = string
  default     = "document-input"
}

