from app import db
from datetime import datetime
import uuid

class Product(db.Model):
    """Product catalog and information"""
    __tablename__ = 'products'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    external_id = db.Column(db.String(255))
    source_platform = db.Column(db.String(100))
    name = db.Column(db.String(500), nullable=False)
    brand = db.Column(db.String(255))
    category = db.Column(db.String(100))
    subcategory = db.Column(db.String(100))
    description = db.Column(db.Text)
    ingredients = db.Column(db.JSON)  # Array of ingredients
    price = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(3), default='USD')
    availability_status = db.Column(db.String(50))
    image_urls = db.Column(db.JSON)  # Array of image URLs
    product_url = db.Column(db.Text)
    rating = db.Column(db.Numeric(3, 2))
    review_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    recommendations = db.relationship('ProductRecommendation', backref='product', cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='product', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def to_dict(self):
        """Convert product to dictionary"""
        return {
            'id': self.id,
            'external_id': self.external_id,
            'source_platform': self.source_platform,
            'name': self.name,
            'brand': self.brand,
            'category': self.category,
            'subcategory': self.subcategory,
            'description': self.description,
            'ingredients': self.ingredients,
            'price': float(self.price) if self.price else None,
            'currency': self.currency,
            'availability_status': self.availability_status,
            'image_urls': self.image_urls,
            'product_url': self.product_url,
            'rating': float(self.rating) if self.rating else None,
            'review_count': self.review_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ProductRecommendation(db.Model):
    """Product recommendations for users"""
    __tablename__ = 'product_recommendations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = db.Column(db.String(36), db.ForeignKey('image_analyses.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False)
    recommendation_score = db.Column(db.Numeric(5, 4))
    recommendation_reason = db.Column(db.Text)
    recommendation_type = db.Column(db.String(100))  # e.g., 'skin_type_match', 'condition_specific', etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    feedback = db.relationship('RecommendationFeedback', backref='recommendation', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ProductRecommendation {self.id}>'
    
    def to_dict(self):
        """Convert recommendation to dictionary"""
        return {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'recommendation_score': float(self.recommendation_score) if self.recommendation_score else None,
            'recommendation_reason': self.recommendation_reason,
            'recommendation_type': self.recommendation_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'product': self.product.to_dict() if self.product else None
        }

class RecommendationFeedback(db.Model):
    """User feedback on recommendations"""
    __tablename__ = 'recommendation_feedback'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recommendation_id = db.Column(db.String(36), db.ForeignKey('product_recommendations.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    feedback_type = db.Column(db.String(50), nullable=False)  # 'like', 'dislike', 'purchase', 'skip', etc.
    rating = db.Column(db.Integer)  # 1-5 rating
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<RecommendationFeedback {self.feedback_type}>'
    
    def to_dict(self):
        """Convert feedback to dictionary"""
        return {
            'id': self.id,
            'recommendation_id': self.recommendation_id,
            'user_id': self.user_id,
            'feedback_type': self.feedback_type,
            'rating': self.rating,
            'comments': self.comments,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 