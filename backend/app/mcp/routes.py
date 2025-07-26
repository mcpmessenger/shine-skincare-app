from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.mcp import mcp_bp
from app.models.mcp import DiscoverySession, DiscoveredContent
from app.models.image_analysis import ImageAnalysis
from app import db
import requests
import json
from datetime import datetime
import time
import threading

def simulate_mcp_discovery(discovery_session_id, search_parameters):
    """Simulate MCP discovery process (replace with actual Firecrawl integration)"""
    try:
        session = DiscoverySession.query.get(discovery_session_id)
        if not session:
            return
        
        # Simulate discovery process
        total_steps = 10
        for step in range(total_steps):
            # Update progress
            session.progress_percentage = int((step + 1) / total_steps * 100)
            session.results_found = step * 2  # Simulate finding results
            
            db.session.commit()
            
            # Simulate processing time
            time.sleep(1)
        
        # Create some mock discovered content
        mock_content = [
            {
                'content_type': 'product',
                'source_url': 'https://example-beauty-store.com/product1',
                'title': 'Hydrating Serum for Dry Skin',
                'description': 'Deeply hydrating serum with hyaluronic acid',
                'image_urls': ['https://example.com/image1.jpg'],
                'quality_score': 0.85,
                'similarity_score': 0.78
            },
            {
                'content_type': 'image',
                'source_url': 'https://example-blog.com/skincare-tips',
                'title': 'Similar Skin Condition Example',
                'description': 'Before and after results with similar skin condition',
                'image_urls': ['https://example.com/image2.jpg'],
                'quality_score': 0.72,
                'similarity_score': 0.65
            }
        ]
        
        for content_data in mock_content:
            discovered_content = DiscoveredContent(
                discovery_session_id=discovery_session_id,
                **content_data
            )
            db.session.add(discovered_content)
        
        # Mark session as completed
        session.session_status = 'completed'
        session.completed_at = datetime.utcnow()
        session.results_found = len(mock_content)
        
        db.session.commit()
        
    except Exception as e:
        print(f"Error in discovery simulation: {e}")
        session = DiscoverySession.query.get(discovery_session_id)
        if session:
            session.session_status = 'failed'
            db.session.commit()

@mcp_bp.route('/discover-similar', methods=['POST'])
@jwt_required()
def discover_similar():
    """Initiate similar image discovery across the web"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        analysis_id = data.get('analysis_id')
        search_parameters = data.get('search_parameters', {})
        result_limit = data.get('result_limit', 20)
        quality_threshold = data.get('quality_threshold', 0.5)
        
        if not analysis_id:
            return jsonify({'error': 'Analysis ID is required'}), 400
        
        # Verify analysis belongs to user
        analysis = ImageAnalysis.query.filter_by(id=analysis_id, user_id=user_id).first()
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        # Create discovery session
        discovery_session = DiscoverySession(
            user_id=user_id,
            analysis_id=analysis_id,
            search_parameters=search_parameters,
            quality_threshold=quality_threshold,
            session_status='active'
        )
        
        db.session.add(discovery_session)
        db.session.commit()
        
        # Start discovery process in background (simulated)
        # In production, this would use Celery or similar task queue
        thread = threading.Thread(
            target=simulate_mcp_discovery,
            args=(discovery_session.id, search_parameters)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'discovery_id': discovery_session.id,
            'status': discovery_session.session_status,
            'estimated_completion_time': 30,  # seconds
            'progress_url': f"/api/mcp/discovery-progress/{discovery_session.id}"
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mcp_bp.route('/discovery-results/<discovery_id>', methods=['GET'])
@jwt_required()
def get_discovery_results(discovery_id):
    """Get discovery results"""
    try:
        user_id = get_jwt_identity()
        
        # Verify discovery session belongs to user
        session = DiscoverySession.query.filter_by(id=discovery_id, user_id=user_id).first()
        if not session:
            return jsonify({'error': 'Discovery session not found'}), 404
        
        # Get discovered content
        discovered_content = DiscoveredContent.query.filter_by(
            discovery_session_id=discovery_id
        ).order_by(DiscoveredContent.quality_score.desc()).all()
        
        # Separate content by type
        similar_images = []
        related_products = []
        
        for content in discovered_content:
            content_data = content.to_dict()
            
            if content.content_type == 'image':
                similar_images.append(content_data)
            elif content.content_type == 'product':
                related_products.append(content_data)
        
        # Calculate overall quality score
        quality_scores = [c.quality_score for c in discovered_content if c.quality_score]
        overall_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return jsonify({
            'similar_images': similar_images,
            'related_products': related_products,
            'discovery_status': session.session_status,
            'quality_score': overall_quality,
            'total_results': len(discovered_content),
            'session_info': session.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mcp_bp.route('/discovery-progress/<discovery_id>', methods=['GET'])
@jwt_required()
def get_discovery_progress(discovery_id):
    """Get real-time discovery progress"""
    try:
        user_id = get_jwt_identity()
        
        # Verify discovery session belongs to user
        session = DiscoverySession.query.filter_by(id=discovery_id, user_id=user_id).first()
        if not session:
            return jsonify({'error': 'Discovery session not found'}), 404
        
        # Calculate estimated remaining time
        estimated_remaining_time = 0
        if session.session_status == 'active':
            # Simple estimation based on progress
            if session.progress_percentage > 0:
                elapsed_time = (datetime.utcnow() - session.created_at).total_seconds()
                estimated_total_time = elapsed_time / (session.progress_percentage / 100)
                estimated_remaining_time = max(0, estimated_total_time - elapsed_time)
            else:
                estimated_remaining_time = 30  # Default estimate
        
        return jsonify({
            'progress_percentage': session.progress_percentage,
            'current_stage': session.session_status,
            'results_found': session.results_found,
            'estimated_remaining_time': int(estimated_remaining_time),
            'session_status': session.session_status
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mcp_bp.route('/discovery-sessions', methods=['GET'])
@jwt_required()
def get_discovery_sessions():
    """Get user's discovery sessions"""
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 10, type=int), 50)
        status_filter = request.args.get('status_filter')
        
        # Build query
        query = DiscoverySession.query.filter_by(user_id=user_id)
        
        if status_filter:
            query = query.filter(DiscoverySession.session_status == status_filter)
        
        # Order by creation date (newest first)
        query = query.order_by(DiscoverySession.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, per_page=limit, error_out=False
        )
        
        sessions = []
        for session in pagination.items:
            session_data = session.to_dict()
            
            # Include analysis info if available
            if session.analysis:
                session_data['analysis'] = {
                    'id': session.analysis.id,
                    'skin_type': session.analysis.skin_type,
                    'confidence_score': float(session.analysis.confidence_score) if session.analysis.confidence_score else None
                }
            
            sessions.append(session_data)
        
        return jsonify({
            'sessions': sessions,
            'total_count': pagination.total,
            'page': page,
            'has_more': pagination.has_next
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mcp_bp.route('/discovery-sessions/<session_id>', methods=['DELETE'])
@jwt_required()
def delete_discovery_session(session_id):
    """Delete a discovery session"""
    try:
        user_id = get_jwt_identity()
        
        session = DiscoverySession.query.filter_by(id=session_id, user_id=user_id).first()
        if not session:
            return jsonify({'error': 'Discovery session not found'}), 404
        
        # Delete session (cascade will handle discovered content)
        db.session.delete(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Discovery session deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 