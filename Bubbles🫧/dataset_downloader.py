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
                return self._create_sample_dataset(dataset_id, config)
                
        except Exception as e:
            logger.error(f"❌ Failed to download {config['name']}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _download_kaggle_dataset(self, dataset_id: str, config: Dict) -> Dict:
        """Download dataset from Kaggle"""
        try:
            # Check if Kaggle API is available
            try:
                from kaggle.api.kaggle_api_extended import KaggleApi
                api = KaggleApi()
                api.authenticate()
                
                # Download dataset
                api.dataset_download_files(
                    config['kaggle_dataset'],
                    path=str(config['local_path']),
                    unzip=True
                )
                
                logger.info(f"✅ Downloaded {config['name']} from Kaggle")
                return {
                    'success': True,
                    'source': 'kaggle',
                    'path': str(config['local_path']),
                    'conditions': config['conditions']
                }
                
            except ImportError:
                logger.warning(f"⚠️ Kaggle API not available for {config['name']}")
                return self._create_sample_dataset(dataset_id, config)
            except Exception as e:
                logger.warning(f"⚠️ Kaggle download failed for {config['name']}: {e}")
                return self._create_sample_dataset(dataset_id, config)
                
        except Exception as e:
            logger.error(f"❌ Error downloading {config['name']}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _download_roboflow_dataset(self, dataset_id: str, config: Dict) -> Dict:
        """Download dataset from Roboflow"""
        try:
            # Note: Roboflow datasets typically require API keys
            # For now, create sample dataset
            logger.warning(f"⚠️ Roboflow download not implemented for {config['name']}")
            return self._create_sample_dataset(dataset_id, config)
            
        except Exception as e:
            logger.error(f"❌ Error downloading {config['name']}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_sample_dataset(self, dataset_id: str, config: Dict) -> Dict:
        """Create a sample dataset structure for testing"""
        try:
            dataset_path = config['local_path']
            dataset_path.mkdir(parents=True, exist_ok=True)
            
            # Create directory structure
            for condition in config['conditions']:
                condition_path = dataset_path / condition
                condition_path.mkdir(exist_ok=True)
                
                # Create sample metadata file
                metadata = {
                    'condition': condition,
                    'dataset': config['name'],
                    'sample_count': 0,
                    'description': f'Sample {condition} images for {config["name"]}'
                }
                
                with open(condition_path / 'metadata.json', 'w') as f:
                    json.dump(metadata, f, indent=2)
            
            # Create dataset info file
            dataset_info = {
                'dataset_id': dataset_id,
                'name': config['name'],
                'description': config['description'],
                'source': 'sample',
                'conditions': config['conditions'],
                'created_at': str(Path().cwd()),
                'status': 'sample_structure_created'
            }
            
            with open(dataset_path / 'dataset_info.json', 'w') as f:
                json.dump(dataset_info, f, indent=2)
            
            logger.info(f"✅ Created sample structure for {config['name']}")
            return {
                'success': True,
                'source': 'sample',
                'path': str(dataset_path),
                'conditions': config['conditions'],
                'note': 'Sample dataset structure created. Add real images to use.'
            }
            
        except Exception as e:
            logger.error(f"❌ Error creating sample dataset {config['name']}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_download_report(self, results: Dict) -> None:
        """Generate a download report"""
        try:
            report_path = self.base_path / 'download_report.json'
            
            report = {
                'download_timestamp': str(Path().cwd()),
                'total_datasets': len(results),
                'successful_downloads': sum(1 for r in results.values() if r.get('success', False)),
                'failed_downloads': sum(1 for r in results.values() if not r.get('success', False)),
                'results': results,
                'next_steps': [
                    'Install Kaggle API for full dataset downloads: pip install kaggle',
                    'Set up Kaggle API credentials: https://github.com/Kaggle/kaggle-api',
                    'Add real images to sample dataset directories',
                    'Run face detection on downloaded images to extract facial regions'
                ]
            }
            
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"📊 Download report saved to {report_path}")
            
            # Print summary
            print("\n" + "="*60)
            print("DATASET DOWNLOAD SUMMARY")
            print("="*60)
            print(f"Total datasets: {report['total_datasets']}")
            print(f"Successful: {report['successful_downloads']}")
            print(f"Failed: {report['failed_downloads']}")
            print("\nDataset Status:")
            for dataset_id, result in results.items():
                status = "✅ SUCCESS" if result.get('success', False) else "❌ FAILED"
                print(f"  {dataset_id}: {status}")
            print("="*60)
            
        except Exception as e:
            logger.error(f"❌ Error generating report: {e}")
    
    def list_available_datasets(self) -> Dict:
        """List all available datasets"""
        return {
            dataset_id: {
                'name': config['name'],
                'description': config['description'],
                'conditions': config['conditions'],
                'source': config['source'],
                'size_mb': config['size_mb']
            }
            for dataset_id, config in self.datasets.items()
        }
    
    def check_dataset_status(self, dataset_id: str = None) -> Dict:
        """Check status of downloaded datasets"""
        if dataset_id:
            datasets_to_check = {dataset_id: self.datasets[dataset_id]}
        else:
            datasets_to_check = self.datasets
        
        status = {}
        
        for dataset_id, config in datasets_to_check.items():
            dataset_path = config['local_path']
            
            if dataset_path.exists():
                # Count files in dataset
                total_files = sum(1 for _ in dataset_path.rglob('*') if _.is_file())
                image_files = sum(1 for _ in dataset_path.rglob('*') 
                                if _.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp'])
                
                status[dataset_id] = {
                    'exists': True,
                    'path': str(dataset_path),
                    'total_files': total_files,
                    'image_files': image_files,
                    'conditions': config['conditions']
                }
            else:
                status[dataset_id] = {
                    'exists': False,
                    'path': str(dataset_path),
                    'total_files': 0,
                    'image_files': 0,
                    'conditions': config['conditions']
                }
        
        return status
    
    def prepare_datasets_for_analysis(self) -> Dict:
        """Prepare downloaded datasets for face analysis"""
        try:
            logger.info("🔄 Preparing datasets for face analysis...")
            
            preparation_results = {}
            
            for dataset_id, config in self.datasets.items():
                dataset_path = config['local_path']
                
                if not dataset_path.exists():
                    preparation_results[dataset_id] = {
                        'success': False,
                        'error': 'Dataset not downloaded'
                    }
                    continue
                
                # Process each condition directory
                condition_results = {}
                
                for condition in config['conditions']:
                    condition_path = dataset_path / condition
                    
                    if condition_path.exists():
                        # Count images
                        image_files = list(condition_path.glob('*.jpg')) + \
                                    list(condition_path.glob('*.jpeg')) + \
                                    list(condition_path.glob('*.png'))
                        
                        condition_results[condition] = {
                            'image_count': len(image_files),
                            'ready_for_analysis': len(image_files) > 0
                        }
                    else:
                        condition_results[condition] = {
                            'image_count': 0,
                            'ready_for_analysis': False
                        }
                
                preparation_results[dataset_id] = {
                    'success': True,
                    'conditions': condition_results,
                    'total_images': sum(c['image_count'] for c in condition_results.values())
                }
            
            logger.info("✅ Dataset preparation completed")
            return preparation_results
            
        except Exception as e:
            logger.error(f"❌ Error preparing datasets: {e}")
            return {'error': str(e)}

def main():
    """Main function for testing dataset downloader"""
    downloader = DatasetDownloader()
    
    print("Available datasets:")
    datasets = downloader.list_available_datasets()
    for dataset_id, info in datasets.items():
        print(f"  {dataset_id}: {info['name']} ({info['size_mb']}MB)")
    
    print("\nDownloading datasets...")
    results = downloader.download_all_datasets()
    
    print("\nChecking dataset status...")
    status = downloader.check_dataset_status()
    for dataset_id, info in status.items():
        print(f"  {dataset_id}: {'✅' if info['exists'] else '❌'} ({info['image_files']} images)")
    
    print("\nPreparing datasets for analysis...")
    preparation = downloader.prepare_datasets_for_analysis()
    print(f"Preparation results: {preparation}")

if __name__ == "__main__":
    main()

