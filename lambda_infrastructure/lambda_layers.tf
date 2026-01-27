# Create Lambda Layer for jq
resource "aws_lambda_layer_version" "jq_layer" {
  layer_name  = "strands-agents-jq-${var.environment}"
  description = "Lambda layer containing jq utility"

  s3_bucket = aws_s3_bucket.files_bucket.id
  s3_key    = aws_s3_object.file_upload_jq-layer.key

  compatible_runtimes      = ["provided.al2023"]
  compatible_architectures = ["arm64"]

  depends_on = [aws_s3_object.file_upload_jq-layer]
}

# Create a lightweight AWS CLI bootstrap Lambda layer
resource "aws_lambda_layer_version" "aws_layer" {
  layer_name  = "strands-agents-aws-cli-${var.environment}"
  description = "Lambda layer for AWS CLI"

  s3_bucket = aws_s3_bucket.files_bucket.id
  s3_key    = aws_s3_object.file_upload_aws_layer.key

  compatible_runtimes      = ["provided.al2023"]
  compatible_architectures = ["arm64"]

  depends_on = [aws_s3_object.file_upload_aws_layer]
}



