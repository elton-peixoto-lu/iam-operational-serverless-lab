data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "shared_lambda_role" {
  name               = "shared-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
  tags               = local.tags
}

data "aws_iam_policy_document" "shared_lambda_policy" {
  statement {
    sid    = "CloudWatchLogs"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }

  statement {
    sid    = "BroadDynamoDb"
    effect = "Allow"
    actions = [
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:GetItem",
      "dynamodb:Scan",
      "dynamodb:Query",
      "dynamodb:DescribeTable"
    ]
    resources = [aws_dynamodb_table.document_processing.arn]
  }

  statement {
    sid    = "BroadS3"
    effect = "Allow"
    actions = [
      "s3:ListAllMyBuckets",
      "s3:ListBucket",
      "s3:GetObject",
      "s3:PutObject"
    ]
    resources = [
      "*",
      aws_s3_bucket.document_input.arn,
      "${aws_s3_bucket.document_input.arn}/*"
    ]
  }

  statement {
    sid    = "BroadSqs"
    effect = "Allow"
    actions = [
      "sqs:ChangeMessageVisibility",
      "sqs:DeleteMessage",
      "sqs:ReceiveMessage",
      "sqs:SendMessage",
      "sqs:GetQueueAttributes",
      "sqs:GetQueueUrl"
    ]
    resources = [
      aws_sqs_queue.document_processing.arn,
      aws_sqs_queue.unauthorized_test.arn
    ]
  }
}

resource "aws_iam_role_policy" "shared_lambda_policy" {
  name   = "shared-lambda-policy"
  role   = aws_iam_role.shared_lambda_role.id
  policy = data.aws_iam_policy_document.shared_lambda_policy.json
}
