#!/usr/bin/env python3
"""
🎨 SIMPLE SKIN CONDITION GENERATOR
Creates basic skin condition variations from UTKFace healthy faces
Focus: Get started with training while fixing data access
"""

import os
import json
import logging
import numpy as np
import cv2
from pathlib import Path
import random
from PIL import Image, ImageEnhance, ImageFilter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleSkinConditionGenerator:
    """
    Generates simple skin condition variations from UTKFace healthy faces
    """
    
    def __init__(self):
        self.base_dir = Path('data/utkface/utkface_aligned_cropped/crop_part1')
        self.output_dir = Path('data/simple_skin_conditions')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Simple skin conditions we can realistically simulate
        self.skin_conditions = {
            'healthy': {
                'description': 'Clear, healthy skin (original)',
                'augmentation': 'none',
                'target_count': 500
            },
            'acne': {
                'description': 'Simple acne simulation',
                'augmentation': 'red_spots',
                'target_count': 400
            },
            'redness': {
                'description': 'General facial redness',
                'augmentation': 'redness_enhancement',
                'target_count': 300
            },
            'texture': {
                'description': 'Rough skin texture',
                'augmentation': 'texture_roughness',
                'target_count': 300
            }
        }
        
        logger.info("🎨 SIMPLE SKIN CONDITION GENERATOR INITIALIZED!")
        logger.info(f"📁 Source: {self.base_dir}")
        logger.info(f"📁 Output: {self.output_dir}")
        logger.info(f"🎯 Classes: {len(self.skin_conditions)} basic conditions")
    
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
        """Simulate simple acne with red spots"""
        img_array = np.array(image)
        height, width = img_array.shape[:2]
        
        # Add 2-5 red spots
        for _ in range(random.randint(2, 5)):
            x = random.randint(width//4, 3*width//4)
            y = random.randint(height//4, 3*height//4)
            radius = random.randint(2, 4)
            
            # Red color
            color = [random.randint(200, 255), random.randint(50, 100), random.randint(50, 100)]
            
            # Draw spot
            cv2.circle(img_array, (x, y), radius, color, -1)
        
        return Image.fromarray(img_array)
    
    def simulate_redness(self, image):
        """Simulate general facial redness"""
        # Enhance red channel
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.2)
        
        # Add slight redness to cheeks
        img_array = np.array(image)
        height, width = img_array.shape[:2]
        
        # Create cheek regions
        left_cheek = img_array[height//3:2*height//3, width//6:width//3]
        right_cheek = img_array[height//3:2*height//3, 2*width//3:5*width//6]
        
        # Enhance redness in cheeks
        left_cheek[:, :, 0] = np.clip(left_cheek[:, :, 0] * 1.3, 0, 255)
        right_cheek[:, :, 0] = np.clip(right_cheek[:, :, 0] * 1.3, 0, 255)
        
        return Image.fromarray(img_array)
    
    def simulate_texture(self, image):
        """Simulate rough skin texture"""
        # Add texture roughness
        image = image.filter(ImageFilter.EDGE_ENHANCE)
        
        # Add some noise
        img_array = np.array(image)
        noise = np.random.normal(0, 10, img_array.shape).astype(np.uint8)
        img_array = np.clip(img_array + noise, 0, 255)
        
        return Image.fromarray(img_array)
    
    def apply_skin_condition(self, image, condition):
        """Apply specific skin condition simulation"""
        if condition == 'healthy':
            return image  # No changes
        elif condition == 'acne':
            return self.simulate_acne(image)
        elif condition == 'redness':
            return self.simulate_redness(image)
        elif condition == 'texture':
            return self.simulate_texture(image)
        else:
            return image
    
    def generate_simple_dataset(self):
        """Generate the simple skin condition dataset"""
        logger.info("🚀 STARTING SIMPLE SKIN CONDITION DATASET GENERATION!")
        
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
            if i % 50 == 0:
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
            'name': 'Simple Skin Conditions Dataset',
            'description': 'Generated from UTKFace using basic augmentation',
            'classes': list(self.skin_conditions.keys()),
            'total_images': sum(self.skin_conditions[c]['target_count'] for c in self.skin_conditions.keys()),
            'generation_date': str(Path().cwd()),
            'source': 'UTKFace + Simple Augmentation',
            'usage': 'Basic training data for skin condition classification',
            'note': 'This is a simplified dataset to get started while fixing data access issues'
        }
        
        info_path = self.output_dir / 'dataset_info.json'
        with open(info_path, 'w') as f:
            json.dump(info, f, indent=2)
        
        logger.info(f"📄 Dataset info saved to: {info_path}")
        return info


def main():
    """Main execution function"""
    logger.info("🎨 SIMPLE SKIN CONDITION GENERATOR")
    logger.info("🎯 Focus: Basic skin conditions to get started with training")
    logger.info("="*70)
    
    generator = SimpleSkinConditionGenerator()
    
    # Generate dataset
    if generator.generate_simple_dataset():
        logger.info("🎉 SIMPLE DATASET GENERATION COMPLETE!")
        
        # Create dataset info
        info = generator.create_dataset_info()
        
        logger.info("🚀 Ready for basic Hare Run V6 training!")
        logger.info(f"📊 Total images: {info['total_images']}")
        logger.info(f"🏷️ Classes: {', '.join(info['classes'])}")
        logger.info("💡 Note: This is a simplified dataset to get started")
        logger.info("🔧 Next: Fix Kaggle access for real facial skin disease images")
    else:
        logger.error("❌ SIMPLE DATASET GENERATION FAILED!")
    
    logger.info("="*70)


if __name__ == "__main__":
    main()
