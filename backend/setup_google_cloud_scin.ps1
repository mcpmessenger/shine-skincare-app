# Google Cloud Setup for SCIN Dataset Processing

Write-Host "🧠 Setting up Google Cloud for SCIN dataset processing..." -ForegroundColor Green

# 1. Create Google Cloud Storage bucket
Write-Host "📦 Creating SCIN dataset bucket..." -ForegroundColor Yellow
gsutil mb gs://shine-scin-dataset

# 2. Enable required APIs
Write-Host "🔧 Enabling required APIs..." -ForegroundColor Yellow
gcloud services enable aiplatform.googleapis.com
gcloud services enable vision.googleapis.com
gcloud services enable storage.googleapis.com

# 3. Set up IAM permissions
Write-Host "🔐 Setting up IAM permissions..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding shine-skincare-app `
    --member="serviceAccount:shine-skincare-app@appspot.gserviceaccount.com" `
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding shine-skincare-app `
    --member="serviceAccount:shine-skincare-app@appspot.gserviceaccount.com" `
    --role="roles/storage.objectViewer"

# 4. Upload SCIN dataset (after manual download)
Write-Host "📤 Uploading SCIN dataset to Google Cloud Storage..." -ForegroundColor Yellow
if (Test-Path "scin_dataset/raw") {
    gsutil cp -r scin_dataset/raw/* gs://shine-scin-dataset/scin_dataset/
} else {
    Write-Host "⚠️ SCIN dataset not found. Please download it first." -ForegroundColor Yellow
}

Write-Host "✅ Google Cloud setup complete!" -ForegroundColor Green
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Download SCIN dataset manually" -ForegroundColor White
Write-Host "   2. Run: python scin_preprocessor.py" -ForegroundColor White
Write-Host "   3. Test with: python test_scin_integration.py" -ForegroundColor White 