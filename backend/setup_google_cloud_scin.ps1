# Google Cloud Storage Setup for SCIN Dataset
# Alternative to Kaggle authentication

Write-Host "🚀 Setting up Google Cloud Storage for SCIN Dataset..." -ForegroundColor Green

# Check if gcloud is installed
try {
    $gcloudVersion = gcloud --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Google Cloud CLI found" -ForegroundColor Green
    } else {
        Write-Host "❌ Google Cloud CLI not found" -ForegroundColor Red
        Write-Host "Please install Google Cloud CLI first: https://cloud.google.com/sdk/docs/install"
        exit 1
    }
} catch {
    Write-Host "❌ Google Cloud CLI not found" -ForegroundColor Red
    Write-Host "Please install Google Cloud CLI first: https://cloud.google.com/sdk/docs/install"
    exit 1
}

# Set project
Write-Host "📋 Setting project to shine-466907..." -ForegroundColor Yellow
gcloud config set project shine-466907

# Create bucket for SCIN dataset
$bucketName = "shine-scin-dataset"
Write-Host "🪣 Creating bucket: $bucketName..." -ForegroundColor Yellow
gsutil mb gs://$bucketName

# Create directory structure in bucket
Write-Host "📁 Creating directory structure..." -ForegroundColor Yellow
gsutil mb gs://$bucketName/scin_dataset/
gsutil mb gs://$bucketName/scin_dataset/acne/
gsutil mb gs://$bucketName/scin_dataset/rosacea/
gsutil mb gs://$bucketName/scin_dataset/melanoma/
gsutil mb gs://$bucketName/scin_dataset/normal/
gsutil mb gs://$bucketName/scin_dataset/basal_cell_carcinoma/
gsutil mb gs://$bucketName/scin_dataset/nevus/

# Download sample images from public sources
Write-Host "📥 Downloading sample dermatological images..." -ForegroundColor Yellow

# Create local temp directory
New-Item -ItemType Directory -Force -Path "temp_download"

# Download sample images (placeholder URLs - in production, these would be real dermatological images)
$sampleImages = @{
    "acne" = @(
        "https://example.com/acne_sample1.jpg",
        "https://example.com/acne_sample2.jpg"
    )
    "rosacea" = @(
        "https://example.com/rosacea_sample1.jpg", 
        "https://example.com/rosacea_sample2.jpg"
    )
    "melanoma" = @(
        "https://example.com/melanoma_sample1.jpg",
        "https://example.com/melanoma_sample2.jpg"
    )
}

# For now, create placeholder images
Write-Host "🔧 Creating placeholder images for testing..." -ForegroundColor Yellow

$conditions = @("acne", "rosacea", "melanoma", "normal", "basal_cell_carcinoma", "nevus")

foreach ($condition in $conditions) {
    $localDir = "temp_download/$condition"
    New-Item -ItemType Directory -Force -Path $localDir
    
    # Create 5 placeholder images per condition
    for ($i = 1; $i -le 5; $i++) {
        $imagePath = "$localDir/${condition}_$($i.ToString('000')).jpg"
        
        # Create a simple colored square as placeholder
        # In production, this would be a real dermatological image
        $color = switch ($condition) {
            "acne" { "#FF6464" }  # Red
            "rosacea" { "#FF9696" }  # Light red
            "melanoma" { "#643232" }  # Dark brown
            "normal" { "#FFDCC8" }  # Skin tone
            "basal_cell_carcinoma" { "#C89664" }  # Tan
            "nevus" { "#966432" }  # Brown
            default { "#C8C8C8" }  # Gray
        }
        
        # Create a simple HTML file that renders as a colored square
        $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>$condition Sample $i</title>
    <style>
        body { margin: 0; padding: 0; background-color: $color; }
        .container { 
            width: 100px; height: 100px; 
            background-color: $color; 
            display: flex; 
            align-items: center; 
            justify-content: center;
            color: black;
            font-family: Arial, sans-serif;
            font-size: 12px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        $condition.ToUpper()<br>Sample $i
    </div>
</body>
</html>
"@
        
        # Save as HTML file (we'll convert this to an image later)
        $htmlPath = $imagePath -replace "\.jpg$", ".html"
        $html | Out-File -FilePath $htmlPath -Encoding UTF8
        
        Write-Host "Created placeholder: $imagePath" -ForegroundColor Gray
    }
}

# Upload to Google Cloud Storage
Write-Host "☁️ Uploading images to Google Cloud Storage..." -ForegroundColor Yellow
gsutil -m cp -r temp_download/* gs://$bucketName/scin_dataset/

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

$metadata | ConvertTo-Json -Depth 10 | Out-File -FilePath "temp_download/metadata.json" -Encoding UTF8
gsutil cp temp_download/metadata.json gs://$bucketName/scin_dataset/

# Clean up
Write-Host "🧹 Cleaning up temporary files..." -ForegroundColor Yellow
Remove-Item -Recurse -Force temp_download

Write-Host "✅ Google Cloud Storage setup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "   Bucket: gs://$bucketName" -ForegroundColor White
Write-Host "   Project: shine-466907" -ForegroundColor White
Write-Host "   Images: 30 placeholder images" -ForegroundColor White
Write-Host "   Conditions: $($conditions -join ', ')" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Update scin_preprocessor.py to use this bucket" -ForegroundColor White
Write-Host "   2. Run: python scin_preprocessor.py" -ForegroundColor White
Write-Host "   3. Test: python test_real_analysis.py" -ForegroundColor White
Write-Host ""
Write-Host "💡 To add real images:" -ForegroundColor Yellow
Write-Host "   - Upload real dermatological images to gs://$bucketName/scin_dataset/" -ForegroundColor White
Write-Host "   - Run the preprocessor again" -ForegroundColor White 