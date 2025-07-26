from app import db
from datetime import datetime
import uuid

class Order(db.Model):
    """Customer orders"""
    __tablename__ = 'orders'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    order_number = db.Column(db.String(100), unique=True, nullable=False)
    order_status = db.Column(db.String(50), default='pending')
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    payment_status = db.Column(db.String(50), default='pending')
    fulfillment_status = db.Column(db.String(50), default='pending')
    shipping_address = db.Column(db.JSON)
    billing_address = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='order', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.order_number}>'
    
    def to_dict(self):
        """Convert order to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'order_number': self.order_number,
            'order_status': self.order_status,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'currency': self.currency,
            'payment_status': self.payment_status,
            'fulfillment_status': self.fulfillment_status,
            'shipping_address': self.shipping_address,
            'billing_address': self.billing_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items],
            'payments': [payment.to_dict() for payment in self.payments]
        }

class OrderItem(db.Model):
    """Individual items within orders"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<OrderItem {self.id}>'
    
    def to_dict(self):
        """Convert order item to dictionary"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'total_price': float(self.total_price) if self.total_price else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'product': self.product.to_dict() if self.product else None
        }

class Payment(db.Model):
    """Payment transactions"""
    __tablename__ = 'payments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    stripe_payment_intent_id = db.Column(db.String(255), unique=True)
    payment_method = db.Column(db.String(100))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    payment_status = db.Column(db.String(50), default='pending')
    processed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Payment {self.id}>'
    
    def to_dict(self):
        """Convert payment to dictionary"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'stripe_payment_intent_id': self.stripe_payment_intent_id,
            'payment_method': self.payment_method,
            'amount': float(self.amount) if self.amount else None,
            'currency': self.currency,
            'payment_status': self.payment_status,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 