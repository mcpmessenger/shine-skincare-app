# 🦫 MANUAL DNS FIX SCRIPT
# This script provides the exact commands to fix your DNS routing
# and get your face detection API working immediately.

Write-Host "🚀 SHINE SKINCARE APP - DNS FIX SCRIPT" -ForegroundColor Cyan
Write-Host "🦫 Sprint 1: Fix DNS Routing to Working ALB" -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "🎯 PROBLEM IDENTIFIED:" -ForegroundColor Red
Write-Host "Your domain api.shineskincollective.com is pointing to the WRONG load balancer!" -ForegroundColor White
Write-Host ""
Write-Host "❌ CURRENT (BROKEN):" -ForegroundColor Red
Write-Host "   Domain → Elastic Beanstalk ALB (awseb--AWSEB-ydAUJ3jj2fwA)" -ForegroundColor White
Write-Host "   Target Group: shine-api-tg-eb-8000 (UNHEALTHY)" -ForegroundColor White
Write-Host ""
Write-Host "✅ WORKING SOLUTION:" -ForegroundColor Green
Write-Host "   Domain → Production ALB (production-shine-skincare-alb)" -ForegroundColor White
Write-Host "   Target Group: shine-api-tg-8000-fixed (HEALTHY)" -ForegroundColor White
Write-Host ""

Write-Host "🔧 IMMEDIATE FIX REQUIRED:" -ForegroundColor Yellow
Write-Host "Update your DNS to point to the working ALB:" -ForegroundColor White
Write-Host ""

Write-Host "📋 DNS FIX COMMANDS:" -ForegroundColor Cyan
Write-Host "1. Go to Route 53 in AWS Console" -ForegroundColor White
Write-Host "2. Find your hosted zone for 'shineskincollective.com'" -ForegroundColor White
Write-Host "3. Update the A record for 'api.shineskincollective.com'" -ForegroundColor White
Write-Host "4. Change the alias target to: production-shine-skincare-alb" -ForegroundColor White
Write-Host ""

Write-Host "🌐 ALTERNATIVE: Use AWS CLI (if you have Route 53 permissions):" -ForegroundColor Cyan
Write-Host "aws route53 change-resource-record-sets --hosted-zone-id YOUR_HOSTED_ZONE_ID --change-batch '{ \"Changes\": [{ \"Action\": \"UPSERT\", \"ResourceRecordSet\": { \"Name\": \"api.shineskincollective.com\", \"Type\": \"A\", \"AliasTarget\": { \"HostedZoneId\": \"Z35SXDOTRQ7X7K\", \"DNSName\": \"production-shine-skincare-alb-8bc3d14421300795.us-east-1.elb.amazonaws.com\", \"EvaluateTargetHealth\": true } } } ] }'" -ForegroundColor White
Write-Host ""

Write-Host "🎯 EXPECTED RESULT:" -ForegroundColor Green
Write-Host "After DNS update:" -ForegroundColor White
Write-Host "✅ api.shineskincollective.com/health → 200 OK" -ForegroundColor Green
Write-Host "✅ Face detection API working" -ForegroundColor Green
Write-Host "✅ ALB target health: Healthy" -ForegroundColor Green
Write-Host ""

Write-Host "⏱️  TIMELINE:" -ForegroundColor Yellow
Write-Host "DNS propagation: 5-10 minutes" -ForegroundColor White
Write-Host "API working: Immediately after propagation" -ForegroundColor White
Write-Host ""

Write-Host "🦫 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Fix DNS routing (above)" -ForegroundColor White
Write-Host "2. Test API endpoints" -ForegroundColor White
Write-Host "3. Document success" -ForegroundColor White
Write-Host "4. Plan Terraform automation" -ForegroundColor White
Write-Host ""

Write-Host "🚀 Your face detection API will be working in under 10 minutes!" -ForegroundColor Green
