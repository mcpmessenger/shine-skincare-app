# 🚀 Manual ECS Deployment Guide - Complete ML Backend

**You've successfully created the ECS cluster!** ✅  
Now let's complete the deployment step by step.

## ✅ **What We've Done:**
- **ECS Cluster**: `shine-ml-cluster` created successfully
- **Docker Image**: `396608803476.dkr.ecr.us-east-1.amazonaws.com/shine-ml-backend:latest` ready in ECR

## 🎯 **Next Steps - Choose Your Approach:**

### **Option 1: Complete via AWS Console (Recommended)**
This is the fastest and most reliable approach:

1. **Open AWS Console** → **ECS** → **Task Definitions**
2. **Create new task definition**:
   - **Family**: `shine-ml-backend`
   - **Launch type**: **Fargate**
   - **CPU**: 1024 (1 vCPU)
   - **Memory**: 3072 (3GB)
   
3. **Container Configuration**:
   - **Name**: `shine-ml-container`
   - **Image**: `396608803476.dkr.ecr.us-east-1.amazonaws.com/shine-ml-backend:latest`
   - **Port**: 5000
   - **Environment**:
     - `FLASK_ENV=production`
     - `AWS_REGION=us-east-1`

4. **Create Service**:
   - **Cluster**: `shine-ml-cluster` (already created ✅)
   - **Service name**: `shine-ml-service`
   - **Desired tasks**: 1
   - **Public IP**: Enabled
   - **Security group**: Allow port 5000

---

### **Option 2: Continue with CLI Commands**
If you want to continue with CLI, here are the remaining commands:

```powershell
# Get VPC ID
$VPC_ID = aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query 'Vpcs[0].VpcId' --output text --region us-east-1

# Get Subnets
$SUBNET_IDS = aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" "Name=map-public-ip-on-launch,Values=true" --query 'Subnets[].SubnetId' --output text --region us-east-1

# Create Security Group
$SG_ID = aws ec2 create-security-group --group-name shine-ml-sg --description "Shine ML Backend" --vpc-id $VPC_ID --query 'GroupId' --output text --region us-east-1

# Allow port 5000
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 5000 --cidr 0.0.0.0/0 --region us-east-1
```

---

### **Option 3: Simple Task Run (Quick Test)**
For a quick test without load balancer:

```powershell
# Create simple task definition file
@'
{
    "family": "shine-ml-backend",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "1024",
    "memory": "3072",
    "executionRoleArn": "arn:aws:iam::396608803476:role/ecsTaskExecutionRole",
    "containerDefinitions": [
        {
            "name": "shine-ml-container",
            "image": "396608803476.dkr.ecr.us-east-1.amazonaws.com/shine-ml-backend:latest",
            "portMappings": [{"containerPort": 5000, "protocol": "tcp"}],
            "essential": true,
            "environment": [
                {"name": "FLASK_ENV", "value": "production"},
                {"name": "AWS_REGION", "value": "us-east-1"}
            ]
        }
    ]
}
'@ | Out-File -FilePath "simple-task-def.json" -Encoding UTF8

# Register task definition
aws ecs register-task-definition --cli-input-json file://simple-task-def.json --region us-east-1
```

---

## 🎯 **My Recommendation:**

**Use Option 1 (AWS Console)** - it's the most reliable and gives you:
- ✅ Visual feedback during deployment
- ✅ Easy troubleshooting
- ✅ Load balancer setup (optional)
- ✅ Complete control over configuration

## 🧪 **After Deployment:**

Once your service is running, test it with:
```powershell
# Get the public IP from ECS Console, then:
python test_ecs_deployment.py http://[PUBLIC-IP]:5000
```

## 🎉 **Expected Result:**

**Complete TensorFlow ML functionality** with:
- 🧠 **Medical-grade skin analysis**
- 👁️ **Advanced face detection**
- ⚡ **Production-ready scaling**
- 🔗 **Ready for frontend integration**

---

## 🔄 **Restart Service to Apply S3 Permissions:**

After adding S3 permissions to the task role, restart the service:

1. Go to **ECS** > **Clusters** > **shine-ml-cluster**
2. Click on **Services** tab  
3. Select your service (`shine-ml-backend-service-5hs5zi52`)
4. Click **Update**
5. Check **Force new deployment**
6. Click **Update service**
7. Wait for the new task to start and get the **new Public IP**

### ✅ **Verify S3 Access:**
```powershell
# Test with new Public IP
Invoke-WebRequest -Uri "http://[NEW_PUBLIC_IP]:5000/api/v5/skin/health"
```

The response should show `"model_loaded": true` if S3 access is working!

---

**Which option would you prefer?** I recommend the AWS Console approach for the smoothest experience! 🚀

