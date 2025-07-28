#!/usr/bin/env node

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔧 QUICK FRONTEND FIX SCRIPT');
console.log('=============================');

// Step 1: Kill all Node.js processes
console.log('\n1️⃣ Killing all Node.js processes...');
try {
    const { execSync } = require('child_process');
    execSync('taskkill /F /IM node.exe', { stdio: 'ignore' });
    console.log('✅ Killed all Node.js processes');
} catch (error) {
    console.log('⚠️  No Node.js processes to kill or already killed');
}

// Step 2: Clean environment
console.log('\n2️⃣ Cleaning environment...');
const dirsToClean = ['.next', 'node_modules'];
const filesToClean = ['package-lock.json'];

dirsToClean.forEach(dir => {
    if (fs.existsSync(dir)) {
        try {
            fs.rmSync(dir, { recursive: true, force: true });
            console.log(`✅ Removed ${dir}`);
        } catch (error) {
            console.log(`⚠️  Could not remove ${dir}: ${error.message}`);
        }
    }
});

filesToClean.forEach(file => {
    if (fs.existsSync(file)) {
        try {
            fs.unlinkSync(file);
            console.log(`✅ Removed ${file}`);
        } catch (error) {
            console.log(`⚠️  Could not remove ${file}: ${error.message}`);
        }
    }
});

// Step 3: Reinstall dependencies
console.log('\n3️⃣ Reinstalling dependencies...');
const npmInstall = spawn('npm', ['install'], { 
    stdio: 'pipe',
    shell: true 
});

npmInstall.stdout.on('data', (data) => {
    console.log(`📦 ${data.toString().trim()}`);
});

npmInstall.stderr.on('data', (data) => {
    console.log(`⚠️  ${data.toString().trim()}`);
});

npmInstall.on('close', (code) => {
    if (code === 0) {
        console.log('✅ Dependencies installed successfully');
        
        // Step 4: Start development server
        console.log('\n4️⃣ Starting development server...');
        console.log('🚀 Running: npm run dev');
        console.log('📱 Open http://localhost:3000 in your browser');
        console.log('🔍 Check browser console (F12) for any errors');
        
        const devServer = spawn('npm', ['run', 'dev'], { 
            stdio: 'inherit',
            shell: true 
        });
        
        devServer.on('error', (error) => {
            console.error('❌ Failed to start dev server:', error.message);
        });
        
        // Auto-kill after 5 minutes if needed
        setTimeout(() => {
            console.log('\n⏰ Auto-stopping after 5 minutes...');
            devServer.kill();
            process.exit(0);
        }, 300000);
        
    } else {
        console.error(`❌ Failed to install dependencies (code: ${code})`);
        process.exit(1);
    }
});

// Handle script interruption
process.on('SIGINT', () => {
    console.log('\n🛑 Script interrupted by user');
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n🛑 Script terminated');
    process.exit(0);
}); 