#!/usr/bin/env python3
"""
Database seeding script for Shine backend
Run this script to populate the database with initial test data
"""

from app import create_app, db
from app.models.products import Product
from datetime import datetime

def seed_products():
    """Seed the database with sample skincare products"""
    
    products = [
        {
            'name': 'HydraBoost Serum',
            'brand': 'AquaGlow',
            'category': 'serum',
            'subcategory': 'hydrating',
            'description': 'A powerful hydrating serum infused with hyaluronic acid and ceramides to deeply moisturize and plump the skin.',
            'ingredients': ['Hyaluronic Acid', 'Ceramides', 'Niacinamide', 'Glycerin'],
            'price': 39.99,
            'currency': 'USD',
            'availability_status': 'available',
            'image_urls': ['/placeholder.svg?height=200&width=300'],
            'rating': 4.5,
            'review_count': 127
        },
        {
            'name': 'ClearSkin Acne Treatment',
            'brand': 'DermPure',
            'category': 'treatment',
            'subcategory': 'acne',
            'description': 'Target stubborn breakouts with this salicylic acid and tea tree oil formula, designed to clear pores and reduce inflammation.',
            'ingredients': ['Salicylic Acid', 'Tea Tree Oil', 'Zinc PCA', 'Niacinamide'],
            'price': 24.50,
            'currency': 'USD',
            'availability_status': 'available',
            'image_urls': ['/placeholder.svg?height=200&width=300'],
            'rating': 4.0,
            'review_count': 89
        },
        {
            'name': 'Radiant C Cream',
            'brand': 'VitaBright',
            'category': 'moisturizer',
            'subcategory': 'brightening',
            'description': 'Brighten and even skin tone with this potent Vitamin C cream, packed with antioxidants for a youthful glow.',
            'ingredients': ['Vitamin C', 'Ferulic Acid', 'Vitamin E', 'Hyaluronic Acid'],
            'price': 55.00,
            'currency': 'USD',
            'availability_status': 'available',
            'image_urls': ['/placeholder.svg?height=200&width=300'],
            'rating': 4.8,
            'review_count': 203
        },
        {
            'name': 'Gentle Foaming Cleanser',
            'brand': 'PureSkin',
            'category': 'cleanser',
            'subcategory': 'gentle',
            'description': 'A gentle, non-stripping cleanser that removes impurities while maintaining skin\'s natural moisture barrier.',
            'ingredients': ['Glycerin', 'Aloe Vera', 'Chamomile Extract', 'Panthenol'],
            'price': 18.99,
            'currency': 'USD',
            'availability_status': 'available',
            'image_urls': ['/placeholder.svg?height=200&width=300'],
            'rating': 4.2,
            'review_count': 156
        },
        {
            'name': 'Retinol Night Serum',
            'brand': 'AgeDefy',
            'category': 'serum',
            'subcategory': 'anti-aging',
            'description': 'Advanced retinol formula that reduces fine lines and wrinkles while improving skin texture and tone.',
            'ingredients': ['Retinol', 'Peptides', 'Hyaluronic Acid', 'Vitamin E'],
            'price': 68.00,
            'currency': 'USD',
            'availability_status': 'available',
            'image_urls': ['/placeholder.svg?height=200&width=300'],
            'rating': 4.6,
            'review_count': 94
        },
        {
            'name': 'Oil-Free Moisturizer',
            'brand': 'MatteFinish',
            'category': 'moisturizer',
            'subcategory': 'oil-free',
            'description': 'Lightweight, oil-free moisturizer that hydrates without leaving a greasy residue, perfect for oily skin.',
            'ingredients': ['Niacinamide', 'Hyaluronic Acid', 'Ceramides', 'Zinc PCA'],
            'price': 32.99,
            'currency': 'USD',
            'availability_status': 'available',
            'image_urls': ['/placeholder.svg?height=200&width=300'],
            'rating': 4.3,
            'review_count': 178
        },
        {
            'name': 'Sensitive Skin Relief Cream',
            'brand': 'CalmCare',
            'category': 'moisturizer',
            'subcategory': 'sensitive',
            'description': 'Soothing cream specifically formulated for sensitive skin, reducing redness and irritation.',
            'ingredients': ['Centella Asiatica', 'Aloe Vera', 'Panthenol', 'Ceramides'],
            'price': 28.50,
            'currency': 'USD',
            'availability_status': 'available',
            'image_urls': ['/placeholder.svg?height=200&width=300'],
            'rating': 4.7,
            'review_count': 112
        },
        {
            'name': 'Exfoliating Toner',
            'brand': 'GlowUp',
            'category': 'toner',
            'subcategory': 'exfoliating',
            'description': 'Gentle exfoliating toner with AHAs and BHAs to unclog pores and reveal brighter, smoother skin.',
            'ingredients': ['Glycolic Acid', 'Salicylic Acid', 'Lactic Acid', 'Witch Hazel'],
            'price': 22.99,
            'currency': 'USD',
            'availability_status': 'available',
            'image_urls': ['/placeholder.svg?height=200&width=300'],
            'rating': 4.1,
            'review_count': 67
        }
    ]
    
    for product_data in products:
        # Check if product already exists
        existing_product = Product.query.filter_by(
            name=product_data['name'],
            brand=product_data['brand']
        ).first()
        
        if not existing_product:
            product = Product(**product_data)
            db.session.add(product)
            print(f"Added product: {product_data['name']} by {product_data['brand']}")
        else:
            print(f"Product already exists: {product_data['name']} by {product_data['brand']}")
    
    db.session.commit()
    print("Database seeding completed!")

def main():
    """Main seeding function"""
    app = create_app()
    
    with app.app_context():
        print("Starting database seeding...")
        seed_products()
        print("Seeding completed successfully!")

if __name__ == '__main__':
    main() 