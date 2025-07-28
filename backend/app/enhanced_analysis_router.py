"""
Enhanced Analysis Router - Centralized router for enhanced AI analysis endpoints

This module provides a comprehensive router for enhanced skin analysis with real AI integration,
status tracking, and history management while maintaining backward compatibility.
"""

import os
import logging
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from werkzeug.utils import secure_filename

from app.service_manager import service_manager
from app.error_handlers import (
    APIError, ServiceError, ValidationError, ResourceNotFoundError,
    safe_service_call, create_error_context
)
from app.logging_config import get_service_logger, log_service_operation, log_api_request

logger = logging.getLogger(__name__)

# Data Models
@dataclass
class AnalysisRequest:
    """Analysis request model"""
    image_data: bytes
    user_id: str
    analysis_type: str
    metadata: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'analysis_type': self.analysis_type,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
            'image_size': len(self.image_data)
        }

@dataclass
class AnalysisResult:
    """Analysis result model"""
    analysis_id: str
    user_id: str
    skin_classification: Dict[str, Any]
    demographic_matches: List[Dict[str, Any]]
    recommendations: List[str]
    confidence_scores: Dict[str, float]
    processing_time: float
    timestamp: datetime
    status: str = 'completed'
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class SkinClassification:
    """Skin classification model"""
    skin_type: str
    skin_tone: str
    conditions: List[str]
    concerns: List[str]
    confidence_score: float
    features: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class DemographicProfile:
    """Demographic profile model"""
    profile_id: str
    age_range: str
    skin_type: str
    ethnicity: str
    geographic_region: str
    similarity_score: float
    scin_data_reference: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EnhancedAnalysisRouter:
    """
    Enhanced Analysis Router class with new API endpoints and real AI service integration
    """
    
    def __init__(self, blueprint_name: str = 'enhanced_analysis'):
        """Initialize the enhanced analysis router"""
        self.blueprint = Blueprint(blueprint_name, __name__)
        self.analysis_cache = {}  # In-memory cache for analysis status
        self.analysis_history = {}  # In-memory history storage
        self._setup_routes()
        logger.info(f"Enhanced Analysis Router initialized with blueprint: {blueprint_name}")
    
    def _wrap_method(self, method):
        """Wrap instance methods for Flask route registration"""
        def wrapper(*args, **kwargs):
            return method(*args, **kwargs)
        return wrapper
    
    def _setup_routes(self):
        """Setup all routes for the enhanced analysis router"""
        
        # Main enhanced analysis endpoint
        self.blueprint.add_url_rule(
            '/api/enhanced-analysis',
            'enhanced_analysis',
            self._wrap_method(self.analyze_image),
            methods=['POST']
        )
        
        # Analysis status tracking endpoint
        self.blueprint.add_url_rule(
            '/api/enhanced-analysis/status/<analysis_id>',
            'analysis_status',
            self._wrap_method(self.get_analysis_status),
            methods=['GET']
        )
        
        # Analysis history retrieval endpoint
        self.blueprint.add_url_rule(
            '/api/enhanced-analysis/history',
            'analysis_history',
            self._wrap_method(self.get_analysis_history),
            methods=['GET']
        )
        
        # Backward compatibility endpoint
        self.blueprint.add_url_rule(
            '/api/skin-analysis',
            'skin_analysis_compat',
            self._wrap_method(self.skin_analysis_compatibility),
            methods=['POST']
        )
        
        # Enhanced health check endpoint
        self.blueprint.add_url_rule(
            '/api/enhanced-analysis/health',
            'enhanced_health',
            self._wrap_method(self.health_check),
            methods=['GET']
        )
        
        # Guest analysis endpoint
        self.blueprint.add_url_rule(
            '/api/enhanced-analysis/guest',
            'guest_analysis',
            self._wrap_method(self.analyze_image_guest),
            methods=['POST']
        )
    
    def analyze_image(self):
        """
        Enhanced image analysis endpoint with real AI service integration
        
        This endpoint processes images through the complete AI pipeline:
        1. Google Vision API for initial image processing
        2. Skin Classifier Service for skin type classification
        3. Demographic Search Service for similar profile matching
        4. FAISS Vector Database for similarity search
        """
        start_time = time.time()
        analysis_id = str(uuid.uuid4())
        
        try:
            # Get current user (optional for guest access)
            try:
                verify_jwt_in_request(optional=True)
                current_user_id = get_jwt_identity() or f"guest_{uuid.uuid4().hex[:8]}"
            except:
                current_user_id = f"guest_{uuid.uuid4().hex[:8]}"
            
            # Validate request
            if 'image' not in request.files:
                raise ValidationError('No image file provided', field='image')
            
            file = request.files['image']
            if file.filename == '':
                raise ValidationError('No image file selected', field='image')
            
            # Validate file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
            if not ('.' in file.filename and 
                    file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
                raise ValidationError(
                    f'Invalid file type. Allowed: {", ".join(allowed_extensions)}',
                    field='image'
                )
            
            # Read image data
            image_data = file.read()
            if len(image_data) == 0:
                raise ValidationError('Empty image file', field='image')
            
            # Get optional parameters
            ethnicity = request.form.get('ethnicity', '')
            analysis_type = request.form.get('analysis_type', 'comprehensive')
            
            # Create analysis request
            analysis_request = AnalysisRequest(
                image_data=image_data,
                user_id=current_user_id,
                analysis_type=analysis_type,
                metadata={
                    'ethnicity': ethnicity,
                    'filename': secure_filename(file.filename),
                    'file_size': len(image_data)
                },
                timestamp=datetime.utcnow()
            )
            
            # Store analysis status as processing
            self._update_analysis_status(analysis_id, 'processing', analysis_request.to_dict())
            
            logger.info(f"Starting enhanced analysis {analysis_id} for user {current_user_id}")
            
            # Step 1: Google Vision Analysis
            logger.info(f"Step 1: Google Vision analysis for {analysis_id}")
            google_vision_service = service_manager.get_service('google_vision')
            vision_result = safe_service_call(
                'google_vision', 'analyze_image_from_bytes',
                google_vision_service.analyze_image_from_bytes, image_data
            )
            
            if vision_result.get('status') != 'success':
                raise ServiceError(f"Google Vision analysis failed: {vision_result.get('error', 'Unknown error')}")
            
            # Step 2: Skin Classification
            logger.info(f"Step 2: Skin classification for {analysis_id}")
            skin_classifier_service = service_manager.get_service('skin_classifier')
            skin_classification = safe_service_call(
                'skin_classifier', 'classify_skin_type',
                skin_classifier_service.classify_skin_type,
                image_data, ethnicity=ethnicity if ethnicity else None
            )
            
            # Step 3: Demographic Search
            logger.info(f"Step 3: Demographic search for {analysis_id}")
            demographic_search_service = service_manager.get_service('demographic_search')
            
            # Extract features for demographic search
            search_features = {
                'skin_type': skin_classification.get('fitzpatrick_type', 'III'),
                'ethnicity': ethnicity,
                'age_group': 'adult',  # Default for now
                'vision_features': vision_result.get('results', {})
            }
            
            demographic_matches = safe_service_call(
                'demographic_search', 'search_similar_profiles',
                demographic_search_service.search_similar_profiles,
                search_features
            )
            
            # Step 4: Generate comprehensive recommendations
            logger.info(f"Step 4: Generating recommendations for {analysis_id}")
            recommendations = self._generate_enhanced_recommendations(
                vision_result, skin_classification, demographic_matches
            )
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Create analysis result
            analysis_result = AnalysisResult(
                analysis_id=analysis_id,
                user_id=current_user_id,
                skin_classification=skin_classification,
                demographic_matches=demographic_matches or [],
                recommendations=recommendations,
                confidence_scores={
                    'overall': skin_classification.get('confidence', 0.8),
                    'vision': vision_result.get('confidence', 0.8),
                    'demographic': 0.7  # Default demographic confidence
                },
                processing_time=processing_time,
                timestamp=datetime.utcnow()
            )
            
            # Store analysis result
            self._store_analysis_result(analysis_id, analysis_result)
            
            # Update status to completed
            self._update_analysis_status(analysis_id, 'completed', analysis_result.to_dict())
            
            logger.info(f"Enhanced analysis {analysis_id} completed in {processing_time:.2f}s")
            
            # Return response
            return jsonify({
                'success': True,
                'analysis_id': analysis_id,
                'status': 'completed',
                'processing_time': processing_time,
                'data': {
                    'skin_analysis': self._format_skin_analysis_response(
                        vision_result, skin_classification, recommendations
                    ),
                    'demographic_insights': demographic_matches,
                    'confidence_scores': analysis_result.confidence_scores,
                    'metadata': {
                        'analysis_type': analysis_type,
                        'ethnicity_considered': bool(ethnicity),
                        'timestamp': analysis_result.timestamp.isoformat()
                    }
                }
            }), 200
            
        except ValidationError as e:
            self._update_analysis_status(analysis_id, 'failed', {'error': str(e)})
            return jsonify({
                'success': False,
                'analysis_id': analysis_id,
                'error': str(e),
                'error_type': 'validation_error'
            }), 400
            
        except ServiceError as e:
            self._update_analysis_status(analysis_id, 'failed', {'error': str(e)})
            return jsonify({
                'success': False,
                'analysis_id': analysis_id,
                'error': str(e),
                'error_type': 'service_error'
            }), 500
            
        except Exception as e:
            logger.error(f"Unexpected error in enhanced analysis {analysis_id}: {str(e)}")
            self._update_analysis_status(analysis_id, 'failed', {'error': str(e)})
            return jsonify({
                'success': False,
                'analysis_id': analysis_id,
                'error': 'Internal server error',
                'error_type': 'internal_error'
            }), 500
    
    def get_analysis_status(self, analysis_id: str):
        """Get analysis status by ID"""
        try:
            if analysis_id not in self.analysis_cache:
                raise ResourceNotFoundError(f"Analysis {analysis_id} not found")
            
            status_info = self.analysis_cache[analysis_id]
            
            return jsonify({
                'success': True,
                'analysis_id': analysis_id,
                'status': status_info['status'],
                'created_at': status_info.get('created_at'),
                'updated_at': status_info.get('updated_at'),
                'data': status_info.get('data', {})
            }), 200
            
        except ResourceNotFoundError as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_type': 'not_found'
            }), 404
            
        except Exception as e:
            logger.error(f"Error getting analysis status {analysis_id}: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), 500
    
    @jwt_required
    def get_analysis_history(self):
        """Get analysis history for the current user"""
        try:
            current_user_id = get_jwt_identity()
            
            # Get pagination parameters
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 10, type=int), 50)  # Max 50 per page
            
            # Get user's analysis history
            user_history = self.analysis_history.get(current_user_id, [])
            
            # Sort by timestamp (newest first)
            user_history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Paginate results
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_history = user_history[start_idx:end_idx]
            
            return jsonify({
                'success': True,
                'data': {
                    'analyses': paginated_history,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': len(user_history),
                        'pages': (len(user_history) + per_page - 1) // per_page
                    }
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting analysis history: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), 500
    
    def skin_analysis_compatibility(self):
        """
        Backward compatibility endpoint for existing /skin-analysis requests
        
        This endpoint maintains compatibility with the existing frontend while
        providing enhanced analysis capabilities under the hood.
        """
        try:
            logger.info("Processing skin analysis request (compatibility mode)")
            
            # Process the request using the enhanced analysis pipeline
            # but format the response to match the legacy format
            enhanced_response = self.analyze_image()
            
            # If enhanced analysis succeeded, format for legacy compatibility
            if enhanced_response[1] == 200:  # HTTP 200 OK
                enhanced_data = enhanced_response[0].get_json()
                
                if enhanced_data.get('success'):
                    skin_analysis = enhanced_data['data']['skin_analysis']
                    
                    # Format response to match legacy skin analysis format
                    legacy_response = {
                        'status': 'success',
                        'skinType': skin_analysis.get('skinType', 'Combination'),
                        'concerns': skin_analysis.get('concerns', []),
                        'hydration': skin_analysis.get('hydration', 75),
                        'oiliness': skin_analysis.get('oiliness', 45),
                        'sensitivity': skin_analysis.get('sensitivity', 30),
                        'recommendations': skin_analysis.get('recommendations', []),
                        'products': skin_analysis.get('products', []),
                        'confidence': enhanced_data['confidence_scores'].get('overall', 0.8),
                        'analysis_id': enhanced_data['analysis_id'],
                        'timestamp': enhanced_data['data']['metadata']['timestamp']
                    }
                    
                    return jsonify(legacy_response), 200
            
            # If enhanced analysis failed, return error in legacy format
            return jsonify({
                'status': 'error',
                'error': 'Analysis failed',
                'timestamp': datetime.utcnow().isoformat()
            }), 500
            
        except Exception as e:
            logger.error(f"Error in skin analysis compatibility endpoint: {str(e)}")
            return jsonify({
                'status': 'error',
                'error': 'Internal server error',
                'timestamp': datetime.utcnow().isoformat()
            }), 500
    
    def analyze_image_guest(self):
        """Guest analysis endpoint without authentication"""
        try:
            logger.info("Processing guest enhanced analysis request")
            
            # Process using the main analysis method (it already handles guest users)
            return self.analyze_image()
                
        except Exception as e:
            logger.error(f"Error in guest analysis: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Internal server error',
                'error_type': 'internal_error'
            }), 500
    
    def health_check(self):
        """Enhanced health check for all AI services"""
        try:
            # Check all services
            services_status = {}
            overall_healthy = True
            
            service_names = ['google_vision', 'skin_classifier', 'demographic_search', 'faiss']
            
            for service_name in service_names:
                try:
                    service = service_manager.get_service(service_name)
                    is_available = service.is_available()
                    services_status[service_name] = {
                        'status': 'healthy' if is_available else 'unhealthy',
                        'available': is_available
                    }
                    if not is_available:
                        overall_healthy = False
                except Exception as e:
                    services_status[service_name] = {
                        'status': 'error',
                        'available': False,
                        'error': str(e)
                    }
                    overall_healthy = False
            
            # Get service info
            service_info = service_manager.get_service_info()
            
            return jsonify({
                'status': 'healthy' if overall_healthy else 'degraded',
                'timestamp': datetime.utcnow().isoformat(),
                'services': services_status,
                'service_info': service_info,
                'analysis_cache_size': len(self.analysis_cache),
                'version': '1.0.0'
            }), 200 if overall_healthy else 503
            
        except Exception as e:
            logger.error(f"Error in health check: {str(e)}")
            return jsonify({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500
    
    def _update_analysis_status(self, analysis_id: str, status: str, data: Dict[str, Any]):
        """Update analysis status in cache"""
        current_time = datetime.utcnow().isoformat()
        
        if analysis_id not in self.analysis_cache:
            self.analysis_cache[analysis_id] = {
                'created_at': current_time
            }
        
        self.analysis_cache[analysis_id].update({
            'status': status,
            'updated_at': current_time,
            'data': data
        })
    
    def _store_analysis_result(self, analysis_id: str, result: AnalysisResult):
        """Store analysis result in history"""
        user_id = result.user_id
        
        if user_id not in self.analysis_history:
            self.analysis_history[user_id] = []
        
        # Add to user's history
        self.analysis_history[user_id].append({
            'analysis_id': analysis_id,
            'timestamp': result.timestamp.isoformat(),
            'status': result.status,
            'processing_time': result.processing_time,
            'skin_type': result.skin_classification.get('fitzpatrick_type', 'Unknown'),
            'confidence': result.confidence_scores.get('overall', 0.0),
            'concerns_count': len(result.skin_classification.get('concerns', [])),
            'recommendations_count': len(result.recommendations)
        })
        
        # Keep only last 100 analyses per user
        if len(self.analysis_history[user_id]) > 100:
            self.analysis_history[user_id] = self.analysis_history[user_id][-100:]
    
    def _generate_enhanced_recommendations(self, vision_result: Dict, skin_classification: Dict, demographic_matches: List) -> List[str]:
        """Generate enhanced recommendations based on all analysis results"""
        recommendations = []
        
        # Base recommendations from skin classification
        fitzpatrick_type = skin_classification.get('fitzpatrick_type', 'III')
        concerns = skin_classification.get('concerns', [])
        
        # Fitzpatrick-specific recommendations
        if fitzpatrick_type in ['I', 'II']:
            recommendations.extend([
                'Use SPF 50+ sunscreen daily - your fair skin is highly susceptible to UV damage',
                'Consider gentle, fragrance-free products to avoid irritation',
                'Use a rich moisturizer to combat natural dryness'
            ])
        elif fitzpatrick_type in ['III', 'IV']:
            recommendations.extend([
                'Use SPF 30+ sunscreen daily for optimal protection',
                'Consider vitamin C serum for brightening and antioxidant protection',
                'Maintain consistent hydration with a balanced moisturizer'
            ])
        elif fitzpatrick_type in ['V', 'VI']:
            recommendations.extend([
                'Use SPF 30+ sunscreen daily - darker skin still needs UV protection',
                'Consider products with niacinamide to address hyperpigmentation',
                'Use gentle exfoliation to maintain even skin tone'
            ])
        
        # Concern-specific recommendations
        if 'acne' in [c.lower() for c in concerns]:
            recommendations.append('Consider salicylic acid cleanser for acne-prone skin')
        
        if 'hyperpigmentation' in [c.lower() for c in concerns]:
            recommendations.append('Use products with kojic acid or arbutin for dark spots')
        
        if 'sensitivity' in [c.lower() for c in concerns]:
            recommendations.append('Patch test all new products and avoid harsh ingredients')
        
        # Demographic-based recommendations
        if demographic_matches:
            # Add recommendations based on similar demographic profiles
            recommendations.append('Based on similar skin profiles, consider a gentle retinol product')
        
        # Vision analysis-based recommendations
        vision_results = vision_result.get('results', {})
        if vision_results.get('face_detection', {}).get('faces_found', 0) > 0:
            recommendations.append('Focus on targeted treatments for facial skin care')
        
        # Remove duplicates and limit to top 6 recommendations
        unique_recommendations = list(dict.fromkeys(recommendations))
        return unique_recommendations[:6]
    
    def _format_skin_analysis_response(self, vision_result: Dict, skin_classification: Dict, recommendations: List[str]) -> Dict[str, Any]:
        """Format the skin analysis response for frontend consumption"""
        
        # Map Fitzpatrick type to user-friendly skin type
        fitzpatrick_type = skin_classification.get('fitzpatrick_type', 'III')
        skin_type_mapping = {
            'I': 'Very Fair',
            'II': 'Fair',
            'III': 'Light',
            'IV': 'Medium',
            'V': 'Dark',
            'VI': 'Very Dark'
        }
        
        skin_type = skin_type_mapping.get(fitzpatrick_type, 'Medium')
        concerns = skin_classification.get('concerns', ['Even Skin Tone', 'Hydration'])
        
        # Calculate metrics based on classification
        confidence = skin_classification.get('confidence', 0.8)
        
        # Generate metrics (simplified for now)
        hydration = max(60, min(90, int(confidence * 100) - 10))
        oiliness = max(20, min(70, int((1 - confidence) * 80) + 20))
        sensitivity = max(15, min(60, int((1 - confidence) * 50) + 15))
        
        # Mock product recommendations (in real implementation, this would come from a product database)
        products = [
            {
                'name': 'Gentle Daily Cleanser',
                'category': 'Cleanser',
                'rating': 4.5,
                'price': 24.99,
                'image': '/products/cleanser.jpg',
                'suitable_for': skin_type
            },
            {
                'name': 'Brightening Vitamin C Serum',
                'category': 'Serum',
                'rating': 4.8,
                'price': 45.99,
                'image': '/products/serum.jpg',
                'suitable_for': skin_type
            },
            {
                'name': 'Hydrating Daily Moisturizer',
                'category': 'Moisturizer',
                'rating': 4.3,
                'price': 32.99,
                'image': '/products/moisturizer.jpg',
                'suitable_for': skin_type
            }
        ]
        
        return {
            'status': 'success',
            'skinType': skin_type,
            'fitzpatrick_type': fitzpatrick_type,
            'concerns': concerns[:3],  # Limit to top 3 concerns
            'hydration': hydration,
            'oiliness': oiliness,
            'sensitivity': sensitivity,
            'recommendations': recommendations,
            'products': products,
            'enhanced_features': {
                'monk_tone': skin_classification.get('monk_tone'),
                'ethnicity_considered': skin_classification.get('ethnicity_considered', False),
                'confidence_breakdown': {
                    'skin_type': skin_classification.get('confidence', 0.8),
                    'tone_analysis': vision_result.get('confidence', 0.8)
                }
            }
        }


# Create the enhanced analysis router instance
enhanced_analysis_router = EnhancedAnalysisRouter()

# Export the blueprint for registration
enhanced_analysis_bp = enhanced_analysis_router.blueprint