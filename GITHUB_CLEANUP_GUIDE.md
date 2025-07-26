# 🧹 GitHub Repository Cleanup Guide

## 🚨 Current Issue
GitHub is blocking pushes due to secrets detected in git history:
- Google Cloud Service Account Credentials
- Google OAuth Client Secrets  
- Stripe API Keys

## 🎯 Solution: Complete Git History Cleanup

### Step 1: Create Backup (Optional but Recommended)
```powershell
# Run backup script
.\backup-before-cleanup.ps1
```

### Step 2: Clean Git History
```powershell
# Run cleanup script
.\clean-git-history.ps1
```

**What this does:**
- Creates a new orphan branch (no history)
- Adds all current files (excluding secrets via .gitignore)
- Creates a single clean commit
- Replaces the entire git history
- Force pushes to GitHub

### Step 3: Verify Cleanup
```powershell
# Check git status
git status

# Check git log (should show only 1 commit)
git log --oneline

# Test push (should work now)
git push origin main
```

## 🔐 Security Status After Cleanup

### ✅ What Will Be Clean:
- No secrets in git history
- No sensitive files tracked
- Clean repository ready for deployment

### ✅ What Will Be Preserved:
- All your code
- All configuration files
- All documentation
- All project structure

### ✅ What Will Be Ignored (via .gitignore):
- `backend/google-vision-key.json`
- `aws-infrastructure/.env.aws`
- `REAL_OAUTH_DEPLOYMENT_GUIDE.md`
- `REAL_OAUTH_SETUP_COMPLETE.md`
- `backend/start_backend.ps1`
- `start_real_oauth.ps1`

## 🚀 After Cleanup - Deployment Options

### Option 1: Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Add environment variables in Vercel dashboard:
# - GOOGLE_CREDENTIALS_JSON
# - SUPABASE_URL
# - SUPABASE_KEY
# - JWT_SECRET_KEY
# - GOOGLE_CLIENT_ID
# - GOOGLE_CLIENT_SECRET
```

### Option 2: Netlify
```bash
# Install Netlify CLI
npm i -g netlify-cli

# Deploy
netlify deploy --prod

# Add environment variables in Netlify dashboard
```

### Option 3: AWS Amplify
```bash
# Push to GitHub (will work after cleanup)
git push origin main

# Amplify will auto-deploy from GitHub
```

## ⚠️ Important Notes

1. **This will completely replace your git history**
2. **All previous commits will be lost**
3. **The backup script preserves your work locally**
4. **After cleanup, you can push to GitHub safely**

## 🔄 Alternative: Manual Cleanup

If you prefer manual cleanup:

```powershell
# 1. Create new orphan branch
git checkout --orphan clean-main

# 2. Add all files
git add .

# 3. Commit
git commit -m "Initial commit - Clean repository"

# 4. Delete old main
git branch -D main

# 5. Rename branch
git branch -m main

# 6. Force push
git push origin main --force
```

## 🎉 Expected Result

After cleanup:
- ✅ GitHub pushes will work
- ✅ No secrets in repository
- ✅ Ready for any deployment platform
- ✅ Clean git history
- ✅ All your work preserved

## 🆘 If Something Goes Wrong

1. **Check your backup folder** - all files are preserved
2. **Restore from backup** if needed
3. **Contact support** if you need help

---

**Ready to clean up your repository? Run the scripts above!** 🚀 