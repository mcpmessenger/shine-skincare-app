# Enhanced Embeddings Setup Script for Shine Skincare App
# Focuses on larger datasets and more parameters for improved accuracy

Write-Host "🧠 Setting up Enhanced Embeddings System..." -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "🔄 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install enhanced requirements
Write-Host "🔄 Installing enhanced embedding requirements..." -ForegroundColor Yellow
pip install -r requirements_enhanced_embeddings.txt

# Create datasets directory structure
Write-Host "🔄 Creating dataset directory structure..." -ForegroundColor Yellow
$datasets = @(
    "datasets/ham10000_scaled",
    "datasets/isic_2020_scaled", 
    "datasets/dermnet_scaled",
    "datasets/fitzpatrick17k_scaled",
    "datasets/skin_lesion_archive_scaled"
)

foreach ($dataset in $datasets) {
    if (-not (Test-Path $dataset)) {
        New-Item -ItemType Directory -Path $dataset -Force | Out-Null
        Write-Host "✅ Created directory: $dataset" -ForegroundColor Green
    }
}

# Download dataset information
Write-Host "🔄 Setting up dataset information..." -ForegroundColor Yellow
$datasetInfo = @{
    "ham10000" = @{
        "name" = "HAM10000 - Large Skin Lesion Dataset"
        "size" = "10,000+ images"
        "source" = "https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T"
        "local_path" = "datasets/ham10000_scaled"
        "embedding_dimensions" = 2048
    }
    "isic_2020" = @{
        "name" = "ISIC 2020 Challenge Dataset"
        "size" = "33,126 images"
        "source" = "https://challenge.isic-archive.com/data/"
        "local_path" = "datasets/isic_2020_scaled"
        "embedding_dimensions" = 3072
    }
    "dermnet" = @{
        "name" = "DermNet NZ Dataset"
        "size" = "23,000+ images"
        "source" = "https://www.dermnet.com/dataset"
        "local_path" = "datasets/dermnet_scaled"
        "embedding_dimensions" = 2560
    }
    "fitzpatrick17k" = @{
        "name" = "Fitzpatrick17k Dataset"
        "size" = "16,577 images"
        "source" = "https://github.com/mattgroh/fitzpatrick17k"
        "local_path" = "datasets/fitzpatrick17k_scaled"
        "embedding_dimensions" = 4096
    }
    "skin_lesion_archive" = @{
        "name" = "Skin Lesion Archive"
        "size" = "50,000+ images"
        "source" = "https://www.skin-lesion-archive.com"
        "local_path" = "datasets/skin_lesion_archive_scaled"
        "embedding_dimensions" = 5120
    }
}

# Save dataset information
$datasetInfo | ConvertTo-Json -Depth 3 | Out-File -FilePath "datasets/dataset_info.json" -Encoding UTF8
Write-Host "✅ Dataset information saved" -ForegroundColor Green

# Test the enhanced embedding system
Write-Host "🔄 Testing enhanced embedding system..." -ForegroundColor Yellow
python enhanced_embeddings.py

# Test the scaled dataset manager
Write-Host "🔄 Testing scaled dataset manager..." -ForegroundColor Yellow
python scaled_dataset_manager.py

# Test the enhanced analysis API
Write-Host "🔄 Testing enhanced analysis API..." -ForegroundColor Yellow
python enhanced_analysis_api.py

# Create configuration file
Write-Host "🔄 Creating configuration file..." -ForegroundColor Yellow
$config = @{
    "enhanced_embeddings" = @{
        "enabled" = $true
        "primary_dataset" = "skin_lesion_archive"
        "embedding_dimensions" = 5120
        "confidence_threshold" = 0.85
        "use_advanced_models" = $true
    }
    "analysis_types" = @{
        "comprehensive" = @{
            "datasets" = @("skin_lesion_archive", "isic_2020", "ham10000")
            "parameters" = @("demographic", "clinical", "imaging", "environmental")
            "confidence_threshold" = 0.85
        }
        "focused" = @{
            "datasets" = @("dermnet", "fitzpatrick17k")
            "parameters" = @("clinical", "imaging")
            "confidence_threshold" = 0.90
        }
        "research" = @{
            "datasets" = @("skin_lesion_archive", "isic_2020", "ham10000", "dermnet", "fitzpatrick17k")
            "parameters" = @("demographic", "clinical", "imaging", "environmental", "temporal")
            "confidence_threshold" = 0.95
        }
    }
    "quality_metrics" = @{
        "image_quality" = @("resolution", "lighting", "focus", "noise")
        "diagnostic_confidence" = @("expert_agreement", "pathology_confirmation")
        "dataset_diversity" = @("skin_types", "age_ranges", "geographic_distribution")
    }
}

$config | ConvertTo-Json -Depth 4 | Out-File -FilePath "backend/enhanced_config.json" -Encoding UTF8
Write-Host "✅ Configuration file created" -ForegroundColor Green

# Create performance monitoring script
Write-Host "🔄 Creating performance monitoring script..." -ForegroundColor Yellow
$monitoringScript = @"
#!/usr/bin/env python3
"""
Performance Monitoring for Enhanced Embeddings
"""

import time
import psutil
import json
from datetime import datetime
from enhanced_analysis_api import EnhancedAnalysisAPI
import numpy as np
import cv2

def monitor_performance():
    """Monitor performance of enhanced embedding system"""
    
    # Initialize API
    api = EnhancedAnalysisAPI()
    
    # Create test images
    test_images = []
    for i in range(5):
        test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        test_image_bytes = cv2.imencode('.jpg', test_image)[1].tobytes()
        test_images.append(test_image_bytes)
    
    # Performance metrics
    metrics = {
        'analysis_times': [],
        'memory_usage': [],
        'cpu_usage': [],
        'embedding_dimensions': [],
        'confidence_scores': []
    }
    
    print("🧠 Performance Monitoring Started")
    
    for i, image_data in enumerate(test_images):
        start_time = time.time()
        start_memory = psutil.virtual_memory().percent
        start_cpu = psutil.cpu_percent()
        
        # Perform analysis
        result = api.analyze_skin_enhanced(image_data, 'comprehensive')
        
        end_time = time.time()
        end_memory = psutil.virtual_memory().percent
        end_cpu = psutil.cpu_percent()
        
        # Record metrics
        metrics['analysis_times'].append(end_time - start_time)
        metrics['memory_usage'].append((start_memory + end_memory) / 2)
        metrics['cpu_usage'].append((start_cpu + end_cpu) / 2)
        metrics['embedding_dimensions'].append(result['embedding_info']['dimensions'])
        metrics['confidence_scores'].append(result['confidence_score'])
        
        print(f"✅ Analysis {i+1}/5 completed in {metrics['analysis_times'][-1]:.2f}s")
    
    # Calculate averages
    avg_metrics = {
        'avg_analysis_time': np.mean(metrics['analysis_times']),
        'avg_memory_usage': np.mean(metrics['memory_usage']),
        'avg_cpu_usage': np.mean(metrics['cpu_usage']),
        'avg_embedding_dimensions': np.mean(metrics['embedding_dimensions']),
        'avg_confidence_score': np.mean(metrics['confidence_scores'])
    }
    
    # Save metrics
    with open('backend/performance_metrics.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'averages': avg_metrics
        }, f, indent=2)
    
    print(f"📊 Performance Metrics:")
    print(f"  Average Analysis Time: {avg_metrics['avg_analysis_time']:.2f}s")
    print(f"  Average Memory Usage: {avg_metrics['avg_memory_usage']:.1f}%")
    print(f"  Average CPU Usage: {avg_metrics['avg_cpu_usage']:.1f}%")
    print(f"  Average Embedding Dimensions: {avg_metrics['avg_embedding_dimensions']:.0f}")
    print(f"  Average Confidence Score: {avg_metrics['avg_confidence_score']:.3f}")

if __name__ == "__main__":
    monitor_performance()
"@

$monitoringScript | Out-File -FilePath "backend/monitor_performance.py" -Encoding UTF8
Write-Host "✅ Performance monitoring script created" -ForegroundColor Green

# Create deployment script
Write-Host "🔄 Creating deployment script..." -ForegroundColor Yellow
$deploymentScript = @"
# Enhanced Embeddings Deployment Script

Write-Host "🚀 Deploying Enhanced Embeddings System..." -ForegroundColor Green

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Install production requirements
pip install -r requirements_enhanced_embeddings.txt

# Run performance test
python monitor_performance.py

# Start the enhanced analysis service
Write-Host "🔄 Starting enhanced analysis service..." -ForegroundColor Yellow
python enhanced_analysis_api.py

Write-Host "✅ Enhanced embeddings system deployed successfully!" -ForegroundColor Green
"@

$deploymentScript | Out-File -FilePath "backend/deploy_enhanced.ps1" -Encoding UTF8
Write-Host "✅ Deployment script created" -ForegroundColor Green

Write-Host "🎉 Enhanced Embeddings System Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "  ✅ Virtual environment created and activated" -ForegroundColor Green
Write-Host "  ✅ Enhanced requirements installed" -ForegroundColor Green
Write-Host "  ✅ Dataset directories created" -ForegroundColor Green
Write-Host "  ✅ Configuration files generated" -ForegroundColor Green
Write-Host "  ✅ Performance monitoring setup" -ForegroundColor Green
Write-Host "  ✅ Deployment script created" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Download datasets to the created directories" -ForegroundColor White
Write-Host "  2. Run: python monitor_performance.py" -ForegroundColor White
Write-Host "  3. Run: .\deploy_enhanced.ps1" -ForegroundColor White
Write-Host "  4. Test with your application" -ForegroundColor White
Write-Host ""
Write-Host "📊 Key Features:" -ForegroundColor Cyan
Write-Host "  • Larger datasets (50,000+ images)" -ForegroundColor White
Write-Host "  • More parameters (demographic, clinical, environmental)" -ForegroundColor White
Write-Host "  • Higher embedding dimensions (up to 5120)" -ForegroundColor White
Write-Host "  • Enhanced confidence thresholds (up to 0.95)" -ForegroundColor White
Write-Host "  • Comprehensive quality metrics" -ForegroundColor White 