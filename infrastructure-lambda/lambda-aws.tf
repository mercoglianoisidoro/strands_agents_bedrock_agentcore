


data "archive_file" "lambda_source_code" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_aws_source_code"
  output_path = "${path.module}/lambda_aws_function.zip"
}

resource "aws_lambda_function" "lambda-aws" {
  function_name = local.lambda_function_name
  role          = aws_iam_role.lambda_aws_role_exec.arn
  handler       = "aws.handler"
  runtime       = "provided.al2023"

  filename         = data.archive_file.lambda_source_code.output_path
  source_code_hash = filebase64sha256(data.archive_file.lambda_source_code.output_path)
  architectures    = ["arm64"]

  memory_size = 3008
  timeout     = 300

  layers = [
    aws_lambda_layer_version.jq_layer.arn,
    aws_lambda_layer_version.aws_layer.arn
  ]

  environment {
    variables = {
      CHUNKS_BUCKET = aws_s3_bucket.files_chunks.bucket

    }
  }
  tags = local.default_tags



  depends_on = [aws_lambda_layer_version.jq_layer, aws_lambda_layer_version.aws_layer, data.archive_file.lambda_source_code]
}




# IAM Role: Defines WHO can assume permissions (Lambda service in this case)
# Think of it as an identity that Lambda uses to interact with AWS services
resource "aws_iam_role" "lambda_aws_role_exec" {
  name = local.iam_role_name

  # Trust policy: Allows Lambda service to assume this role
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = local.default_tags
}


resource "aws_lambda_permission" "allow_bedrock_invoke" {
  statement_id  = "bedrock"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda-aws.function_name
  principal     = "bedrock.amazonaws.com"
}


# Attach AWS managed policy for basic Lambda execution (CloudWatch Logs)
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_aws_role_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# IAM Policy: Defines WHAT actions are allowed on WHICH resources
# This policy grants specific S3 permissions on our buckets only
resource "aws_iam_policy" "lambda_s3_access" {
  name        = local.iam_policy_name
  description = "Allow Lambda to access specific S3 buckets"

  # Permission policy: Specifies allowed actions on specific resources
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ],
        Resource = [
          "${aws_s3_bucket.files_bucket.arn}/*",
          "${aws_s3_bucket.files_chunks.arn}/*"
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "s3:ListBucket"
        ],
        Resource = [
          aws_s3_bucket.files_bucket.arn,
          aws_s3_bucket.files_chunks.arn
        ]
      }
    ]
  })

  tags = local.default_tags
}

# Attach the custom S3 policy to the Lambda role
resource "aws_iam_role_policy_attachment" "lambda_s3_access" {
  role       = aws_iam_role.lambda_aws_role_exec.name
  policy_arn = aws_iam_policy.lambda_s3_access.arn
}




# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda_aws_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.lambda-aws.function_name}"
  retention_in_days = 14

  tags = local.default_tags
}



//debugging log group
resource "aws_cloudwatch_log_group" "debug_lambda_aws_log_group" {
  name              = "/aws/lambda/${local.debug_log_group_name}"
  retention_in_days = 14

  tags =local.default_tags
}

resource "aws_cloudwatch_log_stream" "debug_lambda_aws_log_stream" {
  name           = "cli-commands"
  log_group_name = aws_cloudwatch_log_group.debug_lambda_aws_log_group.name
}

