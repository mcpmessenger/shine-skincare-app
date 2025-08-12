#!/usr/bin/env python3
"""
🎨 SYNTHETIC FACIAL SKIN CONDITION DATASET GENERATOR
Creates a synthetic dataset for facial skin conditions using UTKFace + augmentation
Focus: Generate realistic facial skin condition variations for training
"""

import os
import json
import logging
import numpy as np
import cv2
from pathlib import Path
import random
from PIL import Image, ImageEnhance, ImageFilter
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # AWS-compatible backend

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SyntheticFacialDatasetGenerator:
    """
    Generates synthetic facial skin condition dataset using UTKFace + augmentation
    """
    
    def __init__(self):
        self.base_dir = Path('data/utkface/utkface_aligned_cropped/crop_part1')
        self.output_dir = Path('data/synthetic_facial_skin_conditions')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Skin condition classes with realistic characteristics
        self.skin_conditions = {
            'healthy': {
                'description': 'Clear, healthy skin',
                'augmentation': 'minimal',
                'target_count': 1000
            },
            'acne': {
                'description': 'Acne and blemishes',
                'augmentation': 'acne_simulation',
                'target_count': 800
            },
            'rosacea': {
                'description': 'Redness and inflammation',
                'augmentation': 'redness_enhancement',
                'target_count': 600
            },
            'eczema': {
                'description': 'Dry, irritated skin patches',
                'augmentation': 'texture_roughness',
                'target_count': 600
            },
            'hyperpigmentation': {
                'description': 'Dark spots and uneven tone',
                'augmentation': 'dark_spot_simulation',
                'target_count': 500
            },
            'hypopigmentation': {
                'description': 'Light spots and vitiligo-like',
                'augmentation': 'light_spot_simulation',
                'target_count': 400
            }
        }
        
        logger.info("🎨 SYNTHETIC FACIAL SKIN CONDITION DATASET GENERATOR INITIALIZED!")
        logger.info(f"📁 Source: {self.base_dir}")
        logger.info(f"📁 Output: {self.output_dir}")
        logger.info(f"🎯 Classes: {len(self.skin_conditions)} skin conditions")
    
    def check_utkface_data(self):
        """Check if UTKFace dataset is available"""
        if not self.base_dir.exists():
            logger.error(f"❌ UTKFace dataset not found at: {self.base_dir}")
            return False
        
        # Count available images
        image_files = list(self.base_dir.glob('*.jpg')) + list(self.base_dir.glob('*.png'))
        logger.info(f"📊 Found {len(image_files)} UTKFace images")
        
        if len(image_files) < 100:
            logger.warning("⚠️ Limited UTKFace images available")
            return False
        
        return True
    
    def create_dataset_structure(self):
        """Create organized dataset structure"""
        logger.info("🏗️ Creating dataset structure...")
        
        # Create main directories
        train_dir = self.output_dir / 'train'
        val_dir = self.output_dir / 'val'
        
        train_dir.mkdir(exist_ok=True)
        val_dir.mkdir(exist_ok=True)
        
        # Create class directories
        for condition in self.skin_conditions.keys():
            (train_dir / condition).mkdir(exist_ok=True)
            (val_dir / condition).mkdir(exist_ok=True)
        
        logger.info("✅ Dataset structure created!")
        return train_dir, val_dir
    
    def simulate_acne(self, image):
        """Simulate acne and blemishes on facial images"""
        # Convert to numpy array
        img_array = np.array(image)
        
        # Create acne-like spots
        height, width = img_array.shape[:2]
        
        # Add random blemishes
        for _ in range(random.randint(3, 8)):
            # Random position
            x = random.randint(width//4, 3*width//4)
            y = random.randint(height//4, 3*height//4)
            
            # Random size
            radius = random.randint(2, 6)
            
            # Random color (reddish)
            color = [random.randint(180, 255), random.randint(100, 150), random.randint(100, 150)]
            
            # Draw blemish
            cv2.circle(img_array, (x, y), radius, color, -1)
        
        return Image.fromarray(img_array)
    
    def simulate_rosacea(self, image):
        """Simulate rosacea (redness and inflammation)"""
        # Enhance red channel
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.3)
        
        # Add redness to cheeks
        img_array = np.array(image)
        height, width = img_array.shape[:2]
        
        # Create cheek regions
        left_cheek = img_array[height//3:2*height//3, width//6:width//3]
        right_cheek = img_array[height//3:2*height//3, 2*width//3:5*width//6]
        
        # Enhance redness in cheeks
        left_cheek[:, :, 0] = np.clip(left_cheek[:, :, 0] * 1.4, 0, 255)
        right_cheek[:, :, 0] = np.clip(right_cheek[:, :, 0] * 1.4, 0, 255)
        
        return Image.fromarray(img_array)
    
    def simulate_eczema(self, image):
        """Simulate eczema (dry, rough patches)"""
        # Add texture roughness
        image = image.filter(ImageFilter.EDGE_ENHANCE)
        
        # Reduce brightness slightly
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(0.9)
        
        # Add some noise for texture
        img_array = np.array(image)
        noise = np.random.normal(0, 15, img_array.shape).astype(np.uint8)
        img_array = np.clip(img_array + noise, 0, 255)
        
        return Image.fromarray(img_array)
    
    def simulate_hyperpigmentation(self, image):
        """Simulate dark spots and uneven tone"""
        img_array = np.array(image)
        height, width = img_array.shape[:2]
        
        # Add dark spots
        for _ in range(random.randint(2, 5)):
            x = random.randint(width//4, 3*width//4)
            y = random.randint(height//4, 3*height//4)
            radius = random.randint(3, 8)
            
            # Dark brown color
            color = [random.randint(50, 100), random.randint(30, 80), random.randint(20, 60)]
            
            # Draw dark spot
            cv2.circle(img_array, (x, y), radius, color, -1)
        
        return Image.fromarray(img_array)
    
    def simulate_hypopigmentation(self, image):
        """Simulate light spots and vitiligo-like conditions"""
        img_array = np.array(image)
        height, width = img_array.shape[:2]
        
        # Add light spots
        for _ in range(random.randint(1, 4)):
            x = random.randint(width//4, 3*width//4)
            y = random.randint(height//4, 3*height//4)
            radius = random.randint(4, 10)
            
            # Light color
            color = [random.randint(200, 255), random.randint(200, 255), random.randint(200, 255)]
            
            # Draw light spot
            cv2.circle(img_array, (x, y), radius, color, -1)
        
        return Image.fromarray(img_array)
    
    def apply_skin_condition(self, image, condition):
        """Apply specific skin condition simulation"""
        if condition == 'healthy':
            return image  # Minimal changes
        elif condition == 'acne':
            return self.simulate_acne(image)
        elif condition == 'rosacea':
            return self.simulate_rosacea(image)
        elif condition == 'eczema':
            return self.simulate_eczema(image)
        elif condition == 'hyperpigmentation':
            return self.simulate_hyperpigmentation(image)
        elif condition == 'hypopigmentation':
            return self.simulate_hypopigmentation(image)
        else:
            return image
    
    def generate_synthetic_dataset(self):
        """Generate the complete synthetic dataset"""
        logger.info("🚀 STARTING SYNTHETIC DATASET GENERATION!")
        
        if not self.check_utkface_data():
            return False
        
        # Create structure
        train_dir, val_dir = self.create_dataset_structure()
        
        # Get available images
        image_files = list(self.base_dir.glob('*.jpg')) + list(self.base_dir.glob('*.png'))
        random.shuffle(image_files)
        
        logger.info(f"📊 Processing {len(image_files)} UTKFace images...")
        
        # Track generated images
        generated_counts = {condition: 0 for condition in self.skin_conditions.keys()}
        
        for i, image_path in enumerate(image_files):
            if i % 100 == 0:
                logger.info(f"🔄 Progress: {i}/{len(image_files)} images processed")
            
            try:
                # Load image
                image = Image.open(image_path)
                
                # Resize to standard size
                image = image.resize((224, 224), Image.Resampling.LANCZOS)
                
                # Generate variations for each condition
                for condition, config in self.skin_conditions.items():
                    if generated_counts[condition] >= config['target_count']:
                        continue
                    
                    # Apply skin condition
                    modified_image = self.apply_skin_condition(image, condition)
                    
                    # Determine train/val split
                    if random.random() < 0.8:  # 80% train, 20% val
                        output_path = train_dir / condition / f"{condition}_{generated_counts[condition]:04d}.jpg"
                    else:
                        output_path = val_dir / condition / f"{condition}_{generated_counts[condition]:04d}.jpg"
                    
                    # Save image
                    modified_image.save(output_path, 'JPEG', quality=95)
                    generated_counts[condition] += 1
                    
                    # Check if we've reached target for this condition
                    if generated_counts[condition] >= config['target_count']:
                        logger.info(f"✅ {condition}: {generated_counts[condition]} images generated")
                
                # Check if all conditions are complete
                if all(count >= config['target_count'] for condition, config in self.skin_conditions.items()):
                    logger.info("🎉 All conditions reached target counts!")
                    break
                    
            except Exception as e:
                logger.warning(f"⚠️ Error processing {image_path}: {e}")
                continue
        
        # Final summary
        logger.info("🎯 FINAL GENERATION SUMMARY:")
        for condition, count in generated_counts.items():
            target = self.skin_conditions[condition]['target_count']
            logger.info(f"  {condition}: {count}/{target} images")
        
        return True
    
    def create_dataset_info(self):
        """Create dataset information file"""
        info = {
            'name': 'Synthetic Facial Skin Conditions Dataset',
            'description': 'Generated from UTKFace using augmentation techniques',
            'classes': list(self.skin_conditions.keys()),
            'total_images': sum(self.skin_conditions[c]['target_count'] for c in self.skin_conditions.keys()),
            'generation_date': str(Path().cwd()),
            'source': 'UTKFace + Synthetic Augmentation',
            'usage': 'Training data for facial skin condition classification'
        }
        
        info_path = self.output_dir / 'dataset_info.json'
        with open(info_path, 'w') as f:
            json.dump(info, f, indent=2)
        
        logger.info(f"📄 Dataset info saved to: {info_path}")
        return info


def main():
    """Main execution function"""
    logger.info("🎨 SYNTHETIC FACIAL SKIN CONDITION DATASET GENERATOR")
    logger.info("="*70)
    
    generator = SyntheticFacialDatasetGenerator()
    
    # Generate dataset
    if generator.generate_synthetic_dataset():
        logger.info("🎉 SYNTHETIC DATASET GENERATION COMPLETE!")
        
        # Create dataset info
        info = generator.create_dataset_info()
        
        logger.info("🚀 Ready for Hare Run V6 training!")
        logger.info(f"📊 Total images: {info['total_images']}")
        logger.info(f"🏷️ Classes: {', '.join(info['classes'])}")
    else:
        logger.error("❌ SYNTHETIC DATASET GENERATION FAILED!")
    
    logger.info("="*70)


if __name__ == "__main__":
    main()
