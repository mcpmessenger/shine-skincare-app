#!/usr/bin/env python3
"""
UTKFace Integration for Shine Skincare App
Provides integration with UTKFace dataset for healthy skin baselines
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UTKFaceIntegration:
    """
    UTKFace integration for healthy skin baseline analysis
    Integrates with existing 103 demographic baselines
    """

    def __init__(self):
        """Initialize the UTKFace integration"""
        self.dataset_path = Path(__file__).parent / "data" / "utkface"
        self.baselines = self._load_baselines()
        
        logger.info("✅ UTKFace integration initialized")

    def _load_baselines(self) -> Dict:
        """Load UTKFace baselines"""
        try:
            baselines_path = Path(__file__).parent / "data" / "demographic_baselines.npy"
            if baselines_path.exists():
                baselines = np.load(str(baselines_path), allow_pickle=True).item()
                logger.info(f"✅ Loaded {len(baselines)} UTKFace baselines")
                return baselines
            else:
                logger.warning("⚠️ UTKFace baselines file not found, using empty dict")
                return {}
        except Exception as e:
            logger.error(f"❌ Failed to load UTKFace baselines: {e}")
            return {}

    def get_healthy_baseline(self, demographics: Dict) -> Optional[np.ndarray]:
        """Get healthy baseline for specific demographics"""
        key = self._create_demographic_key(demographics)
        return self.baselines.get(key)

    def _create_demographic_key(self, demographics: Dict) -> str:
        """Create a key from demographic information"""
        age_group = demographics.get('age_group', 'unknown')
        gender = demographics.get('gender', 'unknown')
        ethnicity = demographics.get('ethnicity', 'unknown')
        return f"{age_group}_{gender}_{ethnicity}"

    def get_system_status(self) -> Dict:
        """Get system status"""
        return {
            'status': 'operational',
            'baselines_loaded': len(self.baselines),
            'dataset_path': str(self.dataset_path),
            'timestamp': datetime.now().isoformat()
        } 