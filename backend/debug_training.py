#!/usr/bin/env python3
"""
Debug script for Hare Run V6 training
"""

from hare_run_v6_facial_training import HareRunV6FacialTrainer

def main():
    print("🐇 Debugging Hare Run V6 Training...")
    
    # Initialize trainer
    trainer = HareRunV6FacialTrainer()
    
    # Check config
    print("Config keys:", list(trainer.config.keys()))
    print("Dataset keys:", list(trainer.config['dataset'].keys()))
    
    # Check specific values
    print("Dataset path:", trainer.config['dataset']['path'])
    print("CSV file:", trainer.config['dataset']['csv_file'])
    
    # Test dataset loading
    try:
        print("Testing dataset loading...")
        images, labels = trainer.load_facial_dataset()
        print(f"✅ Successfully loaded {len(images)} images")
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
