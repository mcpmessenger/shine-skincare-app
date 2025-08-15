# 🏗️ Shine Skincare App Infrastructure Diagram

## Current Production Architecture

```mermaid
graph TB
    %% User Layer
    User[👤 User]
    Frontend[🌐 Frontend<br/>shineskincollective.com<br/>AWS Amplify]
    
    %% DNS Layer
    DNS[🌍 DNS<br/>api.shineskincollective.com]
    
    %% Load Balancer Layer
    ALB[⚖️ Application Load Balancer<br/>production-shine-skincare-alb<br/>Port: 5000]
    
    %% Target Groups
    TG_Fixed[🎯 Target Group<br/>shine-api-tg-fixed<br/>Port: 8000<br/>Health Check: /health]
    TG_Old1[🚫 Old Target Group<br/>production-shine-ml-service-tg<br/>Port: 5000]
    TG_Old2[🚫 Old Target Group<br/>production-shine-api-gateway-tg<br/>Port: 8080]
    
    %% ECS Layer
    ECS_Cluster[🐳 ECS Cluster<br/>production-shine-cluster]
    ECS_Service[🚀 ECS Service<br/>shine-api-gateway<br/>Task Definition: 17<br/>Port: 8000]
    Container[📦 Container<br/>Port: 8000<br/>Health Check: localhost:8000/health]
    
    %% Backend Application
    App[🐍 Python App<br/>application_hare_run_v6.py<br/>Procfile: gunicorn :8000]
    
    %% Data Layer
    S3[☁️ S3 Models<br/>facial_embedding_model.h5<br/>embeddings.npz]
    
    %% Network Layer
    VPC[🏗️ VPC<br/>vpc-0ab2e8965e091065a]
    Subnet[🌐 Subnet<br/>subnet-08924ec7f5d6af857<br/>us-east-1b]
    SecurityGroup[🔒 Security Group<br/>sg-071029ab14d753733]
    
    %% Connections
    User --> Frontend
    Frontend --> DNS
    DNS --> ALB
    
    %% ALB Routing (Current Configuration)
    ALB -->|Port 5000| TG_Fixed
    ALB -.->|Port 8080| TG_Old2
    ALB -.->|Port 443| TG_Old2
    ALB -.->|Port 80| TG_Old2
    
    %% Target Group to ECS
    TG_Fixed --> ECS_Service
    ECS_Service --> Container
    Container --> App
    
    %% ECS Infrastructure
    ECS_Service --> ECS_Cluster
    ECS_Cluster --> VPC
    ECS_Service --> Subnet
    ECS_Service --> SecurityGroup
    
    %% App Dependencies
    App --> S3
    
    %% Styling
    classDef working fill:#90EE90,stroke:#006400,stroke-width:2px
    classDef broken fill:#FFB6C1,stroke:#8B0000,stroke-width:2px
    classDef fixed fill:#87CEEB,stroke:#00008B,stroke-width:2px
    classDef infrastructure fill:#F0E68C,stroke:#B8860B,stroke-width:2px
    
    class User,Frontend,DNS,ALB,TG_Fixed,ECS_Service,Container,App,S3 working
    class TG_Old1,TG_Old2 broken
    class ECS_Cluster,VPC,Subnet,SecurityGroup infrastructure
```

## 🔧 **Current Configuration Status**

### ✅ **Working Components:**
- **Frontend:** AWS Amplify hosting
- **DNS:** `api.shineskincollective.com` → ALB
- **ALB:** `production-shine-skincare-alb`
- **Target Group:** `shine-api-tg-fixed` (port 8000)
- **ECS Service:** `shine-api-gateway` (port 8000)
- **Backend:** Python app on port 8000

### ❌ **Issues Fixed:**
- **ALB Listener:** Updated to forward port 5000 → `shine-api-tg-fixed`
- **Port Mismatch:** ECS service updated from port 5000 → 8000
- **Task Definition:** Created revision 17 with correct port configuration

### 🔄 **Current Status:**
- **Deployment:** In progress (ECS rolling out new configuration)
- **Target Health:** Transitioning between targets
- **Health Endpoint:** Not yet responding (container startup in progress)

## 🚀 **Traffic Flow**

1. **User** → Frontend (Amplify)
2. **Frontend** → DNS (`api.shineskincollective.com`)
3. **DNS** → ALB (port 5000)
4. **ALB** → Target Group `shine-api-tg-fixed` (port 8000)
5. **Target Group** → ECS Service (port 8000)
6. **ECS Service** → Container (port 8000)
7. **Container** → Python App (port 8000)
8. **Python App** → S3 Models

## 📊 **Port Configuration Summary**

| Component | Port | Status |
|-----------|------|---------|
| ALB Listener | 5000 | ✅ Forwarding to correct target group |
| Target Group | 8000 | ✅ Health checks on port 8000 |
| ECS Service | 8000 | ✅ Updated from port 5000 |
| Container | 8000 | ✅ Exposed on port 8000 |
| Python App | 8000 | ✅ Running on port 8000 |

## 🎯 **Next Steps**

1. **Wait for deployment completion** (5-10 minutes)
2. **Verify target health** becomes `healthy`
3. **Test health endpoint** `http://api.shineskincollective.com/health`
4. **Validate face detection** working in production
