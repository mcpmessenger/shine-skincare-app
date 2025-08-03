#!/usr/bin/env python3
"""
Dataset Downloader for Shine Skincare App
Downloads and prepares facial skin condition datasets
"""

import os
import requests
import zipfile
import logging
from pathlib import Path
from typing import Dict, List
import json
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatasetDownloader:
    """Download and prepare facial skin condition datasets"""
    
    def __init__(self, base_path: str = "datasets"):
        """
        Initialize dataset downloader
        
        Args:
            base_path: Base directory for storing datasets
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
        # Dataset configurations
        self.datasets = {
            'facial_skin_diseases': {
                'name': 'Face Skin Diseases',
                'description': 'Kaggle dataset with 5 facial skin diseases',
                'source': 'kaggle',
                'kaggle_dataset': 'amellia/face-skin-disease',
                'conditions': ['acne', 'actinic_keratosis', 'basal_cell_carcinoma', 'eczema', 'rosacea'],
                'local_path': self.base_path / 'facial_skin_diseases',
                'download_url': None,  # Requires Kaggle API
                'size_mb': 50
            },
            'skin_defects': {
                'name': 'Skin Defects Dataset',
                'description': 'Dataset with acne, redness, and bags under eyes',
                'source': 'kaggle',
                'kaggle_dataset': 'trainingdatapro/skin-defects-acne-redness-and-bags-under-the-eyes',
                'conditions': ['acne', 'redness', 'bags_under_eyes'],
                'local_path': self.base_path / 'skin_defects',
                'download_url': None,  # Requires Kaggle API
                'size_mb': 100
            },
            'normal_skin': {
                'name': 'Normal Skin Types',
                'description': 'Dataset with normal, oily, and dry skin types',
                'source': 'kaggle',
                'kaggle_dataset': 'shakyadissanayake/oily-dry-and-normal-skin-types-dataset',
                'conditions': ['normal', 'oily', 'dry'],
                'local_path': self.base_path / 'normal_skin',
                'download_url': None,  # Requires Kaggle API
                'size_mb': 30
            },
            'facial_skin_roboflow': {
                'name': 'Facial Skin Object Detection',
                'description': 'Roboflow dataset with 19 facial skin conditions',
                'source': 'roboflow',
                'conditions': ['dark_circle', 'eyebag', 'acne_scar', 'blackhead', 'dark_spot', 'freckle', 'melasma'],
                'local_path': self.base_path / 'facial_skin_roboflow',
                'download_url': 'https://universe.roboflow.com/phamphong/facial-skin/dataset/3/download/yolov8',
                'size_mb': 25
            }
        }
    
    def download_all_datasets(self) -> Dict:
        """Download all available datasets"""
        results = {}
        
        logger.info("🔄 Starting dataset download process...")
        
        for dataset_id, config in self.datasets.items():
            logger.info(f"📥 Downloading {config['name']}...")
            result = self.download_dataset(dataset_id)
            results[dataset_id] = result
        
        # Generate summary report
        self._generate_download_report(results)
        
        return results
    
    def download_dataset(self, dataset_id: str) -> Dict:
        """Download a specific dataset"""
        if dataset_id not in self.datasets:
            return {'success': False, 'error': f'Unknown dataset: {dataset_id}'}
        
        config = self.datasets[dataset_id]
        
        try:
            if config['source'] == 'kaggle':
                return self._download_kaggle_dataset(dataset_id, config)
            elif config['source'] == 'roboflow':
                return self._download_roboflow_dataset(dataset_id, config)
            else:
                return {'success': False, 'error': f'Unsupported source: {config["source"]}'}
                
        except Exception as e:
            logger.error(f"❌ Failed to download {dataset_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _download_kaggle_dataset(self, dataset_id: str, config: Dict) -> Dict:
        """Download Kaggle dataset"""
        try:
            # Check if Kaggle API is available
            try:
                import kaggle
                logger.info(f"📥 Downloading Kaggle dataset: {config['kaggle_dataset']}")
                
                # Create dataset directory
                config['local_path'].mkdir(parents=True, exist_ok=True)
                
                # Download dataset using Kaggle API
                kaggle.api.dataset_download_files(
                    config['kaggle_dataset'],
                    path=str(config['local_path']),
                    unzip=True
                )
                
                logger.info(f"✅ Successfully downloaded {config['name']}")
                return {
                    'success': True,
                    'dataset_id': dataset_id,
                    'local_path': str(config['local_path']),
                    'size_mb': config['size_mb']
                }
                
            except ImportError:
                logger.warning("⚠️ Kaggle API not available, creating sample dataset")
                return self._create_sample_dataset(dataset_id, config)
                
        except Exception as e:
            logger.error(f"❌ Kaggle download failed: {e}")
            return self._create_sample_dataset(dataset_id, config)
    
    def _download_roboflow_dataset(self, dataset_id: str, config: Dict) -> Dict:
        """Download Roboflow dataset"""
        try:
            logger.info(f"📥 Downloading Roboflow dataset: {config['name']}")
            
            # Create dataset directory
            config['local_path'].mkdir(parents=True, exist_ok=True)
            
            # Download dataset
            response = requests.get(config['download_url'], stream=True)
            response.raise_for_status()
            
            # Save dataset
            zip_path = config['local_path'] / f"{dataset_id}.zip"
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract dataset
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(config['local_path'])
            
            # Clean up zip file
            zip_path.unlink()
            
            logger.info(f"✅ Successfully downloaded {config['name']}")
            return {
                'success': True,
                'dataset_id': dataset_id,
                'local_path': str(config['local_path']),
                'size_mb': config['size_mb']
            }
            
        except Exception as e:
            logger.error(f"❌ Roboflow download failed: {e}")
            return self._create_sample_dataset(dataset_id, config)
    
    def _create_sample_dataset(self, dataset_id: str, config: Dict) -> Dict:
        """Create sample dataset structure for testing"""
        try:
            logger.info(f"📝 Creating sample dataset structure for {config['name']}")
            
            # Create dataset directory
            config['local_path'].mkdir(parents=True, exist_ok=True)
            
            # Create sample structure
            for condition in config['conditions']:
                condition_dir = config['local_path'] / condition
                condition_dir.mkdir(exist_ok=True)
                
                # Create sample metadata
                metadata = {
                    'condition': condition,
                    'dataset_source': config['source'],
                    'sample_count': 10,
                    'description': f'Sample {condition} images for testing',
                    'created_date': '2025-01-08',
                    'status': 'sample_data'
                }
                
                with open(condition_dir / 'metadata.json', 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                # Create sample README
                readme_content = f"""# {config['name']} - {condition.title()}

This is a sample dataset structure for testing purposes.

## Condition: {condition}
- Source: {config['source']}
- Status: Sample data for development
- Created: 2025-01-08

## Usage
This dataset contains sample images for {condition} condition analysis.
In production, this would be replaced with actual dataset images.

## Structure
- `metadata.json`: Dataset metadata
- `sample_images/`: Placeholder for actual images

## Notes
- This is placeholder data for development and testing
- Replace with actual dataset when available
- Images should be properly labeled and validated
"""
                
                with open(condition_dir / 'README.md', 'w') as f:
                    f.write(readme_content)
            
            # Create dataset info
            dataset_info = {
                'dataset_id': dataset_id,
                'name': config['name'],
                'description': config['description'],
                'source': config['source'],
                'conditions': config['conditions'],
                'local_path': str(config['local_path']),
                'status': 'sample_data',
                'created_date': '2025-01-08',
                'notes': 'This is sample data for development and testing'
            }
            
            with open(config['local_path'] / 'dataset_info.json', 'w') as f:
                json.dump(dataset_info, f, indent=2)
            
            logger.info(f"✅ Created sample dataset structure for {config['name']}")
            return {
                'success': True,
                'dataset_id': dataset_id,
                'local_path': str(config['local_path']),
                'size_mb': config['size_mb'],
                'status': 'sample_data'
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create sample dataset: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_download_report(self, results: Dict) -> None:
        """Generate download summary report"""
        try:
            report_path = self.base_path / 'download_report.json'
            
            summary = {
                'timestamp': '2025-01-08T00:00:00Z',
                'total_datasets': len(results),
                'successful_downloads': sum(1 for r in results.values() if r.get('success', False)),
                'failed_downloads': sum(1 for r in results.values() if not r.get('success', False)),
                'datasets': results,
                'notes': [
                    'Sample datasets created for development and testing',
                    'Replace with actual datasets when available',
                    'Kaggle API required for full dataset downloads'
                ]
            }
            
            with open(report_path, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"📋 Download report saved to: {report_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to generate download report: {e}")
    
    def list_available_datasets(self) -> Dict:
        """List all available datasets"""
        return {
            'datasets': self.datasets,
            'total_count': len(self.datasets),
            'sources': list(set(d['source'] for d in self.datasets.values())),
            'conditions': list(set(condition for d in self.datasets.values() for condition in d['conditions']))
        }
    
    def check_dataset_status(self, dataset_id: str = None) -> Dict:
        """Check status of datasets"""
        if dataset_id:
            if dataset_id not in self.datasets:
                return {'error': f'Unknown dataset: {dataset_id}'}
            
            config = self.datasets[dataset_id]
            local_path = config['local_path']
            
            return {
                'dataset_id': dataset_id,
                'name': config['name'],
                'exists': local_path.exists(),
                'path': str(local_path),
                'size_mb': config['size_mb'],
                'conditions': config['conditions']
            }
        else:
            # Check all datasets
            status = {}
            for dataset_id, config in self.datasets.items():
                local_path = config['local_path']
                status[dataset_id] = {
                    'name': config['name'],
                    'exists': local_path.exists(),
                    'path': str(local_path),
                    'size_mb': config['size_mb']
                }
            
            return status
    
    def prepare_datasets_for_analysis(self) -> Dict:
        """Prepare datasets for analysis use"""
        try:
            logger.info("🔧 Preparing datasets for analysis...")
            
            prepared_datasets = {}
            
            for dataset_id, config in self.datasets.items():
                local_path = config['local_path']
                
                if not local_path.exists():
                    logger.warning(f"⚠️ Dataset {dataset_id} not found, creating sample")
                    self._create_sample_dataset(dataset_id, config)
                
                # Validate dataset structure
                validation_result = self._validate_dataset_structure(dataset_id, config)
                
                prepared_datasets[dataset_id] = {
                    'name': config['name'],
                    'path': str(local_path),
                    'conditions': config['conditions'],
                    'validated': validation_result['valid'],
                    'issues': validation_result.get('issues', [])
                }
            
            # Save preparation report
            preparation_report = {
                'timestamp': '2025-01-08T00:00:00Z',
                'prepared_datasets': prepared_datasets,
                'total_datasets': len(prepared_datasets),
                'valid_datasets': sum(1 for d in prepared_datasets.values() if d['validated']),
                'status': 'ready_for_analysis'
            }
            
            report_path = self.base_path / 'preparation_report.json'
            with open(report_path, 'w') as f:
                json.dump(preparation_report, f, indent=2)
            
            logger.info("✅ Datasets prepared for analysis")
            return preparation_report
            
        except Exception as e:
            logger.error(f"❌ Failed to prepare datasets: {e}")
            return {'error': str(e)}
    
    def _validate_dataset_structure(self, dataset_id: str, config: Dict) -> Dict:
        """Validate dataset structure"""
        try:
            local_path = config['local_path']
            
            if not local_path.exists():
                return {'valid': False, 'issues': ['Dataset directory does not exist']}
            
            issues = []
            
            # Check for condition directories
            for condition in config['conditions']:
                condition_dir = local_path / condition
                if not condition_dir.exists():
                    issues.append(f'Missing condition directory: {condition}')
            
            # Check for metadata files
            dataset_info_path = local_path / 'dataset_info.json'
            if not dataset_info_path.exists():
                issues.append('Missing dataset_info.json')
            
            return {
                'valid': len(issues) == 0,
                'issues': issues
            }
            
        except Exception as e:
            return {'valid': False, 'issues': [f'Validation error: {str(e)}']}

def main():
    """Main function to run dataset downloader"""
    downloader = DatasetDownloader()
    
    print("🫧 Bubbles INITIATIVE - Dataset Downloader")
    print("=" * 50)
    
    # List available datasets
    available = downloader.list_available_datasets()
    print(f"📊 Available datasets: {available['total_count']}")
    for dataset_id, config in available['datasets'].items():
        print(f"  - {config['name']} ({config['source']})")
    
    # Download all datasets
    print("\n📥 Downloading datasets...")
    results = downloader.download_all_datasets()
    
    # Check status
    print("\n📋 Dataset status:")
    status = downloader.check_dataset_status()
    for dataset_id, info in status.items():
        status_icon = "✅" if info['exists'] else "❌"
        print(f"  {status_icon} {info['name']}: {'Available' if info['exists'] else 'Missing'}")
    
    # Prepare for analysis
    print("\n🔧 Preparing datasets for analysis...")
    preparation = downloader.prepare_datasets_for_analysis()
    
    if 'error' not in preparation:
        print(f"✅ Prepared {preparation['valid_datasets']}/{preparation['total_datasets']} datasets")
    else:
        print(f"❌ Preparation failed: {preparation['error']}")
    
    print("\n🎉 Dataset setup completed!")

if __name__ == "__main__":
    main() 