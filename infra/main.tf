provider "aws" {
    region = "eu-central-1"
}

# S3 Bucket for Model Storage
resource "aws_s3_bucket" "model_bucket" {
  bucket = "house-price-prediction-model-bucket"
}

resource "aws_s3_object" "model_file" {
  bucket = aws_s3_bucket.model_bucket.id
  key    = "model_1744656136812.pkl"
  source = "./bundles/model_1744656136812.pkl"
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "lambda_s3_access_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "lambda_s3_policy" {
  name = "lambda_s3_access_policy"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject"]
      Resource = "${aws_s3_bucket.model_bucket.arn}/*"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "attach_s3_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_s3_policy.arn
}

# Lambda Function
resource "aws_lambda_function" "house_price_prediction_lambda" {
  function_name    = "house-price-prediction"
  runtime         = "python3.8"
  handler         = "lambda_function.lambda_handler"
  role            = aws_iam_role.lambda_role.arn
  timeout         = 30
  memory_size     = 256

  filename         = "./bundles/house_price_prediction_lmb_17444706363N.zip"  # Package your Lambda code into a ZIP file
  source_code_hash = filebase64sha256("./bundles/house_price_prediction_lmb_17444706363N.zip")

  environment {
    variables = {
      MODEL_S3_BUCKET = aws_s3_bucket.model_bucket.id
      MODEL_S3_KEY    = "model_1744656136812.pkl"
    }
  }
  layers = [
    aws_lambda_layer_version.external_packages_layer.arn,
    aws_lambda_layer_version.internal_packages_layer.arn,
  ]
}

# API Gateway
resource "aws_apigatewayv2_api" "http_api" {
  name          = "ml-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.house_price_prediction_lambda.invoke_arn
}

resource "aws_apigatewayv2_route" "lambda_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /predict"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_lambda_permission" "apigw" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.house_price_prediction_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*"
}

output "api_gateway_url" {
  value = aws_apigatewayv2_api.http_api.api_endpoint
}

# =============================================Uploading of Layers to S3
# Upload external_packages_layer to S3
resource "aws_s3_object" "external_packages_layer" {
  bucket = aws_s3_bucket.model_bucket.id
  key    = "external_pkgs_layer_17446516473N.zip"
  source = "./bundles/external_pkgs_layer_17446516473N.zip" # Path to your local zip file
  etag   = filemd5("./bundles/external_pkgs_layer_17446516473N.zip")
}

# Upload internal_packages_layer to S3
resource "aws_s3_object" "internal_packages_layer" {
  bucket = aws_s3_bucket.model_bucket.id
  key    = "internal_packages_layer_17446524453N.zip"
  source = "./bundles/internal_packages_layer_17446524453N.zip" # Path to your local zip file
  etag   = filemd5("./bundles/internal_packages_layer_17446524453N.zip")
}

# =============================================Creation of Layers
#  Create the Lambda Layer with Terraform
resource "aws_lambda_layer_version" "external_packages_layer" {
  layer_name          = "external-packages-layer"
  description         = "Lambda with external packages"
  compatible_runtimes = ["python3.8"] # Specify the runtimes
  s3_bucket           = aws_s3_bucket.model_bucket.id
  s3_key              = aws_s3_object.external_packages_layer.key
}

#  Create the build_model_layer Layer with Terraform
resource "aws_lambda_layer_version" "internal_packages_layer" {
  layer_name          = "internal-packages-layer"
  description         = "Lambda layer with internal packages codebase"
  compatible_runtimes = ["python3.8"] # Specify the runtimes
  s3_bucket           = aws_s3_bucket.model_bucket.id
  s3_key              = aws_s3_object.internal_packages_layer.key
}

resource "aws_iam_role" "lambda_exec" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}