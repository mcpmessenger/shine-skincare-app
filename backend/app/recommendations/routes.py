from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.recommendations import recommendations_bp
from app.models.products import Product, ProductRecommendation, RecommendationFeedback
from app.models.image_analysis import ImageAnalysis
from app.models.user import User, UserPreferences
from app import db
from datetime import datetime, timedelta
import random

def generate_recommendations(analysis_id, user_id, limit=10):
    """Generate product recommendations based on analysis and user preferences"""
    try:
        # Get analysis data
        analysis = ImageAnalysis.query.get(analysis_id)
        if not analysis:
            return []
        
        # Get user preferences
        user = User.query.get(user_id)
        preferences = user.preferences if user else None
        
        # Get all available products (in production, this would be filtered by availability)
        products = Product.query.filter_by(availability_status='available').limit(100).all()
        
        recommendations = []
        
        for product in products:
            # Calculate recommendation score based on various factors
            score = 0.0
            reason_parts = []
            
            # Factor 1: Skin type matching (if available)
            if analysis.skin_type and product.ingredients:
                # Simple skin type matching logic
                if analysis.skin_type == 'dry' and any('hydrating' in str(ing).lower() for ing in product.ingredients):
                    score += 0.3
                    reason_parts.append("Hydrating formula for dry skin")
                elif analysis.skin_type == 'oily' and any('oil-free' in str(ing).lower() for ing in product.ingredients):
                    score += 0.3
                    reason_parts.append("Oil-free formula for oily skin")
            
            # Factor 2: Condition-specific recommendations
            if analysis.detected_conditions:
                for condition in analysis.detected_conditions:
                    if condition.get('type') == 'acne' and any('salicylic' in str(ing).lower() for ing in (product.ingredients or [])):
                        score += 0.4
                        reason_parts.append("Contains salicylic acid for acne treatment")
                    elif condition.get('type') == 'aging' and any('retinol' in str(ing).lower() for ing in (product.ingredients or [])):
                        score += 0.4
                        reason_parts.append("Contains retinol for anti-aging")
            
            # Factor 3: Brand preference (if user has preferences)
            if preferences and preferences.preferred_brands:
                if product.brand in preferences.preferred_brands:
                    score += 0.2
                    reason_parts.append("From your preferred brand")
            
            # Factor 4: Price range (if user has preferences)
            if preferences and preferences.price_range_min and preferences.price_range_max:
                if product.price and preferences.price_range_min <= product.price <= preferences.price_range_max:
                    score += 0.1
                    reason_parts.append("Within your price range")
            
            # Factor 5: Product rating
            if product.rating:
                score += min(product.rating / 5.0, 0.2)
                reason_parts.append(f"Highly rated ({product.rating}/5)")
            
            # Add some randomness to avoid always showing the same products
            score += random.uniform(0, 0.1)
            
            # Only include products with a minimum score
            if score > 0.1:
                recommendations.append({
                    'product': product,
                    'score': min(score, 1.0),
                    'reason': '; '.join(reason_parts) if reason_parts else "Recommended based on your skin analysis"
                })
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:limit]
        
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return []

@recommendations_bp.route('/<analysis_id>', methods=['GET'])
@jwt_required()
def get_recommendations(analysis_id):
    """Get product recommendations for a specific analysis"""
    try:
        user_id = get_jwt_identity()
        
        # Verify analysis belongs to user
        analysis = ImageAnalysis.query.filter_by(id=analysis_id, user_id=user_id).first()
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        # Get query parameters
        category = request.args.get('category')
        price_range = request.args.get('price_range')
        brand_preference = request.args.get('brand_preference')
        availability = request.args.get('availability', 'available')
        limit = min(request.args.get('limit', 10, type=int), 50)
        
        # Check if recommendations already exist
        existing_recommendations = ProductRecommendation.query.filter_by(
            analysis_id=analysis_id
        ).all()
        
        if not existing_recommendations:
            # Generate new recommendations
            recommendations_data = generate_recommendations(analysis_id, user_id, limit)
            
            # Save recommendations to database
            for rec_data in recommendations_data:
                recommendation = ProductRecommendation(
                    analysis_id=analysis_id,
                    user_id=user_id,
                    product_id=rec_data['product'].id,
                    recommendation_score=rec_data['score'],
                    recommendation_reason=rec_data['reason'],
                    recommendation_type='analysis_based'
                )
                db.session.add(recommendation)
            
            db.session.commit()
            
            # Get the saved recommendations
            existing_recommendations = ProductRecommendation.query.filter_by(
                analysis_id=analysis_id
            ).all()
        
        # Apply filters
        filtered_recommendations = []
        for rec in existing_recommendations:
            product = rec.product
            
            # Category filter
            if category and product.category != category:
                continue
            
            # Price range filter
            if price_range:
                min_price, max_price = map(float, price_range.split('-'))
                if not product.price or not (min_price <= product.price <= max_price):
                    continue
            
            # Brand preference filter
            if brand_preference and product.brand != brand_preference:
                continue
            
            # Availability filter
            if availability and product.availability_status != availability:
                continue
            
            filtered_recommendations.append(rec)
        
        # Sort by recommendation score
        filtered_recommendations.sort(key=lambda x: x.recommendation_score or 0, reverse=True)
        
        # Limit results
        filtered_recommendations = filtered_recommendations[:limit]
        
        # Prepare response
        recommendations_data = [rec.to_dict() for rec in filtered_recommendations]
        
        return jsonify({
            'recommendations': recommendations_data,
            'total_count': len(filtered_recommendations),
            'filters_applied': {
                'category': category,
                'price_range': price_range,
                'brand_preference': brand_preference,
                'availability': availability
            },
            'recommendation_score': analysis.confidence_score
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recommendations_bp.route('/feedback', methods=['POST'])
@jwt_required()
def submit_feedback():
    """Submit feedback on recommendations"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        recommendation_id = data.get('recommendation_id')
        feedback_type = data.get('feedback_type')
        rating = data.get('rating')
        comments = data.get('comments')
        
        if not recommendation_id or not feedback_type:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Verify recommendation belongs to user
        recommendation = ProductRecommendation.query.filter_by(
            id=recommendation_id, user_id=user_id
        ).first()
        
        if not recommendation:
            return jsonify({'error': 'Recommendation not found'}), 404
        
        # Create feedback record
        feedback = RecommendationFeedback(
            recommendation_id=recommendation_id,
            user_id=user_id,
            feedback_type=feedback_type,
            rating=rating,
            comments=comments
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        # Update user preferences based on feedback (simplified)
        user = User.query.get(user_id)
        if user and not user.preferences:
            user.preferences = UserPreferences(user_id=user_id)
        
        if user and user.preferences:
            # Update preferences based on feedback
            if feedback_type == 'like' and rating and rating >= 4:
                # User liked a product, consider adding brand to preferences
                product = recommendation.product
                if product.brand:
                    current_brands = user.preferences.preferred_brands or []
                    if product.brand not in current_brands:
                        current_brands.append(product.brand)
                        user.preferences.preferred_brands = current_brands
            
            db.session.commit()
        
        return jsonify({
            'success': True,
            'updated_preferences': user.preferences.to_dict() if user and user.preferences else None,
            'message': 'Feedback submitted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recommendations_bp.route('/trending', methods=['GET'])
def get_trending_products():
    """Get trending product recommendations"""
    try:
        # Get query parameters
        category = request.args.get('category')
        time_period = request.args.get('time_period', '7d')  # 7d, 30d, 90d
        geographic_region = request.args.get('geographic_region')
        limit = min(request.args.get('limit', 10, type=int), 50)
        
        # Calculate date range based on time period
        if time_period == '7d':
            start_date = datetime.utcnow() - timedelta(days=7)
        elif time_period == '30d':
            start_date = datetime.utcnow() - timedelta(days=30)
        elif time_period == '90d':
            start_date = datetime.utcnow() - timedelta(days=90)
        else:
            start_date = datetime.utcnow() - timedelta(days=7)
        
        # Get trending products based on feedback and recommendations
        # This is a simplified implementation - in production, you'd use more sophisticated algorithms
        
        # Get products with recent positive feedback
        trending_products = db.session.query(Product).join(
            ProductRecommendation
        ).join(
            RecommendationFeedback
        ).filter(
            RecommendationFeedback.feedback_type.in_(['like', 'purchase']),
            RecommendationFeedback.rating >= 4,
            RecommendationFeedback.created_at >= start_date
        ).group_by(Product.id).order_by(
            db.func.count(RecommendationFeedback.id).desc()
        ).limit(limit).all()
        
        # If not enough trending products, add some popular products
        if len(trending_products) < limit:
            popular_products = Product.query.filter(
                Product.rating >= 4.0,
                Product.review_count >= 10
            ).order_by(Product.rating.desc()).limit(limit - len(trending_products)).all()
            
            trending_products.extend(popular_products)
        
        # Apply category filter if specified
        if category:
            trending_products = [p for p in trending_products if p.category == category]
        
        # Calculate trend score (simplified)
        trend_scores = []
        for product in trending_products:
            # Calculate trend score based on recent activity
            recent_feedback = db.session.query(RecommendationFeedback).join(
                ProductRecommendation
            ).filter(
                ProductRecommendation.product_id == product.id,
                RecommendationFeedback.created_at >= start_date
            ).count()
            
            trend_score = min(recent_feedback / 10.0, 1.0)  # Normalize to 0-1
            trend_scores.append(trend_score)
        
        # Prepare response
        trending_data = []
        for product, trend_score in zip(trending_products, trend_scores):
            product_data = product.to_dict()
            product_data['trend_score'] = trend_score
            trending_data.append(product_data)
        
        return jsonify({
            'trending_products': trending_data,
            'trend_score': sum(trend_scores) / len(trend_scores) if trend_scores else 0,
            'time_period': time_period,
            'last_updated': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 

@recommendations_bp.route('/products', methods=['GET'])
def get_products():
    """Get all available products"""
    try:
        # Get query parameters
        category = request.args.get('category')
        brand = request.args.get('brand')
        limit = min(request.args.get('limit', 50, type=int), 100)
        
        # Build query
        query = Product.query.filter_by(availability_status='available')
        
        if category:
            query = query.filter(Product.category == category)
        if brand:
            query = query.filter(Product.brand == brand)
        
        # Order by rating and review count
        query = query.order_by(Product.rating.desc(), Product.review_count.desc())
        
        # Limit results
        products = query.limit(limit).all()
        
        # Prepare response
        products_data = [product.to_dict() for product in products]
        
        return jsonify({
            'products': products_data,
            'total_count': len(products_data),
            'filters_applied': {
                'category': category,
                'brand': brand,
                'limit': limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 