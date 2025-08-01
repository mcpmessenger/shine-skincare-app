"""
SCIN Vector Search Service - FAISS-based similarity search for SCIN dataset

This service is part of Operation Left Brain and provides efficient vector search
capabilities for finding similar skin conditions in the SCIN dataset.
"""

import logging
import os
import pickle
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

# Try to import FAISS
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("FAISS not available - using fallback similarity search")

logger = logging.getLogger(__name__)

@dataclass
class SCINCase:
    """SCIN case data structure"""
    case_id: str
    condition_type: str
    age_group: str
    ethnicity: str
    treatment_history: str
    outcome: str
    similarity_score: float
    image_path: Optional[str] = None

class SCINVectorSearchService:
    """
    Service for FAISS-based vector search in SCIN dataset
    """
    
    def __init__(self, index_path: str = "scin_faiss_index.bin", 
                 metadata_path: str = "scin_metadata.pkl"):
        """
        Initialize the SCIN vector search service
        
        Args:
            index_path: Path to the FAISS index file
            metadata_path: Path to the SCIN metadata file
        """
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.faiss_index = None
        self.scin_metadata = None
        self.scin_cases_df = None
        self.is_loaded = False
        
        # Load the index and metadata
        self._load_index_and_metadata()
    
    def _load_index_and_metadata(self):
        """Load FAISS index and SCIN metadata"""
        try:
            if not FAISS_AVAILABLE:
                logger.warning("FAISS not available - using fallback search")
                self._initialize_fallback_search()
                return
            
            # Check if files exist
            if not os.path.exists(self.index_path) or not os.path.exists(self.metadata_path):
                logger.warning(f"SCIN index files not found: {self.index_path}, {self.metadata_path}")
                self._initialize_fallback_search()
                return
            
            # Load FAISS index
            self.faiss_index = faiss.read_index(self.index_path)
            logger.info(f"✅ Loaded FAISS index with {self.faiss_index.ntotal} vectors")
            
            # Load metadata
            self.scin_metadata = pd.read_pickle(self.metadata_path)
            logger.info(f"✅ Loaded SCIN metadata with {len(self.scin_metadata)} entries")
            
            # Load full SCIN cases data if available
            self._load_scin_cases_data()
            
            self.is_loaded = True
            logger.info("✅ SCIN vector search service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to load SCIN index: {e}")
            self._initialize_fallback_search()
    
    def _load_scin_cases_data(self):
        """Load full SCIN cases data for detailed information"""
        try:
            # Try to load the full SCIN cases CSV
            scin_cases_path = "scin_cases.csv"
            scin_labels_path = "scin_labels.csv"
            
            if os.path.exists(scin_cases_path) and os.path.exists(scin_labels_path):
                cases_df = pd.read_csv(scin_cases_path, dtype={'case_id': str})
                labels_df = pd.read_csv(scin_labels_path, dtype={'case_id': str})
                self.scin_cases_df = pd.merge(cases_df, labels_df, on='case_id', how='left')
                logger.info(f"✅ Loaded full SCIN cases data with {len(self.scin_cases_df)} cases")
            else:
                logger.warning("SCIN cases CSV files not found - using metadata only")
                
        except Exception as e:
            logger.error(f"Failed to load SCIN cases data: {e}")
    
    def _initialize_fallback_search(self):
        """Initialize fallback search when FAISS is not available"""
        logger.info("Initializing fallback similarity search")
        self.is_loaded = True
    
    def search_similar_cases(self, query_embedding: np.ndarray, k: int = 5) -> List[SCINCase]:
        """
        Search for similar cases in the SCIN dataset
        
        Args:
            query_embedding: Query image embedding
            k: Number of similar cases to retrieve
            
        Returns:
            List of similar SCIN cases
        """
        if not self.is_loaded:
            logger.warning("SCIN search service not loaded - returning empty results")
            return []
        
        try:
            if FAISS_AVAILABLE and self.faiss_index is not None:
                return self._faiss_search(query_embedding, k)
            else:
                return self._fallback_search(query_embedding, k)
                
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    def _faiss_search(self, query_embedding: np.ndarray, k: int) -> List[SCINCase]:
        """Perform FAISS-based similarity search"""
        try:
            # Ensure query embedding is the right format
            query_vector = np.array([query_embedding]).astype('float32')
            
            # Search the index
            distances, indices = self.faiss_index.search(query_vector, k)
            
            similar_cases = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx == -1:  # No result found
                    continue
                
                # Get case ID from metadata
                case_id = self.scin_metadata.iloc[idx]['case_id']
                
                # Calculate similarity score (normalize distance to 0-1 range)
                similarity_score = max(0, 1 - (distance / 1000))  # Normalize distance
                
                # Get detailed case information
                case_details = self._get_case_details(case_id)
                
                scin_case = SCINCase(
                    case_id=case_id,
                    condition_type=case_details.get('condition_type', 'unknown'),
                    age_group=case_details.get('age_group', 'unknown'),
                    ethnicity=case_details.get('ethnicity', 'unknown'),
                    treatment_history=case_details.get('treatment_history', 'unknown'),
                    outcome=case_details.get('outcome', 'unknown'),
                    similarity_score=similarity_score,
                    image_path=case_details.get('image_path')
                )
                
                similar_cases.append(scin_case)
            
            logger.debug(f"Found {len(similar_cases)} similar cases")
            return similar_cases
            
        except Exception as e:
            logger.error(f"FAISS search error: {e}")
            return []
    
    def _fallback_search(self, query_embedding: np.ndarray, k: int) -> List[SCINCase]:
        """Fallback similarity search when FAISS is not available"""
        # Generate mock similar cases for demonstration
        mock_cases = []
        
        for i in range(min(k, 3)):
            case = SCINCase(
                case_id=f"mock_case_{i+1}",
                condition_type="acne_vulgaris",
                age_group="18-25",
                ethnicity="mixed",
                treatment_history="topical_retinoids",
                outcome="improved",
                similarity_score=0.85 - (i * 0.1),
                image_path=None
            )
            mock_cases.append(case)
        
        logger.debug(f"Generated {len(mock_cases)} mock similar cases")
        return mock_cases
    
    def _get_case_details(self, case_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific case"""
        if self.scin_cases_df is not None:
            case_data = self.scin_cases_df[self.scin_cases_df['case_id'] == case_id]
            if not case_data.empty:
                case_row = case_data.iloc[0]
                return {
                    'condition_type': case_row.get('condition_type', 'unknown'),
                    'age_group': case_row.get('age_group', 'unknown'),
                    'ethnicity': case_row.get('ethnicity', 'unknown'),
                    'treatment_history': case_row.get('treatment_history', 'unknown'),
                    'outcome': case_row.get('outcome', 'unknown'),
                    'image_path': case_row.get('image_1_path')
                }
        
        # Return default values if case not found
        return {
            'condition_type': 'unknown',
            'age_group': 'unknown',
            'ethnicity': 'unknown',
            'treatment_history': 'unknown',
            'outcome': 'unknown',
            'image_path': None
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get the status of the SCIN search service"""
        return {
            'is_loaded': self.is_loaded,
            'faiss_available': FAISS_AVAILABLE,
            'index_loaded': self.faiss_index is not None,
            'metadata_loaded': self.scin_metadata is not None,
            'cases_loaded': self.scin_cases_df is not None,
            'total_vectors': self.faiss_index.ntotal if self.faiss_index else 0,
            'total_cases': len(self.scin_cases_df) if self.scin_cases_df is not None else 0
        }
    
    def build_index_from_embeddings(self, embeddings: np.ndarray, case_ids: List[str], 
                                   save_path: str = None) -> bool:
        """
        Build a new FAISS index from embeddings
        
        Args:
            embeddings: Array of embeddings (n_embeddings x embedding_dim)
            case_ids: List of case IDs corresponding to embeddings
            save_path: Path to save the index (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if not FAISS_AVAILABLE:
            logger.error("FAISS not available - cannot build index")
            return False
        
        try:
            # Ensure embeddings are float32
            embeddings = embeddings.astype('float32')
            dimension = embeddings.shape[1]
            
            # Create FAISS index
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings)
            
            # Save index
            if save_path:
                faiss.write_index(index, save_path)
                logger.info(f"✅ Built and saved FAISS index with {index.ntotal} vectors to {save_path}")
            
            # Save metadata
            metadata_df = pd.DataFrame({'case_id': case_ids})
            metadata_path = save_path.replace('.bin', '_metadata.pkl') if save_path else 'scin_metadata.pkl'
            metadata_df.to_pickle(metadata_path)
            logger.info(f"✅ Saved metadata to {metadata_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to build FAISS index: {e}")
            return False

# Global instance for reuse
scin_search_service = SCINVectorSearchService() 