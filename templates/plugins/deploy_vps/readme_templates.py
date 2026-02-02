"""
README templates for deploy-vps plugin.
Generates README.md and QUICK_START.md documentation.
"""


def generate_readme() -> str:
    """Generate README.md file content."""
    return '''# Deploy-VPS: Reusable Deployment System

A template-based, zero-hardcoded deployment system for FastAPI + PostgreSQL + Redis + Celery applications. Deploy the same codebase to different servers and domains by changing a single configuration file.

## Table of Contents

- [What Makes This Different](#what-makes-this-different)
- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Configuration Reference](#configuration-reference)
- [Available Commands](#available-commands)
- [Troubleshooting](#troubleshooting)

---

## What Makes This Different

### Key Features
✅ **Zero hardcoded domains** - everything from `config.env`
✅ **Template-based** - `{{PLACEHOLDERS}}` auto-replaced
✅ **Project-agnostic** - works for any FastAPI project
✅ **Cross-platform** - bash string substitution (no sed)
✅ **Single source of truth** - one config file controls everything
✅ **Environment support** - production and staging from same templates

---

## Quick Start

**📚 New to deployment? See [QUICK_START.md](./QUICK_START.md) for step-by-step guide!**

```bash
# 1. Navigate to deploy-vps directory
cd deploy-vps

# 2. Make scripts executable (on server)
chmod +x scripts/*.sh scripts/optional/*.sh scripts/common/*.sh

# 3. Run complete setup (system checks + config + generation)
./scripts/setup.sh

# 4. Review and customize the generated environment file
nano .env.production
# Add your API keys (SMS, Sentry, Object Storage, etc.)

# 5. Validate configuration
./scripts/validate.sh --env production

# 6. Deploy to production
./scripts/deploy.sh init --env production

# 7. Setup SSL certificates
./scripts/ssl.sh setup --env production

# 8. Check deployment status
./scripts/deploy.sh status --env production
```

**Done!** Your application is now deployed with SSL at `https://api.yourdomain.com` 🎉

---

## Prerequisites

### Required
- **Docker** (v20.10+) - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** (v2.0+ or v1.29+)
- **Git** - For version control
- **Bash** (v4.0+) - Already on Linux/macOS

### Optional but Recommended
- **OpenSSL** - For generating secure secrets (usually pre-installed)
- **Domain with DNS access** - For production deployment
- **Server with root access** - For production deployment

### Verify Prerequisites

```bash
# Check Docker
docker --version
docker compose version  # or docker-compose --version

# Check Bash version
bash --version

# Check OpenSSL
openssl version
```

---

## Configuration Reference

### config.env (Single Source of Truth)

Located at: `deploy-vps/config.env`

**Core Settings:**
```bash
# Project Identity
PROJECT_NAME=myproject               # Your project name
BASE_DOMAIN=example.com              # Your main domain

# Subdomains
API_SUBDOMAIN=api                    # API accessible at api.example.com
FLOWER_SUBDOMAIN=flower              # Flower at flower.example.com

# Contact
ACME_EMAIL=admin@example.com         # SSL certificate notifications
```

**Environment-Specific Settings:**
```bash
# Production
PRODUCTION_API_WORKERS=4             # Gunicorn workers
PRODUCTION_CELERY_WORKERS=4          # Celery concurrency
PRODUCTION_POSTGRES_HOST=db-managed.example.com
PRODUCTION_POSTGRES_PORT=25060
PRODUCTION_DB_SSL_MODE=require

# Staging (for testing)
STAGING_API_WORKERS=2                # Fewer workers for staging
STAGING_CELERY_WORKERS=2
STAGING_POSTGRES_HOST=postgres       # Uses containerized PostgreSQL
STAGING_POSTGRES_PORT=5432
STAGING_DB_SSL_MODE=disable
```

---

## Available Commands

### Core Scripts

#### 1. `setup.sh` - Complete Initial Setup
```bash
# Run interactive setup (system checks + config + generation)
./scripts/setup.sh

# Force regenerate existing configuration
./scripts/setup.sh --force
```

#### 2. `validate.sh` - Configuration Validation
```bash
# Validate configuration before deployment
./scripts/validate.sh --env production
./scripts/validate.sh --env staging
```

#### 3. `deploy.sh` - Deployment Management

```bash
# Initial deployment
./scripts/deploy.sh init --env production

# Update deployment (git pull, rebuild, rolling restart)
./scripts/deploy.sh update --env production

# Restart all services
./scripts/deploy.sh restart --env production

# Stop all services
./scripts/deploy.sh stop --env production

# Check service status
./scripts/deploy.sh status --env production

# View logs (live tail)
./scripts/deploy.sh logs --env production
```

#### 4. `ssl.sh` - SSL Certificate Management

```bash
# Initial SSL setup
./scripts/ssl.sh setup --env production

# Force certificate renewal
./scripts/ssl.sh renew --env production

# Check certificate expiry
./scripts/ssl.sh check --env production

# Test SSL configuration
./scripts/ssl.sh test --env production

# Test with Let's Encrypt staging (no rate limits)
./scripts/ssl.sh setup --env production --staging
```

### Optional Scripts

#### 5. `backup.sh` - Database Backups (Optional)

```bash
# Full backup (database, Redis, logs, config)
./scripts/optional/backup.sh full --env production

# Database only backup
./scripts/optional/backup.sh db --env production

# Restore from backup
./scripts/optional/backup.sh restore --env production backups/backup.tar.gz
```

#### 6. `security-setup.sh` - Server Hardening (Optional)

```bash
# Setup firewall, fail2ban, automatic updates (run once on fresh server)
sudo ./scripts/optional/security-setup.sh
```

---

## Directory Structure

```
deploy-vps/
├── QUICK_START.md             # ← Step-by-step deployment guide
├── README.md                  # ← Comprehensive reference (this file)
├── config.env                 # ← Edit this (single source of truth)
├── .env.production            # ← Generated (add secrets here)
├── .env.staging               # ← Generated
│
├── templates/                 # ← Template files (never edit)
│   ├── env/
│   ├── docker/
│   ├── nginx/
│   └── redis/
│
├── generated/                 # ← Auto-generated (never edit directly)
│   ├── docker-compose.production.yml
│   ├── docker-compose.staging.yml
│   ├── nginx/
│   └── redis/
│
└── scripts/                   # ← Core automation scripts
    ├── setup.sh               # Complete setup (checks + config + generation)
    ├── validate.sh            # Configuration validation
    ├── deploy.sh              # Deployment management
    ├── ssl.sh                 # SSL certificate management
    ├── common/                # Shared utility functions
    └── optional/              # Optional scripts (backup, security)
```

---

## Troubleshooting

### Issue: DNS not resolving

**Solution:**
1. Verify DNS records are configured correctly
2. Wait 5-60 minutes for DNS propagation
3. Check with: `nslookup api.example.com`

### Issue: Port already in use

**Solution:**
1. Check what's using the port: `sudo lsof -i :80`
2. Stop conflicting service: `sudo systemctl stop apache2` (or nginx)

### Issue: SSL certificate failed

**Solution:**
1. Ensure DNS resolves correctly (critical!)
2. Check firewall allows ports 80 and 443
3. Use staging environment for testing:
   ```bash
   ./scripts/ssl.sh setup --env production --staging
   ```

### Get Help

**Check logs:**
```bash
# All services
./scripts/deploy.sh logs --env production

# Specific service
docker logs myproject_api
docker logs myproject_nginx
docker logs myproject_redis
```

---

## License

MIT License

---

*Generated by FCube CLI - Modern FastAPI Project & Module Generator*
'''


def generate_quick_start() -> str:
    """Generate QUICK_START.md file content."""
    return '''# Deploy-VPS Quick Start Guide

Simple step-by-step guide to deploy your application from development to production server.

---

## 📋 Prerequisites

Before starting, ensure you have:
- **Production Server**: Ubuntu/Debian Linux server with SSH access
- **Domain**: Registered domain with DNS access (e.g., example.com)
- **Database**: PostgreSQL database (for production) or use containerized DB (for staging)

---

## 🚀 Deployment Steps

### **Step 1: Prepare Your Server**

SSH into your production server:
```bash
ssh user@your-server-ip
```

Install required packages:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Logout and login again for docker group to take effect
exit
ssh user@your-server-ip
```

Verify Docker installation:
```bash
docker --version
docker compose version
```

---

### **Step 2: Clone Repository on Server**

```bash
# Clone your repository
cd ~
git clone https://github.com/your-org/your-project.git
cd your-project/deploy-vps

# Make scripts executable
chmod +x scripts/*.sh
chmod +x scripts/optional/*.sh
chmod +x scripts/common/*.sh
```

---

### **Step 3: Configure DNS**

Before proceeding, configure your DNS records:

**For Production:**
- `api.yourdomain.com` → Server IP Address (A record)
- `flower.yourdomain.com` → Server IP Address (A record)

**Wait 5-10 minutes for DNS propagation**, then verify:
```bash
dig api.yourdomain.com
dig flower.yourdomain.com
```

---

### **Step 4: Run Initial Setup**

This will check system prerequisites and collect your configuration:

```bash
./scripts/setup.sh
```

**The setup will:**
1. ✅ Check Docker, Docker Compose, and system requirements
2. ✅ Ask you to configure Production, Staging, or Both
3. ✅ Collect project information (name, domain, email)
4. ✅ Collect database credentials
5. ✅ Generate all configuration files automatically
6. ✅ Generate secure secrets (SECRET_KEY, JWT_SECRET_KEY, etc.)

---

### **Step 5: Add API Keys**

After setup completes, edit the generated environment files:

```bash
nano .env.production
```

**Add your API keys:**
```bash
# SMS Service
FAST2SMS_API_KEY=your_fast2sms_key_here

# Error Tracking
SENTRY_DSN=your_sentry_dsn_here

# Object Storage
DO_SPACES_REGION=nyc3
DO_SPACES_BUCKET=your-bucket-name
DO_SPACES_KEY=your_spaces_key
DO_SPACES_SECRET=your_spaces_secret
```

Save and exit (Ctrl+X, then Y, then Enter)

---

### **Step 6: Validate Configuration**

Before deploying, validate everything is correct:

```bash
./scripts/validate.sh --env production
```

**Fix any errors** before proceeding.

---

### **Step 7: Initial Deployment**

Deploy your application:

```bash
./scripts/deploy.sh init --env production
```

**This will:**
1. 🐳 Pull Docker images
2. 🏗️ Build application containers
3. 🚀 Start services (Redis, API, Celery, Flower)
4. 📊 Run database migrations
5. ✅ Verify services are running

**Wait for the process to complete** (3-5 minutes)

---

### **Step 8: Setup SSL Certificates**

Setup Let's Encrypt SSL certificates (required for HTTPS):

```bash
./scripts/ssl.sh setup --env production
```

**⚠️ Important:**
- Use `--staging` flag for testing: `./scripts/ssl.sh setup --env production --staging`
- Let's Encrypt has rate limits (5 per domain per week)
- Test with staging server first, then run without `--staging` for real certificates

---

### **Step 9: Verify Deployment**

Check if everything is running:

```bash
./scripts/deploy.sh status --env production
```

Test your API endpoints:
```bash
# Check API health
curl https://api.yourdomain.com/health

# Check Flower (monitoring)
# Open in browser: https://flower.yourdomain.com
```

---

## 🔧 Daily Operations

### Update Deployment (After Code Changes)

```bash
./scripts/deploy.sh update --env production
```

### Restart Services

```bash
./scripts/deploy.sh restart --env production
```

### View Logs

```bash
./scripts/deploy.sh logs --env production
```

### Check Status

```bash
./scripts/deploy.sh status --env production
```

---

## 🎯 Summary

**Minimum commands for a fresh deployment:**

```bash
# 1. On server: Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh

# 2. Clone and setup
git clone <your-repo>
cd your-project/deploy-vps
chmod +x scripts/*.sh scripts/optional/*.sh scripts/common/*.sh

# 3. Configure DNS (api.domain.com → server IP)

# 4. Run setup
./scripts/setup.sh

# 5. Add API keys
nano .env.production

# 6. Validate
./scripts/validate.sh --env production

# 7. Deploy
./scripts/deploy.sh init --env production

# 8. Setup SSL
./scripts/ssl.sh setup --env production

# 9. Done! Test your app
curl https://api.yourdomain.com/health
```

---

*Generated by FCube CLI - Modern FastAPI Project & Module Generator*
'''
