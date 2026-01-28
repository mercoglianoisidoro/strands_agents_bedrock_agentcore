# region
output "region" {
  value = var.region
}

output "account_id_used" {
  value = data.aws_caller_identity.current.account_id
}

output "lambda_function_name" {
  value = aws_lambda_function.lambda-aws.function_name
}

output "lambda_function_arn" {
  value = aws_lambda_function.lambda-aws.arn
}

output "chunks_bucket_name" {
  value = aws_s3_bucket.files_chunks.bucket
}

output "layers_bucket_name" {
  value = aws_s3_bucket.files_bucket.bucket
}