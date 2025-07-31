from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.image_analysis import image_bp
from app.models.image_analysis import ImageUpload, ImageAnalysis, AnalysisFeatures
from app.models.user import User
from app import db
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from PIL import Image
import io

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_skin_image(image_path):
    """Basic skin analysis using OpenCV"""
    try:
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            return None, "Failed to read image"
        
        # Convert to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Basic skin detection (simplified)
        # Convert to HSV for better skin detection
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Define skin color range
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Create mask for skin
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Calculate skin percentage
        total_pixels = skin_mask.shape[0] * skin_mask.shape[1]
        skin_pixels = cv2.countNonZero(skin_mask)
        skin_percentage = (skin_pixels / total_pixels) * 100
        
        # Basic analysis results
        analysis_results = {
            'skin_percentage': skin_percentage,
            'image_size': image.shape,
            'skin_detected': skin_percentage > 10,  # Basic threshold
            'confidence_score': min(skin_percentage / 50, 1.0)  # Normalize confidence
        }
        
        return analysis_results, None
        
    except Exception as e:
        return None, str(e)

@image_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_image():
    """Handle image upload and initiate analysis"""
    try:
        user_id = get_jwt_identity()
        
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Get additional parameters
        analysis_type = request.form.get('analysis_type', 'skin_analysis')
        privacy_level = request.form.get('privacy_level', 'private')
        
        # Secure filename and create unique path
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Ensure upload directory exists
        upload_dir = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        # Create upload record
        upload = ImageUpload(
            user_id=user_id,
            original_filename=filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=file.content_type,
            upload_status='uploaded',
            privacy_level=privacy_level
        )
        
        db.session.add(upload)
        db.session.flush()  # Get the upload ID
        
        # Create analysis record
        analysis = ImageAnalysis(
            upload_id=upload.id,
            user_id=user_id,
            analysis_status='processing'
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        # Perform basic analysis (in production, this would be async)
        analysis_results, error = analyze_skin_image(file_path)
        
        if error:
            analysis.analysis_status = 'failed'
            analysis.analysis_metadata = {'error': error}
        else:
            analysis.analysis_status = 'completed'
            analysis.confidence_score = analysis_results['confidence_score']
            analysis.analysis_metadata = analysis_results
            analysis.completed_at = datetime.utcnow()
            
            # Update upload status
            upload.upload_status = 'processed'
            upload.processed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'upload_id': upload.id,
            'status': upload.upload_status,
            'estimated_processing_time': 30,  # seconds
            'analysis_url': f"/api/analysis/results/{upload.id}"
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@image_bp.route('/results/<upload_id>', methods=['GET'])
@jwt_required()
def get_analysis_results(upload_id):
    """Get analysis results for a specific upload"""
    try:
        user_id = get_jwt_identity()
        
        # Find upload and analysis
        upload = ImageUpload.query.filter_by(id=upload_id, user_id=user_id).first()
        if not upload:
            return jsonify({'error': 'Upload not found'}), 404
        
        analysis = ImageAnalysis.query.filter_by(upload_id=upload_id).first()
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        # Get features if available
        features = AnalysisFeatures.query.filter_by(analysis_id=analysis.id).all()
        features_data = [feature.to_dict() for feature in features]
        
        # Prepare response
        response_data = {
            'analysis_id': analysis.id,
            'status': analysis.analysis_status,
            'confidence_score': float(analysis.confidence_score) if analysis.confidence_score else None,
            'skin_type': analysis.skin_type,
            'conditions': analysis.detected_conditions or [],
            'recommendations': [],  # Will be populated by recommendation service
            'features': features_data,
            'metadata': analysis.analysis_metadata
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@image_bp.route('/history', methods=['GET'])
@jwt_required()
def get_analysis_history():
    """Get user's analysis history"""
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 10, type=int), 50)  # Max 50 per page
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Build query
        query = ImageAnalysis.query.filter_by(user_id=user_id)
        
        if date_from:
            query = query.filter(ImageAnalysis.created_at >= date_from)
        if date_to:
            query = query.filter(ImageAnalysis.created_at <= date_to)
        
        # Order by creation date (newest first)
        query = query.order_by(ImageAnalysis.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, per_page=limit, error_out=False
        )
        
        analyses = []
        for analysis in pagination.items:
            analysis_data = analysis.to_dict()
            # Include upload info
            if analysis.upload:
                analysis_data['upload'] = analysis.upload.to_dict()
            analyses.append(analysis_data)
        
        return jsonify({
            'analyses': analyses,
            'total_count': pagination.total,
            'page': page,
            'has_more': pagination.has_next
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@image_bp.route('/upload/<upload_id>', methods=['DELETE'])
@jwt_required()
def delete_upload(upload_id):
    """Delete an image upload and its analysis"""
    try:
        user_id = get_jwt_identity()
        
        upload = ImageUpload.query.filter_by(id=upload_id, user_id=user_id).first()
        if not upload:
            return jsonify({'error': 'Upload not found'}), 404
        
        # Delete file from filesystem
        if os.path.exists(upload.file_path):
            os.remove(upload.file_path)
        
        # Delete from database (cascade will handle related records)
        db.session.delete(upload)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Upload deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 