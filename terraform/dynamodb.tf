resource "aws_dynamodb_table" "document_processing" {
  name         = "DocumentProcessing"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "documentId"

  attribute {
    name = "documentId"
    type = "S"
  }

  tags = local.tags
}

