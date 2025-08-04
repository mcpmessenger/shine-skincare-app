#!/usr/bin/env python3
"""
Embed skin condition images using real database integration
"""

import os
import sys
import logging
import numpy as np
import json
import cv2
from pathlib import Path
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from real_database_integration import RealDatabaseIntegration
from enhanced_embeddings import EnhancedEmbeddingSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def embed_skin_conditions():
    """Create embeddings for skin condition images"""
    try:
        logger.info("🔄 Creating skin condition embeddings...")
        
        # Initialize systems
        db_integration = RealDatabaseIntegration()
        embedding_system = EnhancedEmbeddingSystem()
        
        # Get the condition databases from the database integration
        condition_databases = db_integration.condition_databases
        logger.info(f"📊 Found {len(condition_databases)} conditions: {list(condition_databases.keys())}")
        
        condition_embeddings = {}
        
        for condition_name, images in condition_databases.items():
            logger.info(f"🔄 Processing condition: {condition_name}")
            
            if not images:
                logger.warning(f"⚠️ No images found for condition: {condition_name}")
                continue
            
            # Generate embeddings for this condition
            embeddings = []
            valid_images = []
            
            # Process up to 20 images per condition for speed
            for i, img_array in enumerate(images[:20]):
                try:
                    logger.info(f"  Processing image {i+1}/{min(len(images), 20)}")
                    
                    # Convert numpy array to temporary file for embedding
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                        # Save the image array to temporary file
                        cv2.imwrite(tmp_file.name, img_array)
                        tmp_file_path = tmp_file.name
                    
                    # Generate embedding from temporary file
                    with open(tmp_file_path, 'rb') as f:
                        image_data = f.read()
                    embedding_result = embedding_system.generate_enhanced_embeddings(image_data)
                    embedding = embedding_result.get('combined', None)
                    
                    # Clean up temporary file
                    os.unlink(tmp_file_path)
                    
                    if embedding is not None:
                        embeddings.append(embedding)
                        valid_images.append(f"image_{i+1}")
                        logger.info(f"  ✅ Successfully embedded")
                    else:
                        logger.warning(f"  ⚠️ Failed to generate embedding")
                        
                except Exception as e:
                    logger.warning(f"  ⚠️ Failed to process image {i+1}: {e}")
                    continue
            
            if embeddings:
                # Average embeddings for this condition
                avg_embedding = np.mean(embeddings, axis=0)
                condition_embeddings[condition_name] = {
                    'embedding': avg_embedding,
                    'image_count': len(embeddings),
                    'image_paths': valid_images,
                    'embedding_dimensions': len(avg_embedding)
                }
                logger.info(f"✅ Created embedding for {condition_name} ({len(embeddings)} images)")
            else:
                logger.warning(f"⚠️ No valid embeddings for condition: {condition_name}")
        
        if not condition_embeddings:
            logger.error("❌ No condition embeddings created")
            return False
        
        # Save condition embeddings
        embeddings_path = Path("data/condition_embeddings.npy")
        np.save(embeddings_path, condition_embeddings)
        logger.info(f"✅ Saved condition embeddings to {embeddings_path}")
        
        # Create summary
        create_condition_summary(condition_embeddings)
        
        logger.info("✅ Skin condition embeddings created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create condition embeddings: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def create_condition_summary(embeddings: dict):
    """Create a summary report of the condition embeddings"""
    try:
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_conditions': len(embeddings),
            'conditions': list(embeddings.keys()),
            'embedding_info': {
                'dimensions': len(list(embeddings.values())[0]['embedding']) if embeddings else 0,
                'embedding_type': 'Enhanced_Multi_Model'
            },
            'condition_details': {}
        }
        
        # Add details for each condition
        for condition, data in embeddings.items():
            summary['condition_details'][condition] = {
                'image_count': data['image_count'],
                'embedding_dimensions': data['embedding_dimensions']
            }
        
        # Save summary
        summary_path = Path("data/condition_embeddings_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"✅ Saved condition embeddings summary to {summary_path}")
        
        # Print summary
        print("\n" + "="*50)
        print("SKIN CONDITION EMBEDDINGS SUMMARY")
        print("="*50)
        print(f"Total conditions: {summary['total_conditions']}")
        print(f"Conditions: {summary['conditions']}")
        print(f"Embedding dimensions: {summary['embedding_info']['dimensions']}")
        print("\nCondition details:")
        for condition, details in summary['condition_details'].items():
            print(f"  {condition}: {details['image_count']} images")
        print("="*50)
        
    except Exception as e:
        logger.error(f"❌ Failed to create condition summary: {e}")

def verify_condition_embeddings():
    """Verify that condition embeddings are working correctly"""
    try:
        logger.info("🔄 Verifying condition embeddings...")
        
        # Load embeddings
        embeddings_path = Path("data/condition_embeddings.npy")
        if not embeddings_path.exists():
            logger.error("❌ Condition embeddings file not found")
            return False
        
        embeddings = np.load(embeddings_path, allow_pickle=True).item()
        
        if not embeddings:
            logger.error("❌ No condition embeddings loaded")
            return False
        
        logger.info(f"✅ Loaded {len(embeddings)} condition embeddings")
        
        # Test similarity search
        embedding_system = EnhancedEmbeddingSystem()
        
        # Test with a sample image from the database
        db_integration = RealDatabaseIntegration()
        test_images = db_integration.condition_databases.get('acne', [])
        
        if test_images:
            test_img_array = test_images[0]
            # Convert numpy array to temporary file for testing
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                cv2.imwrite(tmp_file.name, test_img_array)
                test_image_path = tmp_file.name
                logger.info(f"Testing with: {os.path.basename(test_image_path)}")
                with open(test_image_path, 'rb') as f:
                    test_image_data = f.read()
                test_embedding_result = embedding_system.generate_enhanced_embeddings(test_image_data)
                test_embedding = test_embedding_result.get('combined', None)
                
                # Clean up temporary file
                os.unlink(test_image_path)
                
                if test_embedding is not None:
                    # Find most similar condition
                    similarities = {}
                    for condition, data in embeddings.items():
                        similarity = np.dot(test_embedding, data['embedding']) / (
                            np.linalg.norm(test_embedding) * np.linalg.norm(data['embedding'])
                        )
                        similarities[condition] = similarity
                    
                    # Sort by similarity
                    sorted_similarities = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
                    logger.info("Similarity scores:")
                    for condition, score in sorted_similarities:
                        logger.info(f"  {condition}: {score:.3f}")
                    
                    best_match = sorted_similarities[0]
                    logger.info(f"✅ Best match: {best_match[0]} (similarity: {best_match[1]:.3f})")
        
        logger.info("✅ Condition embeddings verification completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Condition embeddings verification failed: {e}")
        return False

def main():
    """Main function to embed skin conditions"""
    print("🔄 Skin Condition Embeddings Creation")
    print("="*50)
    
    # Check if embeddings already exist
    embeddings_path = Path("data/condition_embeddings.npy")
    if embeddings_path.exists():
        print("📋 Condition embeddings already exist")
        response = input("Do you want to recreate them? (y/N): ")
        if response.lower() != 'y':
            print("✅ Using existing embeddings")
            verify_condition_embeddings()
            return
    
    # Create embeddings
    if embed_skin_conditions():
        print("✅ Skin condition embeddings created successfully!")
        
        # Verify embeddings
        print("\n🔄 Verifying embeddings...")
        if verify_condition_embeddings():
            print("✅ All condition embeddings verified successfully!")
        else:
            print("⚠️ Some condition embedding verification issues found")
    else:
        print("❌ Skin condition embeddings creation failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 