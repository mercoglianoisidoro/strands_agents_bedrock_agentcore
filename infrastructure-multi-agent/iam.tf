# IAM role for SearxNG EC2 instance
resource "aws_iam_role" "searxng_ec2" {
  name = "${local.name_prefix}_searxng_ec2_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(local.default_tags, {
    Name = "${local.name_prefix}_searxng_ec2_role"
  })
}

# Attach AWS managed policy for SSM
resource "aws_iam_role_policy_attachment" "searxng_ssm" {
  role       = aws_iam_role.searxng_ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# Policy allowing EC2 to write CloudWatch logs
resource "aws_iam_role_policy" "searxng_cloudwatch" {
  name = "${local.name_prefix}_searxng_cloudwatch_policy"
  role = aws_iam_role.searxng_ec2.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/ec2/searxng:*"
      }
    ]
  })
}

# Instance profile to attach IAM role to EC2
resource "aws_iam_instance_profile" "searxng" {
  name = "${local.name_prefix}_searxng_instance_profile"
  role = aws_iam_role.searxng_ec2.name
}
