#!/usr/bin/env python3
"""
SCIN Dataset Integration Setup Script

This script sets up the SCIN dataset integration for the Shine skincare app.
It initializes all services, tests connectivity, and provides a guided setup process.
"""

import os
import sys
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.scin_integration_manager import SCINIntegrationManager
from app.services.scin_dataset_service import SCINDatasetService
from app.services.enhanced_image_vectorization_service import EnhancedImageVectorizationService
from app.services.faiss_service import FAISSService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SCINSetupManager:
    """Manager for SCIN integration setup"""
    
    def __init__(self):
        self.integration_manager = None
        self.setup_status = {
            'completed': False,
            'steps_completed': [],
            'errors': [],
            'warnings': []
        }
    
    def run_setup(self) -> bool:
        """Run the complete SCIN integration setup"""
        print("=" * 60)
        print("SCIN Dataset Integration Setup")
        print("=" * 60)
        
        try:
            # Step 1: Check environment
            if not self._check_environment():
                return False
            
            # Step 2: Initialize services
            if not self._initialize_services():
                return False
            
            # Step 3: Test SCIN dataset access
            if not self._test_scin_access():
                return False
            
            # Step 4: Test vectorization service
            if not self._test_vectorization():
                return False
            
            # Step 5: Test FAISS service
            if not self._test_faiss():
                return False
            
            # Step 6: Initialize integration
            if not self._initialize_integration():
                return False
            
            # Step 7: Generate sample index (optional)
            if self._ask_user("Would you like to build a sample similarity index? (y/n): "):
                self._build_sample_index()
            
            # Step 8: Generate setup report
            self._generate_setup_report()
            
            self.setup_status['completed'] = True
            print("\n" + "=" * 60)
            print("SCIN Integration Setup Completed Successfully!")
            print("=" * 60)
            return True
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            self.setup_status['errors'].append(f"Setup failed: {str(e)}")
            return False
    
    def _check_environment(self) -> bool:
        """Check if the environment is properly configured"""
        print("\n1. Checking environment configuration...")
        
        # Check required environment variables
        required_vars = [
            'GOOGLE_APPLICATION_CREDENTIALS',
            'FAISS_INDEX_PATH',
            'FAISS_DIMENSION'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            print("Please set these variables in your .env file")
            self.setup_status['errors'].append(f"Missing environment variables: {missing_vars}")
            return False
        
        print("✅ Environment configuration looks good")
        self.setup_status['steps_completed'].append('environment_check')
        return True
    
    def _initialize_services(self) -> bool:
        """Initialize all required services"""
        print("\n2. Initializing services...")
        
        try:
            # Initialize integration manager
            self.integration_manager = SCINIntegrationManager()
            
            # Load SCIN metadata first to make service available
            print("Loading SCIN dataset metadata...")
            if not self.integration_manager.scin_service.load_metadata():
                print("❌ Failed to load SCIN metadata")
                self.setup_status['errors'].append("Failed to load SCIN metadata")
                return False
            
            # Check service availability
            services_status = self.integration_manager.get_integration_status()
            
            if not services_status['services']['scin_service']:
                print("❌ SCIN service not available")
                self.setup_status['errors'].append("SCIN service not available")
                return False
            
            if not services_status['services']['vectorization_service']:
                print("❌ Vectorization service not available")
                self.setup_status['errors'].append("Vectorization service not available")
                return False
            
            if not services_status['services']['faiss_service']:
                print("⚠️  FAISS service not available (will be created during processing)")
                self.setup_status['warnings'].append("FAISS service not available")
            
            print("✅ Services initialized successfully")
            self.setup_status['steps_completed'].append('services_initialization')
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize services: {e}")
            self.setup_status['errors'].append(f"Service initialization failed: {str(e)}")
            return False
    
    def _test_scin_access(self) -> bool:
        """Test access to SCIN dataset"""
        print("\n3. Testing SCIN dataset access...")
        
        try:
            # Test loading metadata
            if self.integration_manager.scin_service.load_metadata():
                dataset_info = self.integration_manager.scin_service.get_dataset_info()
                print(f"✅ SCIN dataset loaded successfully")
                print(f"   - Total records: {dataset_info['total_records']}")
                print(f"   - Conditions: {dataset_info.get('total_conditions', 'N/A')}")
                
                # Show sample conditions
                if dataset_info.get('condition_distribution'):
                    conditions = list(dataset_info['condition_distribution'].keys())[:5]
                    print(f"   - Sample conditions: {', '.join(conditions)}")
                else:
                    print("   - No condition data available")
                
                self.setup_status['steps_completed'].append('scin_access_test')
                return True
            else:
                print("❌ Failed to load SCIN dataset metadata")
                self.setup_status['errors'].append("Failed to load SCIN dataset metadata")
                return False
                
        except Exception as e:
            print(f"❌ SCIN access test failed: {e}")
            self.setup_status['errors'].append(f"SCIN access test failed: {str(e)}")
            return False
    
    def _test_vectorization(self) -> bool:
        """Test image vectorization service"""
        print("\n4. Testing image vectorization service...")
        
        try:
            # Get model info
            model_info = self.integration_manager.vectorization_service.get_model_info()
            print(f"✅ Vectorization service ready")
            print(f"   - Model: {model_info['model_name']}")
            print(f"   - Feature dimension: {model_info['feature_dimension']}")
            print(f"   - Device: {model_info['device']}")
            
            self.setup_status['steps_completed'].append('vectorization_test')
            return True
            
        except Exception as e:
            print(f"❌ Vectorization test failed: {e}")
            self.setup_status['errors'].append(f"Vectorization test failed: {str(e)}")
            return False
    
    def _test_faiss(self) -> bool:
        """Test FAISS similarity search service"""
        print("\n5. Testing FAISS similarity search service...")
        
        try:
            faiss_info = self.integration_manager.faiss_service.get_index_info()
            print(f"✅ FAISS service ready")
            print(f"   - Total vectors: {faiss_info['total_vectors']}")
            print(f"   - Dimension: {faiss_info['dimension']}")
            
            self.setup_status['steps_completed'].append('faiss_test')
            return True
            
        except Exception as e:
            print(f"❌ FAISS test failed: {e}")
            self.setup_status['errors'].append(f"FAISS test failed: {str(e)}")
            return False
    
    def _initialize_integration(self) -> bool:
        """Initialize the complete integration pipeline"""
        print("\n6. Initializing integration pipeline...")
        
        try:
            result = self.integration_manager.initialize_integration()
            
            if result['success']:
                print("✅ Integration pipeline initialized successfully")
                self.setup_status['steps_completed'].append('integration_initialization')
                return True
            else:
                print("❌ Integration initialization failed")
                print(f"   Errors: {result['errors']}")
                print(f"   Warnings: {result['warnings']}")
                self.setup_status['errors'].extend(result['errors'])
                self.setup_status['warnings'].extend(result['warnings'])
                return False
                
        except Exception as e:
            print(f"❌ Integration initialization failed: {e}")
            self.setup_status['errors'].append(f"Integration initialization failed: {str(e)}")
            return False
    
    def _build_sample_index(self) -> bool:
        """Build a sample similarity index"""
        print("\n7. Building sample similarity index...")
        
        try:
            # Ask user for parameters
            max_images = self._ask_user_int("Enter maximum number of images to process (default 100): ", 100)
            batch_size = self._ask_user_int("Enter batch size (default 50): ", 50)
            
            print(f"Building index with {max_images} images, batch size {batch_size}...")
            
            result = self.integration_manager.build_similarity_index(
                max_images=max_images,
                batch_size=batch_size
            )
            
            if result['success']:
                print("✅ Sample index built successfully")
                print(f"   - Processed images: {result['details']['processed_images']}")
                print(f"   - Successful vectors: {result['details']['successful_vectors']}")
                print(f"   - FAISS additions: {result['details']['faiss_additions']}")
                self.setup_status['steps_completed'].append('sample_index_build')
                return True
            else:
                print("❌ Sample index build failed")
                print(f"   Errors: {result['errors']}")
                self.setup_status['errors'].extend(result['errors'])
                return False
                
        except Exception as e:
            print(f"❌ Sample index build failed: {e}")
            self.setup_status['errors'].append(f"Sample index build failed: {str(e)}")
            return False
    
    def _generate_setup_report(self):
        """Generate a setup report"""
        print("\n8. Generating setup report...")
        
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'setup_status': self.setup_status,
                'integration_status': self.integration_manager.get_integration_status()
            }
            
            report_path = 'scin_setup_report.json'
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"✅ Setup report generated: {report_path}")
            self.setup_status['steps_completed'].append('report_generation')
            
        except Exception as e:
            print(f"❌ Failed to generate setup report: {e}")
            self.setup_status['errors'].append(f"Report generation failed: {str(e)}")
    
    def _ask_user(self, prompt: str) -> bool:
        """Ask user for yes/no input"""
        while True:
            response = input(prompt).lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")
    
    def _ask_user_int(self, prompt: str, default: int) -> int:
        """Ask user for integer input with default"""
        while True:
            response = input(prompt).strip()
            if not response:
                return default
            try:
                return int(response)
            except ValueError:
                print("Please enter a valid number")

def main():
    """Main setup function"""
    setup_manager = SCINSetupManager()
    
    try:
        success = setup_manager.run_setup()
        
        if success:
            print("\n🎉 SCIN Integration Setup Completed Successfully!")
            print("\nNext steps:")
            print("1. Start your Flask application")
            print("2. Test the SCIN integration endpoints:")
            print("   - GET /api/scin/health")
            print("   - GET /api/scin/status")
            print("   - POST /api/scin/search")
            print("3. Check the setup report: scin_setup_report.json")
        else:
            print("\n❌ SCIN Integration Setup Failed!")
            print("\nPlease check the errors above and try again.")
            print("Common issues:")
            print("- Missing environment variables")
            print("- Network connectivity to Google Cloud Storage")
            print("- Insufficient disk space for caching")
            print("- Missing Python dependencies")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        return 1
    except Exception as e:
        print(f"\nUnexpected error during setup: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 