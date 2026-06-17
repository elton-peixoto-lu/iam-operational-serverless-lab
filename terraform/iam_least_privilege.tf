resource "aws_iam_role" "receiver_lambda_role" {
  count              = var.use_least_privilege_roles ? 1 : 0
  name               = "receiver-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
  tags               = local.tags
}

data "aws_iam_policy_document" "receiver_lambda_policy" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:GetItem"
    ]
    resources = [aws_dynamodb_table.document_processing.arn]
  }
}

resource "aws_iam_role_policy" "receiver_lambda_policy" {
  count  = var.use_least_privilege_roles ? 1 : 0
  name   = "receiver-lambda-policy"
  role   = aws_iam_role.receiver_lambda_role[0].id
  policy = data.aws_iam_policy_document.receiver_lambda_policy.json
}

resource "aws_iam_role" "processor_lambda_role" {
  count              = var.use_least_privilege_roles ? 1 : 0
  name               = "processor-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
  tags               = local.tags
}

data "aws_iam_policy_document" "processor_lambda_policy" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }

  statement {
    effect = "Allow"
    actions = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.document_input.arn}/*"]
  }

  statement {
    effect = "Allow"
    actions = ["s3:ListBucket"]
    resources = [aws_s3_bucket.document_input.arn]
  }

  statement {
    effect = "Allow"
    actions = [
      "dynamodb:UpdateItem",
      "dynamodb:GetItem",
      "dynamodb:PutItem"
    ]
    resources = [aws_dynamodb_table.document_processing.arn]
  }

  statement {
    effect = "Allow"
    actions = [
      "sqs:SendMessage",
      "sqs:GetQueueAttributes",
      "sqs:GetQueueUrl"
    ]
    resources = [aws_sqs_queue.document_processing.arn]
  }
}

resource "aws_iam_role_policy" "processor_lambda_policy" {
  count  = var.use_least_privilege_roles ? 1 : 0
  name   = "processor-lambda-policy"
  role   = aws_iam_role.processor_lambda_role[0].id
  policy = data.aws_iam_policy_document.processor_lambda_policy.json
}

resource "aws_iam_role" "worker_lambda_role" {
  count              = var.use_least_privilege_roles ? 1 : 0
  name               = "worker-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
  tags               = local.tags
}

data "aws_iam_policy_document" "worker_lambda_policy" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "dynamodb:UpdateItem",
      "dynamodb:GetItem",
      "dynamodb:PutItem"
    ]
    resources = [aws_dynamodb_table.document_processing.arn]
  }

  statement {
    effect = "Allow"
    actions = [
      "sqs:ChangeMessageVisibility",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:ReceiveMessage"
    ]
    resources = [aws_sqs_queue.document_processing.arn]
  }
}

resource "aws_iam_role_policy" "worker_lambda_policy" {
  count  = var.use_least_privilege_roles ? 1 : 0
  name   = "worker-lambda-policy"
  role   = aws_iam_role.worker_lambda_role[0].id
  policy = data.aws_iam_policy_document.worker_lambda_policy.json
}
