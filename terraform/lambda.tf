resource "aws_cloudwatch_log_group" "receiver" {
  name              = "/aws/lambda/receiver-lambda"
  retention_in_days = 7
  tags              = local.tags
}

resource "aws_cloudwatch_log_group" "processor" {
  name              = "/aws/lambda/processor-lambda"
  retention_in_days = 7
  tags              = local.tags
}

resource "aws_cloudwatch_log_group" "worker" {
  name              = "/aws/lambda/worker-lambda"
  retention_in_days = 7
  tags              = local.tags
}

resource "aws_lambda_function" "receiver" {
  function_name    = "receiver-lambda"
  role             = local.receiver_role_arn
  runtime          = "python3.12"
  handler          = "app.handler"
  filename         = "${path.module}/../build/receiver.zip"
  source_code_hash = filebase64sha256("${path.module}/../build/receiver.zip")
  timeout          = 10

  environment {
    variables = {
      TABLE_NAME  = aws_dynamodb_table.document_processing.name
      BUCKET_NAME = aws_s3_bucket.document_input.bucket
    }
  }

  depends_on = [aws_cloudwatch_log_group.receiver]
  tags       = local.tags
}

resource "aws_lambda_function" "processor" {
  function_name    = "processor-lambda"
  role             = local.processor_role_arn
  runtime          = "python3.12"
  handler          = "app.handler"
  filename         = "${path.module}/../build/processor.zip"
  source_code_hash = filebase64sha256("${path.module}/../build/processor.zip")
  timeout          = 20

  environment {
    variables = {
      TABLE_NAME             = aws_dynamodb_table.document_processing.name
      BUCKET_NAME            = aws_s3_bucket.document_input.bucket
      QUEUE_URL              = aws_sqs_queue.document_processing.id
      UNAUTHORIZED_QUEUE_URL = aws_sqs_queue.unauthorized_test.id
    }
  }

  depends_on = [aws_cloudwatch_log_group.processor]
  tags       = local.tags
}

resource "aws_lambda_function" "worker" {
  function_name    = "worker-lambda"
  role             = local.worker_role_arn
  runtime          = "python3.12"
  handler          = "app.handler"
  filename         = "${path.module}/../build/worker.zip"
  source_code_hash = filebase64sha256("${path.module}/../build/worker.zip")
  timeout          = 20

  environment {
    variables = {
      TABLE_NAME  = aws_dynamodb_table.document_processing.name
      BUCKET_NAME = aws_s3_bucket.document_input.bucket
      QUEUE_URL   = aws_sqs_queue.document_processing.id
    }
  }

  depends_on = [aws_cloudwatch_log_group.worker]
  tags       = local.tags
}

resource "aws_lambda_event_source_mapping" "worker_sqs" {
  event_source_arn = aws_sqs_queue.document_processing.arn
  function_name    = aws_lambda_function.worker.arn
  batch_size       = 1
  enabled          = true
}

resource "aws_lambda_permission" "allow_s3_invoke_processor" {
  statement_id  = "AllowS3InvokeProcessor"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.document_input.arn
}

