# Simple Google Cloud Storage Setup for SCIN Dataset

Write-Host "🚀 Setting up Google Cloud Storage for SCIN Dataset..." -ForegroundColor Green

# Set project
Write-Host "📋 Setting project to shine-466907..." -ForegroundColor Yellow
gcloud config set project shine-466907

# Create bucket for SCIN dataset
$bucketName = "shine-scin-dataset"
Write-Host "🪣 Creating bucket: $bucketName..." -ForegroundColor Yellow
gsutil mb gs://$bucketName

# Create local directory structure
Write-Host "📁 Creating local directory structure..." -ForegroundColor Yellow
$conditions = @("acne", "rosacea", "melanoma", "normal", "basal_cell_carcinoma", "nevus")

foreach ($condition in $conditions) {
    $localDir = "scin_dataset/raw/$condition"
    New-Item -ItemType Directory -Force -Path $localDir
    
    # Create 5 placeholder images per condition
    for ($i = 1; $i -le 5; $i++) {
        $imagePath = "$localDir/${condition}_$($i.ToString('000')).jpg"
        
        # Create a simple text file as placeholder (in production, this would be a real image)
        $placeholderContent = "PLACEHOLDER_IMAGE_FOR_$condition`nSample $i`nCreated: $(Get-Date)"
        $placeholderContent | Out-File -FilePath $imagePath -Encoding UTF8
        
        Write-Host "Created placeholder: $imagePath" -ForegroundColor Gray
    }
}

# Upload to Google Cloud Storage
Write-Host "☁️ Uploading to Google Cloud Storage..." -ForegroundColor Yellow
gsutil -m cp -r scin_dataset/raw/* gs://$bucketName/scin_dataset/

# Create metadata file
Write-Host "📝 Creating metadata..." -ForegroundColor Yellow
$metadata = @{
    dataset_info = @{
        name = "SCIN Dataset for Shine Skincare App"
        version = "1.0"
        description = "Dermatological images for skin condition analysis"
        total_images = 30
        conditions = $conditions
        created_date = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    }
    storage_info = @{
        bucket = $bucketName
        project = "shine-466907"
        location = "us-central1"
    }
}

$metadata | ConvertTo-Json -Depth 10 | Out-File -FilePath "scin_dataset/metadata.json" -Encoding UTF8
gsutil cp scin_dataset/metadata.json gs://$bucketName/scin_dataset/

Write-Host "✅ Google Cloud Storage setup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "   Bucket: gs://$bucketName" -ForegroundColor White
Write-Host "   Project: shine-466907" -ForegroundColor White
Write-Host "   Images: 30 placeholder images" -ForegroundColor White
Write-Host "   Conditions: $($conditions -join ', ')" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Run: python scin_preprocessor.py" -ForegroundColor White
Write-Host "   2. Test: python test_real_analysis.py" -ForegroundColor White
Write-Host ""
Write-Host "💡 To add real images:" -ForegroundColor Yellow
Write-Host "   - Replace placeholder files with real dermatological images" -ForegroundColor White
Write-Host "   - Upload to gs://$bucketName/scin_dataset/" -ForegroundColor White
Write-Host "   - Run the preprocessor again" -ForegroundColor White 