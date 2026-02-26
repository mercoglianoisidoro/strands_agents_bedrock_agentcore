# Network Architecture Explanation

## Overview

This infrastructure creates a **secure, isolated network** for running SearxNG with controlled internet access.

```
┌─────────────────────────────────────────────────────────────────┐
│ VPC: 10.0.0.0/16                                                │
│                                                                 │
│  ┌────────────────────────┐      ┌────────────────────────┐   │
│  │ Public Subnet          │      │ Private Subnet         │   │
│  │ 10.0.100.0/24          │      │ 10.0.1.0/24            │   │
│  │                        │      │                        │   │
│  │  ┌──────────────┐      │      │  ┌──────────────┐     │   │
│  │  │ NAT Gateway  │      │      │  │ EC2 SearxNG  │     │   │
│  │  │ (has EIP)    │      │      │  │ (no public IP)│     │   │
│  │  └──────┬───────┘      │      │  └──────┬───────┘     │   │
│  │         │              │      │         │             │   │
│  └─────────┼──────────────┘      └─────────┼─────────────┘   │
│            │                               │                 │
│            │                               │                 │
│       ┌────▼────┐                     ┌────▼────┐            │
│       │   IGW   │                     │ Private │            │
│       │         │                     │ Route   │            │
│       └────┬────┘                     │ Table   │            │
│            │                          └─────────┘            │
└────────────┼───────────────────────────────────────────────────┘
             │
             ▼
         Internet
```

---

## Components Explained

### 1. VPC (Virtual Private Cloud)
**CIDR**: `10.0.0.0/16`

- Your own **isolated network** in AWS
- Can contain up to 65,536 IP addresses (10.0.0.0 - 10.0.255.255)
- Completely isolated from other AWS customers
- DNS enabled for name resolution

**Think of it as**: Your own private data center in the cloud

---

### 2. Private Subnet (SearxNG)
**CIDR**: `10.0.1.0/24`  
**Location**: Availability Zone A  
**IP Range**: 10.0.1.0 - 10.0.1.255 (256 addresses)

**What lives here**:
- ✅ EC2 instance running SearxNG
- ✅ **No public IP** - cannot be accessed from internet
- ✅ Can only be reached from within the VPC

**Outbound traffic**:
- Goes through NAT Gateway → Internet
- SearxNG can query Google, Bing, etc.

**Inbound traffic**:
- Only from VPC (10.0.0.0/16)
- AgentCore agent can reach it on port 8080
- Admin can SSH from specific IP

**Think of it as**: A locked room with one-way mirror - can see out, but outsiders can't see in

---

### 3. Public Subnet (NAT Gateway)
**CIDR**: `10.0.100.0/24`  
**Location**: Availability Zone A  
**IP Range**: 10.0.100.0 - 10.0.100.255 (256 addresses)

**What lives here**:
- ✅ NAT Gateway only
- ✅ Has public IP addresses
- ✅ Connected to Internet Gateway

**Purpose**:
- Allows private subnet to access internet
- Does NOT allow internet to access private subnet

**Think of it as**: A secure proxy/gateway that forwards requests

---

### 4. Internet Gateway (IGW)
**Purpose**: Connects VPC to the internet

- Attached to VPC
- Allows public subnet to reach internet
- Allows internet to reach public subnet
- Stateless (doesn't track connections)

**Think of it as**: The front door to your VPC

---

### 5. NAT Gateway
**Purpose**: Allows private subnet to access internet without exposing it

**How it works**:
1. SearxNG (10.0.1.X) wants to query Google
2. Request goes to NAT Gateway (10.0.100.X)
3. NAT Gateway uses its **Elastic IP** (public) to make request
4. Response comes back to NAT Gateway
5. NAT Gateway forwards response to SearxNG

**Key feature**: **One-way only**
- ✅ Private → Internet: YES
- ❌ Internet → Private: NO

**Think of it as**: A bouncer that lets people leave but doesn't let strangers in

---

### 6. Elastic IP (EIP)
**Purpose**: Static public IP address for NAT Gateway

- Doesn't change (unlike regular public IPs)
- Attached to NAT Gateway
- This is the IP that search engines see

**Think of it as**: Your permanent phone number

---

### 7. Route Tables

#### Public Route Table
**Routes**:
- `0.0.0.0/0` → Internet Gateway

**Meaning**: "Send all traffic to the internet via IGW"

**Associated with**: Public subnet (NAT Gateway)

---

#### Private Route Table
**Routes**:
- `0.0.0.0/0` → NAT Gateway

**Meaning**: "Send all traffic to NAT Gateway (which then goes to internet)"

**Associated with**: Private subnet (SearxNG)

---

## Traffic Flow Examples

### Example 1: SearxNG Queries Google

```
1. SearxNG (10.0.1.50) → "I want to query google.com"
   ↓
2. Private Route Table → "Send to NAT Gateway"
   ↓
3. NAT Gateway (10.0.100.10) → "I'll use my Elastic IP"
   ↓
4. Internet Gateway → "Forward to internet"
   ↓
5. Google.com receives request from Elastic IP
   ↓
6. Response flows back: Google → IGW → NAT → SearxNG
```

**Key point**: Google sees the Elastic IP, not SearxNG's private IP

---

### Example 2: AgentCore Agent Calls SearxNG

```
1. AgentCore Agent (in VPC) → "Search for Python"
   ↓
2. Sends HTTP request to http://10.0.1.50:8080
   ↓
3. Security Group checks: "Is source from VPC?" → YES
   ↓
4. SearxNG receives request and processes
   ↓
5. Response flows back directly (no NAT needed, same VPC)
```

**Key point**: Internal VPC traffic doesn't go through NAT

---

### Example 3: Hacker Tries to Access SearxNG

```
1. Hacker (internet) → "I want to access 10.0.1.50:8080"
   ↓
2. Internet Gateway → "10.0.1.50 is private, not routable"
   ↓
3. Request BLOCKED ❌
```

**Key point**: Private IPs are not accessible from internet

---

## Security Layers

### Layer 1: Network Isolation
- ✅ SearxNG in **private subnet** (no public IP)
- ✅ Not directly accessible from internet

### Layer 2: Security Group
- ✅ Port 8080: Only from VPC (10.0.0.0/16)
- ✅ Port 22: Only from admin IP
- ✅ All other ports: BLOCKED

### Layer 3: Route Tables
- ✅ Private subnet can't receive inbound from internet
- ✅ All outbound goes through NAT Gateway

### Layer 4: NAT Gateway
- ✅ Stateful: Only allows responses to requests from private subnet
- ✅ Doesn't allow unsolicited inbound connections

---

## Why This Architecture?

### ✅ Security
- SearxNG is **not exposed** to internet
- Can't be attacked directly
- Only accessible from within VPC

### ✅ Functionality
- SearxNG can still query search engines
- NAT Gateway provides internet access
- AgentCore can reach SearxNG internally

### ✅ Compliance
- Follows AWS best practices
- Defense in depth (multiple security layers)
- Principle of least privilege

---

## Cost Breakdown

| Component | Monthly Cost | Why? |
|-----------|--------------|------|
| VPC | Free | AWS doesn't charge for VPCs |
| Subnets | Free | No charge for subnets |
| Internet Gateway | Free | No charge for IGW itself |
| NAT Gateway | ~$32 | **Most expensive** - charged per hour + data |
| Elastic IP | Free* | Free when attached to running resource |
| Route Tables | Free | No charge for route tables |

**Total**: ~$32/month (just for NAT Gateway)

---

## Alternative: NAT Instance (Cost Optimization)

Instead of NAT Gateway, you could use a **NAT Instance** (EC2 t3.nano):

**Cost**: ~$3.80/month (vs $32 for NAT Gateway)

**Trade-offs**:
- ❌ You manage it (updates, patches)
- ❌ Single point of failure
- ❌ Lower throughput
- ✅ Much cheaper

**For prototype**: NAT Instance is fine

---

## Common Questions

### Q: Why not put SearxNG in public subnet?
**A**: Security. Public subnet means public IP, which means internet can try to attack it.

### Q: Can I SSH to SearxNG?
**A**: Yes, but only from your admin IP (configured in `admin_ip_cidr`). You'd need a bastion host or AWS Systems Manager Session Manager.

### Q: What if NAT Gateway fails?
**A**: SearxNG loses internet access (can't query search engines). AgentCore can still reach it internally.

### Q: Can I add more EC2 instances?
**A**: Yes, just add them to the private subnet. They'll automatically use the same NAT Gateway.

### Q: Why separate subnets?
**A**: Security isolation. Public subnet is for internet-facing resources, private for internal resources.

---

## Diagram: Security Boundaries

```
┌─────────────────────────────────────────────────────────┐
│ Internet (Untrusted)                                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
          ┌──────────────────┐
          │ Internet Gateway │ ← Boundary 1: VPC Edge
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │  NAT Gateway     │ ← Boundary 2: Public/Private
          │  (Public Subnet) │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ Security Group   │ ← Boundary 3: Instance Firewall
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ EC2 SearxNG      │ ← Boundary 4: Application
          │ (Private Subnet) │
          └──────────────────┘
```

**4 layers of security** between internet and SearxNG!

---

## Summary

**What you built**:
- Secure, isolated network for SearxNG
- Private subnet (no public IP)
- NAT Gateway for outbound internet access
- Multiple security layers

**Key principle**: **Defense in depth**
- Network isolation (private subnet)
- Firewall (security group)
- Controlled routing (route tables)
- Stateful NAT (NAT Gateway)

**Result**: SearxNG can query the internet, but the internet can't reach SearxNG directly.
