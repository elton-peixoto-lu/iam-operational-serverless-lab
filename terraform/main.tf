locals {
  tags = {
    Project     = var.project_name
    Owner       = var.owner
    Environment = var.environment
  }

  receiver_role_arn  = var.use_least_privilege_roles ? aws_iam_role.receiver_lambda_role[0].arn : aws_iam_role.shared_lambda_role.arn
  processor_role_arn = var.use_least_privilege_roles ? aws_iam_role.processor_lambda_role[0].arn : aws_iam_role.shared_lambda_role.arn
  worker_role_arn    = var.use_least_privilege_roles ? aws_iam_role.worker_lambda_role[0].arn : aws_iam_role.shared_lambda_role.arn
}

resource "random_id" "bucket_suffix" {
  byte_length = 3
}

