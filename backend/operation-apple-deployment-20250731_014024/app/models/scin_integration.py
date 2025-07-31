from app import db
from datetime import datetime
import uuid
import json

class SCINProcessedImage(db.Model):
    """Track processed SCIN dataset images"""
    __tablename__ = 'scin_processed_images'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = db.Column(db.String(100), unique=True, nullable=False)
    image_filename = db.Column(db.String(255), nullable=False)
    gcs_path = db.Column(db.Text, nullable=False)
    
    # SCIN metadata
    condition = db.Column(db.String(100))
    skin_type = db.Column(db.String(50))
    skin_tone = db.Column(db.String(50))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    
    # Processing status
    vectorized = db.Column(db.Boolean, default=False)
    faiss_indexed = db.Column(db.Boolean, default=False)
    processing_status = db.Column(db.String(50), default='pending')
    error_message = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    # Relationships
    similarity_results = db.relationship('SCINSimilarityResult', backref='processed_image', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SCINProcessedImage {self.case_id}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'case_id': self.case_id,
            'image_filename': self.image_filename,
            'gcs_path': self.gcs_path,
            'condition': self.condition,
            'skin_type': self.skin_type,
            'skin_tone': self.skin_tone,
            'age': self.age,
            'gender': self.gender,
            'vectorized': self.vectorized,
            'faiss_indexed': self.faiss_indexed,
            'processing_status': self.processing_status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }

class SCINSimilarityResult(db.Model):
    """Track similarity search results"""
    __tablename__ = 'scin_similarity_results'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query_image_id = db.Column(db.String(36), db.ForeignKey('scin_processed_images.id'), nullable=False)
    similar_image_id = db.Column(db.String(36), db.ForeignKey('scin_processed_images.id'), nullable=False)
    
    # Similarity metrics
    distance = db.Column(db.Float, nullable=False)
    similarity_score = db.Column(db.Float)
    
    # Search metadata
    search_conditions = db.Column(db.JSON)  # Conditions used in search
    search_skin_types = db.Column(db.JSON)  # Skin types used in search
    rank = db.Column(db.Integer)  # Rank in search results
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SCINSimilarityResult {self.query_image_id} -> {self.similar_image_id}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'query_image_id': self.query_image_id,
            'similar_image_id': self.similar_image_id,
            'distance': self.distance,
            'similarity_score': self.similarity_score,
            'search_conditions': self.search_conditions,
            'search_skin_types': self.search_skin_types,
            'rank': self.rank,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SCINIntegrationStatus(db.Model):
    """Track SCIN integration status and metadata"""
    __tablename__ = 'scin_integration_status'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Integration status
    scin_loaded = db.Column(db.Boolean, default=False)
    vectors_generated = db.Column(db.Boolean, default=False)
    faiss_populated = db.Column(db.Boolean, default=False)
    
    # Dataset statistics
    total_records = db.Column(db.Integer, default=0)
    processed_records = db.Column(db.Integer, default=0)
    successful_vectors = db.Column(db.Integer, default=0)
    failed_vectors = db.Column(db.Integer, default=0)
    
    # Configuration
    batch_size = db.Column(db.Integer, default=100)
    max_images = db.Column(db.Integer)
    feature_dimension = db.Column(db.Integer, default=2048)
    model_name = db.Column(db.String(100), default='resnet50')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SCINIntegrationStatus {self.id}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'scin_loaded': self.scin_loaded,
            'vectors_generated': self.vectors_generated,
            'faiss_populated': self.faiss_populated,
            'total_records': self.total_records,
            'processed_records': self.processed_records,
            'successful_vectors': self.successful_vectors,
            'failed_vectors': self.failed_vectors,
            'batch_size': self.batch_size,
            'max_images': self.max_images,
            'feature_dimension': self.feature_dimension,
            'model_name': self.model_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_update': self.last_update.isoformat() if self.last_update else None
        }

class SCINSearchSession(db.Model):
    """Track similarity search sessions"""
    __tablename__ = 'scin_search_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Search parameters
    query_image_path = db.Column(db.Text, nullable=False)
    k_results = db.Column(db.Integer, default=5)
    conditions_filter = db.Column(db.JSON)
    skin_types_filter = db.Column(db.JSON)
    skin_tones_filter = db.Column(db.JSON)
    
    # Search results
    results_count = db.Column(db.Integer, default=0)
    search_duration_ms = db.Column(db.Integer)
    
    # Status
    search_status = db.Column(db.String(50), default='completed')
    error_message = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    search_results = db.relationship('SCINSearchResult', backref='search_session', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SCINSearchSession {self.id}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'query_image_path': self.query_image_path,
            'k_results': self.k_results,
            'conditions_filter': self.conditions_filter,
            'skin_types_filter': self.skin_types_filter,
            'skin_tones_filter': self.skin_tones_filter,
            'results_count': self.results_count,
            'search_duration_ms': self.search_duration_ms,
            'search_status': self.search_status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class SCINSearchResult(db.Model):
    """Individual search results within a session"""
    __tablename__ = 'scin_search_results'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    search_session_id = db.Column(db.String(36), db.ForeignKey('scin_search_sessions.id'), nullable=False)
    similar_image_id = db.Column(db.String(36), db.ForeignKey('scin_processed_images.id'), nullable=False)
    
    # Result metrics
    distance = db.Column(db.Float, nullable=False)
    similarity_score = db.Column(db.Float)
    rank = db.Column(db.Integer, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SCINSearchResult {self.search_session_id} rank {self.rank}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'search_session_id': self.search_session_id,
            'similar_image_id': self.similar_image_id,
            'distance': self.distance,
            'similarity_score': self.similarity_score,
            'rank': self.rank,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 