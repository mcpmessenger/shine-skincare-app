# Design Document

## Overview

The Backend AI Upgrade for Shine Skin Collective involves enhancing the existing AI-powered skin analysis system with three major improvements: transitioning from L2 distance to cosine similarity for vector search, implementing demographic-weighted search capabilities, and creating an enhanced skin type classification system. The design follows a microservices architecture pattern, integrating seamlessly with the existing Flask backend deployed on Vercel.

## Architecture

### High-Level Architecture

```mermaid
graph TB
    A[Client Request] --> B[Flask API Layer]
    B --> C[Enhanced Analysis Service]
    C --> D[FAISS Service - Cosine Similarity]
    C --> E[Demographic Weighted Search]
    C --> F[Enhanced Skin Type Classifier]
    
    D --> G[Vector Index - Normalized]
    E --> H[Supabase Service]
    E --> D
    F --> I[Fitzpatrick Model]
    F --> J[Monk Scale Model]
    
    H --> K[Demographic Metadata]
    G --> L[Similarity Results]
    
    style C fill:#e1f5fe
    style D fill:#f3e5f5
    style E fill:#e8f5e8
    style F fill:#fff3e0
```

### Service Dependencies

- **Enhanced Analysis Service**: Orchestrates the entire analysis workflow
- **FAISS Service**: Handles vector similarity search with cosine similarity
- **Demographic Weighted Search**: Combines visual and demographic similarity
- **Enhanced Skin Type Classifier**: Provides multi-scale skin classification
- **Supabase Service**: Manages demographic metadata and analysis storage

## Components and Interfaces

### 1. Enhanced FAISS Service

**Purpose**: Implement cosine similarity-based vector search with proper normalization

**Key Methods**:
```python
class FAISSService:
    def __init__(self, dimension: int = 2048)
    def add_vector(self, vector: np.ndarray, image_id: str) -> bool
    def search_similar(self, query_vector: np.ndarray, k: int = 5) -> List[Tuple[str, float]]
    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray
```

**Implementation Details**:
- Uses `faiss.IndexFlatIP` for inner product calculations
- All vectors are L2-normalized before indexing and searching
- Handles zero-vector edge cases gracefully
- Converts similarity scores to distance format for backward compatibility

### 2. Demographic Weighted Search Service

**Purpose**: Combine visual similarity with demographic context for personalized results

**Key Methods**:
```python
class DemographicWeightedSearch:
    def __init__(self, faiss_service: FAISSService, supabase_service: SupabaseService)
    def search_with_demographics(self, query_vector, user_demographics, k=10) -> List[Tuple[str, float]]
    def _extract_demographics(self, analysis) -> Dict[str, str]
    def _calculate_demographic_similarity(self, user_demographics, result_demographics) -> float
```

**Weighting Algorithm**:
- Visual similarity weight: 70% (configurable)
- Demographic similarity weight: 30% (configurable)
- Ethnicity matching: 60% of demographic weight
- Skin type matching: 30% of demographic weight
- Age group matching: 10% of demographic weight

### 3. Enhanced Skin Type Classifier

**Purpose**: Provide accurate skin type classification using multiple scales and ethnicity context

**Key Methods**:
```python
class EnhancedSkinTypeClassifier:
    def __init__(self)
    def classify_skin_type(self, image_data, ethnicity=None) -> Dict[str, Any]
    def _extract_skin_regions(self, image_data) -> np.ndarray
    def _classify_fitzpatrick(self, skin_regions) -> str
    def _classify_monk(self, skin_regions) -> int
    def _apply_ethnicity_context(self, fitzpatrick_type, monk_tone, ethnicity) -> Tuple[str, int]
    def _calculate_confidence(self, skin_regions, ethnicity) -> float
```

**Classification Scales**:
- **Fitzpatrick Scale**: Types I-VI for sun sensitivity classification
- **Monk Scale**: 1-10 scale for inclusive skin tone representation
- **Ethnicity Adjustments**: Context-based refinements for accuracy

### 4. API Integration Layer

**Enhanced Endpoints**:
```python
@app.route('/api/v2/analyze/guest', methods=['POST'])
def analyze_guest_enhanced()

@app.route('/api/v2/similarity/demographic', methods=['POST'])
def similarity_search_demographic()

@app.route('/api/v2/classify/skin-type', methods=['POST'])
def classify_skin_type_enhanced()
```

## Data Models

### Vector Storage Model
```python
@dataclass
class NormalizedVector:
    image_id: str
    vector: np.ndarray  # L2-normalized
    dimension: int
    created_at: datetime
```

### Demographic Profile Model
```python
@dataclass
class DemographicProfile:
    ethnicity: Optional[str]
    skin_type: Optional[str]
    age_group: Optional[str]
    fitzpatrick_type: Optional[str]
    monk_tone: Optional[int]
```

### Analysis Result Model
```python
@dataclass
class EnhancedAnalysisResult:
    image_id: str
    visual_similarity_score: float
    demographic_similarity_score: float
    combined_score: float
    fitzpatrick_classification: str
    monk_classification: int
    confidence_score: float
    ethnicity_considered: bool
```

### Similarity Search Result Model
```python
@dataclass
class SimilarityResult:
    image_id: str
    distance: float
    demographic_match: bool
    metadata: Dict[str, Any]
```

## Error Handling

### Vector Processing Errors
- **Zero Vector Handling**: Graceful fallback for edge cases
- **Dimension Mismatch**: Validation and error reporting
- **Normalization Failures**: Robust error recovery

### Demographic Search Errors
- **Missing Metadata**: Fallback to visual-only search
- **Invalid Demographics**: Input validation and sanitization
- **Database Connection Issues**: Retry logic and graceful degradation

### Classification Errors
- **Model Loading Failures**: Fallback to basic classification
- **Image Processing Errors**: Clear error messages and recovery
- **Confidence Calculation Issues**: Default confidence values

### API Error Responses
```python
{
    "error": {
        "code": "VECTOR_NORMALIZATION_FAILED",
        "message": "Unable to normalize input vector",
        "details": "Vector contains only zero values",
        "timestamp": "2025-07-26T10:30:00Z"
    }
}
```

## Testing Strategy

### Unit Testing
- **Vector Normalization**: Test edge cases and mathematical correctness
- **Demographic Similarity**: Validate scoring algorithms
- **Classification Logic**: Test ethnicity adjustments and confidence calculations
- **Error Handling**: Comprehensive error scenario coverage

### Integration Testing
- **Service Interactions**: Test FAISS ↔ Demographic Search integration
- **Database Operations**: Validate Supabase metadata retrieval
- **API Endpoints**: End-to-end request/response validation
- **Performance Testing**: Load testing with concurrent requests

### Validation Testing
- **Similarity Accuracy**: Compare results with curated test datasets
- **Demographic Relevance**: Validate improved personalization
- **Classification Accuracy**: Test against known skin type examples
- **Cross-Demographic Testing**: Ensure fairness across ethnic groups

### Performance Benchmarks
- **Search Response Time**: < 2 seconds for demographic-weighted search
- **Classification Speed**: < 1 second for skin type classification
- **Memory Usage**: Efficient vector storage and retrieval
- **Concurrent Users**: Support for 100+ simultaneous requests

## Deployment Considerations

### Vercel Serverless Constraints
- **Cold Start Optimization**: Minimize initialization time for new services
- **Memory Limits**: Efficient vector storage and model loading
- **Execution Time**: Optimize for serverless function timeouts
- **Stateless Design**: Ensure all services are stateless and scalable

### Environment Configuration
```python
# Required environment variables
FAISS_DIMENSION=2048
DEMOGRAPHIC_WEIGHT=0.3
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
CLASSIFICATION_CONFIDENCE_THRESHOLD=0.7
```

### Monitoring and Observability
- **Performance Metrics**: Track search latency and accuracy
- **Error Rates**: Monitor classification and search failures
- **Usage Analytics**: Track demographic search adoption
- **Model Performance**: Monitor classification confidence trends