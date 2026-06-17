output "api_endpoint" {
  value = aws_apigatewayv2_stage.default.invoke_url
}

output "document_bucket_name" {
  value = aws_s3_bucket.document_input.bucket
}

output "document_queue_url" {
  value = aws_sqs_queue.document_processing.id
}

output "unauthorized_queue_url" {
  value = aws_sqs_queue.unauthorized_test.id
}

output "document_table_name" {
  value = aws_dynamodb_table.document_processing.name
}

output "receiver_function_name" {
  value = aws_lambda_function.receiver.function_name
}

output "processor_function_name" {
  value = aws_lambda_function.processor.function_name
}

output "worker_function_name" {
  value = aws_lambda_function.worker.function_name
}

output "role_mode" {
  value = var.use_least_privilege_roles ? "least-privilege" : "shared-role"
}

