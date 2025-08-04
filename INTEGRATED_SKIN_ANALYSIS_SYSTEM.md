# Integrated Skin Analysis System

## Overview

The Integrated Skin Analysis System addresses the key issues identified in the original analysis:

1. **HAM10000 is for skin lesions, not faces** - Removed from facial analysis
2. **Missing healthy face examples** - Now uses UTKFace for healthy baselines
3. **Need proper integration** - Combines UTKFace healthy baselines with facial conditions dataset
4. **Need normalization** - Compares against demographic-specific healthy baselines

## System Architecture

### Core Components

1. **IntegratedSkinAnalysis** (`integrated_skin_analysis.py`)
   - Main orchestrator that combines all analysis systems
   - Handles dataset loading and embedding generation
   - Performs normalized analysis using healthy baselines

2. **Enhanced Embedding System** (`enhanced_embeddings.py`)
   - Multi-model embedding generation (CLIP, DINO, custom)
   - 2304-dimensional combined embeddings
   - Quality assessment and similarity calculations

3. **UTKFace Integration** (`utkface_integration.py`)
   - Demographic-specific healthy skin baselines
   - Age, gender, and ethnicity-aware analysis
   - ResNet50-based embedding generation

4. **Facial Conditions Dataset** (`real_database_integration.py`)
   - 492 images across 6 conditions: acne, actinic_keratosis, basal_cell_carcinoma, eczema, healthy, rosacea
   - Condition-specific embedding matching
   - Severity assessment and recommendations

## Key Features

### 1. Demographic Normalization
- **UTKFace Healthy Baselines**: Demographic-specific healthy skin references
- **Age Groups**: 5-80 years (filtered for skin analysis relevance)
- **Gender**: Male (0) / Female (1)
- **Ethnicity**: White (0), Black (1), Asian (2), Indian (3), Others (4)

### 2. Condition Matching
- **6 Facial Conditions**: acne, actinic_keratosis, basal_cell_carcinoma, eczema, healthy, rosacea
- **Similarity Scoring**: Cosine similarity against condition embeddings
- **Severity Assessment**: mild, moderate, severe based on similarity scores

### 3. Normalized Analysis
- **Healthy Baseline Comparison**: Compares user image against demographic-matched healthy baseline
- **Condition Severity Adjustment**: Reduces severity if very similar to healthy baseline
- **Overall Health Score**: Weighted combination of condition analysis and healthy baseline comparison

## API Endpoints

### 1. Normalized Analysis (Recommended)
```
POST /api/v3/skin/analyze-normalized
```
**Payload:**
```json
{
  "image": "base64_encoded_image",
  "age": 25,           // optional: 0-120
  "gender": 0,         // optional: 0=male, 1=female
  "ethnicity": 0       // optional: 0-4 (white, black, asian, indian, others)
}
```

**Response:**
```json
{
  "analysis_timestamp": "2024-01-01T12:00:00",
  "basic_analysis": { /* enhanced_analysis_algorithms results */ },
  "similar_conditions": [ /* top 10 similar conditions */ ],
  "demographic_analysis": {
    "baseline_similarity": 0.85,
    "health_score": 0.92,
    "deviation_from_healthy": 0.15,
    "is_healthy": true
  },
  "normalized_results": {
    "conditions_detected": [
      {
        "condition": "acne",
        "severity": "mild",
        "confidence": 0.75,
        "similarity_score": 0.68
      }
    ],
    "overall_assessment": "mild_concerns",
    "recommendations": [ /* personalized recommendations */ ]
  },
  "overall_health_score": 0.82,
  "demographics_used": { "age": 25, "gender": 0, "ethnicity": 0 },
  "healthy_baseline_available": true
}
```

### 2. Basic Analysis (No Demographics)
```
POST /api/v3/skin/analyze-basic
```
**Payload:**
```json
{
  "image": "base64_encoded_image"
}
```

### 3. System Status
```
GET /api/v3/skin/status
```

### 4. Face Detection
```
POST /api/v3/skin/face-detect
```

## Dataset Integration

### UTKFace Healthy Baselines
- **Location**: `data/utkface/demographic_baselines.npy`
- **Format**: Dictionary with demographic keys (e.g., "25_0_0" for age=25, gender=0, ethnicity=0)
- **Embedding Dimensions**: 2048 (ResNet50 GlobalAveragePooling)
- **Setup**: Run `setup_utkface_baselines.py` to create baselines

### Facial Conditions Dataset
- **Location**: `data/facial_skin_diseases/`
- **Images**: 492 total across 6 conditions
- **Embeddings**: `condition_embeddings.npy` (auto-generated)
- **Metadata**: `condition_metadata.csv`

## Analysis Flow

### 1. Image Processing
```python
# Convert image bytes to array
img_array = self._bytes_to_array(image_data)

# Basic skin analysis
basic_analysis = self.skin_analyzer.analyze_skin_conditions(img_array)

# Generate enhanced embeddings
embedding_result = self.embedding_system.generate_enhanced_embeddings(image_data)
user_embedding = embedding_result.get('combined', [])
```

### 2. Condition Matching
```python
# Find similar conditions in database
similar_conditions = self._find_similar_conditions(user_embedding)

# Filter by similarity threshold
detected_conditions = {}
for condition_data in similar_conditions:
    if condition_data['similarity_score'] > self.analysis_config['condition_threshold']:
        # Add to detected conditions
```

### 3. Demographic Baseline Comparison
```python
# Get healthy baseline for demographics
healthy_baseline = self.utkface_integration.get_relevant_baseline(age, gender, ethnicity)

# Compare against healthy baseline
demographic_analysis = self._analyze_vs_healthy_baseline(user_embedding, healthy_baseline)
```

### 4. Normalization
```python
# Adjust severity based on healthy baseline
if healthy_baseline is not None and condition != 'healthy':
    baseline_similarity = demographic_analysis.get('baseline_similarity', 0.5)
    if baseline_similarity > 0.8:
        avg_similarity *= 0.7  # Reduce severity
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements_enhanced.txt
```

### 2. Download UTKFace Dataset
```bash
# Download UTKFace dataset to data/utkface/raw_images/
# Extract images with demographic information in filenames
```

### 3. Setup UTKFace Baselines
```bash
cd backend
python setup_utkface_baselines.py
```

### 4. Generate Condition Embeddings
```bash
# The system will auto-generate embeddings on first run
# Or manually trigger:
python integrated_skin_analysis.py
```

### 5. Start the API
```bash
python enhanced_app.py
```

## Configuration

### Analysis Parameters
```python
analysis_config = {
    'healthy_threshold': 0.7,      # Similarity threshold for healthy skin
    'condition_threshold': 0.6,    # Similarity threshold for condition detection
    'demographic_weight': 0.3,     # Weight for demographic matching
    'condition_weight': 0.7,       # Weight for condition matching
    'normalization_enabled': True
}
```

### Severity Thresholds
```python
# Condition severity based on similarity scores
if max_similarity > 0.85:
    severity = 'severe'
elif max_similarity > 0.7:
    severity = 'moderate'
elif max_similarity > 0.5:
    severity = 'mild'
else:
    severity = 'very_mild'
```

## Benefits of the Integrated System

### 1. **Accurate Normalization**
- Compares against demographic-matched healthy baselines
- Reduces false positives by considering healthy skin variations
- Provides context-aware severity assessment

### 2. **Comprehensive Condition Coverage**
- 6 major facial skin conditions
- 492 high-quality medical images
- Condition-specific similarity matching

### 3. **Demographic Awareness**
- Age-specific healthy skin baselines
- Gender and ethnicity considerations
- Culturally appropriate recommendations

### 4. **Robust Analysis Pipeline**
- Multi-model embedding generation
- Quality assessment and confidence scoring
- Fallback mechanisms for missing data

## Example Usage

### Python Client
```python
import requests
import base64

# Load and encode image
with open("face_image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

# Perform normalized analysis
response = requests.post("http://localhost:8000/api/v3/skin/analyze-normalized", json={
    "image": image_data,
    "age": 25,
    "gender": 0,  # male
    "ethnicity": 0  # white
})

result = response.json()
print(f"Health Score: {result['overall_health_score']}")
print(f"Assessment: {result['normalized_results']['overall_assessment']}")
```

### JavaScript Client
```javascript
// Convert image to base64
const imageFile = document.getElementById('imageInput').files[0];
const reader = new FileReader();
reader.onload = function() {
    const base64Image = reader.result.split(',')[1];
    
    // Perform analysis
    fetch('/api/v3/skin/analyze-normalized', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            image: base64Image,
            age: 25,
            gender: 0,
            ethnicity: 0
        })
    })
    .then(response => response.json())
    .then(result => {
        console.log('Analysis Result:', result);
    });
};
reader.readAsDataURL(imageFile);
```

## Troubleshooting

### Common Issues

1. **UTKFace Baselines Not Found**
   - Run `setup_utkface_baselines.py`
   - Ensure UTKFace dataset is downloaded to `data/utkface/raw_images/`

2. **Condition Embeddings Missing**
   - The system auto-generates embeddings on first run
   - Check `data/facial_skin_diseases/condition_embeddings.npy`

3. **Memory Issues**
   - Reduce batch size in embedding generation
   - Use smaller image sizes for analysis

4. **API Errors**
   - Check all dependencies are installed
   - Verify dataset paths are correct
   - Check logs for specific error messages

## Performance Considerations

### Optimization Tips
- **Image Size**: Resize to 224x224 for optimal performance
- **Batch Processing**: Process multiple images in batches
- **Caching**: Embeddings are cached for repeated analysis
- **Memory**: Monitor memory usage during embedding generation

### Scalability
- **Horizontal Scaling**: Multiple API instances
- **Database**: Consider vector database for large-scale similarity search
- **CDN**: Serve static assets through CDN
- **Load Balancing**: Distribute requests across multiple servers

## Future Enhancements

### Planned Features
1. **Real-time Analysis**: WebSocket support for live camera feeds
2. **Advanced Models**: Integration with state-of-the-art vision models
3. **Multi-language Support**: Internationalization for recommendations
4. **Mobile Optimization**: Lightweight models for mobile devices
5. **Privacy Features**: On-device analysis options

### Dataset Expansion
1. **More Conditions**: Additional skin conditions and variations
2. **Diverse Demographics**: More comprehensive demographic coverage
3. **Temporal Data**: Progression tracking over time
4. **Treatment Data**: Outcome-based recommendations

This integrated system provides a robust, accurate, and scalable solution for skin analysis with proper normalization against healthy baselines and comprehensive condition matching. 