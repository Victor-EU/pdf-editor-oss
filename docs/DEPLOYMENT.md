# Deployment Guide

Complete guide for deploying the PDF Editor application to production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Configuration](#environment-configuration)
- [Deployment Options](#deployment-options)
  - [Docker Deployment](#docker-deployment)
  - [Traditional Server Deployment](#traditional-server-deployment)
  - [Cloud Platform Deployment](#cloud-platform-deployment)
- [Production Best Practices](#production-best-practices)
- [Monitoring and Logging](#monitoring-and-logging)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum**:
- CPU: 2 cores
- RAM: 2GB
- Disk: 10GB free space
- OS: Linux (Ubuntu 20.04+, CentOS 8+) or macOS

**Recommended**:
- CPU: 4+ cores
- RAM: 4GB+
- Disk: 20GB+ SSD
- OS: Ubuntu 22.04 LTS

### Software Requirements

- Python 3.9+
- Node.js 16+
- Nginx (recommended) or Apache
- poppler-utils
- Tesseract OCR
- Git
- SSL certificate (for HTTPS)

---

## Environment Configuration

### Backend Configuration

Create a production `.env` file:

```bash
# backend-python/.env
ENV=production
DEBUG=false
HOST=0.0.0.0
PORT=8080

# CORS - Update with your domain
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# File paths
UPLOAD_DIR=/var/www/pdf-editor/uploads
OUTPUT_DIR=/var/www/pdf-editor/output

# File limits
MAX_FILE_SIZE=52428800  # 50MB in bytes
MAX_UPLOAD_FILES=10

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/pdf-editor/app.log

# Tesseract
TESSERACT_CMD=/usr/bin/tesseract
```

### Frontend Configuration

Create production environment file:

```bash
# frontend/.env.production
VITE_API_BASE_URL=https://api.your-domain.com
VITE_ENABLE_ANALYTICS=true
```

---

## Deployment Options

## Docker Deployment (Recommended)

### 1. Create Dockerfile for Backend

```dockerfile
# backend-python/Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-spa \
    tesseract-ocr-fra \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads output

# Expose port
EXPOSE 8080

# Run with Gunicorn for production
CMD ["gunicorn", "main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8080", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

### 2. Create Dockerfile for Frontend

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build for production
RUN npm run build

# Production image
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 3. Create docker-compose.yml

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend-python
      dockerfile: Dockerfile
    container_name: pdf-editor-backend
    restart: unless-stopped
    ports:
      - "8080:8080"
    volumes:
      - ./uploads:/app/uploads
      - ./output:/app/output
      - ./logs:/app/logs
    environment:
      - ENV=production
      - DEBUG=false
      - CORS_ORIGINS=https://your-domain.com
    networks:
      - pdf-editor-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: pdf-editor-frontend
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
    networks:
      - pdf-editor-network

networks:
  pdf-editor-network:
    driver: bridge
```

### 4. Deploy with Docker

```bash
# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

---

## Traditional Server Deployment

### 1. Server Setup (Ubuntu 22.04)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    nodejs \
    npm \
    nginx \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    supervisor \
    git

# Install Node.js 18 (if not available)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

### 2. Deploy Backend

```bash
# Create application directory
sudo mkdir -p /var/www/pdf-editor
sudo chown $USER:$USER /var/www/pdf-editor

# Clone repository
cd /var/www/pdf-editor
git clone https://github.com/Victor-EU/pdf-editor.git .

# Set up Python environment
cd backend-python
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Create directories
mkdir -p uploads output logs

# Create .env file
nano .env  # Add production configuration

# Test run
gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8080
```

### 3. Create Supervisor Configuration

```bash
# /etc/supervisor/conf.d/pdf-editor.conf
[program:pdf-editor-backend]
directory=/var/www/pdf-editor/backend-python
command=/var/www/pdf-editor/backend-python/venv/bin/gunicorn main:app
    --workers 4
    --worker-class uvicorn.workers.UvicornWorker
    --bind 0.0.0.0:8080
    --access-logfile /var/www/pdf-editor/backend-python/logs/access.log
    --error-logfile /var/www/pdf-editor/backend-python/logs/error.log
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/supervisor/pdf-editor-backend.err.log
stdout_logfile=/var/log/supervisor/pdf-editor-backend.out.log
```

```bash
# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start pdf-editor-backend

# Check status
sudo supervisorctl status pdf-editor-backend
```

### 4. Deploy Frontend

```bash
cd /var/www/pdf-editor/frontend

# Install dependencies
npm ci --production=false

# Build for production
npm run build

# Copy build to web root
sudo mkdir -p /var/www/html/pdf-editor
sudo cp -r dist/* /var/www/html/pdf-editor/
```

### 5. Configure Nginx

```nginx
# /etc/nginx/sites-available/pdf-editor
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/ssl/certs/your-domain.com.crt;
    ssl_certificate_key /etc/ssl/private/your-domain.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Frontend
    root /var/www/html/pdf-editor;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8080/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Increase timeouts for large file uploads
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
        send_timeout 600s;

        # Increase buffer sizes
        client_max_body_size 50M;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8080/health;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript
               application/x-javascript application/xml+rss
               application/javascript application/json;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/pdf-editor /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 6. Set Up SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal is configured automatically
# Test renewal
sudo certbot renew --dry-run
```

---

## Cloud Platform Deployment

### AWS Deployment

#### Using EC2

1. **Launch EC2 Instance**:
   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t3.medium (or higher)
   - Security Group: Allow ports 80, 443, 22

2. **Configure Security Group**:
   ```
   Inbound Rules:
   - SSH (22) - Your IP
   - HTTP (80) - 0.0.0.0/0
   - HTTPS (443) - 0.0.0.0/0
   ```

3. **Follow Traditional Server Deployment** steps above

#### Using Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 pdf-editor-backend

# Create environment
eb create pdf-editor-prod

# Deploy
eb deploy

# Open application
eb open
```

### Google Cloud Platform

#### Using Compute Engine

1. Create VM instance with Ubuntu 22.04
2. Follow Traditional Server Deployment
3. Configure Cloud Load Balancer
4. Set up SSL certificate

#### Using Cloud Run (Serverless)

```bash
# Build and push Docker image
gcloud builds submit --tag gcr.io/PROJECT_ID/pdf-editor-backend

# Deploy to Cloud Run
gcloud run deploy pdf-editor-backend \
    --image gcr.io/PROJECT_ID/pdf-editor-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

### Azure Deployment

#### Using App Service

1. Create App Service Plan
2. Create Web App for Python 3.11
3. Deploy using Git or Azure CLI
4. Configure custom domain and SSL

---

## Production Best Practices

### Security

1. **Use HTTPS** everywhere with valid SSL certificates
2. **Set proper CORS** origins - don't use wildcards
3. **Implement rate limiting** to prevent abuse
4. **Enable firewall** (UFW on Ubuntu):
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

5. **Regular updates**:
   ```bash
   sudo apt update && sudo apt upgrade
   ```

### Performance

1. **Use process managers** (Supervisor, systemd)
2. **Configure worker processes** based on CPU cores
3. **Enable gzip compression** in Nginx
4. **Set up caching** headers for static assets
5. **Use CDN** for frontend assets (CloudFlare, etc.)

### Backup

1. **Database backup** (if added later):
   ```bash
   # Add to cron
   0 2 * * * /path/to/backup-script.sh
   ```

2. **Application files backup**:
   ```bash
   # Backup uploads and output directories
   tar -czf backup-$(date +%Y%m%d).tar.gz uploads/ output/
   ```

### File Cleanup

Set up automated cleanup of processed files:

```bash
# /etc/cron.daily/pdf-editor-cleanup
#!/bin/bash
find /var/www/pdf-editor/backend-python/uploads -type f -mtime +1 -delete
find /var/www/pdf-editor/backend-python/output -type f -mtime +7 -delete
```

```bash
sudo chmod +x /etc/cron.daily/pdf-editor-cleanup
```

---

## Monitoring and Logging

### Application Logging

Configure logging in production:

```python
# backend-python/config.py
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/pdf-editor/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'default',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file'],
    },
}
```

### Nginx Access Logs

```nginx
# In nginx.conf
access_log /var/log/nginx/pdf-editor-access.log;
error_log /var/log/nginx/pdf-editor-error.log;
```

### Log Rotation

```bash
# /etc/logrotate.d/pdf-editor
/var/log/pdf-editor/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

### Monitoring Tools

**Prometheus + Grafana**:
```bash
# Install Prometheus
sudo apt install prometheus

# Install Grafana
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
sudo apt-get update
sudo apt-get install grafana

# Start services
sudo systemctl start prometheus grafana-server
sudo systemctl enable prometheus grafana-server
```

**Health Check Endpoint**:
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }
```

---

## Troubleshooting

### Common Issues

#### 1. Backend won't start

```bash
# Check logs
sudo supervisorctl tail -f pdf-editor-backend

# Check if port is in use
sudo lsof -i :8080

# Check Python environment
source /var/www/pdf-editor/backend-python/venv/bin/activate
which python
python --version
```

#### 2. Frontend shows CORS errors

```bash
# Check backend CORS configuration
grep CORS_ORIGINS /var/www/pdf-editor/backend-python/.env

# Verify Nginx proxy headers
sudo nginx -T | grep proxy_set_header
```

#### 3. File uploads fail

```bash
# Check Nginx client_max_body_size
sudo nginx -T | grep client_max_body_size

# Check directory permissions
ls -la /var/www/pdf-editor/backend-python/uploads
sudo chown -R www-data:www-data /var/www/pdf-editor/backend-python/uploads
```

#### 4. OCR not working

```bash
# Check Tesseract installation
tesseract --version
tesseract --list-langs

# Install missing languages
sudo apt-get install tesseract-ocr-spa  # Spanish
sudo apt-get install tesseract-ocr-fra  # French
```

#### 5. High memory usage

```bash
# Check running processes
top
htop

# Reduce Gunicorn workers
# Edit supervisor config: --workers 2

# Monitor memory
free -h
```

### Debug Mode (Temporary)

Enable debug mode temporarily:

```bash
# Edit .env
DEBUG=true

# Restart application
sudo supervisorctl restart pdf-editor-backend
```

**Remember to disable debug mode in production!**

---

## Performance Tuning

### Gunicorn Worker Configuration

```bash
# Calculate workers: 2 * CPU_CORES + 1
# For 4 cores: 9 workers
--workers 9
```

### Nginx Tuning

```nginx
# /etc/nginx/nginx.conf
worker_processes auto;
worker_connections 1024;
keepalive_timeout 65;

# Buffer sizes
client_body_buffer_size 10K;
client_header_buffer_size 1k;
client_max_body_size 50M;
large_client_header_buffers 2 1k;
```

### System Limits

```bash
# /etc/security/limits.conf
www-data soft nofile 65536
www-data hard nofile 65536

# /etc/sysctl.conf
net.core.somaxconn = 1024
net.ipv4.tcp_max_syn_backlog = 2048
```

---

## Scaling

### Vertical Scaling

- Upgrade server resources (CPU, RAM)
- Increase Gunicorn workers
- Optimize Nginx configuration

### Horizontal Scaling

1. **Load Balancer**: Nginx, HAProxy, or cloud LB
2. **Multiple Backend Instances**: Run on different servers
3. **Shared Storage**: NFS or cloud storage for uploads/output
4. **Session Management**: Redis for future features

---

**Last Updated**: November 2024
**Version**: 1.0

For additional support, please open an issue on GitHub.
