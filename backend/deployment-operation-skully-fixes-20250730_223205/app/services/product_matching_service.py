import os
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class Product:
    """💀☠️ Operation Skully Product Model"""
    def __init__(self, id: str, name: str, brand: str, category: str, 
                 price: float, image_url: str, description: str, 
                 ingredients: List[str], match_score: float = 0.0):
        self.id = id
        self.name = name
        self.brand = brand
        self.category = category
        self.price = price
        self.image_url = image_url
        self.description = description
        self.ingredients = ingredients
        self.match_score = match_score
        self.matching_ingredients = []

class ProductMatchingService:
    """💀☠️ Operation Skully Product Matching Service"""
    
    def __init__(self, db_connection=None):
        """
        Initialize the product matching service
        As specified in Operation_Skully.md section 3.5
        """
        self.db = db_connection
        self.products = self._load_mock_products()  # 💀☠️ Operation Skully: Mock data for now
        
    def match_products_to_ingredients(self, recommended_ingredients: List[str]) -> List[Product]:
        """
        💀☠️ Operation Skully: Match recommended ingredients to actual products
        Implements the core logic from Operation_Skully.md section 3.5
        """
        try:
            logger.info(f"💀☠️ Operation Skully: Matching {len(recommended_ingredients)} ingredients to products")
            
            matching_products = []
            
            for ingredient in recommended_ingredients:
                products = self.get_products_by_ingredient(ingredient)
                for product in products:
                    product.match_score = self.calculate_match_score(product, recommended_ingredients)
                    product.matching_ingredients = self.get_matching_ingredients(product, recommended_ingredients)
                    matching_products.append(product)
            
            # 💀☠️ Operation Skully: Sort by match score as specified in architecture
            sorted_products = sorted(matching_products, key=lambda p: p.match_score, reverse=True)
            
            logger.info(f"💀☠️ Operation Skully: Found {len(sorted_products)} matching products")
            return sorted_products
            
        except Exception as e:
            logger.error(f"💀☠️ Operation Skully Error: Failed to match products: {e}")
            return []
    
    def get_products_by_ingredient(self, ingredient: str) -> List[Product]:
        """
        💀☠️ Operation Skully: Query database for products containing specific ingredient
        Uses the schema from Operation_Skully.md section 3.6
        """
        matching_products = []
        
        for product in self.products:
            if ingredient.lower() in [ing.lower() for ing in product.ingredients]:
                matching_products.append(product)
        
        return matching_products
    
    def calculate_match_score(self, product: Product, recommended_ingredients: List[str]) -> float:
        """
        💀☠️ Operation Skully: Calculate how well a product matches the user's needs
        """
        product_ingredients = set([ing.lower() for ing in product.ingredients])
        recommended_set = set([ing.lower() for ing in recommended_ingredients])
        
        # Calculate overlap
        overlap = len(product_ingredients.intersection(recommended_set))
        total_recommended = len(recommended_set)
        
        if total_recommended == 0:
            return 0.0
        
        # 💀☠️ Operation Skully: Boost score for products with more matching ingredients
        base_score = overlap / total_recommended
        boost_factor = min(overlap / 3.0, 1.0)  # Boost up to 100% for 3+ matching ingredients
        
        return min(base_score + boost_factor, 1.0)
    
    def get_matching_ingredients(self, product: Product, recommended_ingredients: List[str]) -> List[str]:
        """
        💀☠️ Operation Skully: Get list of ingredients that match user's needs
        """
        product_ingredients = set([ing.lower() for ing in product.ingredients])
        recommended_set = set([ing.lower() for ing in recommended_ingredients])
        
        matching = product_ingredients.intersection(recommended_set)
        return list(matching)
    
    def _load_mock_products(self) -> List[Product]:
        """
        💀☠️ Operation Skully: Load mock product data (50-100 products as specified)
        In production, this would query the database from Operation_Skully.md schema
        """
        mock_products = [
            Product(
                id="1",
                name="Gentle Foaming Cleanser",
                brand="CeraVe",
                category="cleanser",
                price=14.99,
                image_url="/products/cerave-cleanser.jpg",
                description="Non-comedogenic cleanser with ceramides",
                ingredients=["ceramides", "glycerin", "hyaluronic_acid"]
            ),
            Product(
                id="2",
                name="Hyaluronic Acid Serum",
                brand="The Ordinary",
                category="serum",
                price=7.99,
                image_url="/products/ordinary-ha.jpg",
                description="Hydrating serum for all skin types",
                ingredients=["hyaluronic_acid", "sodium_hyaluronate"]
            ),
            Product(
                id="3",
                name="Salicylic Acid Treatment",
                brand="Paula's Choice",
                category="treatment",
                price=29.99,
                image_url="/products/paula-choice-bha.jpg",
                description="Exfoliating treatment for acne",
                ingredients=["salicylic_acid", "niacinamide", "vitamin_c"]
            ),
            Product(
                id="4",
                name="Ceramide Moisturizer",
                brand="Drunk Elephant",
                category="moisturizer",
                price=68.00,
                image_url="/products/drunk-elephant-moisturizer.jpg",
                description="Rich moisturizer for dry skin",
                ingredients=["ceramides", "hyaluronic_acid", "cholesterol"]
            ),
            Product(
                id="5",
                name="Niacinamide Serum",
                brand="The Ordinary",
                category="serum",
                price=5.99,
                image_url="/products/ordinary-niacinamide.jpg",
                description="Brightening and pore-refining serum",
                ingredients=["niacinamide", "zinc", "hyaluronic_acid"]
            ),
            Product(
                id="6",
                name="Vitamin C Serum",
                brand="SkinCeuticals",
                category="serum",
                price=169.00,
                image_url="/products/skinceuticals-vitamin-c.jpg",
                description="Antioxidant serum for brightening",
                ingredients=["vitamin_c", "vitamin_e", "ferulic_acid"]
            ),
            Product(
                id="7",
                name="Centella Asiatica Serum",
                brand="Purito",
                category="serum",
                price=12.99,
                image_url="/products/purito-centella.jpg",
                description="Soothing serum for sensitive skin",
                ingredients=["centella_asiatica", "niacinamide", "hyaluronic_acid"]
            ),
            Product(
                id="8",
                name="Aloe Vera Gel",
                brand="Nature Republic",
                category="moisturizer",
                price=8.99,
                image_url="/products/nature-republic-aloe.jpg",
                description="Soothing gel for irritated skin",
                ingredients=["aloe_vera", "glycerin", "centella_asiatica"]
            ),
            Product(
                id="9",
                name="Tea Tree Oil Treatment",
                brand="The Body Shop",
                category="treatment",
                price=15.99,
                image_url="/products/body-shop-tea-tree.jpg",
                description="Targeted treatment for acne",
                ingredients=["tea_tree_oil", "salicylic_acid", "niacinamide"]
            ),
            Product(
                id="10",
                name="Green Tea Extract Serum",
                brand="Innisfree",
                category="serum",
                price=11.99,
                image_url="/products/innisfree-green-tea.jpg",
                description="Antioxidant serum for all skin types",
                ingredients=["green_tea", "niacinamide", "hyaluronic_acid"]
            )
        ]
        
        logger.info(f"💀☠️ Operation Skully: Loaded {len(mock_products)} mock products")
        return mock_products
    
    def is_available(self) -> bool:
        """💀☠️ Operation Skully: Check if the service is available"""
        return True 