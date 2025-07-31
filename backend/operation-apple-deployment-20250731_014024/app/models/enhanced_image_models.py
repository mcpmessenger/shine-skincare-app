from app import db
from datetime import datetime
import uuid

class Image(db.Model):
    """Enhanced image model for FAISS and Google Vision AI integration"""
    __tablename__ = 'images'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    image_url = db.Column(db.Text, nullable=False)  # URL to image in Supabase Storage
    faiss_index_id = db.Column(db.Integer)  # ID of the image in the FAISS index
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    analyses = db.relationship('Analysis', backref='image', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Image {self.id}>'
    
    def to_dict(self):
        """Convert image to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'image_url': self.image_url,
            'faiss_index_id': self.faiss_index_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Analysis(db.Model):
    """Google Vision AI analysis results"""
    __tablename__ = 'analyses'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    image_id = db.Column(db.String(36), db.ForeignKey('images.id'), nullable=False)
    google_vision_result = db.Column(db.JSON)  # Full JSON response from Google Vision AI
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Analysis {self.id}>'
    
    def to_dict(self):
        """Convert analysis to dictionary"""
        return {
            'id': self.id,
            'image_id': self.image_id,
            'google_vision_result': self.google_vision_result,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ImageVector(db.Model):
    """Image vectors for FAISS similarity search"""
    __tablename__ = 'image_vectors'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    image_id = db.Column(db.String(36), db.ForeignKey('images.id'), nullable=False)
    vector_data = db.Column(db.JSON)  # Vector embedding as JSON array
    vector_dimension = db.Column(db.Integer, nullable=False)
    model_name = db.Column(db.String(100), nullable=False)  # e.g., 'resnet50'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ImageVector {self.id}>'
    
    def to_dict(self):
        """Convert vector to dictionary"""
        return {
            'id': self.id,
            'image_id': self.image_id,
            'vector_dimension': self.vector_dimension,
            'model_name': self.model_name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 