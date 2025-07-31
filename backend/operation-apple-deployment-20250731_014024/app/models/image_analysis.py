from app import db
from datetime import datetime
import uuid

class ImageUpload(db.Model):
    """Image upload tracking and management"""
    __tablename__ = 'image_uploads'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    original_filename = db.Column(db.String(255))
    file_path = db.Column(db.Text, nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    upload_status = db.Column(db.String(50), default='pending')
    privacy_level = db.Column(db.String(50), default='private')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    # Relationships
    analyses = db.relationship('ImageAnalysis', backref='upload', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ImageUpload {self.id}>'
    
    def to_dict(self):
        """Convert upload to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'upload_status': self.upload_status,
            'privacy_level': self.privacy_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }

class ImageAnalysis(db.Model):
    """Image analysis results and metadata"""
    __tablename__ = 'image_analyses'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    upload_id = db.Column(db.String(36), db.ForeignKey('image_uploads.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    analysis_status = db.Column(db.String(50), default='processing')
    confidence_score = db.Column(db.Numeric(5, 4))
    skin_type = db.Column(db.String(50))
    skin_tone = db.Column(db.String(50))
    detected_conditions = db.Column(db.JSON)  # JSON array of conditions
    analysis_data = db.Column(db.JSON)  # Additional analysis data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    features = db.relationship('AnalysisFeatures', backref='analysis', cascade='all, delete-orphan')
    recommendations = db.relationship('ProductRecommendation', backref='analysis', cascade='all, delete-orphan')
    discovery_sessions = db.relationship('DiscoverySession', backref='analysis', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ImageAnalysis {self.id}>'
    
    def to_dict(self):
        """Convert analysis to dictionary"""
        return {
            'id': self.id,
            'upload_id': self.upload_id,
            'user_id': self.user_id,
            'analysis_status': self.analysis_status,
            'confidence_score': float(self.confidence_score) if self.confidence_score else None,
            'skin_type': self.skin_type,
            'skin_tone': self.skin_tone,
            'detected_conditions': self.detected_conditions,
            'analysis_data': self.analysis_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class AnalysisFeatures(db.Model):
    """Extracted visual features for similarity matching"""
    __tablename__ = 'analysis_features'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = db.Column(db.String(36), db.ForeignKey('image_analyses.id'), nullable=False)
    feature_type = db.Column(db.String(100), nullable=False)
    feature_vector = db.Column(db.JSON)  # Array of feature values
    feature_metadata = db.Column(db.JSON)  # Additional feature data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AnalysisFeatures {self.feature_type}>'
    
    def to_dict(self):
        """Convert features to dictionary"""
        return {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'feature_type': self.feature_type,
            'feature_vector': self.feature_vector,
            'feature_metadata': self.feature_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 