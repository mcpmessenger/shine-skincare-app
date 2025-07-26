#!/usr/bin/env python3
"""
Database Setup Script for Shine Skincare App
This script sets up the database with migrations and initial data
"""

import os
import sys
import psycopg2
import boto3
import json
from datetime import datetime
import argparse

def get_aws_secret(secret_name, region='us-east-2'):
    """Get secret from AWS Secrets Manager"""
    try:
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region
        )
        
        response = client.get_secret_value(SecretId=secret_name)
        if 'SecretString' in response:
            return json.loads(response['SecretString'])
    except Exception as e:
        print(f"Error getting secret {secret_name}: {e}")
        return None

def get_database_connection(host, port, database, username, password):
    """Create database connection"""
    try:
        connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=username,
            password=password
        )
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def create_database(host, port, username, password, database_name):
    """Create database if it doesn't exist"""
    try:
        # Connect to default postgres database
        connection = psycopg2.connect(
            host=host,
            port=port,
            database='postgres',
            user=username,
            password=password
        )
        connection.autocommit = True
        cursor = connection.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {database_name}")
            print(f"Database '{database_name}' created successfully")
        else:
            print(f"Database '{database_name}' already exists")
        
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def run_migrations(connection):
    """Run database migrations"""
    try:
        cursor = connection.cursor()
        
        # Create migrations table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id SERIAL PRIMARY KEY,
                migration_name VARCHAR(255) NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Define migrations
        migrations = [
            {
                'name': '001_create_users_table',
                'sql': '''
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        google_id VARCHAR(255) UNIQUE NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        picture_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                '''
            },
            {
                'name': '002_create_user_preferences_table',
                'sql': '''
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        skin_type VARCHAR(50),
                        skin_concerns TEXT[],
                        allergies TEXT[],
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                '''
            },
            {
                'name': '003_create_image_uploads_table',
                'sql': '''
                    CREATE TABLE IF NOT EXISTS image_uploads (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        image_url TEXT NOT NULL,
                        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        analysis_status VARCHAR(50) DEFAULT 'pending'
                    )
                '''
            },
            {
                'name': '004_create_image_analysis_table',
                'sql': '''
                    CREATE TABLE IF NOT EXISTS image_analysis (
                        id SERIAL PRIMARY KEY,
                        image_upload_id INTEGER REFERENCES image_uploads(id) ON DELETE CASCADE,
                        analysis_data JSONB,
                        analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        confidence_score DECIMAL(5,2)
                    )
                '''
            },
            {
                'name': '005_create_products_table',
                'sql': '''
                    CREATE TABLE IF NOT EXISTS products (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        brand VARCHAR(255),
                        category VARCHAR(100),
                        description TEXT,
                        price DECIMAL(10,2),
                        image_url TEXT,
                        ingredients TEXT[],
                        skin_types TEXT[],
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                '''
            },
            {
                'name': '006_create_product_recommendations_table',
                'sql': '''
                    CREATE TABLE IF NOT EXISTS product_recommendations (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                        analysis_id INTEGER REFERENCES image_analysis(id) ON DELETE CASCADE,
                        confidence_score DECIMAL(5,2),
                        recommendation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                '''
            },
            {
                'name': '007_create_orders_table',
                'sql': '''
                    CREATE TABLE IF NOT EXISTS orders (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        stripe_payment_intent_id VARCHAR(255),
                        total_amount DECIMAL(10,2) NOT NULL,
                        status VARCHAR(50) DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                '''
            },
            {
                'name': '008_create_order_items_table',
                'sql': '''
                    CREATE TABLE IF NOT EXISTS order_items (
                        id SERIAL PRIMARY KEY,
                        order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
                        product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                        quantity INTEGER NOT NULL,
                        unit_price DECIMAL(10,2) NOT NULL,
                        total_price DECIMAL(10,2) NOT NULL
                    )
                '''
            }
        ]
        
        # Run each migration
        for migration in migrations:
            # Check if migration already applied
            cursor.execute("SELECT 1 FROM migrations WHERE migration_name = %s", (migration['name'],))
            if not cursor.fetchone():
                cursor.execute(migration['sql'])
                cursor.execute("INSERT INTO migrations (migration_name) VALUES (%s)", (migration['name'],))
                print(f"Applied migration: {migration['name']}")
            else:
                print(f"Migration already applied: {migration['name']}")
        
        connection.commit()
        print("All migrations completed successfully")
        return True
    except Exception as e:
        print(f"Error running migrations: {e}")
        connection.rollback()
        return False

def seed_initial_data(connection):
    """Seed database with initial data"""
    try:
        cursor = connection.cursor()
        
        # Sample products
        products = [
            {
                'name': 'Gentle Daily Cleanser',
                'brand': 'Shine',
                'category': 'cleanser',
                'description': 'A gentle, non-stripping cleanser suitable for all skin types',
                'price': 24.99,
                'image_url': 'https://example.com/cleanser.jpg',
                'ingredients': ['water', 'glycerin', 'cocamidopropyl betaine'],
                'skin_types': ['normal', 'dry', 'oily', 'combination']
            },
            {
                'name': 'Hydrating Moisturizer',
                'brand': 'Shine',
                'category': 'moisturizer',
                'description': 'Lightweight moisturizer with hyaluronic acid for all-day hydration',
                'price': 32.99,
                'image_url': 'https://example.com/moisturizer.jpg',
                'ingredients': ['water', 'hyaluronic acid', 'ceramides', 'niacinamide'],
                'skin_types': ['normal', 'dry', 'combination']
            },
            {
                'name': 'Vitamin C Serum',
                'brand': 'Shine',
                'category': 'serum',
                'description': 'Brightening serum with 15% Vitamin C for radiant skin',
                'price': 45.99,
                'image_url': 'https://example.com/serum.jpg',
                'ingredients': ['ascorbic acid', 'ferulic acid', 'vitamin e'],
                'skin_types': ['normal', 'dry', 'oily', 'combination']
            },
            {
                'name': 'SPF 30 Sunscreen',
                'brand': 'Shine',
                'category': 'sunscreen',
                'description': 'Broad-spectrum sunscreen with zinc oxide',
                'price': 28.99,
                'image_url': 'https://example.com/sunscreen.jpg',
                'ingredients': ['zinc oxide', 'titanium dioxide', 'niacinamide'],
                'skin_types': ['normal', 'dry', 'oily', 'combination']
            }
        ]
        
        # Insert products
        for product in products:
            cursor.execute("""
                INSERT INTO products (name, brand, category, description, price, image_url, ingredients, skin_types)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                product['name'],
                product['brand'],
                product['category'],
                product['description'],
                product['price'],
                product['image_url'],
                product['ingredients'],
                product['skin_types']
            ))
        
        connection.commit()
        print("Initial data seeded successfully")
        return True
    except Exception as e:
        print(f"Error seeding data: {e}")
        connection.rollback()
        return False

def create_indexes(connection):
    """Create database indexes for better performance"""
    try:
        cursor = connection.cursor()
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id)",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_image_uploads_user_id ON image_uploads(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_image_analysis_upload_id ON image_analysis(image_upload_id)",
            "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)",
            "CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand)",
            "CREATE INDEX IF NOT EXISTS idx_product_recommendations_user_id ON product_recommendations(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)",
            "CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        connection.commit()
        print("Database indexes created successfully")
        return True
    except Exception as e:
        print(f"Error creating indexes: {e}")
        connection.rollback()
        return False

def main():
    parser = argparse.ArgumentParser(description='Setup Shine Skincare Database')
    parser.add_argument('--host', required=True, help='Database host')
    parser.add_argument('--port', default=5432, help='Database port')
    parser.add_argument('--username', required=True, help='Database username')
    parser.add_argument('--password', required=True, help='Database password')
    parser.add_argument('--database', default='shine_production', help='Database name')
    parser.add_argument('--region', default='us-east-2', help='AWS region')
    parser.add_argument('--secret-name', help='AWS Secrets Manager secret name')
    
    args = parser.parse_args()
    
    # If secret name provided, get credentials from AWS Secrets Manager
    if args.secret_name:
        secret = get_aws_secret(args.secret_name, args.region)
        if secret:
            args.host = secret.get('host', args.host)
            args.port = secret.get('port', args.port)
            args.username = secret.get('username', args.username)
            args.password = secret.get('password', args.password)
            args.database = secret.get('database', args.database)
    
    print(f"Setting up database: {args.database}")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Username: {args.username}")
    
    # Create database
    if not create_database(args.host, args.port, args.username, args.password, args.database):
        sys.exit(1)
    
    # Connect to the database
    connection = get_database_connection(args.host, args.port, args.database, args.username, args.password)
    if not connection:
        sys.exit(1)
    
    try:
        # Run migrations
        if not run_migrations(connection):
            sys.exit(1)
        
        # Create indexes
        if not create_indexes(connection):
            sys.exit(1)
        
        # Seed initial data
        if not seed_initial_data(connection):
            sys.exit(1)
        
        print("Database setup completed successfully!")
        
    finally:
        connection.close()

if __name__ == "__main__":
    main() 