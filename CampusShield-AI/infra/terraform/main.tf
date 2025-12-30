provider "aws" {
  region = "us-west-2"
}

resource "aws_s3_bucket" "campus_shield_bucket" {
  bucket = "campus-shield-ai-bucket"
  acl    = "private"
}

resource "aws_dynamodb_table" "incidents_table" {
  name         = "Incidents"
  billing_mode = "PAY_PER_REQUEST"
  attribute {
    name = "incident_id"
    type = "S"
  }
  hash_key = "incident_id"
}

resource "aws_lambda_function" "incident_handler" {
  function_name = "incidentHandler"
  runtime       = "python3.8"
  handler       = "handler.lambda_handler"
  s3_bucket     = aws_s3_bucket.campus_shield_bucket.bucket
  s3_key        = "lambda/incident_handler.zip"
}

output "s3_bucket_name" {
  value = aws_s3_bucket.campus_shield_bucket.bucket
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.incidents_table.name
}

output "lambda_function_name" {
  value = aws_lambda_function.incident_handler.function_name
}