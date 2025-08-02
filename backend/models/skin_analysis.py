"""
Data Models for Operation Right Brain 🧠 - Skin Analysis
Defines the data structures for skin analysis results and SCIN matches.

Author: Manus AI
Date: August 2, 2025
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class SCINMatch:
    """
    Represents a match from the SCIN dataset similarity search.
    """
    case_id: str
    condition_name: str
    description: str
    symptoms: List[str]
    recommendations: List[str]
    severity: str  # 'mild', 'moderate', 'severe', 'unknown'
    similarity_score: float  # 0.0 to 1.0
    image_path: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

@dataclass
class SkinAnalysisResult:
    """
    Represents the complete result of a skin analysis.
    Implements BR6 & BR7: Structured skin analysis results.
    """
    confidence: float  # Overall confidence score (0.0 to 100.0)
    conditions: List[Dict[str, Any]]  # List of detected conditions
    recommendations: List[str]  # Personalized recommendations
    message: str  # Human-readable message
    analysis_id: Optional[str] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        """Set default values after initialization."""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
        if self.analysis_id is None:
            self.analysis_id = f"analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "analysis_id": self.analysis_id,
            "confidence": self.confidence,
            "conditions": self.conditions,
            "recommendations": self.recommendations,
            "message": self.message,
            "timestamp": self.timestamp
        }
    
    def get_top_condition(self) -> Optional[Dict[str, Any]]:
        """Get the condition with highest confidence."""
        if not self.conditions:
            return None
        return max(self.conditions, key=lambda c: c.get('confidence', 0))
    
    def get_conditions_by_severity(self, severity: str) -> List[Dict[str, Any]]:
        """Get conditions filtered by severity."""
        return [c for c in self.conditions if c.get('severity') == severity]
    
    def has_high_confidence(self, threshold: float = 80.0) -> bool:
        """Check if the analysis has high confidence."""
        return self.confidence >= threshold

@dataclass
class SkinAnalysisRequest:
    """
    Represents a skin analysis request from the frontend.
    """
    image_data: bytes
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    analysis_type: str = "enhanced"  # 'basic', 'enhanced', 'medical'
    include_metadata: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging (excluding image data)."""
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "analysis_type": self.analysis_type,
            "include_metadata": self.include_metadata,
            "image_size_bytes": len(self.image_data)
        }

@dataclass
class AnalysisMetadata:
    """
    Metadata about the analysis process.
    """
    processing_time_ms: float
    face_detected: bool
    embedding_dimensions: int
    scin_matches_found: int
    api_calls_made: int
    errors_encountered: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

@dataclass
class ConditionDetails:
    """
    Detailed information about a skin condition.
    """
    name: str
    description: str
    symptoms: List[str]
    causes: List[str]
    risk_factors: List[str]
    treatment_options: List[str]
    prevention_tips: List[str]
    severity_levels: List[str]
    related_conditions: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

@dataclass
class Recommendation:
    """
    A personalized recommendation for the user.
    """
    title: str
    description: str
    category: str  # 'immediate', 'lifestyle', 'medical', 'prevention'
    priority: int  # 1 (highest) to 5 (lowest)
    actionable: bool
    source: str  # 'ai_analysis', 'medical_guidelines', 'user_history'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

class SkinAnalysisBuilder:
    """
    Builder class for constructing skin analysis results.
    """
    
    def __init__(self):
        self.conditions = []
        self.recommendations = []
        self.metadata = {}
    
    def add_condition(self, condition: Dict[str, Any]) -> 'SkinAnalysisBuilder':
        """Add a detected condition."""
        self.conditions.append(condition)
        return self
    
    def add_recommendation(self, recommendation: str) -> 'SkinAnalysisBuilder':
        """Add a recommendation."""
        self.recommendations.append(recommendation)
        return self
    
    def set_confidence(self, confidence: float) -> 'SkinAnalysisBuilder':
        """Set the overall confidence score."""
        self.metadata['confidence'] = confidence
        return self
    
    def set_message(self, message: str) -> 'SkinAnalysisBuilder':
        """Set the analysis message."""
        self.metadata['message'] = message
        return self
    
    def build(self) -> SkinAnalysisResult:
        """Build the final skin analysis result."""
        confidence = self.metadata.get('confidence', 0.0)
        message = self.metadata.get('message', 'Analysis completed.')
        
        return SkinAnalysisResult(
            confidence=confidence,
            conditions=self.conditions,
            recommendations=self.recommendations,
            message=message
        )

# Utility functions for working with skin analysis data

def calculate_confidence_score(matches: List[SCINMatch]) -> float:
    """
    Calculate overall confidence score based on SCIN matches.
    
    Args:
        matches: List of SCIN matches
        
    Returns:
        Confidence score (0.0 to 100.0)
    """
    if not matches:
        return 0.0
    
    # Weight by similarity score and number of matches
    total_score = sum(match.similarity_score for match in matches)
    avg_score = total_score / len(matches)
    
    # Convert to percentage and cap at 95%
    confidence = min(avg_score * 100, 95.0)
    
    return confidence

def categorize_conditions(conditions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Categorize conditions by severity.
    
    Args:
        conditions: List of condition dictionaries
        
    Returns:
        Dictionary with conditions grouped by severity
    """
    categorized = {
        'mild': [],
        'moderate': [],
        'severe': [],
        'unknown': []
    }
    
    for condition in conditions:
        severity = condition.get('severity', 'unknown')
        if severity in categorized:
            categorized[severity].append(condition)
        else:
            categorized['unknown'].append(condition)
    
    return categorized

def generate_summary_message(conditions: List[Dict[str, Any]], confidence: float) -> str:
    """
    Generate a human-readable summary message.
    
    Args:
        conditions: List of detected conditions
        confidence: Overall confidence score
        
    Returns:
        Summary message string
    """
    if not conditions:
        return "No skin conditions were detected in your image. Please ensure good lighting and a clear view of the affected area."
    
    top_condition = max(conditions, key=lambda c: c.get('confidence', 0))
    condition_name = top_condition.get('name', 'skin condition')
    
    if confidence >= 80:
        confidence_level = "high"
    elif confidence >= 60:
        confidence_level = "moderate"
    else:
        confidence_level = "low"
    
    return f"Analysis detected {len(conditions)} potential skin condition(s) with {confidence_level} confidence. The most likely condition is {condition_name}. Please consult a dermatologist for professional evaluation." 