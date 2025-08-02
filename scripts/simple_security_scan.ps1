# Simple Security Scan for GitHub Push
Write-Host "Security Scan for GitHub Push" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green

# Define sensitive patterns to scan for
$sensitivePatterns = @(
    @{ Pattern = "sk-[a-zA-Z0-9]{48}"; Name = "OpenAI API Key" },
    @{ Pattern = "AIza[a-zA-Z0-9_-]{35}"; Name = "Google API Key" },
    @{ Pattern = "AKIA[a-zA-Z0-9]{16}"; Name = "AWS Access Key ID" },
    @{ Pattern = '"type":\s*"service_account"'; Name = "Google Service Account" },
    @{ Pattern = "GOOGLE_CLOUD_PROJECT\s*=\s*(?!your-project-id)[a-zA-Z0-9]{12,}"; Name = "Google Cloud Project ID" },
    @{ Pattern = "SCIN_BUCKET\s*=\s*(?!your-scin-bucket)[a-zA-Z0-9]{12,}"; Name = "SCIN Bucket Name" }
)

# Files to exclude from scanning
$excludePatterns = @(
    "node_modules",
    ".git",
    ".next",
    "*.log",
    "*.tmp",
    "*.cache",
    "*.pyc",
    "__pycache__",
    "venv",
    "env",
    ".env",
    ".env.local",
    ".env.production",
    "*.exe",
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.ico",
    "*.svg",
    "*.woff",
    "*.woff2",
    "*.ttf",
    "*.eot",
    "package-lock.json",
    "test-output.css"
)

# Get all files to scan
Write-Host "Scanning files for sensitive information..." -ForegroundColor Yellow

$filesToScan = Get-ChildItem -Recurse -File | Where-Object {
    $file = $_
    $shouldExclude = $false
    
    foreach ($excludePattern in $excludePatterns) {
        if ($file.FullName -like "*$excludePattern*") {
            $shouldExclude = $true
            break
        }
    }
    
    return -not $shouldExclude
}

Write-Host "Found $($filesToScan.Count) files to scan" -ForegroundColor Cyan

# Scan for sensitive information
$foundSensitive = @()

foreach ($file in $filesToScan) {
    try {
        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        if ($content) {
            foreach ($pattern in $sensitivePatterns) {
                if ($content -match $pattern.Pattern) {
                    $foundSensitive += @{
                        File = $file.FullName
                        Pattern = $pattern.Name
                    }
                }
            }
        }
    }
    catch {
        Write-Host "Could not read file: $($file.FullName)" -ForegroundColor Yellow
    }
}

# Report findings
if ($foundSensitive.Count -gt 0) {
    Write-Host "SENSITIVE INFORMATION FOUND!" -ForegroundColor Red
    Write-Host "===========================" -ForegroundColor Red
    
    foreach ($item in $foundSensitive) {
        Write-Host "File: $($item.File)" -ForegroundColor Yellow
        Write-Host "Pattern: $($item.Pattern)" -ForegroundColor Red
    }
    
    Write-Host "RECOMMENDATIONS:" -ForegroundColor Red
    Write-Host "1. Remove or replace sensitive information" -ForegroundColor White
    Write-Host "2. Use environment variables for secrets" -ForegroundColor White
    Write-Host "3. Add files to .gitignore" -ForegroundColor White
    
    exit 1
} else {
    Write-Host "No sensitive information found!" -ForegroundColor Green
    Write-Host "Safe to push to GitHub" -ForegroundColor Green
}

# Check for .env files
$envFiles = Get-ChildItem -Recurse -Name "*.env*" -ErrorAction SilentlyContinue
if ($envFiles) {
    Write-Host "Found .env files:" -ForegroundColor Yellow
    foreach ($file in $envFiles) {
        Write-Host "   - $file" -ForegroundColor Yellow
    }
    Write-Host "   Make sure these are in .gitignore" -ForegroundColor White
}

Write-Host "Security scan complete!" -ForegroundColor Green 