from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from typing import Dict, Any, Optional
import os

from ..services.scin_integration_manager import SCINIntegrationManager
from ..services.scin_dataset_service import SCINDatasetService
from ..services.enhanced_image_vectorization_service import EnhancedImageVectorizationService
from ..services.faiss_service import FAISSService

logger = logging.getLogger(__name__)

# Create blueprint
scin_bp = Blueprint('scin_integration', __name__, url_prefix='/api/scin')

# Global integration manager instance
integration_manager = None

def get_integration_manager() -> SCINIntegrationManager:
    """Get or create the integration manager instance"""
    global integration_manager
    if integration_manager is None:
        integration_manager = SCINIntegrationManager()
    return integration_manager

@scin_bp.route('/status', methods=['GET'])
@jwt_required()
def get_integration_status():
    """Get the current SCIN integration status"""
    try:
        manager = get_integration_manager()
        status = manager.get_integration_status()
        return jsonify({
            'success': True,
            'status': status
        }), 200
    except Exception as e:
        logger.error(f"Error getting integration status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scin_bp.route('/initialize', methods=['POST'])
@jwt_required()
def initialize_integration():
    """Initialize the SCIN integration pipeline"""
    try:
        manager = get_integration_manager()
        result = manager.initialize_integration()
        
        return jsonify({
            'success': result['success'],
            'result': result
        }), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"Error initializing integration: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scin_bp.route('/build-index', methods=['POST'])
@jwt_required()
def build_similarity_index():
    """Build similarity search index from SCIN dataset"""
    try:
        data = request.get_json() or {}
        
        # Extract parameters
        conditions = data.get('conditions')
        skin_types = data.get('skin_types')
        skin_tones = data.get('skin_tones')
        max_images = data.get('max_images')
        batch_size = data.get('batch_size', 100)
        
        manager = get_integration_manager()
        result = manager.build_similarity_index(
            conditions=conditions,
            skin_types=skin_types,
            skin_tones=skin_tones,
            max_images=max_images,
            batch_size=batch_size
        )
        
        return jsonify({
            'success': result['success'],
            'result': result
        }), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"Error building similarity index: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scin_bp.route('/search', methods=['POST'])
@jwt_required()
def search_similar_images():
    """Search for similar images in the SCIN dataset"""
    try:
        data = request.get_json()
        if not data or 'query_image_path' not in data:
            return jsonify({
                'success': False,
                'error': 'query_image_path is required'
            }), 400
        
        query_image_path = data['query_image_path']
        k = data.get('k', 5)
        conditions = data.get('conditions')
        skin_types = data.get('skin_types')
        
        # Validate query image path
        if not os.path.exists(query_image_path):
            return jsonify({
                'success': False,
                'error': f'Query image not found: {query_image_path}'
            }), 404
        
        manager = get_integration_manager()
        results = manager.search_similar_images(
            query_image_path=query_image_path,
            k=k,
            conditions=conditions,
            skin_types=skin_types
        )
        
        return jsonify(results), 200 if results['success'] else 400
    except Exception as e:
        logger.error(f"Error searching similar images: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scin_bp.route('/dataset/info', methods=['GET'])
@jwt_required()
def get_dataset_info():
    """Get information about the SCIN dataset"""
    try:
        manager = get_integration_manager()
        if not manager.integration_status['scin_loaded']:
            return jsonify({
                'success': False,
                'error': 'SCIN dataset not loaded. Please initialize integration first.'
            }), 400
        
        dataset_info = manager.scin_service.get_dataset_info()
        return jsonify({
            'success': True,
            'dataset_info': dataset_info
        }), 200
    except Exception as e:
        logger.error(f"Error getting dataset info: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scin_bp.route('/dataset/statistics', methods=['GET'])
@jwt_required()
def get_dataset_statistics():
    """Get detailed statistics about the SCIN dataset"""
    try:
        manager = get_integration_manager()
        if not manager.integration_status['scin_loaded']:
            return jsonify({
                'success': False,
                'error': 'SCIN dataset not loaded. Please initialize integration first.'
            }), 400
        
        statistics = manager.scin_service.get_condition_statistics()
        return jsonify({
            'success': True,
            'statistics': statistics
        }), 200
    except Exception as e:
        logger.error(f"Error getting dataset statistics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scin_bp.route('/dataset/sample', methods=['GET'])
@jwt_required()
def get_sample_images():
    """Get sample images from the SCIN dataset"""
    try:
        data = request.args
        n = int(data.get('n', 5))
        conditions = data.get('conditions')
        if conditions:
            conditions = conditions.split(',')
        
        manager = get_integration_manager()
        if not manager.integration_status['scin_loaded']:
            return jsonify({
                'success': False,
                'error': 'SCIN dataset not loaded. Please initialize integration first.'
            }), 400
        
        samples = manager.scin_service.get_sample_images(n=n, conditions=conditions)
        return jsonify({
            'success': True,
            'samples': samples
        }), 200
    except Exception as e:
        logger.error(f"Error getting sample images: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scin_bp.route('/export/report', methods=['POST'])
@jwt_required()
def export_integration_report():
    """Export integration status and statistics to a JSON file"""
    try:
        data = request.get_json() or {}
        output_path = data.get('output_path', 'scin_integration_report.json')
        
        manager = get_integration_manager()
        success = manager.export_integration_report(output_path)
        
        return jsonify({
            'success': success,
            'output_path': output_path if success else None,
            'error': None if success else 'Failed to export report'
        }), 200 if success else 500
    except Exception as e:
        logger.error(f"Error exporting integration report: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scin_bp.route('/clear', methods=['POST'])
@jwt_required()
def clear_all_data():
    """Clear all cached and indexed data"""
    try:
        manager = get_integration_manager()
        manager.clear_all_data()
        
        return jsonify({
            'success': True,
            'message': 'All cached and indexed data cleared successfully'
        }), 200
    except Exception as e:
        logger.error(f"Error clearing data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scin_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for SCIN integration services"""
    try:
        manager = get_integration_manager()
        status = manager.get_integration_status()
        
        # Check if all services are available
        services_healthy = all(status['services'].values())
        
        return jsonify({
            'success': True,
            'healthy': services_healthy,
            'services': status['services'],
            'integration_status': {
                'scin_loaded': status['scin_loaded'],
                'vectors_generated': status['vectors_generated'],
                'faiss_populated': status['faiss_populated']
            }
        }), 200
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return jsonify({
            'success': False,
            'healthy': False,
            'error': str(e)
        }), 500

# Error handlers
@scin_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@scin_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500 