# Pre-commit security check script
# Run this before any git commit to check for sensitive information

Write-Host "🔍 Running security check..." -ForegroundColor Yellow

# Check for potential secrets in staged files
$sensitivePatterns = @(
    "shine-466907",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
    "sk_live_",
    "sk_test_",
    "-----BEGIN PRIVATE KEY-----",
    "GOOGLE_CREDENTIALS_JSON.*{",
    "SUPABASE_KEY.*eyJ",
    "SECRET_KEY.*[a-zA-Z0-9]{20,}"
)

$foundSecrets = $false

foreach ($pattern in $sensitivePatterns) {
    $matches = git diff --cached --name-only | ForEach-Object {
        if (Test-Path $_) {
            Select-String -Path $_ -Pattern $pattern -Quiet
        }
    }
    
    if ($matches) {
        Write-Host "❌ SECURITY ALERT: Potential secret found matching pattern: $pattern" -ForegroundColor Red
        $foundSecrets = $true
    }
}

# Check for credential files
$credentialFiles = @(
    "shine-466907-09b8909d49ec.json",
    ".env.local",
    ".env.production",
    "credentials.json"
)

foreach ($file in $credentialFiles) {
    if (git diff --cached --name-only | Select-String $file) {
        Write-Host "❌ SECURITY ALERT: Credential file staged for commit: $file" -ForegroundColor Red
        $foundSecrets = $true
    }
}

if ($foundSecrets) {
    Write-Host "🚨 COMMIT BLOCKED: Remove sensitive information before committing" -ForegroundColor Red
    Write-Host "💡 Use environment variables instead of hardcoded secrets" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "✅ Security check passed" -ForegroundColor Green
    exit 0
}