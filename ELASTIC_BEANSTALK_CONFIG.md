# 🔧 Elastic Beanstalk Load Balancer Configuration

## 🎯 **Correct Configuration for HTTPS**

### **Load Balancer Settings**:

#### **1. HTTPS Listener (Port 443)**
```
Protocol: HTTPS
SSL Certificate: arn:aws:acm:us-east-1:396608803476:certificate/d22adc54-b99d-4be1-95ae-df3ea291da6b
Default Process: default
Target Group: HTTP on port 8000
```

#### **2. HTTP Listener (Port 80)**
```
Protocol: HTTP
Default Process: default
Target Group: HTTP on port 8000
```

#### **3. Target Group**
```
Protocol: HTTP
Port: 8000
Health Check Path: /api/health
Health Check Interval: 15 seconds
Health Check Timeout: 5 seconds
Healthy Threshold: 3
Unhealthy Threshold: 5
```

### **Security Groups**:
- **Inbound**: Port 80, 443 from 0.0.0.0/0
- **Outbound**: All traffic

### **Environment Type**:
- **Environment Type**: Load Balanced
- **Load Balancer Type**: Application Load Balancer

## 🚀 **Deployment Steps**:

1. **Upload the new zip file**: `backend-deployment-python.zip`
2. **Wait for deployment** to complete
3. **Test the domain**: `https://api.shineskincollective.com/api/health`

## ✅ **Expected Results**:
- ✅ HTTPS working on port 443
- ✅ SSL certificate valid
- ✅ Custom domain accessible
- ✅ No Mixed Content errors 