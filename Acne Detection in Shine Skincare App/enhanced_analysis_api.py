        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            return jsonify({'error': f'Invalid image data: {e}'}), 400
        
        # Get user demographics (required for normalized analysis)
        demographics = data.get('demographics', {})
        if not demographics:
            return jsonify({'error': 'Demographics required for normalized analysis'}), 400
        
        # Perform normalized analysis
        if integrated_analyzer:
            results = integrated_analyzer.analyze_skin_comprehensive(image_bytes, demographics)
        else:
            return jsonify({'error': 'Analysis system not available'}), 500
        
        # Convert results for JSON serialization
        serializable_results = convert_numpy_types(results)
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'normalized',
            'demographics_used': demographics,
            'results': serializable_results
        })
        
    except Exception as e:
        logger.error(f"❌ Normalized analysis failed: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/v3/face/detect', methods=['POST'])
def face_detect():
    """
    Enhanced face detection endpoint with robust image processing
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract image data
        image_data = data.get('image_data')
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Use enhanced face detection with robust image processing
        result = enhanced_face_detect_endpoint(image_data)
        
        if result['success']:
            return jsonify({
                'status': 'success',
                'face_detected': result['face_detected'],
                'confidence': result['confidence'],
                'face_bounds': result['face_bounds'],
                'quality_metrics': result.get('quality_metrics', {}),
                'guidance': result.get('guidance', {}),
                'processing_metadata': result.get('processing_metadata', {})
            })
        else:
            return jsonify({
                'status': 'error',
                'error': result['error'],
                'details': result.get('details', ''),
                'metadata': result.get('metadata', {})
            }), 400
            
    except Exception as e:
        logger.error(f"Face detection error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': f'Face detection failed: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/v3/skin/analyze-enhanced-embeddings', methods=['POST'])
def analyze_skin_enhanced_embeddings():
    """
    Enhanced skin analysis with embeddings and cosine similarity search
    Performs face detection and analysis in a single step
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract image data
        image_data = data.get('image_data') or data.get('image')
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            return jsonify({'error': f'Invalid image data: {e}'}), 400
        