resource "aws_apigatewayv2_api" "http_api" {
  name          = "iam-operational-serverless-lab-api"
  protocol_type = "HTTP"
  tags          = local.tags
}

resource "aws_apigatewayv2_integration" "receiver" {
  api_id                 = aws_apigatewayv2_api.http_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.receiver.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "receiver" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /documents"
  target    = "integrations/${aws_apigatewayv2_integration.receiver.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true
  tags        = local.tags
}

resource "aws_lambda_permission" "allow_apigw_invoke_receiver" {
  statement_id  = "AllowApiGatewayInvokeReceiver"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.receiver.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

