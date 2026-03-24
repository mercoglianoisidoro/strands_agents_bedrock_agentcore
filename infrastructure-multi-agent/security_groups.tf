# Security group for SearxNG EC2 - allows HTTP from VPC and SSH from admin
resource "aws_security_group" "searxng" {
  name        = "${local.name_prefix}_searxng_sg"
  description = "Security group for SearxNG EC2 instance"
  vpc_id      = aws_vpc.multi_agent.id

  ingress {
    description = "HTTP from VPC"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.multi_agent.cidr_block]
  }

  ingress {
    description = "SSH from admin IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [local.admin_ip]
  }

  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.default_tags, {
    Name = "${local.name_prefix}_searxng_sg"
  })
}
