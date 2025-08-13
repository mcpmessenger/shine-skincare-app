# 🚀 Shine Skincare App - Deployment Guide

## Quick Start

### 1. Local Development
```powershell
# Start local development environment
.\scripts\dev-local.ps1

# Or use the quick deploy script
.\scripts\quick-deploy.ps1
```

### 2. Deploy to Staging
```powershell
# Deploy to staging environment
.\scripts\deploy-staging.ps1
```

### 3. Deploy to Production
```powershell
# Deploy to production environment
.\scripts\deploy-production.ps1
```

### 4. Health Check
```powershell
# Check service health
.\scripts\health-check.ps1
```

## 📁 Scripts Overview

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `dev-local.ps1` | Start local development | Daily development |
| `deploy-staging.ps1` | Deploy to staging | Before production |
| `deploy-production.ps1` | Deploy to production | Live deployment |
| `health-check.ps1` | Check service health | Monitoring |
| `quick-deploy.ps1` | Interactive deployment | Quick actions |

## 🔧 Setup Requirements

### Prerequisites
- PowerShell 5.1+ (Windows)
- Git
- Node.js 18+
- Python 3.9+
- AWS CLI configured

### Environment Setup
1. Copy `env-local-template.txt` to `.env.local`
2. Customize the values for your local environment
3. Ensure backend is accessible at `http://localhost:5000`

## 🚀 Deployment Workflow

### Development → Staging → Production

```
Local Development → Staging → Production
      ↓              ↓          ↓
   Test Locally → Test Staging → Live
```

### 1. Local Development
- Make changes to code
- Test locally using `dev-local.ps1`
- Ensure all functionality works
- Run tests and linting

### 2. Staging Deployment
- Create staging branch
- Deploy to staging environment
- Test all functionality
- Validate backend connectivity
- Run health checks

### 3. Production Deployment
- Merge staging to main
- Deploy to production
- Monitor deployment
- Run post-deployment checks
- Monitor error rates

## 📋 Pre-Deployment Checklist

### Code Quality
- [ ] All tests pass
- [ ] No linting errors
- [ ] TypeScript compilation successful
- [ ] Build completes without errors
- [ ] Code review completed

### Environment
- [ ] Environment variables configured
- [ ] Backend services healthy
- [ ] Database migrations ready
- [ ] Feature flags configured

### Testing
- [ ] Local testing completed
- [ ] Staging testing completed
- [ ] Performance benchmarks met
- [ ] Security scan passed

## 🚨 Rollback Procedures

### Quick Rollback
```bash
# Revert last commit
git revert HEAD
git push origin main
```

### Emergency Rollback
```bash
# Force push to previous version
git reset --hard HEAD~1
git push --force origin main
```

## 🔍 Monitoring & Health Checks

### Automated Health Checks
- Backend API responsiveness
- Frontend availability
- DNS resolution
- SSL certificate validity

### Manual Health Checks
- Face detection functionality
- Skin analysis accuracy
- User authentication flows
- Cart and checkout processes

## 🛠️ Troubleshooting

### Common Issues

#### Backend Connection Failed
```powershell
# Check backend health
.\scripts\health-check.ps1

# Verify backend is running
Get-Process -Name "python"
```

#### Build Failures
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install

# Check for TypeScript errors
npm run type-check
```

#### Deployment Issues
```bash
# Check git status
git status

# Verify branch
git branch --show-current

# Check remote
git remote -v
```

### Environment Issues
- Verify `.env.local` exists and is configured
- Check backend URL is accessible
- Ensure all required services are running

## 📊 Performance Monitoring

### Key Metrics
- API response times
- Page load times
- Error rates
- User session duration
- Feature usage rates

### Alert Thresholds
- API errors > 5%
- Response time > 3 seconds
- Failed authentication > 10%
- Face detection failures > 15%

## 🔐 Security Considerations

### Pre-Deployment
- Security scan completed
- No sensitive data in code
- Environment variables secured
- Dependencies updated

### Post-Deployment
- Monitor security events
- Check access logs
- Validate authentication flows
- Monitor for suspicious activity

## 📚 Additional Resources

### Documentation
- [DEPLOYMENT_PIPELINE.md](./DEPLOYMENT_PIPELINE.md) - Detailed pipeline documentation
- [README.md](./README.md) - Project overview
- [OPERATION_TORTOISE_PROGRESS.md](./docs/markdown/backend/OPERATION_TORTOISE_PROGRESS.md) - Infrastructure progress

### AWS Services
- [AWS Amplify Console](https://console.aws.amazon.com/amplify/) - Frontend deployment
- [Elastic Beanstalk Console](https://console.aws.amazon.com/elasticbeanstalk/) - Backend deployment
- [Route 53 Console](https://console.aws.amazon.com/route53/) - DNS management

## 🆘 Support

### Emergency Contacts
- **DevOps Lead**: [Your Name]
- **Backend Engineer**: [Backend Team]
- **Frontend Engineer**: [Frontend Team]

### Escalation Procedures
1. Check health status using scripts
2. Review recent deployments
3. Check AWS service status
4. Contact team lead
5. Initiate rollback if necessary

---

*Last Updated: December 2024*
*Version: 1.0*

