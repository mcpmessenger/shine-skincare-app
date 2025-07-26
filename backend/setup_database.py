#!/usr/bin/env python3
"""
Database setup script for Shine backend
This script initializes the PostgreSQL database and runs migrations
"""

import os
import sys

from app import create_app, db
from app.models import *  # Import all models

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # For SQLite, the database file will be created automatically
        print("✅ Using SQLite database (no setup required)")
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        sys.exit(1)

def setup_database():
    """Set up the database schema and seed data"""
    try:
        app = create_app()
        
        print("Creating database tables...")
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Seed the database with initial data
            print("Seeding database with initial data...")
            from seed_data import seed_products
            seed_products()
            print("✅ Database seeded successfully!")
            
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        sys.exit(1)

def test_database_connection():
    """Test the database connection"""
    try:
        app = create_app()
        
        with app.app_context():
            # Test a simple query
            from app.models.user import User
            user_count = User.query.count()
            print(f"✅ Database connection successful! Found {user_count} users.")
            
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        sys.exit(1)

def main():
    """Main setup function"""
    print("🚀 Setting up Shine Database...")
    print("=" * 50)
    
    # Step 1: Create database
    print("\n1. Creating database...")
    create_database()
    
    # Step 2: Set up schema and seed data
    print("\n2. Setting up database schema...")
    setup_database()
    
    # Step 3: Test connection
    print("\n3. Testing database connection...")
    test_database_connection()
    
    print("\n" + "=" * 50)
    print("🎉 Database setup completed successfully!")
    print("\nNext steps:")
    print("1. Start the backend server: python run.py")
    print("2. Start the frontend: npm run dev")
    print("3. Test the application at http://localhost:3000")

if __name__ == '__main__':
    main() 