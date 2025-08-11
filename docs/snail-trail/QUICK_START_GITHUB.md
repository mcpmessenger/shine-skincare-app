# 🐌 **QUICK START: OPERATION SNAIL TRAIL GITHUB WORKFLOW**

> *"Get started with your snail trail journey in just a few commands!"* 🚀

## 🚀 **IMMEDIATE SETUP (5 minutes)**

### **Step 1: Create and Switch to Develop Branch**
```bash
# Create develop branch from main
git checkout main
git pull origin main
git checkout -b develop
git push -u origin develop
```

### **Step 2: Create Phase 1 Branch**
```bash
# Create Phase 1 branch for simple health app
git checkout develop
git pull origin develop
git checkout -b phase-1-simple-health
git push -u origin phase-1-simple-health
```

### **Step 3: Start Development**
```bash
# You're now on phase-1-simple-health branch
# Start developing your simple health app!
```

---

## 🔄 **DAILY WORKFLOW**

### **Morning: Start Work**
```bash
# Switch to your phase branch
git checkout phase-1-simple-health
git pull origin phase-1-simple-health

# Create feature branch for today's work
git checkout -b feature/phase-1-[description]
```

### **During Development: Commit Progress**
```bash
# Add your changes
git add .

# Commit with descriptive message
git commit -m "feat: [What you accomplished]"

# Push to feature branch
git push origin feature/phase-1-[description]
```

### **Evening: Update Progress Log**
```bash
# Switch back to phase branch
git checkout phase-1-simple-health

# Merge your feature
git merge --squash feature/phase-1-[description]
git commit -m "feat: [Summary of today's progress]"

# Push to phase branch
git push origin phase-1-simple-health

# Delete feature branch (optional)
git branch -d feature/phase-1-[description]
git push origin --delete feature/phase-1-[description]
```

---

## 📋 **PHASE COMPLETION WORKFLOW**

### **When Phase 1 is Complete:**
```bash
# 1. Merge to develop
git checkout develop
git pull origin develop
git merge --no-ff phase-1-simple-health
git commit -m "feat: Complete Phase 1 - Simple Health App operational"
git push origin develop

# 2. Create Phase 2 branch
git checkout -b phase-2-hybrid-ml
git push -u origin phase-2-hybrid-ml

# 3. Update progress log
# Edit docs/snail-trail/SNAIL_TRAIL_LOG.md
# Mark Phase 1 as complete
```

### **When Ready for Production:**
```bash
# 1. Merge develop to main
git checkout main
git pull origin main
git merge --no-ff develop
git commit -m "release: Deploy Phase 1 to production"
git push origin main

# 2. Create release tag
git tag v1.0.0-simple-health
git push origin v1.0.0-simple-health
```

---

## 🎯 **PROGRESS TRACKING**

### **Update Your Progress Log:**
```bash
# Edit the progress log
code docs/snail-trail/SNAIL_TRAIL_LOG.md

# Add today's progress
# Update checkboxes
# Log any challenges encountered
# Record lessons learned
```

### **Commit Progress Updates:**
```bash
git add docs/snail-trail/SNAIL_TRAIL_LOG.md
git commit -m "docs: Update progress log - [What you accomplished]"
git push origin phase-1-simple-health
```

---

## 🚨 **EMERGENCY PROCEDURES**

### **If You Need to Rollback:**
```bash
# Rollback to previous commit
git reset --hard HEAD~1
git push --force origin phase-1-simple-health

# Or rollback to specific commit
git reset --hard [commit-hash]
git push --force origin phase-1-simple-health
```

### **If You Need to Start Over:**
```bash
# Reset phase branch to develop
git checkout phase-1-simple-health
git reset --hard develop
git push --force origin phase-1-simple-health
```

---

## 📊 **BRANCH STATUS CHECK**

### **See All Branches:**
```bash
# List all branches
git branch -a

# See branch status
git status

# See recent commits
git log --oneline -10
```

### **Check Remote Status:**
```bash
# See remote branches
git branch -r

# See tracking info
git branch -vv
```

---

## 🎉 **CELEBRATION COMMANDS**

### **Phase Completion:**
```bash
# When Phase 1 is complete
echo "🎯 Phase 1 Complete - Basic system operational!"
echo "🐌 Snail has reached the starting line!"
```

### **Victory Declaration:**
```bash
# When all phases are complete
echo "🏆 OPERATION SNAIL TRAIL: MISSION ACCOMPLISHED!"
echo "🐌 Snail has completed the journey!"
```

---

## 🐌 **SNAIL'S QUICK START WISDOM**

> *"The journey of a thousand commits begins with a single `git checkout`."*

**Remember:**
- **Start small**: One feature at a time
- **Commit often**: Every meaningful change
- **Push regularly**: Keep your trail visible
- **Document progress**: Update the log daily
- **Celebrate milestones**: Each phase completion is a victory!

---

**Ready to start your snail trail journey? Run the setup commands above and begin Phase 1!** 🚀
