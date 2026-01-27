

# S3 bucket for storing layers and chunks
resource "aws_s3_bucket" "files_bucket" {
  bucket = local.bucket_name
  tags = merge(
    local.default_tags,
    {
      description = "Strands agents Lambda layers storage"
      goal = "layers"
    }
  )
}



# Upload a file to the S3 bucket
resource "aws_s3_object" "file_upload_jq-layer" {
  bucket = aws_s3_bucket.files_bucket.id
  key    = "jq-layer.zip"
  source = "${path.module}/lambda-layers-files/jq-layer.zip"

  # Calculate etag to ensure file updates are detected
  etag = filemd5("${path.module}/lambda-layers-files/jq-layer.zip")

}

resource "aws_s3_object" "file_upload_aws_layer" {
  bucket = aws_s3_bucket.files_bucket.id
  key    = "aws-lambda-layer.zip"
  source = "${path.module}/lambda-layers-files/aws_lambda_layer.zip"

  # Calculate etag to ensure file updates are detected
  etag = filemd5("${path.module}/lambda-layers-files/aws_lambda_layer.zip")

}








# ------------------------------ CHUNKS


resource "aws_s3_bucket" "files_chunks" {
  bucket        = "${aws_s3_bucket.files_bucket.id}-chunks" # Use a globally unique bucket name
  force_destroy = true                                      # Important!
  tags = merge(
    local.default_tags,
    {
      description = "Strands agents temporary chunks storage"
      goal = "chunks"
    }
  )
}

# Add lifecycle configuration to expire objects after 30 minutes
resource "aws_s3_bucket_lifecycle_configuration" "chunks_lifecycle" {
  bucket = aws_s3_bucket.files_chunks.id

  rule {
    id     = "expire-after-30-minutes"
    status = "Enabled"

    expiration {
      days = 1 # Minimum allowed value in days
    }

    # For more granular control (30 minutes)
    noncurrent_version_expiration {
      noncurrent_days = 1
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }

    filter {
      prefix = ""
    }
  }
}




resource "aws_s3_bucket_policy" "chunks_bucket_policy" {
  bucket = aws_s3_bucket.files_chunks.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          "AWS" : aws_iam_role.lambda_aws_role_exec.arn
        },
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ],
        Resource = [
          aws_s3_bucket.files_chunks.arn,
          "${aws_s3_bucket.files_chunks.arn}/*"
        ]
      }
    ]
  })
}
