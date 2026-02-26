# CloudWatch log group for SearxNG EC2 logs
resource "aws_cloudwatch_log_group" "searxng" {
  name              = "/aws/ec2/${var.environment}_searxng"
  retention_in_days = 7

  tags = merge(local.default_tags, {
    Name = "${local.name_prefix}_searxng_logs"
  })
}
