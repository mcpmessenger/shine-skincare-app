"""
Operation Right Brain 🧠 - Backend Implementation
Shine Skincare App - AI-Powered Skin Analysis Backend

This module implements the core backend functionality for the AI-powered skin analysis
system using Google Cloud Vertex AI Multimodal Embeddings and Google Vision API.

Author: Manus AI
Date: August 2, 2025
"""

import os
import json
import logging
import base64
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import traceback

# Flask imports
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# Google Cloud imports
from google.cloud import vision
from google.cloud import aiplatform
from google.cloud.aiplatform_v1 import FindNearestNeighborsRequest
from google.cloud.aiplatform_v1.types import FindNearestNeighborsResponse

# Image processing
import cv2
import numpy as np
from PIL import Image
import io

# Configuration and utilities
from config import Config
from utils.logging_config import setup_logging
from utils.error_handling import handle_api_error, validate_image
from services.google_vision_service import GoogleVisionService
from services.vertex_ai_service import VertexAIService
from services.vector_db_service import VectorDBService
from models.skin_analysis import SkinAnalysisResult, SCINMatch

# Setup logging
logger = setup_logging(__name__)

class OperationRightBrain:
    """
    Main backend class implementing the AI-powered skin analysis system.
    Implements the requirements from the Operation Right Brain 🧠 PRD.
    """
    
    def __init__(self):
        """Initialize the Operation Right Brain backend system."""
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Initialize Google Cloud services
        self.vision_service = GoogleVisionService()
        self.vertex_ai_service = VertexAIService()
        self.vector_db_service = VectorDBService()
        
        # Setup routes
        self._setup_routes()
        
        logger.info("Operation Right Brain 🧠 backend initialized successfully")
    
    def _setup_routes(self):
        """Setup API routes according to PRD requirements."""
        
        @self.app.route('/api/v3/skin/analyze-enhanced', methods=['POST'])
        def analyze_skin_enhanced():
            """
            BR1: Enhanced skin analysis endpoint using Google Cloud services.
            
            Process flow:
            1. Receive image from frontend
            2. Call Google Vision API for face detection and isolation
            3. Call Vertex AI Multimodal Embeddings to generate embedding
            4. Perform similarity search against SCIN dataset
            5. Retrieve and structure relevant SCIN data
            6. Return structured skin analysis results
            """
            try:
                # BR8: Robust error handling
                if 'image' not in request.files:
                    return handle_api_error("No image provided", 400)
                
                image_file = request.files['image']
                if not image_file.filename:
                    return handle_api_error("Invalid image file", 400)
                
                # BR9: Secure handling of image data
                image_data = image_file.read()
                if not validate_image(image_data):
                    return handle_api_error("Invalid image format", 400)
                
                logger.info(f"Processing skin analysis request for image: {image_file.filename}")
                
                # Step 1: Face detection and isolation using Google Vision API
                # BR2: Integration with Google Vision API
                face_image = self.vision_service.detect_and_isolate_face(image_data)
                if face_image is None:
                    return handle_api_error("No face detected in image", 400)
                
                # Step 2: Generate embedding using Vertex AI Multimodal Embeddings
                # BR3: Integration with Vertex AI Multimodal Embeddings
                embedding = self.vertex_ai_service.generate_image_embedding(face_image)
                if embedding is None:
                    return handle_api_error("Failed to generate image embedding", 500)
                
                # Step 3: Perform similarity search against SCIN dataset
                # BR4 & BR5: Vector database connection and similarity search
                scin_matches = self.vector_db_service.find_similar_conditions(
                    embedding, 
                    top_k=5
                )
                
                # Step 4: Retrieve and structure relevant SCIN data
                # BR6: Retrieve and structure SCIN dataset information
                analysis_result = self._process_scin_matches(scin_matches)
                
                # Step 5: Return structured skin analysis results
                # BR7: Return JSON response with skin analysis results
                response_data = analysis_result.to_dict()
                
                logger.info(f"Skin analysis completed successfully for {image_file.filename}")
                return jsonify(response_data), 200
                
            except Exception as e:
                logger.error(f"Error in skin analysis: {str(e)}")
                logger.error(traceback.format_exc())
                return handle_api_error("Internal server error", 500)
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint for monitoring."""
            return jsonify({
                "status": "healthy",
                "service": "Operation Right Brain 🧠",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }), 200
        
        @self.app.route('/api/v3/skin/analyze-enhanced/status', methods=['GET'])
        def analysis_status():
            """Check the status of the AI analysis pipeline."""
            try:
                status = {
                    "vision_api": self.vision_service.check_health(),
                    "vertex_ai": self.vertex_ai_service.check_health(),
                    "vector_db": self.vector_db_service.check_health(),
                    "timestamp": datetime.utcnow().isoformat()
                }
                return jsonify(status), 200
            except Exception as e:
                logger.error(f"Error checking analysis status: {str(e)}")
                return handle_api_error("Failed to check analysis status", 500)
    
    def _process_scin_matches(self, scin_matches: List[SCINMatch]) -> SkinAnalysisResult:
        """
        Process SCIN matches and create structured analysis results.
        
        Args:
            scin_matches: List of SCIN matches from similarity search
            
        Returns:
            SkinAnalysisResult: Structured analysis results
        """
        if not scin_matches:
            return SkinAnalysisResult(
                confidence=0.0,
                conditions=[],
                recommendations=[],
                message="No similar conditions found in our database."
            )
        
        # Calculate overall confidence based on top matches
        top_match = scin_matches[0]
        confidence = min(top_match.similarity_score * 100, 95.0)  # Cap at 95%
        
        # Extract conditions and metadata
        conditions = []
        for match in scin_matches[:3]:  # Top 3 matches
            condition = {
                "name": match.condition_name,
                "confidence": match.similarity_score * 100,
                "description": match.description,
                "symptoms": match.symptoms,
                "recommendations": match.recommendations,
                "severity": match.severity,
                "case_id": match.case_id
            }
            conditions.append(condition)
        
        # Generate recommendations based on matches
        recommendations = self._generate_recommendations(scin_matches)
        
        return SkinAnalysisResult(
            confidence=confidence,
            conditions=conditions,
            recommendations=recommendations,
            message=f"Analysis completed with {confidence:.1f}% confidence."
        )
    
    def _generate_recommendations(self, scin_matches: List[SCINMatch]) -> List[str]:
        """
        Generate personalized recommendations based on SCIN matches.
        
        Args:
            scin_matches: List of SCIN matches
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Add general recommendations
        recommendations.append("Schedule a consultation with a dermatologist for professional evaluation.")
        
        # Add condition-specific recommendations
        for match in scin_matches[:2]:  # Top 2 matches
            if match.recommendations:
                recommendations.extend(match.recommendations)
        
        # Add skincare recommendations
        recommendations.append("Use gentle, fragrance-free skincare products.")
        recommendations.append("Apply broad-spectrum sunscreen daily.")
        recommendations.append("Avoid picking or scratching affected areas.")
        
        return list(set(recommendations))  # Remove duplicates
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """
        Run the Operation Right Brain backend server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
            debug: Enable debug mode
        """
        logger.info(f"Starting Operation Right Brain 🧠 backend on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

# Factory function for creating the application
def create_app():
    """Create and configure the Flask application."""
    brain = OperationRightBrain()
    return brain.app

if __name__ == '__main__':
    brain = OperationRightBrain()
    brain.run(debug=True) 