# Main VPC for multi-agent infrastructure
resource "aws_vpc" "multi_agent" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(local.default_tags, {
    Name = "${local.name_prefix}_vpc"
  })
}

# Private subnet for SearxNG EC2 instance (no public IP)
resource "aws_subnet" "searxng_private" {
  vpc_id            = aws_vpc.multi_agent.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${var.aws_region}a"

  tags = merge(local.default_tags, {
    Name = "${local.name_prefix}_private_a"
  })
}

# Public subnet for NAT Gateway
resource "aws_subnet" "nat_public" {
  vpc_id                  = aws_vpc.multi_agent.id
  cidr_block              = "10.0.100.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = merge(local.default_tags, {
    Name = "${local.name_prefix}_public_a"
  })
}

# Internet Gateway for public subnet
resource "aws_internet_gateway" "multi_agent" {
  vpc_id = aws_vpc.multi_agent.id

  tags = merge(local.default_tags, {
    Name = "${local.name_prefix}_igw"
  })
}

# Elastic IP for NAT Gateway
resource "aws_eip" "nat_gateway" {
  domain = "vpc"

  tags = merge(local.default_tags, {
    Name = "${local.name_prefix}_nat_eip"
  })
}

# NAT Gateway for private subnet outbound traffic
resource "aws_nat_gateway" "multi_agent" {
  allocation_id = aws_eip.nat_gateway.id
  subnet_id     = aws_subnet.nat_public.id

  tags = merge(local.default_tags, {
    Name = "${local.name_prefix}--nat"
  })

  depends_on = [aws_internet_gateway.multi_agent]
}

# Route table for public subnet (routes to Internet Gateway)
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.multi_agent.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.multi_agent.id
  }

  tags = merge(local.default_tags, {
    Name = "${local.name_prefix}--public-rt"
  })
}

# Associate public route table with public subnet
resource "aws_route_table_association" "nat_public" {
  subnet_id      = aws_subnet.nat_public.id
  route_table_id = aws_route_table.public.id
}

# Route table for private subnet (routes to NAT Gateway)
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.multi_agent.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.multi_agent.id
  }

  tags = merge(local.default_tags, {
    Name = "${local.name_prefix}--private-rt"
  })
}

# Associate private route table with private subnet
resource "aws_route_table_association" "searxng_private" {
  subnet_id      = aws_subnet.searxng_private.id
  route_table_id = aws_route_table.private.id
}
