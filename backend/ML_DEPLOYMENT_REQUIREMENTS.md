# 📋 ML Deployment Requirements Specification

## 🎯 **Minimum Viable ML Deployment Requirements**

### **Instance Specifications**
```yaml
Instance Type: m5.2xlarge
vCPUs: 8
Memory: 32 GB
Storage: 100 GB EBS gp3
Network: Up to 10 Gbps
Cost: ~$280/month
```

### **Memory Requirements Breakdown**
```yaml
TensorFlow/PyTorch: 1.5 GB
Computer Vision (OpenCV, scikit-image): 0.4 GB
FAISS Similarity Search: 7.0 GB
Additional ML Libraries: 0.9 GB
Application Runtime: 0.8 GB
Buffer/Safety: 4.0 GB
Total Required: 14.6 GB
Available: 32 GB ✅
```

### **Storage Requirements**
```yaml
Base System: 20 GB
ML Libraries: 5 GB
FAISS Indices: 10 GB
SCIN Dataset Cache: 15 GB
Application Data: 5 GB
Logs & Temp: 10 GB
Buffer: 35 GB
Total Required: 100 GB
```

## 🚀 **Full SCIN Dataset Deployment Requirements**

### **Instance Specifications**
```yaml
Instance Type: r5.2xlarge
vCPUs: 8
Memory: 64 GB
Storage: 200 GB EBS gp3
Network: Up to 10 Gbps
Cost: ~$365/month
```

### **Memory Requirements Breakdown**
```yaml
TensorFlow/PyTorch: 1.5 GB
Computer Vision: 0.4 GB
FAISS (Full SCIN): 10.0 GB
SCIN Dataset Cache: 5.0 GB
Additional ML Libraries: 0.9 GB
Application Runtime: 0.8 GB
Buffer/Safety: 6.0 GB
Total Required: 24.6 GB
Available: 64 GB ✅
```

### **Storage Requirements**
```yaml
Base System: 20 GB
ML Libraries: 5 GB
FAISS Indices: 20 GB
SCIN Dataset Cache: 50 GB
Application Data: 10 GB
Logs & Temp: 20 GB
Buffer: 75 GB
Total Required: 200 GB
```

## 🔥 **GPU-Accelerated ML Deployment Requirements**

### **Instance Specifications**
```yaml
Instance Type: g4dn.xlarge
vCPUs: 4
Memory: 16 GB
Storage: 100 GB EBS gp3 + 125 GB NVMe SSD
Network: Up to 25 Gbps
GPU: 1x NVIDIA T4 (16 GB VRAM)
Cost: ~$380/month
```

### **Memory Requirements Breakdown**
```yaml
TensorFlow/PyTorch (GPU): 2.0 GB
Computer Vision: 0.4 GB
FAISS (GPU-optimized): 5.0 GB
Additional ML Libraries: 0.9 GB
Application Runtime: 0.8 GB
Buffer/Safety: 2.0 GB
Total Required: 11.1 GB
Available: 16 GB ✅
```

### **GPU Memory Requirements**
```yaml
TensorFlow Models: 4 GB
PyTorch Models: 4 GB
Image Processing: 2 GB
Model Cache: 4 GB
Buffer: 2 GB
Total GPU Memory: 16 GB
Available: 16 GB ✅
```

## 📊 **Elastic Beanstalk Configuration Requirements**

### **Environment Configuration**
```yaml
option_settings:
  # Instance configuration
  aws:autoscaling:launchconfiguration:
    InstanceType: m5.2xlarge  # or r5.2xlarge for full SCIN
    RootVolumeSize: 100        # or 200 for full SCIN
    RootVolumeType: gp3
    RootVolumeIOPS: 3000
    RootVolumeThroughput: 125
  
  # Auto Scaling
  aws:autoscaling:asg:
    MinSize: 1
    MaxSize: 3
    Cooldown: 300
  
  # Load Balancer
  aws:elasticbeanstalk:environment:
    LoadBalancerType: application
    ServiceRole: aws-elasticbeanstalk-service-role
  
  # Environment variables
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

### **Gunicorn Configuration**
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: simple_server_basic:app
    NumProcesses: 2
    NumThreads: 8
    Timeout: 300
  
  aws:elasticbeanstalk:application:environment:
    GUNICORN_TIMEOUT: 300
    GUNICORN_WORKERS: 2
    GUNICORN_THREADS: 8
    MAX_WORKERS: 4
    ANALYSIS_TIMEOUT: 300
```

### **Nginx Configuration**
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

## 📦 **ML Dependencies Requirements**

### **Core ML Libraries**
```yaml
tensorflow==2.15.0: ~500 MB
torch==2.1.0: ~800 MB
torchvision==0.16.0: ~200 MB
torchaudio==2.1.0: ~100 MB
scikit-learn==1.3.2: ~100 MB
opencv-python-headless==4.8.1.78: ~200 MB
scikit-image==0.21.0: ~150 MB
scipy==1.11.4: ~100 MB
```

### **AI/ML Libraries**
```yaml
faiss-cpu==1.7.4: ~300 MB
transformers==4.35.2: ~500 MB
google-cloud-vision==3.4.4: ~100 MB
google-auth==2.23.4: ~50 MB
supabase==2.0.2: ~50 MB
timm==0.9.12: ~200 MB
```

### **Performance & Monitoring**
```yaml
psutil==5.9.6: ~50 MB
memory-profiler==0.61.0: ~50 MB
pandas==2.1.4: ~200 MB
numpy==1.24.3: ~100 MB
pillow==10.1.0: ~50 MB
```

### **Total ML Dependencies**
```yaml
Core ML: 1.5 GB
AI/ML Libraries: 1.2 GB
Performance & Monitoring: 0.4 GB
Total: 3.1 GB
```

## 🔧 **Deployment Requirements Checklist**

### **Phase 1: Environment Upgrade**
- [ ] Upgrade instance type to m5.2xlarge
- [ ] Increase EBS volume to 100 GB
- [ ] Configure auto-scaling (1-3 instances)
- [ ] Update security groups for ML workloads
- [ ] Configure VPC and subnets

### **Phase 2: ML Package Deployment**
- [ ] Deploy ultra minimal package first (stability)
- [ ] Test basic functionality
- [ ] Gradually add ML dependencies
- [ ] Test each ML component individually
- [ ] Monitor resource utilization

### **Phase 3: Full ML Deployment**
- [ ] Deploy full ML package with all dependencies
- [ ] Configure FAISS indices
- [ ] Load SCIN dataset
- [ ] Test all ML endpoints
- [ ] Monitor performance metrics

### **Phase 4: Optimization**
- [ ] Fine-tune Gunicorn settings
- [ ] Optimize Nginx configuration
- [ ] Configure monitoring and alerts
- [ ] Set up auto-scaling policies
- [ ] Implement caching strategies

## 📈 **Performance Requirements**

### **Target Metrics**
```yaml
CPU Utilization: < 70%
Memory Usage: < 80%
Storage Usage: < 80%
Network Usage: < 50%
Response Time: < 10s
Error Rate: < 1%
ML Inference Time: < 5s
```

### **Health Check Requirements**
```yaml
Environment Status: Green
Health: Healthy
HTTP 5xx Errors: 0%
Instance Health: All healthy
Load Balancer Health: All healthy
```

## 💰 **Cost Requirements**

### **Monthly Cost Breakdown**
```yaml
m5.2xlarge Instance: $280
EBS Storage (100 GB): $10
Data Transfer: $5
Load Balancer: $20
Total Estimated: $315/month
```

### **Budget Considerations**
```yaml
Development Phase: $315/month
Production Phase: $315/month
Scaling Phase: $630/month (2 instances)
Full SCIN Phase: $365/month (r5.2xlarge)
GPU Phase: $380/month (g4dn.xlarge)
```

## 🚨 **Risk Mitigation Requirements**

### **Rollback Strategy**
- [ ] Keep ultra minimal package ready
- [ ] Maintain previous working deployment
- [ ] Monitor deployment logs closely
- [ ] Test each phase before proceeding
- [ ] Have emergency rollback plan

### **Monitoring Requirements**
- [ ] CloudWatch metrics enabled
- [ ] Custom ML performance metrics
- [ ] Resource utilization alerts
- [ ] Error rate monitoring
- [ ] Response time tracking

### **Security Requirements**
- [ ] VPC configuration
- [ ] Security groups for ML workloads
- [ ] IAM roles and policies
- [ ] Data encryption at rest
- [ ] Network encryption in transit

## ✅ **Success Criteria**

### **Environment Health**
- [ ] Status: Green
- [ ] Health: Healthy
- [ ] No HTTP 5xx errors
- [ ] All instances healthy

### **ML Performance**
- [ ] TensorFlow/PyTorch loads successfully
- [ ] FAISS similarity search works
- [ ] SCIN dataset accessible
- [ ] Image processing functional
- [ ] Response time < 10s

### **Resource Utilization**
- [ ] CPU < 70%
- [ ] Memory < 80%
- [ ] Storage < 80%
- [ ] Network < 50%

### **Cost Efficiency**
- [ ] Monthly cost within budget
- [ ] Resource utilization optimized
- [ ] Auto-scaling functional
- [ ] Performance meets requirements

---

**🎯 Key Requirements Summary**:
1. **Minimum**: m5.2xlarge (8 vCPUs, 32 GB RAM, 100 GB storage)
2. **Recommended**: r5.2xlarge (8 vCPUs, 64 GB RAM, 200 GB storage) for full SCIN
3. **Advanced**: g4dn.xlarge (4 vCPUs, 16 GB RAM, GPU) for GPU acceleration
4. **Cost**: $280-$380/month depending on instance type
5. **Deployment**: Gradual approach with ultra minimal → basic → full ML 