from app import db
from datetime import datetime
import uuid

class DiscoverySession(db.Model):
    """Web discovery sessions for image search"""
    __tablename__ = 'discovery_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    analysis_id = db.Column(db.String(36), db.ForeignKey('image_analyses.id'))
    session_status = db.Column(db.String(50), default='active')
    search_parameters = db.Column(db.JSON)  # Search configuration
    progress_percentage = db.Column(db.Integer, default=0)
    results_found = db.Column(db.Integer, default=0)
    quality_threshold = db.Column(db.Numeric(3, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    discovered_content = db.relationship('DiscoveredContent', backref='discovery_session', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<DiscoverySession {self.id}>'
    
    def to_dict(self):
        """Convert discovery session to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'analysis_id': self.analysis_id,
            'session_status': self.session_status,
            'search_parameters': self.search_parameters,
            'progress_percentage': self.progress_percentage,
            'results_found': self.results_found,
            'quality_threshold': float(self.quality_threshold) if self.quality_threshold else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class DiscoveredContent(db.Model):
    """Content discovered through web scraping"""
    __tablename__ = 'discovered_content'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    discovery_session_id = db.Column(db.String(36), db.ForeignKey('discovery_sessions.id'), nullable=False)
    content_type = db.Column(db.String(100), nullable=False)  # 'image', 'product', 'article', etc.
    source_url = db.Column(db.Text, nullable=False)
    content_url = db.Column(db.Text)
    title = db.Column(db.String(500))
    description = db.Column(db.Text)
    image_urls = db.Column(db.JSON)  # Array of image URLs
    content_metadata = db.Column(db.JSON)  # Additional content metadata
    quality_score = db.Column(db.Numeric(5, 4))
    similarity_score = db.Column(db.Numeric(5, 4))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DiscoveredContent {self.content_type}>'
    
    def to_dict(self):
        """Convert discovered content to dictionary"""
        return {
            'id': self.id,
            'discovery_session_id': self.discovery_session_id,
            'content_type': self.content_type,
            'source_url': self.source_url,
            'content_url': self.content_url,
            'title': self.title,
            'description': self.description,
            'image_urls': self.image_urls,
            'content_metadata': self.content_metadata,
            'quality_score': float(self.quality_score) if self.quality_score else None,
            'similarity_score': float(self.similarity_score) if self.similarity_score else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 