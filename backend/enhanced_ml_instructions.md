
# Enhanced ML Integration Instructions

## 1. Start the Enhanced API Server
```bash
python enhanced_api.py
```

## 2. Test the Enhanced Analysis
```bash
curl -X POST -F "image=@test_image.jpg" http://localhost:5000/api/v4/skin/analyze-enhanced
```

## 3. Check Model Status
```bash
curl http://localhost:5000/api/v4/system/enhanced-status
```

## 4. Integration with Frontend
Update your frontend to use the new endpoint:
- Old: /api/v3/skin/analyze-real
- New: /api/v4/skin/analyze-enhanced

## 5. Model Performance
- Overall Accuracy: 60.2%
- Acne Detection: 63.2% F1-score
- Healthy Detection: 71.4% F1-score
- Rosacea Detection: 68.2% F1-score

## 6. Fallback Mechanism
The system includes automatic fallback to basic analysis if the enhanced model fails.
