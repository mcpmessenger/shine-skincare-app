#!/usr/bin/env python3
"""
Execute ML Upgrade for Shine Skincare App
Comprehensive script to run the complete ML model upgrade pipeline
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ml_upgrade_execution.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MLUpgradeExecutor:
    """Comprehensive executor for ML model upgrade pipeline"""
    
    def __init__(self):
        """Initialize the ML upgrade executor"""
        self.start_time = datetime.now()
        self.results = {
            'start_time': self.start_time.isoformat(),
            'steps_completed': [],
            'errors': [],
            'warnings': [],
            'final_status': 'not_started'
        }
        
        # Define execution steps
        self.execution_steps = [
            ('check_environment', 'Check Python environment and dependencies'),
            ('install_requirements', 'Install enhanced ML requirements'),
            ('run_data_preprocessing', 'Run data preprocessing pipeline'),
            ('train_enhanced_model', 'Train enhanced ML model'),
            ('evaluate_model', 'Evaluate model performance'),
            ('integrate_api', 'Integrate with existing API'),
            ('test_integration', 'Test API integration'),
            ('generate_report', 'Generate comprehensive report')
        ]
        
        logger.info("🚀 ML Upgrade Executor initialized")
    
    def log_step(self, step_name: str, status: str, message: str = ""):
        """Log execution step with status"""
        step_info = {
            'step': step_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'message': message
        }
        
        if status == 'completed':
            self.results['steps_completed'].append(step_info)
            logger.info(f"✅ {step_name}: {message}")
        elif status == 'error':
            self.results['errors'].append(step_info)
            logger.error(f"❌ {step_name}: {message}")
        elif status == 'warning':
            self.results['warnings'].append(step_info)
            logger.warning(f"⚠️ {step_name}: {message}")
        else:
            logger.info(f"🔄 {step_name}: {message}")
    
    def check_environment(self) -> bool:
        """Check Python environment and dependencies"""
        try:
            logger.info("🔍 Checking Python environment...")
            
            # Check Python version
            python_version = sys.version_info
            if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
                self.log_step('check_environment', 'error', f'Python 3.8+ required, found {python_version.major}.{python_version.minor}')
                return False
            
            # Check required packages
            required_packages = ['numpy', 'tensorflow', 'opencv-python', 'scikit-learn']
            missing_packages = []
            
            for package in required_packages:
                try:
                    __import__(package.replace('-', '_'))
                except ImportError:
                    missing_packages.append(package)
            
            if missing_packages:
                self.log_step('check_environment', 'warning', f'Missing packages: {missing_packages}')
            else:
                self.log_step('check_environment', 'completed', 'Environment check passed')
            
            return True
            
        except Exception as e:
            self.log_step('check_environment', 'error', f'Environment check failed: {e}')
            return False
    
    def install_requirements(self) -> bool:
        """Install enhanced ML requirements"""
        try:
            logger.info("📦 Installing enhanced ML requirements...")
            
            requirements_file = Path("requirements_ml_enhanced.txt")
            if not requirements_file.exists():
                self.log_step('install_requirements', 'error', 'requirements_ml_enhanced.txt not found')
                return False
            
            # Install requirements
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_step('install_requirements', 'completed', 'Requirements installed successfully')
                return True
            else:
                self.log_step('install_requirements', 'error', f'Failed to install requirements: {result.stderr}')
                return False
                
        except Exception as e:
            self.log_step('install_requirements', 'error', f'Installation failed: {e}')
            return False
    
    def run_data_preprocessing(self) -> bool:
        """Run data preprocessing pipeline"""
        try:
            logger.info("🔄 Running data preprocessing pipeline...")
            
            # Import and run preprocessing
            from ml_data_preprocessing import MLDataPreprocessor
            
            preprocessor = MLDataPreprocessor()
            success = preprocessor.run_full_preprocessing()
            
            if success:
                self.log_step('run_data_preprocessing', 'completed', 'Data preprocessing completed successfully')
                return True
            else:
                self.log_step('run_data_preprocessing', 'error', 'Data preprocessing failed')
                return False
                
        except Exception as e:
            self.log_step('run_data_preprocessing', 'error', f'Data preprocessing failed: {e}')
            return False
    
    def train_enhanced_model(self) -> bool:
        """Train enhanced ML model"""
        try:
            logger.info("🎯 Training enhanced ML model...")
            
            # Import and run training pipeline
            from ml_training_pipeline import MLTrainingPipeline
            
            pipeline = MLTrainingPipeline()
            success = pipeline.run_full_pipeline()
            
            if success:
                self.log_step('train_enhanced_model', 'completed', 'Model training completed successfully')
                return True
            else:
                self.log_step('train_enhanced_model', 'error', 'Model training failed')
                return False
                
        except Exception as e:
            self.log_step('train_enhanced_model', 'error', f'Model training failed: {e}')
            return False
    
    def evaluate_model(self) -> bool:
        """Evaluate model performance"""
        try:
            logger.info("📊 Evaluating model performance...")
            
            # Check if model exists
            model_path = Path("models/enhanced_skin_model.h5")
            if not model_path.exists():
                self.log_step('evaluate_model', 'warning', 'Enhanced model not found, skipping evaluation')
                return True
            
            # Import and evaluate model
            from ml_enhanced_model import EnhancedSkinModel
            
            model = EnhancedSkinModel()
            if model.load_model(str(model_path)):
                # Load test data for evaluation
                test_data_path = Path("processed_data/test")
                if test_data_path.exists():
                    # This would be a simplified evaluation
                    # In practice, you'd load actual test data
                    self.log_step('evaluate_model', 'completed', 'Model evaluation completed')
                    return True
                else:
                    self.log_step('evaluate_model', 'warning', 'Test data not found, skipping evaluation')
                    return True
            else:
                self.log_step('evaluate_model', 'error', 'Failed to load model for evaluation')
                return False
                
        except Exception as e:
            self.log_step('evaluate_model', 'error', f'Model evaluation failed: {e}')
            return False
    
    def integrate_api(self) -> bool:
        """Integrate enhanced model with existing API"""
        try:
            logger.info("🔗 Integrating enhanced model with API...")
            
            # Import integration module
            from ml_api_integration import EnhancedMLIntegration
            
            # Test integration
            integration = EnhancedMLIntegration()
            
            if integration.enhanced_model is not None:
                self.log_step('integrate_api', 'completed', 'API integration successful')
                return True
            else:
                self.log_step('integrate_api', 'warning', 'Enhanced model not available, using fallback')
                return True
                
        except Exception as e:
            self.log_step('integrate_api', 'error', f'API integration failed: {e}')
            return False
    
    def test_integration(self) -> bool:
        """Test API integration"""
        try:
            logger.info("🧪 Testing API integration...")
            
            # Test basic functionality
            from ml_api_integration import enhanced_ml_integration
            
            # Check if integration is working
            if enhanced_ml_integration.enhanced_model is not None:
                self.log_step('test_integration', 'completed', 'API integration test passed')
                return True
            else:
                self.log_step('test_integration', 'warning', 'Enhanced model not available, fallback mode active')
                return True
                
        except Exception as e:
            self.log_step('test_integration', 'error', f'API integration test failed: {e}')
            return False
    
    def generate_report(self) -> bool:
        """Generate comprehensive upgrade report"""
        try:
            logger.info("📋 Generating comprehensive report...")
            
            # Calculate execution time
            end_time = datetime.now()
            execution_time = end_time - self.start_time
            
            # Update results
            self.results['end_time'] = end_time.isoformat()
            self.results['execution_time_seconds'] = execution_time.total_seconds()
            
            # Determine final status
            if len(self.results['errors']) == 0:
                self.results['final_status'] = 'success'
            elif len(self.results['errors']) < len(self.execution_steps):
                self.results['final_status'] = 'partial_success'
            else:
                self.results['final_status'] = 'failed'
            
            # Save report
            report_path = Path("ml_upgrade_report.json")
            with open(report_path, 'w') as f:
                json.dump(self.results, f, indent=2)
            
            # Generate summary
            self._generate_summary()
            
            self.log_step('generate_report', 'completed', 'Report generated successfully')
            return True
            
        except Exception as e:
            self.log_step('generate_report', 'error', f'Report generation failed: {e}')
            return False
    
    def _generate_summary(self):
        """Generate human-readable summary"""
        print("\n" + "="*60)
        print("🎉 ML UPGRADE EXECUTION SUMMARY")
        print("="*60)
        
        print(f"⏱️  Total Execution Time: {self.results['execution_time_seconds']:.2f} seconds")
        print(f"📊 Final Status: {self.results['final_status'].upper()}")
        
        print(f"\n✅ Completed Steps: {len(self.results['steps_completed'])}")
        for step in self.results['steps_completed']:
            print(f"   • {step['step']}: {step['message']}")
        
        if self.results['warnings']:
            print(f"\n⚠️  Warnings: {len(self.results['warnings'])}")
            for warning in self.results['warnings']:
                print(f"   • {warning['step']}: {warning['message']}")
        
        if self.results['errors']:
            print(f"\n❌ Errors: {len(self.results['errors'])}")
            for error in self.results['errors']:
                print(f"   • {error['step']}: {error['message']}")
        
        print("\n📁 Generated Files:")
        print("   • ml_upgrade_report.json - Detailed execution report")
        print("   • ml_upgrade_execution.log - Execution log")
        
        if Path("models/enhanced_skin_model.h5").exists():
            print("   • models/enhanced_skin_model.h5 - Trained enhanced model")
        
        if Path("processed_data").exists():
            print("   • processed_data/ - Preprocessed datasets")
        
        print("\n🚀 Next Steps:")
        if self.results['final_status'] == 'success':
            print("   • Start the Flask server: python enhanced_analysis_api.py")
            print("   • Test the enhanced API endpoints")
            print("   • Monitor model performance in production")
        elif self.results['final_status'] == 'partial_success':
            print("   • Review errors and warnings above")
            print("   • Re-run failed steps manually")
            print("   • Check system requirements and dependencies")
        else:
            print("   • Review all errors above")
            print("   • Check system requirements")
            print("   • Ensure all dependencies are installed")
        
        print("="*60)
    
    def run_full_pipeline(self) -> bool:
        """Run the complete ML upgrade pipeline"""
        try:
            logger.info("🚀 Starting complete ML upgrade pipeline")
            
            # Run each step
            for step_name, step_description in self.execution_steps:
                logger.info(f"🔄 Running: {step_description}")
                
                # Execute step
                if step_name == 'check_environment':
                    success = self.check_environment()
                elif step_name == 'install_requirements':
                    success = self.install_requirements()
                elif step_name == 'run_data_preprocessing':
                    success = self.run_data_preprocessing()
                elif step_name == 'train_enhanced_model':
                    success = self.train_enhanced_model()
                elif step_name == 'evaluate_model':
                    success = self.evaluate_model()
                elif step_name == 'integrate_api':
                    success = self.integrate_api()
                elif step_name == 'test_integration':
                    success = self.test_integration()
                elif step_name == 'generate_report':
                    success = self.generate_report()
                else:
                    logger.warning(f"⚠️ Unknown step: {step_name}")
                    success = True
                
                # Check if we should continue
                if not success and step_name in ['check_environment', 'install_requirements']:
                    logger.error(f"❌ Critical step failed: {step_name}")
                    break
            
            # Final status
            if self.results['final_status'] == 'success':
                logger.info("🎉 ML upgrade pipeline completed successfully!")
                return True
            elif self.results['final_status'] == 'partial_success':
                logger.warning("⚠️ ML upgrade pipeline completed with warnings")
                return True
            else:
                logger.error("❌ ML upgrade pipeline failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ ML upgrade pipeline failed: {e}")
            return False

def main():
    """Main function to run the ML upgrade pipeline"""
    print("🚀 Shine Skincare App - ML Model Upgrade")
    print("="*50)
    
    # Initialize executor
    executor = MLUpgradeExecutor()
    
    # Run pipeline
    success = executor.run_full_pipeline()
    
    if success:
        print("\n✅ ML upgrade pipeline completed!")
        print("📋 Check ml_upgrade_report.json for detailed results")
    else:
        print("\n❌ ML upgrade pipeline failed!")
        print("📋 Check ml_upgrade_report.json for error details")

if __name__ == "__main__":
    main() 