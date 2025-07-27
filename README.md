# Shine Skincare App

A comprehensive skincare analysis and recommendation platform built with Next.js frontend and Python Flask backend.

## 🚀 **Current Deployment Architecture**

- **Frontend**: AWS Amplify (via GitHub)
- **Backend**: AWS Elastic Beanstalk (Python 3.11)
- **Database**: Supabase (PostgreSQL)
- **ML Services**: Google Cloud Vision AI, FAISS vector search

## 🔧 **Quick Start**

### Frontend (AWS Amplify)
```bash
# Frontend is automatically deployed via GitHub
git push origin main
```

### Backend (AWS Elastic Beanstalk)
```bash
cd backend
eb deploy
```

## 🐛 **Bug Bounty Program**

We welcome security researchers to help improve our platform's security and reliability. This bug bounty focuses on AWS-specific vulnerabilities and deployment issues.

### **💰 Bounty Tiers**

| Severity | Reward Range | Description |
|----------|-------------|-------------|
| **Critical** | $500 - $1000 | RCE, data breaches, AWS credential exposure |
| **High** | $200 - $500 | Authentication bypass, privilege escalation |
| **Medium** | $50 - $200 | Information disclosure, configuration issues |
| **Low** | $10 - $50 | UI/UX issues, minor security improvements |

### **🎯 Priority Areas**

#### **1. AWS Infrastructure Security**
- **Elastic Beanstalk Configuration Vulnerabilities**
  - Insecure security group configurations
  - Missing HTTPS/SSL certificate issues
  - Environment variable exposure
  - Instance metadata service (IMDS) vulnerabilities
  - Unrestricted IAM roles and permissions

- **Amplify Security Issues**
  - Environment variable leakage
  - Build-time secret exposure
  - Insecure deployment configurations
  - CORS misconfigurations

#### **2. Application Security**
- **API Endpoint Vulnerabilities**
  - `/api/v2/analyze/guest` - Image upload security
  - `/api/recommendations/trending` - Data exposure
  - `/api/health` - Information disclosure
  - Authentication bypass in protected endpoints

- **Frontend Security**
  - XSS vulnerabilities in React components
  - CSRF token implementation
  - Client-side secret exposure
  - Mixed content security issues

#### **3. ML/AI Security**
- **Google Vision AI Integration**
  - API key exposure
  - Rate limiting bypass
  - Image processing vulnerabilities
  - Data privacy in image analysis

- **FAISS Vector Search**
  - Vector injection attacks
  - Similarity search manipulation
  - Memory-based attacks
  - Index poisoning

#### **4. Data Security**
- **Supabase Integration**
  - Database connection security
  - SQL injection vulnerabilities
  - Row Level Security (RLS) bypass
  - API key exposure

- **User Data Protection**
  - PII exposure in logs
  - Image data retention issues
  - Cross-user data leakage
  - GDPR compliance gaps

#### **5. Deployment & DevOps Security**
- **AWS Resource Security**
  - S3 bucket misconfigurations
  - CloudTrail logging gaps
  - VPC security group issues
  - Lambda function security (if applicable)

- **CI/CD Security**
  - GitHub Actions secret exposure
  - Build artifact security
  - Deployment pipeline vulnerabilities
  - Environment variable management

### **🔍 Specific Vulnerabilities to Look For**

#### **Critical Issues**
1. **AWS Credential Exposure**
   - Check for hardcoded AWS keys in code
   - Look for credentials in environment variables
   - Verify IAM role permissions are minimal

2. **RCE in Image Processing**
   - Test image upload endpoints for code execution
   - Check for path traversal in file uploads
   - Verify image processing libraries are secure

3. **Database Access Vulnerabilities**
   - Test for SQL injection in Supabase queries
   - Check for unauthorized database access
   - Verify RLS policies are properly configured

#### **High Priority Issues**
1. **Authentication Bypass**
   - Test guest endpoints for privilege escalation
   - Check for JWT token vulnerabilities
   - Verify session management security

2. **Information Disclosure**
   - Check for sensitive data in API responses
   - Look for debug information in production
   - Verify error messages don't leak sensitive info

3. **Configuration Issues**
   - Test HTTPS/SSL certificate configuration
   - Check CORS policy implementation
   - Verify security headers are properly set

#### **Medium Priority Issues**
1. **API Security**
   - Test rate limiting implementation
   - Check for input validation bypass
   - Verify proper error handling

2. **Frontend Security**
   - Test for XSS in React components
   - Check for client-side secret exposure
   - Verify proper CSP implementation

#### **Low Priority Issues**
1. **UI/UX Security**
   - Check for clickjacking vulnerabilities
   - Test for UI redressing attacks
   - Verify proper input sanitization

### **🔧 Security Assessment Tools & Methodologies**

#### **Automated Scanning Tools**
```bash
# Web Application Security Testing
owasp-zap -t https://main.d2wy4w2nf9bgxx.amplifyapp.com
burp-suite-pro  # Professional web application security testing

# AWS Security Tools
aws securityhub get-findings
aws config get-compliance-details-by-config-rule
aws guardduty list-findings

# Dependency Scanning
npm audit  # Frontend dependencies
pip-audit  # Backend dependencies
safety check  # Python security scanning

# Infrastructure Scanning
aws ec2 describe-security-groups
aws iam get-account-authorization-details
aws s3api list-buckets --query 'Buckets[].Name'
```

#### **Manual Testing Focus Areas**

##### **1. Authentication & Authorization Bypass**
- **Session Management Testing**
  ```bash
  # Test session tokens
  curl -H "Authorization: Bearer INVALID_TOKEN" \
       https://main.d2wy4w2nf9bgxx.amplifyapp.com/api/protected
  
  # Test guest endpoint privilege escalation
  curl -X POST "http://Shine-backend-poc-env.eba-bpcnncyq.us-east-1.elasticbeanstalk.com/api/v2/analyze/guest" \
       -F "image=@malicious.jpg"
  ```

- **Broken Object Level Authorization (BOLA)**
   ```bash
  # Test user ID manipulation
  curl -H "User-ID: 123" \
       https://main.d2wy4w2nf9bgxx.amplifyapp.com/api/user/456/profile
   ```

##### **2. Image Upload Vulnerabilities**
- **File Upload Security Testing**
   ```bash
  # Test malicious file uploads
  curl -X POST "http://Shine-backend-poc-env.eba-bpcnncyq.us-east-1.elasticbeanstalk.com/api/v2/analyze/guest" \
       -F "image=@shell.php" \
       -F "image=@../../../etc/passwd"
  
  # Test image format parsing
  curl -X POST "http://Shine-backend-poc-env.eba-bpcnncyq.us-east-1.elasticbeanstalk.com/api/v2/analyze/guest" \
       -F "image=@malformed.jpg"
  ```

- **Server-Side Request Forgery (SSRF)**
   ```bash
  # Test SSRF in image processing
  curl -X POST "http://Shine-backend-poc-env.eba-bpcnncyq.us-east-1.elasticbeanstalk.com/api/v2/analyze/guest" \
       -F "image_url=http://169.254.169.254/latest/meta-data/iam/security-credentials/"
   ```

##### **3. API Security Testing**
- **Rate Limiting Bypass**
   ```bash
  # Test rate limiting on sensitive endpoints
  for i in {1..100}; do
    curl -X POST "http://Shine-backend-poc-env.eba-bpcnncyq.us-east-1.elasticbeanstalk.com/api/v2/analyze/guest"
  done
  ```

- **Mass Assignment Testing**
  ```bash
  # Test extra parameters in API requests
  curl -X POST "http://Shine-backend-poc-env.eba-bpcnncyq.us-east-1.elasticbeanstalk.com/api/v2/analyze/guest" \
       -H "Content-Type: application/json" \
       -d '{"image":"data:image/jpeg;base64,...","admin":true,"role":"admin"}'
  ```

##### **4. AWS-Specific Security Testing**
- **IAM Policy Testing**
   ```bash
  # Check for overly permissive IAM roles
  aws iam get-role --role-name aws-elasticbeanstalk-ec2-role
  aws iam list-attached-role-policies --role-name aws-elasticbeanstalk-ec2-role
  ```

- **Security Group Testing**
  ```bash
  # Check security group configurations
  aws ec2 describe-security-groups --group-ids sg-xxxxxxxxx
  aws ec2 describe-instances --filters "Name=instance-id,Values=i-xxxxxxxxx"
  ```

- **S3 Bucket Security**
  ```bash
  # Test for public S3 buckets
  aws s3api get-bucket-policy --bucket your-bucket-name
  aws s3api get-bucket-acl --bucket your-bucket-name
  ```

#### **Code Review Checklist**

##### **Frontend (Next.js)**
- [ ] XSS prevention in React components
- [ ] Proper input validation and sanitization
- [ ] Secure handling of environment variables
- [ ] CSP implementation
- [ ] CSRF token implementation

##### **Backend (Flask)**
- [ ] Input validation on all endpoints
- [ ] Proper error handling without information disclosure
- [ ] Secure file upload handling
- [ ] Authentication and authorization checks
- [ ] SQL injection prevention

##### **AWS Configuration**
- [ ] IAM roles follow principle of least privilege
- [ ] Security groups are properly configured
- [ ] Environment variables are secure
- [ ] CloudTrail logging is enabled
- [ ] S3 buckets are not publicly accessible

### **📋 Submission Guidelines**

#### **Required Information**
1. **Clear Description**
   - Detailed explanation of the vulnerability
   - Impact assessment
   - Steps to reproduce

2. **Proof of Concept**
   - Working exploit code (if applicable)
   - Screenshots or videos
   - Logs demonstrating the issue

3. **Suggested Fix**
   - Recommended solution
   - Code examples (if applicable)
   - Configuration changes needed

#### **Submission Format**
```markdown
## Bug Report: [Title]

### Severity: [Critical/High/Medium/Low]

### Description
[Detailed description of the vulnerability]

### Impact
[What can an attacker do with this vulnerability?]

### Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Proof of Concept
[Code, screenshots, or other evidence]

### Suggested Fix
[Recommended solution]

### Environment
- Frontend: AWS Amplify
- Backend: AWS Elastic Beanstalk
- Database: Supabase
- [Other relevant details]

### Tools Used
- [List of tools used for discovery]
- [Commands executed]
- [Screenshots of tools]
```

### **🚫 Out of Scope**
- Physical security testing
- Social engineering attacks
- DDoS attacks
- Issues in third-party services (unless directly exploitable)
- Issues requiring physical access to AWS infrastructure

### **📧 Submission Process**
1. **Email**: security@shineskincare.com (create this email)
2. **Subject**: `[BUG BOUNTY] [Severity] [Brief Description]`
3. **Response Time**: 48 hours for initial response
4. **Resolution**: 30 days for fix implementation

### **🏆 Recognition**
- Public acknowledgment (with permission)
- Hall of fame listing
- Swag for significant contributions

### **⚠️ Responsible Disclosure**
- Do not publicly disclose vulnerabilities before we've had time to fix them
- Allow reasonable time for fixes (typically 30 days)
- Coordinate disclosure timeline with our team

### **🔧 Testing Environment**
- **Production**: https://main.d2wy4w2nf9bgxx.amplifyapp.com
- **Backend**: http://Shine-backend-poc-env.eba-bpcnncyq.us-east-1.elasticbeanstalk.com
- **API Endpoints**: See `/api/*` routes

### **📚 Resources**
- [AWS Security Best Practices](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [AWS Elastic Beanstalk Security](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/security.html)
- [AWS Security Tools](https://aws.amazon.com/security/security-tools/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)

---

**Note**: This bug bounty program is designed to improve the security of our AWS-based skincare platform. We appreciate all responsible security research and will work with researchers to address any issues found.

## 📝 **Project Status**

### **✅ Completed**
- [x] Frontend deployment on AWS Amplify
- [x] Backend deployment on AWS Elastic Beanstalk
- [x] Basic API endpoints working
- [x] Recommendations endpoint functional
- [x] Environment variable configuration

### **🔄 In Progress**
- [ ] HTTPS configuration for backend
- [ ] Enhanced ML mode deployment
- [ ] Performance optimization
- [ ] Security hardening

### **📋 TODO**
- [ ] Configure SSL certificates for Elastic Beanstalk
- [ ] Implement proper authentication
- [ ] Add comprehensive logging
- [ ] Set up monitoring and alerting
- [ ] Performance testing and optimization

## 🔐 **Security & Environment Variables**

### **Never Commit Secrets**
- AWS credentials
- API keys
- Database passwords
- JWT secrets

### **Use AWS Console for Secrets**
- Store sensitive data in AWS Systems Manager Parameter Store
- Use AWS Secrets Manager for database credentials
- Configure environment variables through AWS Console

### **Pre-commit Checklist**
```bash
# Check for secrets before committing
git status
git diff
# Run secret scanning tools
truffleHog --regex --entropy=False .
gitleaks detect --source .
```

## 🚀 **Deployment Flow**

### **Frontend (AWS Amplify)**
1. Push to GitHub main branch
2. Amplify automatically builds and deploys
3. Environment variables configured in Amplify Console

### **Backend (AWS Elastic Beanstalk)**
1. `eb deploy` from backend directory
2. Environment variables configured in EB Console
3. Health checks monitor deployment

## 📞 **Support**

For technical issues:
- Backend logs: `eb logs`
- Frontend logs: AWS Amplify Console
- Security issues: security@shineskincare.com

---

**Last Updated**: July 27, 2025
**Version**: 1.0.0