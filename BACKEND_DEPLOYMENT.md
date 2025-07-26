# 🔧 Backend Deployment Guide

## **AWS Lambda + API Gateway Deployment**

### **Option 1: Serverless Deployment (Recommended)**

#### **1.1 Install AWS SAM CLI**
```bash
# Windows
pip install aws-sam-cli

# macOS
brew install aws-sam-cli

# Linux
pip install aws-sam-cli
```

#### **1.2 Create SAM Template**
Create `template.yaml` in the backend directory:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Shine Skincare Backend API

Globals:
  Function:
    Timeout: 30
    Runtime: python3.11
    Environment:
      Variables:
        DATABASE_URL: !Ref DatabaseUrl
        GOOGLE_CLIENT_ID: !Ref GoogleClientId
        GOOGLE_CLIENT_SECRET: !Ref GoogleClientSecret
        JWT_SECRET_KEY: !Ref JwtSecretKey
        STRIPE_SECRET_KEY: !Ref StripeSecretKey

Resources:
  # API Gateway
  ShineApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: prod
      Cors:
        AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
        AllowHeaders: "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
        AllowOrigin: "'*'"

  # Main API Function
  ShineApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      Handler: app.handler
      Events:
        ApiEvent:
          Type: Api
          Properties:
            RestApiId: !Ref ShineApi
            Path: /{proxy+}
            Method: ANY

  # Database (RDS)
  ShineDatabase:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: shine-db
      DBInstanceClass: db.t3.micro
      Engine: postgres
      MasterUsername: shine_user
      MasterUserPassword: !Ref DatabasePassword
      AllocatedStorage: 20
      StorageType: gp2
      PubliclyAccessible: false
      VPCSecurityGroups:
        - !Ref DatabaseSecurityGroup

  # Security Group for Database
  DatabaseSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for Shine database
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !GetAtt ShineApiFunction.SecurityGroupId

Parameters:
  DatabaseUrl:
    Type: String
    Description: Database connection URL
    Default: postgresql://shine_user:password@localhost:5432/shine_prod
  
  DatabasePassword:
    Type: String
    NoEcho: true
    Description: Database password
  
  GoogleClientId:
    Type: String
    Description: Google OAuth Client ID
  
  GoogleClientSecret:
    Type: String
    NoEcho: true
    Description: Google OAuth Client Secret
  
  JwtSecretKey:
    Type: String
    NoEcho: true
    Description: JWT Secret Key
  
  StripeSecretKey:
    Type: String
    NoEcho: true
    Description: Stripe Secret Key

Outputs:
  ApiUrl:
    Description: API Gateway endpoint URL
    Value: !Sub "https://${ShineApi}.execute-api.${AWS::Region}.amazonaws.com/prod/"
  
  DatabaseEndpoint:
    Description: Database endpoint
    Value: !GetAtt ShineDatabase.Endpoint.Address
```

#### **1.3 Create Lambda Handler**
Create `app.py` in the backend directory:

```python
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from app import create_app

# Create Flask app
app = create_app()
CORS(app)

def handler(event, context):
    """AWS Lambda handler"""
    try:
        # Parse the event
        path = event.get('path', '/')
        method = event.get('httpMethod', 'GET')
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        # Create a test request context
        with app.test_request_context(
            path=path,
            method=method,
            headers=headers,
            data=body
        ):
            # Process the request
            response = app.full_dispatch_request()
            
            return {
                'statusCode': response.status_code,
                'headers': dict(response.headers),
                'body': response.get_data(as_text=True)
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }

# For local testing
if __name__ == '__main__':
    app.run(debug=True)
```

#### **1.4 Deploy with SAM**
```bash
cd backend

# Build the application
sam build

# Deploy to AWS
sam deploy --guided
```

### **Option 2: EC2 Deployment**

#### **2.1 Create EC2 Instance**
1. Launch EC2 instance (t3.small recommended)
2. Use Ubuntu 22.04 LTS
3. Configure security groups for ports 22, 80, 443, 5000

#### **2.2 Install Dependencies**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.11 python3.11-venv python3-pip nginx -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Create application user
sudo useradd -m -s /bin/bash shine
sudo usermod -aG sudo shine
```

#### **2.3 Deploy Application**
```bash
# Switch to application user
sudo su - shine

# Clone repository
git clone https://github.com/mcpmessenger/shine.git
cd shine/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with production values

# Set up database
python setup_database.py

# Test the application
python run.py
```

#### **2.4 Configure Nginx**
Create `/etc/nginx/sites-available/shine`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/shine /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### **2.5 Set Up Systemd Service**
Create `/etc/systemd/system/shine.service`:

```ini
[Unit]
Description=Shine Skincare API
After=network.target

[Service]
User=shine
WorkingDirectory=/home/shine/shine/backend
Environment=PATH=/home/shine/shine/backend/venv/bin
ExecStart=/home/shine/shine/backend/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Start the service:
```bash
sudo systemctl enable shine
sudo systemctl start shine
sudo systemctl status shine
```

### **Option 3: Docker Deployment**

#### **3.1 Create Dockerfile**
Create `Dockerfile` in the backend directory:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 shine && chown -R shine:shine /app
USER shine

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run the application
CMD ["python", "run.py"]
```

#### **3.2 Create Docker Compose**
Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://shine_user:password@db:5432/shine_prod
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=shine_prod
      - POSTGRES_USER=shine_user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

#### **3.3 Deploy with Docker**
```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f api

# Stop services
docker-compose down
```

## **Environment Variables**

### **Production Environment Variables**
```env
# Database
DATABASE_URL=postgresql://shine_user:password@your-db-host:5432/shine_prod

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=https://your-frontend-domain.com/auth/callback

# JWT
JWT_SECRET_KEY=your_super_secret_jwt_key_here
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=604800

# Stripe
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key

# Redis (for Celery)
REDIS_URL=redis://your-redis-host:6379/0

# Security
CORS_ORIGINS=https://your-frontend-domain.com
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=900

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/shine/app.log
```

## **Database Setup**

### **PostgreSQL Setup**
```sql
-- Create database
CREATE DATABASE shine_prod;

-- Create user
CREATE USER shine_user WITH PASSWORD 'secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE shine_prod TO shine_user;

-- Connect to database and run migrations
\c shine_prod
-- Run your Flask-Migrate commands here
```

### **Run Migrations**
```bash
# Set up migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Seed data
python seed_data.py
```

## **SSL Certificate**

### **Let's Encrypt (Free)**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## **Monitoring & Logging**

### **Application Logs**
```bash
# View logs
sudo journalctl -u shine -f

# Log rotation
sudo logrotate /etc/logrotate.d/shine
```

### **Health Checks**
```bash
# Test API health
curl https://your-api-domain.com/api/health

# Test database connection
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); print('DB connected:', db.engine.execute('SELECT 1').scalar())"
```

## **Backup Strategy**

### **Database Backup**
```bash
# Create backup script
#!/bin/bash
pg_dump shine_prod > /backups/shine_$(date +%Y%m%d_%H%M%S).sql

# Schedule with cron
0 2 * * * /path/to/backup_script.sh
```

### **Application Backup**
```bash
# Backup application files
tar -czf /backups/app_$(date +%Y%m%d_%H%M%S).tar.gz /home/shine/shine/
```

## **Scaling Considerations**

### **Load Balancer**
- Use AWS Application Load Balancer
- Configure health checks
- Set up auto-scaling groups

### **Caching**
- Implement Redis for session storage
- Use CDN for static assets
- Enable database query caching

### **Monitoring**
- Set up CloudWatch alarms
- Monitor CPU, memory, and disk usage
- Track API response times

---

**Choose the deployment option that best fits your needs and budget!** 🚀 