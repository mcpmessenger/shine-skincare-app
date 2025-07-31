# 🚀 Full ML Deployment Specification

## Research Summary: Elastic Beanstalk ML Instance Requirements

### Current Environment Analysis
- **Current Instance Type**: t3.micro (1 vCPU, 1 GB RAM)
- **Current Status**: Severe (50% HTTP 5xx errors)
- **Root Cause**: Insufficient resources for ML workloads
- **Solution**: Upgrade to ML-optimized instance types

## AWS Elastic Beanstalk Instance Types for ML

### 🎯 **Recommended ML Instance Types**

#### **Option 1: m5.2xlarge (Recommended)**
```yaml
Instance Type: m5.2xlarge
vCPUs: 8
Memory: 32 GB
Storage: EBS Optimized
Network: Up to 10 Gbps
Cost: ~$0.384/hour (~$280/month)
```

**Specifications:**
- **CPU**: 8 vCPUs (Intel Xeon Platinum 8175M)
- **Memory**: 32 GB DDR4
- **Storage**: EBS Optimized (up to 4,750 Mbps)
- **Network**: Up to 10 Gbps
- **GPU**: None (CPU-based ML)
- **Use Case**: Full ML deployment with TensorFlow, PyTorch, FAISS

#### **Option 2: c5.2xlarge (Cost-Effective)**
```yaml
Instance Type: c5.2xlarge
vCPUs: 8
Memory: 16 GB
Storage: EBS Optimized
Network: Up to 10 Gbps
Cost: ~$0.34/hour (~$250/month)
```

**Specifications:**
- **CPU**: 8 vCPUs (Intel Xeon Platinum 8275CL)
- **Memory**: 16 GB DDR4
- **Storage**: EBS Optimized (up to 4,750 Mbps)
- **Network**: Up to 10 Gbps
- **GPU**: None
- **Use Case**: ML deployment with moderate memory requirements

#### **Option 3: r5.2xlarge (Memory-Optimized)**
```yaml
Instance Type: r5.2xlarge
vCPUs: 8
Memory: 64 GB
Storage: EBS Optimized
Network: Up to 10 Gbps
Cost: ~$0.504/hour (~$365/month)
```

**Specifications:**
- **CPU**: 8 vCPUs (Intel Xeon Platinum 8175M)
- **Memory**: 64 GB DDR4
- **Storage**: EBS Optimized (up to 4,750 Mbps)
- **Network**: Up to 10 Gbps
- **GPU**: None
- **Use Case**: Large FAISS indices, SCIN dataset processing

### 🚀 **GPU-Enabled Options (Advanced ML)**

#### **Option 4: g4dn.xlarge (GPU-Accelerated)**
```yaml
Instance Type: g4dn.xlarge
vCPUs: 4
Memory: 16 GB
Storage: EBS Optimized + NVMe SSD
Network: Up to 25 Gbps
GPU: 1x NVIDIA T4 (16 GB VRAM)
Cost: ~$0.526/hour (~$380/month)
```

**Specifications:**
- **CPU**: 4 vCPUs (Intel Xeon Cascade Lake)
- **Memory**: 16 GB DDR4
- **Storage**: EBS Optimized + 1x 125 GB NVMe SSD
- **Network**: Up to 25 Gbps
- **GPU**: 1x NVIDIA T4 (16 GB VRAM)
- **Use Case**: GPU-accelerated ML inference, TensorFlow/PyTorch

#### **Option 5: p3.2xlarge (High-Performance GPU)**
```yaml
Instance Type: p3.2xlarge
vCPUs: 8
Memory: 61 GB
Storage: EBS Optimized
Network: Up to 10 Gbps
GPU: 1x NVIDIA V100 (16 GB VRAM)
Cost: ~$3.06/hour (~$2,200/month)
```

**Specifications:**
- **CPU**: 8 vCPUs (Intel Xeon E5-2686 v4)
- **Memory**: 61 GB DDR4
- **Storage**: EBS Optimized
- **Network**: Up to 10 Gbps
- **GPU**: 1x NVIDIA V100 (16 GB VRAM)
- **Use Case**: Advanced ML training, large model inference

## ML Workload Requirements Analysis

### 📊 **Memory Requirements by ML Component**

#### **TensorFlow/PyTorch Base**
```yaml
TensorFlow 2.15.0: ~500 MB
PyTorch 2.1.0: ~800 MB
CUDA Runtime (if GPU): ~200 MB
Total Base ML: ~1.5 GB
```

#### **Computer Vision Libraries**
```yaml
OpenCV (headless): ~200 MB
scikit-image: ~150 MB
Pillow: ~50 MB
Total CV: ~400 MB
```

#### **FAISS Similarity Search**
```yaml
FAISS CPU: ~300 MB
SCIN Dataset Index: ~2-5 GB (depending on size)
Vector Cache: ~1-2 GB
Total FAISS: ~3-7 GB
```

#### **Additional ML Libraries**
```yaml
scikit-learn: ~100 MB
transformers: ~500 MB
timm: ~200 MB
Google Cloud Vision: ~100 MB
Total Additional: ~900 MB
```

#### **Application Runtime**
```yaml
Flask + Dependencies: ~200 MB
Python Runtime: ~100 MB
System Overhead: ~500 MB
Total Runtime: ~800 MB
```

### 📈 **Total Memory Requirements**

#### **Minimum ML Deployment**
```yaml
Base ML Libraries: 1.5 GB
Computer Vision: 0.4 GB
FAISS (minimal): 3.0 GB
Additional ML: 0.9 GB
Application Runtime: 0.8 GB
Buffer/Safety: 2.0 GB
Total Minimum: 8.6 GB
```

#### **Recommended ML Deployment**
```yaml
Base ML Libraries: 1.5 GB
Computer Vision: 0.4 GB
FAISS (full): 7.0 GB
Additional ML: 0.9 GB
Application Runtime: 0.8 GB
Buffer/Safety: 4.0 GB
Total Recommended: 14.6 GB
```

#### **Full SCIN Dataset Deployment**
```yaml
Base ML Libraries: 1.5 GB
Computer Vision: 0.4 GB
FAISS (full SCIN): 10.0 GB
SCIN Dataset Cache: 5.0 GB
Additional ML: 0.9 GB
Application Runtime: 0.8 GB
Buffer/Safety: 6.0 GB
Total Full SCIN: 24.6 GB
```

## Elastic Beanstalk Configuration for ML

### 🔧 **Environment Configuration**

#### **Instance Configuration**
```yaml
option_settings:
  # Instance type for ML workloads
  aws:autoscaling:launchconfiguration:
    InstanceType: m5.2xlarge
    IamInstanceProfile: aws-elasticbeanstalk-ec2-role
  
  # Auto Scaling for ML workloads
  aws:autoscaling:asg:
    MinSize: 1
    MaxSize: 3
    Cooldown: 300
  
  # Load balancer configuration
  aws:elasticbeanstalk:environment:
    LoadBalancerType: application
    ServiceRole: aws-elasticbeanstalk-service-role
  
  # Environment variables for ML
  aws:elasticbeanstalk:application:environment:
    PYTHONUNBUFFERED: 1
    FLASK_ENV: production
    USE_MOCK_SERVICES: false
    ML_AVAILABLE: true
    OPERATION_APPLE_ENABLED: true
    ADVANCED_ANALYSIS_ENABLED: true
    MAX_WORKERS: 4
    ANALYSIS_TIMEOUT: 300
    FAISS_DIMENSION: 512
    SCIN_BUCKET_PATH: gs://dx-scin-public-data/dataset/
    PRELOAD_FAISS: true
    ENABLE_GPU: false  # Set to true for GPU instances
```

#### **Storage Configuration**
```yaml
option_settings:
  # EBS volume configuration
  aws:autoscaling:launchconfiguration:
    RootVolumeSize: 100  # GB for ML datasets
    RootVolumeType: gp3
    RootVolumeIOPS: 3000
    RootVolumeThroughput: 125
  
  # Additional EBS volumes for ML data
  aws:elasticbeanstalk:environment:
    EnvironmentType: LoadBalanced
```

#### **Network Configuration**
```yaml
option_settings:
  # Network configuration for ML workloads
  aws:elasticbeanstalk:environment:
    LoadBalancerType: application
    VPCId: vpc-xxxxxxxxx  # Your VPC
    Subnets: subnet-xxxxxxxxx,subnet-yyyyyyyyy  # Private subnets
  
  # Security groups for ML
  aws:autoscaling:launchconfiguration:
    SecurityGroups: sg-xxxxxxxxx  # ML security group
```

### 🚀 **Performance Optimization**

#### **Gunicorn Configuration for ML**
```yaml
option_settings:
  # Gunicorn settings for ML workloads
  aws:elasticbeanstalk:container:python:
    WSGIPath: simple_server_basic:app
    NumProcesses: 2
    NumThreads: 8
    Timeout: 300
  
  # Memory and CPU optimization
  aws:elasticbeanstalk:application:environment:
    GUNICORN_TIMEOUT: 300
    GUNICORN_WORKERS: 2
    GUNICORN_THREADS: 8
    MAX_WORKERS: 4
    ANALYSIS_TIMEOUT: 300
```

#### **Nginx Configuration for ML**
```yaml
files:
  "/etc/nginx/conf.d/ml-timeout.conf":
    mode: "000644"
    owner: root
    group: root
    content: |
      # Nginx timeout configuration for ML workloads
      proxy_connect_timeout 300s;
      proxy_send_timeout 300s;
      proxy_read_timeout 300s;
      send_timeout 300s;
      client_max_body_size 100M;
      client_body_timeout 300s;
      client_header_timeout 300s;
      
      # ML-specific optimizations
      proxy_buffering on;
      proxy_buffer_size 128k;
      proxy_buffers 4 256k;
      proxy_busy_buffers_size 256k;
```

## Cost Analysis and Recommendations

### 💰 **Monthly Cost Comparison**

| Instance Type | vCPUs | Memory | GPU | Monthly Cost | ML Capability |
|---------------|-------|--------|-----|--------------|---------------|
| **t3.micro** (current) | 2 | 1 GB | None | ~$8 | ❌ Insufficient |
| **m5.large** | 2 | 8 GB | None | ~$70 | ⚠️ Minimal ML |
| **m5.xlarge** | 4 | 16 GB | None | ~$140 | ✅ Basic ML |
| **m5.2xlarge** | 8 | 32 GB | None | ~$280 | ✅ **Recommended** |
| **r5.2xlarge** | 8 | 64 GB | None | ~$365 | ✅ Large datasets |
| **g4dn.xlarge** | 4 | 16 GB | T4 | ~$380 | ✅ GPU acceleration |
| **p3.2xlarge** | 8 | 61 GB | V100 | ~$2,200 | ✅ Advanced ML |

### 🎯 **Recommendation Matrix**

#### **Phase 1: Basic ML (m5.2xlarge)**
```yaml
Instance: m5.2xlarge
Cost: ~$280/month
Capabilities:
  - TensorFlow/PyTorch inference
  - Basic FAISS similarity search
  - OpenCV image processing
  - SCIN dataset (partial)
  - 4 concurrent ML workers
```

#### **Phase 2: Full SCIN (r5.2xlarge)**
```yaml
Instance: r5.2xlarge
Cost: ~$365/month
Capabilities:
  - Full SCIN dataset processing
  - Large FAISS indices
  - Enhanced ML analysis
  - 8 concurrent ML workers
```

#### **Phase 3: GPU Acceleration (g4dn.xlarge)**
```yaml
Instance: g4dn.xlarge
Cost: ~$380/month
Capabilities:
  - GPU-accelerated inference
  - Real-time ML processing
  - Advanced computer vision
  - 4 concurrent GPU workers
```

## Deployment Strategy

### 📋 **Implementation Plan**

#### **Step 1: Environment Upgrade**
```bash
# Update environment configuration
aws elasticbeanstalk update-environment \
  --environment-name your-environment-name \
  --option-settings \
    Namespace=aws:autoscaling:launchconfiguration,OptionName=InstanceType,Value=m5.2xlarge
```

#### **Step 2: Storage Upgrade**
```bash
# Update EBS configuration
aws elasticbeanstalk update-environment \
  --environment-name your-environment-name \
  --option-settings \
    Namespace=aws:autoscaling:launchconfiguration,OptionName=RootVolumeSize,Value=100
```

#### **Step 3: Deploy Full ML Package**
```bash
# Deploy with full ML capabilities
aws elasticbeanstalk create-application-version \
  --application-name your-app-name \
  --version-label full-ml-deployment-$(date +%Y%m%d_%H%M%S) \
  --source-bundle S3Bucket=your-bucket,S3Key=full-ml-deployment.zip

aws elasticbeanstalk update-environment \
  --environment-name your-environment-name \
  --version-label full-ml-deployment-$(date +%Y%m%d_%H%M%S)
```

### 🔍 **Monitoring and Validation**

#### **Performance Metrics**
```yaml
Target Metrics:
  - CPU Utilization: < 70%
  - Memory Usage: < 80%
  - Response Time: < 10s
  - Error Rate: < 1%
  - ML Inference Time: < 5s
```

#### **Health Checks**
```bash
# Monitor environment health
aws elasticbeanstalk describe-environments \
  --environment-names your-environment-name \
  --query "Environments[0].{Status:Status,Health:Health,Instances:Instances}"

# Test ML endpoints
curl -X POST https://your-eb-url/api/analyze/skin \
  -H "Content-Type: application/json" \
  -d '{"test": "ml_capability"}'
```

## Success Criteria

### ✅ **Environment Health**
- Status: Green
- Health: Healthy
- No HTTP 5xx errors
- All instances healthy

### ✅ **ML Performance**
- TensorFlow/PyTorch loads successfully
- FAISS similarity search works
- SCIN dataset accessible
- Image processing functional
- Response time < 10s

### ✅ **Resource Utilization**
- CPU < 70%
- Memory < 80%
- Storage < 80%
- Network < 50%

### ✅ **Cost Efficiency**
- Monthly cost within budget
- Resource utilization optimized
- Auto-scaling functional
- Performance meets requirements

---

**🚀 Key Takeaway**: For full ML deployment, upgrade to **m5.2xlarge** (8 vCPUs, 32 GB RAM) as the minimum viable option. This provides sufficient resources for TensorFlow, PyTorch, FAISS, and SCIN dataset processing while maintaining reasonable costs (~$280/month). 