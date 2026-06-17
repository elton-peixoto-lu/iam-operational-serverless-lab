resource "aws_sqs_queue" "document_processing" {
  name                       = "document-processing-queue"
  visibility_timeout_seconds = 60
  message_retention_seconds  = 1209600
  tags                       = local.tags
}

resource "aws_sqs_queue" "unauthorized_test" {
  name                      = "document-processing-queue-unauthorized"
  message_retention_seconds = 1209600
  tags                      = local.tags
}

