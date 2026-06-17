resource "aws_s3_bucket" "document_input" {
  bucket = "${var.bucket_prefix}-${random_id.bucket_suffix.hex}"
  tags   = local.tags
}

resource "aws_s3_bucket_versioning" "document_input" {
  bucket = aws_s3_bucket.document_input.id

  versioning_configuration {
    status = "Suspended"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "document_input" {
  bucket = aws_s3_bucket.document_input.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_notification" "processor_trigger" {
  bucket = aws_s3_bucket.document_input.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.processor.arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.allow_s3_invoke_processor]
}

