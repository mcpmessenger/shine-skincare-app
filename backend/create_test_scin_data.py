"""
Create simulated SCIN data for testing Operation Right Brain
"""

import json
import numpy as np
from datetime import datetime

def create_simulated_scin_data():
    """Create simulated SCIN dataset for testing"""
    
    # Simulate different skin conditions
    conditions = [
        {
            'condition': 'acne',
            'description': 'Common skin condition characterized by pimples and inflammation',
            'recommendations': [
                'Gentle cleanser with salicylic acid',
                'Non-comedogenic moisturizer',
                'Avoid touching face frequently',
                'Consider benzoyl peroxide treatment'
            ]
        },
        {
            'condition': 'inflammation',
            'description': 'Skin inflammation causing redness and irritation',
            'recommendations': [
                'Use gentle, fragrance-free products',
                'Avoid harsh scrubs and exfoliants',
                'Apply cool compress to reduce redness',
                'Consider anti-inflammatory treatments'
            ]
        },
        {
            'condition': 'hyperpigmentation',
            'description': 'Dark patches on skin caused by excess melanin production',
            'recommendations': [
                'Use vitamin C serum for brightening',
                'Apply sunscreen daily',
                'Consider hydroquinone treatment',
                'Avoid picking at skin'
            ]
        },
        {
            'condition': 'aging',
            'description': 'Signs of aging including fine lines and wrinkles',
            'recommendations': [
                'Use retinol products',
                'Apply sunscreen daily',
                'Consider collagen-boosting treatments',
                'Maintain consistent skincare routine'
            ]
        }
    ]
    
    # Generate simulated data
    simulated_data = []
    
    for i, condition in enumerate(conditions):
        # Create multiple variations for each condition
        for j in range(3):  # 3 variations per condition
            # Generate random embedding (768 dimensions)
            embedding = np.random.rand(768).tolist()
            
            # Create face data
            face_data = {
                'face_detected': True,
                'confidence': 0.85 + (j * 0.05),
                'skin_characteristics': {
                    'texture': 'smooth' if j % 2 == 0 else 'normal',
                    'tone': 'even' if j % 2 == 0 else 'normal',
                    'conditions': [condition['condition']]
                }
            }
            
            # Create processed record
            record = {
                'image_path': f'scin_dataset/{condition["condition"]}_{j+1}.jpg',
                'embedding': embedding,
                'face_data': face_data,
                'processed_at': datetime.utcnow().isoformat(),
                'condition_info': condition
            }
            
            simulated_data.append(record)
    
    # Save to file
    with open('scin_processed_data.json', 'w') as f:
        json.dump(simulated_data, f, indent=2)
    
    print(f"✅ Created simulated SCIN data with {len(simulated_data)} records")
    print("📁 Saved to: scin_processed_data.json")
    
    return simulated_data

if __name__ == "__main__":
    create_simulated_scin_data() 