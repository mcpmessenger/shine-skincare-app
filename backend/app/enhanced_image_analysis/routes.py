import os
import logging
import tempfile
import uuid
from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import numpy as np
from datetime import datetime

from . import enhanced_image_bp
from app.services import (
    GoogleVisionService, 
    ImageVectorizationService, 
    FAISSService, 
    SupabaseService
)

logger = logging.getLogger(__name__)

# Initialize services
google_vision_service = GoogleVisionService()
vectorization_service = ImageVectorizationService()
faiss_service = FAISSService()
supabase_service = SupabaseService()

@enhanced_image_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_image():
    """
    Enhanced image analysis endpoint
    
    Steps:
    1. Upload image to Supabase Storage
    2. Analyze with Google Vision AI
    3. Vectorize image for FAISS
    4. Store metadata in database
    5. Add to FAISS index
    """
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        # Get ethnicity from form data (optional)
        ethnicity = request.form.get('ethnicity', '')
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Read image data
        image_data = file.read()
        filename = secure_filename(file.filename)
        
        # Step 1: Upload to Supabase Storage
        logger.info(f"Uploading image for user {current_user_id}")
        image_url = supabase_service.upload_image(image_data, filename)
        if not image_url:
            return jsonify({'error': 'Failed to upload image'}), 500
        
        # Step 2: Analyze with Google Vision AI
        logger.info("Analyzing image with Google Vision AI")
        vision_result = google_vision_service.analyze_image_from_bytes(image_data)
        
        # Step 3: Vectorize image
        logger.info("Vectorizing image")
        vector = vectorization_service.vectorize_image_from_bytes(image_data)
        if not vector:
            return jsonify({'error': 'Failed to vectorize image'}), 500
        
        # Step 4: Create database records
        logger.info("Creating database records")
        
        # Create image record
        image_record = supabase_service.create_image_record(
            user_id=current_user_id,
            image_url=image_url
        )
        if not image_record:
            return jsonify({'error': 'Failed to create image record'}), 500
        
        image_id = image_record['id']
        
        # Create analysis record with ethnicity data
        if vision_result.get('status') == 'success':
            # Add ethnicity to vision result for enhanced analysis
            enhanced_vision_result = vision_result.copy()
            enhanced_vision_result['ethnicity'] = ethnicity
            enhanced_vision_result['analysis_metadata'] = {
                'ethnicity_considered': bool(ethnicity),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            analysis_record = supabase_service.create_analysis_record(
                image_id=image_id,
                google_vision_result=enhanced_vision_result
            )
        
        # Create vector record
        vector_record = supabase_service.create_vector_record(
            image_id=image_id,
            vector_data=vector.tolist(),
            model_name=vectorization_service.model_name
        )
        
        # Step 5: Add to FAISS index
        logger.info("Adding to FAISS index")
        faiss_success = faiss_service.add_vector(vector, image_id)
        
        # Update image record with FAISS index ID
        if faiss_success:
            # Note: In a real implementation, you'd update the record with the FAISS index ID
            pass
        
        # Prepare response with ethnicity-aware analysis
        response_data = {
            'image_id': image_id,
            'image_url': image_url,
            'analysis': enhanced_vision_result if vision_result.get('status') == 'success' else vision_result,
            'ethnicity': ethnicity,
            'vector_created': vector_record is not None,
            'faiss_indexed': faiss_success,
            'status': 'success'
        }
        
        logger.info(f"Image analysis completed successfully for image {image_id}")
        return jsonify(response_data), 201
        
    except Exception as e:
        logger.error(f"Error in image analysis: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@enhanced_image_bp.route('/similar/<image_id>', methods=['GET'])
@jwt_required()
def find_similar_images(image_id):
    """
    Find similar images using FAISS similarity search
    
    Args:
        image_id: ID of the query image
        k: Number of similar images to return (query parameter)
    """
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        
        # Get number of similar images to return
        k = request.args.get('k', 5, type=int)
        k = min(k, 20)  # Limit to 20 results
        
        # Get the query image record
        image_record = supabase_service.get_image_by_id(image_id)
        if not image_record:
            return jsonify({'error': 'Image not found'}), 404
        
        # Check if user owns the image
        if image_record['user_id'] != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get the vector for the query image
        vector_record = supabase_service.get_vector_by_image_id(image_id)
        if not vector_record:
            return jsonify({'error': 'Image vector not found'}), 404
        
        # Convert vector data to numpy array
        query_vector = np.array(vector_record['vector_data'])
        
        # Search for similar images
        similar_results = faiss_service.search_similar(query_vector, k)
        
        # Get details for similar images
        similar_images = []
        for similar_image_id, distance in similar_results:
            if similar_image_id != image_id:  # Exclude the query image
                similar_image_record = supabase_service.get_image_by_id(similar_image_id)
                if similar_image_record:
                    similar_images.append({
                        'image_id': similar_image_id,
                        'image_url': similar_image_record['image_url'],
                        'similarity_score': 1.0 / (1.0 + distance),  # Convert distance to similarity
                        'distance': distance
                    })
        
        response_data = {
            'query_image_id': image_id,
            'similar_images': similar_images,
            'total_found': len(similar_images)
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error finding similar images: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@enhanced_image_bp.route('/images', methods=['GET'])
@jwt_required()
def get_user_images():
    """Get all images for the current user"""
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        
        # Get user's images
        images = supabase_service.get_images_by_user(current_user_id)
        
        # Add analysis and vector info for each image
        for image in images:
            image_id = image['id']
            
            # Get analysis
            analysis = supabase_service.get_analysis_by_image_id(image_id)
            if analysis:
                image['has_analysis'] = True
                image['analysis_summary'] = _summarize_analysis(analysis['google_vision_result'])
            else:
                image['has_analysis'] = False
            
            # Get vector info
            vector = supabase_service.get_vector_by_image_id(image_id)
            if vector:
                image['has_vector'] = True
                image['vector_model'] = vector['model_name']
            else:
                image['has_vector'] = False
        
        return jsonify({
            'images': images,
            'total_count': len(images)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting user images: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@enhanced_image_bp.route('/analysis/<image_id>', methods=['GET'])
@jwt_required()
def get_image_analysis(image_id):
    """Get detailed analysis for a specific image"""
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        
        # Get image record
        image_record = supabase_service.get_image_by_id(image_id)
        if not image_record:
            return jsonify({'error': 'Image not found'}), 404
        
        # Check if user owns the image
        if image_record['user_id'] != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get analysis
        analysis_record = supabase_service.get_analysis_by_image_id(image_id)
        if not analysis_record:
            return jsonify({'error': 'Analysis not found'}), 404
        
        # Get vector info
        vector_record = supabase_service.get_vector_by_image_id(image_id)
        
        response_data = {
            'image': image_record,
            'analysis': analysis_record['google_vision_result'],
            'vector_info': vector_record
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error getting image analysis: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@enhanced_image_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for enhanced image analysis services"""
    try:
        services_status = {
            'google_vision': google_vision_service.is_available(),
            'vectorization': vectorization_service.is_available(),
            'faiss': faiss_service.is_available(),
            'supabase': supabase_service.is_available()
        }
        
        faiss_info = faiss_service.get_index_info()
        vectorization_info = vectorization_service.get_model_info()
        
        return jsonify({
            'status': 'healthy',
            'services': services_status,
            'faiss_index': faiss_info,
            'vectorization_model': vectorization_info
        }), 200
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return jsonify({'error': 'Health check failed'}), 500

def _summarize_analysis(analysis_result):
    """Create a summary of the analysis result"""
    if not analysis_result or analysis_result.get('status') != 'success':
        return None
    
    results = analysis_result.get('results', {})
    summary = {}
    
    # Face detection summary
    face_data = results.get('face_detection', {})
    if 'faces_found' in face_data:
        summary['faces_found'] = face_data['faces_found']
    
    # Image properties summary
    properties = results.get('image_properties', {})
    if 'color_count' in properties:
        summary['dominant_colors'] = properties['color_count']
    
    # Label detection summary
    labels = results.get('label_detection', {})
    if 'labels_found' in labels:
        summary['labels_found'] = labels['labels_found']
    
    return summary

@enhanced_image_bp.route('/analyze/skin', methods=['POST'])
@jwt_required()
def analyze_skin():
    """
    Enhanced skin analysis endpoint that returns data in frontend-expected format
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Read image data
        image_data = file.read()
        
        # Analyze with Google Vision AI
        logger.info("Analyzing skin with Google Vision AI")
        vision_result = google_vision_service.analyze_image_from_bytes(image_data)
        
        if vision_result.get('status') != 'success':
            return jsonify({
                'error': 'Failed to analyze image',
                'details': vision_result.get('error', 'Unknown error')
            }), 500
        
        # Process Vision results into frontend-expected format
        skin_analysis = _process_skin_analysis(vision_result, current_user_id)
        
        return jsonify(skin_analysis), 200
        
    except Exception as e:
        logger.error(f"Error in skin analysis: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'status': 'error'
        }), 500

@enhanced_image_bp.route('/analyze/guest', methods=['POST'])
def analyze_image_guest():
    """
    Guest-friendly image analysis endpoint (no authentication required)
    """
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Read image data
        image_data = file.read()
        
        # Analyze with Google Vision AI
        logger.info("Analyzing image with Google Vision AI (guest)")
        vision_result = google_vision_service.analyze_image_from_bytes(image_data)
        
        if vision_result.get('status') == 'success':
            # Process skin analysis
            skin_analysis = _process_skin_analysis(vision_result, 'guest')
            
            # Generate a temporary image ID for guest
            temp_image_id = f"guest_{uuid.uuid4().hex[:8]}"
            
            return jsonify({
                'success': True,
                'data': {
                    'image_id': temp_image_id,
                    'analysis': skin_analysis,
                    'message': 'Guest analysis completed. Sign up to save your results!'
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to analyze image'
            }), 500
            
    except Exception as e:
        logger.error(f"Error in guest analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

def _process_skin_analysis(vision_result, user_id):
    """
    Process Google Vision results into frontend-expected format
    """
    try:
        results = vision_result.get('results', {})
        face_data = results.get('face_detection', {})
        image_props = results.get('image_properties', {})
        labels = results.get('label_detection', {})
        
        # Determine skin type based on analysis
        skin_type = _determine_skin_type(face_data, image_props, labels)
        
        # Determine skin concerns
        concerns = _determine_skin_concerns(face_data, labels)
        
        # Calculate metrics
        metrics = _calculate_skin_metrics(face_data, image_props)
        
        # Generate recommendations
        recommendations = _generate_recommendations(skin_type, concerns, metrics)
        
        # Get product recommendations
        products = _get_product_recommendations(skin_type, concerns)
        
        return {
            'status': 'success',
            'skinType': skin_type,
            'concerns': concerns,
            'hydration': metrics['hydration'],
            'oiliness': metrics['oiliness'],
            'sensitivity': metrics['sensitivity'],
            'recommendations': recommendations,
            'products': products,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'analysis_id': str(uuid.uuid4())
        }
        
    except Exception as e:
        logger.error(f"Error processing skin analysis: {str(e)}")
        return {
            'error': str(e),
            'status': 'error'
        }

def _determine_skin_type(face_data, image_props, labels):
    """Determine skin type based on Vision analysis"""
    # Default to combination skin
    skin_type = 'Combination'
    
    # Check if face was detected
    if face_data.get('faces_found', 0) > 0:
        # Analyze face data for skin characteristics
        face_info = face_data.get('face_data', [{}])[0]
        
        # Simple logic based on face detection confidence and image properties
        if face_info.get('confidence', 0) > 0.8:
            # High confidence face detection - could indicate clearer skin
            skin_type = 'Normal'
        elif face_info.get('confidence', 0) > 0.6:
            skin_type = 'Combination'
        else:
            skin_type = 'Sensitive'
    
    return skin_type

def _determine_skin_concerns(face_data, labels):
    """Determine skin concerns based on analysis"""
    concerns = []
    
    # Check labels for skin-related terms
    label_descriptions = [label.get('description', '').lower() for label in labels.get('labels', [])]
    
    # Map labels to concerns
    concern_mapping = {
        'acne': 'Acne',
        'pimple': 'Acne',
        'blemish': 'Acne',
        'dark spot': 'Hyperpigmentation',
        'pigment': 'Hyperpigmentation',
        'freckle': 'Hyperpigmentation',
        'wrinkle': 'Fine Lines',
        'line': 'Fine Lines',
        'dry': 'Dryness',
        'oily': 'Oiliness',
        'red': 'Redness',
        'sensitive': 'Sensitivity'
    }
    
    for label in label_descriptions:
        for key, concern in concern_mapping.items():
            if key in label and concern not in concerns:
                concerns.append(concern)
    
    # Default concerns if none detected
    if not concerns:
        concerns = ['Even Skin Tone', 'Hydration']
    
    return concerns[:3]  # Limit to top 3 concerns

def _calculate_skin_metrics(face_data, image_props):
    """Calculate skin metrics based on analysis"""
    # Default metrics
    metrics = {
        'hydration': 75,
        'oiliness': 45,
        'sensitivity': 30
    }
    
    # Adjust based on face detection confidence
    if face_data.get('faces_found', 0) > 0:
        face_info = face_data.get('face_data', [{}])[0]
        confidence = face_info.get('confidence', 0.5)
        
        # Higher confidence might indicate better skin condition
        if confidence > 0.8:
            metrics['hydration'] = 85
            metrics['oiliness'] = 35
            metrics['sensitivity'] = 25
        elif confidence > 0.6:
            metrics['hydration'] = 75
            metrics['oiliness'] = 45
            metrics['sensitivity'] = 30
        else:
            metrics['hydration'] = 65
            metrics['oiliness'] = 55
            metrics['sensitivity'] = 40
    
    return metrics

def _generate_recommendations(skin_type, concerns, metrics):
    """Generate personalized recommendations"""
    recommendations = []
    
    # Base recommendations by skin type
    type_recommendations = {
        'Normal': [
            'Use a gentle cleanser twice daily',
            'Apply SPF 30+ sunscreen every morning',
            'Maintain a consistent skincare routine'
        ],
        'Combination': [
            'Use a gentle cleanser twice daily',
            'Apply SPF 30+ sunscreen every morning',
            'Consider a vitamin C serum for brightening',
            'Use a lightweight moisturizer for combination skin'
        ],
        'Sensitive': [
            'Use fragrance-free, gentle products',
            'Patch test new products before use',
            'Avoid harsh exfoliants',
            'Use a calming moisturizer'
        ]
    }
    
    recommendations.extend(type_recommendations.get(skin_type, type_recommendations['Combination']))
    
    # Add concern-specific recommendations
    if 'Acne' in concerns:
        recommendations.append('Consider a salicylic acid cleanser')
    if 'Hyperpigmentation' in concerns:
        recommendations.append('Use products with niacinamide or vitamin C')
    if 'Fine Lines' in concerns:
        recommendations.append('Consider a retinol product (start slowly)')
    
    return recommendations[:4]  # Limit to 4 recommendations

def _get_product_recommendations(skin_type, concerns):
    """Get product recommendations based on analysis"""
    # Mock product data - in real app, this would come from a database
    products = [
        {
            'name': 'Gentle Foaming Cleanser',
            'category': 'Cleanser',
            'rating': 4.5,
            'price': 24.99,
            'image': '/products/cleanser.jpg'
        },
        {
            'name': 'Vitamin C Brightening Serum',
            'category': 'Serum',
            'rating': 4.8,
            'price': 45.99,
            'image': '/products/serum.jpg'
        },
        {
            'name': 'Lightweight Hydrating Moisturizer',
            'category': 'Moisturizer',
            'rating': 4.3,
            'price': 32.99,
            'image': '/products/moisturizer.jpg'
        }
    ]
    
    return products 