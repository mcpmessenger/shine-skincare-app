from flask import Blueprint, request, jsonify
import os
import base64
import io
import numpy as np
from PIL import Image
import openai
from google.cloud import vision
import json
import logging

skin_analysis_bp = Blueprint('skin_analysis', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Initialize Google Vision client
vision_client = vision.ImageAnnotatorClient()

@skin_analysis_bp.route('/analyze', methods=['POST'])
def analyze_skin():
    """
    Analyze skin condition using OpenAI embeddings and Google Vision API
    """
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Decode base64 image
        image_data = data['image']
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Step 1: Use Google Vision API to detect and isolate face
        face_region = detect_face_region(image_bytes)
        
        if not face_region:
            return jsonify({'error': 'No face detected in image'}), 400
        
        # Step 2: Crop image to face region
        cropped_face = crop_to_face(image, face_region)
        
        # Step 3: Generate OpenAI embedding for the face
        embedding = generate_image_embedding(cropped_face)
        
        # Step 4: Search SCIN dataset for similar conditions
        similar_conditions = search_scin_dataset(embedding)
        
        # Step 5: Generate analysis and recommendations
        analysis_result = generate_analysis(similar_conditions, data.get('age'), data.get('ethnicity'))
        
        return jsonify({
            'success': True,
            'analysis': analysis_result,
            'similar_conditions': similar_conditions,
            'face_detected': True
        })
        
    except Exception as e:
        logger.error(f"Error in skin analysis: {str(e)}")
        return jsonify({'error': 'Analysis failed', 'details': str(e)}), 500

def detect_face_region(image_bytes):
    """
    Use Google Vision API to detect face region
    """
    try:
        image = vision.Image(content=image_bytes)
        response = vision_client.face_detection(image=image)
        faces = response.face_annotations
        
        if not faces:
            return None
        
        # Get the first face's bounding polygon
        face = faces[0]
        vertices = face.bounding_poly.vertices
        
        # Convert to coordinates
        x_coords = [vertex.x for vertex in vertices]
        y_coords = [vertex.y for vertex in vertices]
        
        return {
            'left': min(x_coords),
            'top': min(y_coords),
            'right': max(x_coords),
            'bottom': max(y_coords)
        }
        
    except Exception as e:
        logger.error(f"Face detection error: {str(e)}")
        return None

def crop_to_face(image, face_region):
    """
    Crop image to face region with some padding
    """
    try:
        # Add padding around face
        padding = 50
        left = max(0, face_region['left'] - padding)
        top = max(0, face_region['top'] - padding)
        right = min(image.width, face_region['right'] + padding)
        bottom = min(image.height, face_region['bottom'] + padding)
        
        cropped = image.crop((left, top, right, bottom))
        
        # Resize to standard size for embedding
        cropped = cropped.resize((224, 224))
        
        return cropped
        
    except Exception as e:
        logger.error(f"Face cropping error: {str(e)}")
        return image.resize((224, 224))

def generate_image_embedding(image):
    """
    Generate OpenAI embedding for the image
    """
    try:
        # Convert PIL image to base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Use OpenAI Vision API to generate embedding
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this facial skin image and describe the skin condition, texture, and any visible issues in detail."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        # Extract description for embedding
        description = response.choices[0].message.content
        
        # Generate text embedding from description
        embedding_response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=description
        )
        
        return {
            'embedding': embedding_response.data[0].embedding,
            'description': description
        }
        
    except Exception as e:
        logger.error(f"Embedding generation error: {str(e)}")
        return None

def search_scin_dataset(embedding_data):
    """
    Search SCIN dataset for similar conditions using FAISS vector search
    """
    try:
        import faiss
        import pickle
        from google.cloud import storage
        
        if not embedding_data or 'embedding' not in embedding_data:
            logger.error("No embedding data provided")
            return []
        
        # Load FAISS index and metadata from Google Cloud Storage
        index, metadata = load_scin_index()
        
        if index is None or metadata is None:
            logger.error("Failed to load SCIN index")
            return []
        
        # Convert embedding to numpy array
        query_embedding = np.array(embedding_data['embedding']).astype('float32').reshape(1, -1)
        
        # Normalize the embedding for cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # Search for top 10 similar images
        k = 10
        similarities, indices = index.search(query_embedding, k)
        
        # Process results
        similar_conditions = []
        for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
            if idx < len(metadata):
                condition_data = metadata[idx]
                
                # Convert FAISS distance to similarity score (0-1)
                similarity_score = max(0, 1 - similarity)
                
                similar_conditions.append({
                    'condition': condition_data.get('condition', 'Unknown'),
                    'similarity': float(similarity_score),
                    'description': condition_data.get('description', ''),
                    'fitzpatrick_type': condition_data.get('fitzpatrick_type', ''),
                    'severity': condition_data.get('severity', 'mild'),
                    'treatment_recommendations': condition_data.get('treatments', []),
                    'image_id': condition_data.get('image_id', ''),
                    'confidence': float(similarity_score)
                })
        
        # Filter results with similarity > 0.6
        filtered_conditions = [c for c in similar_conditions if c['similarity'] > 0.6]
        
        # Sort by similarity score
        filtered_conditions.sort(key=lambda x: x['similarity'], reverse=True)
        
        return filtered_conditions[:5]  # Return top 5 matches
        
    except Exception as e:
        logger.error(f"SCIN search error: {str(e)}")
        return []

def load_scin_index():
    """
    Load FAISS index and metadata from Google Cloud Storage
    """
    try:
        import faiss
        import pickle
        from google.cloud import storage
        import tempfile
        
        # Initialize Google Cloud Storage client
        storage_client = storage.Client()
        bucket_name = os.environ.get('SCIN_BUCKET_NAME', 'shine-scin-dataset')
        bucket = storage_client.bucket(bucket_name)
        
        # Download FAISS index
        index_blob = bucket.blob('scin_embeddings.index')
        metadata_blob = bucket.blob('scin_metadata.pkl')
        
        with tempfile.NamedTemporaryFile() as index_file:
            index_blob.download_to_filename(index_file.name)
            index = faiss.read_index(index_file.name)
        
        with tempfile.NamedTemporaryFile() as metadata_file:
            metadata_blob.download_to_filename(metadata_file.name)
            with open(metadata_file.name, 'rb') as f:
                metadata = pickle.load(f)
        
        logger.info(f"Loaded SCIN index with {index.ntotal} embeddings")
        return index, metadata
        
    except Exception as e:
        logger.error(f"Failed to load SCIN index: {str(e)}")
        return None, None

def build_scin_index():
    """
    Build FAISS index from SCIN dataset (run this as a separate process)
    """
    try:
        import faiss
        import pickle
        from google.cloud import storage
        import pandas as pd
        
        # This would be run as a separate data processing job
        # Load SCIN dataset from Google Cloud Storage
        storage_client = storage.Client()
        bucket_name = os.environ.get('SCIN_BUCKET_NAME', 'shine-scin-dataset')
        bucket = storage_client.bucket(bucket_name)
        
        # Load SCIN metadata CSV
        metadata_blob = bucket.blob('scin_dataset.csv')
        metadata_df = pd.read_csv(metadata_blob.open())
        
        # Process each image and generate embeddings
        embeddings = []
        metadata_list = []
        
        for idx, row in metadata_df.iterrows():
            try:
                # Download image
                image_blob = bucket.blob(f"images/{row['image_filename']}")
                image_data = image_blob.download_as_bytes()
                
                # Generate embedding
                image = Image.open(io.BytesIO(image_data))
                embedding_result = generate_image_embedding(image)
                
                if embedding_result and 'embedding' in embedding_result:
                    embeddings.append(embedding_result['embedding'])
                    metadata_list.append({
                        'image_id': row['image_id'],
                        'condition': row['condition'],
                        'description': row['description'],
                        'fitzpatrick_type': row['fitzpatrick_type'],
                        'severity': row['severity'],
                        'treatments': row['treatments'].split(',') if pd.notna(row['treatments']) else []
                    })
                    
                if len(embeddings) % 100 == 0:
                    logger.info(f"Processed {len(embeddings)} images")
                    
            except Exception as e:
                logger.error(f"Error processing image {row['image_filename']}: {str(e)}")
                continue
        
        # Create FAISS index
        embedding_dim = len(embeddings[0])
        index = faiss.IndexFlatIP(embedding_dim)  # Inner product for cosine similarity
        
        # Add embeddings to index
        embeddings_array = np.array(embeddings).astype('float32')
        faiss.normalize_L2(embeddings_array)  # Normalize for cosine similarity
        index.add(embeddings_array)
        
        # Save index and metadata to Google Cloud Storage
        with tempfile.NamedTemporaryFile() as index_file:
            faiss.write_index(index, index_file.name)
            index_blob = bucket.blob('scin_embeddings.index')
            index_blob.upload_from_filename(index_file.name)
        
        with tempfile.NamedTemporaryFile(mode='wb') as metadata_file:
            pickle.dump(metadata_list, metadata_file)
            metadata_file.flush()
            metadata_blob = bucket.blob('scin_metadata.pkl')
            metadata_blob.upload_from_filename(metadata_file.name)
        
        logger.info(f"Built and saved SCIN index with {len(embeddings)} embeddings")
        return True
        
    except Exception as e:
        logger.error(f"Failed to build SCIN index: {str(e)}")
        return False

def generate_analysis(similar_conditions, age=None, ethnicity=None):
    """
    Generate comprehensive skin analysis based on similar conditions
    """
    try:
        analysis = {
            'primary_concerns': [],
            'skin_type': 'combination',
            'recommendations': [],
            'confidence_score': 0.85
        }
        
        if similar_conditions:
            # Extract primary concerns from similar conditions
            for condition in similar_conditions[:3]:  # Top 3 matches
                analysis['primary_concerns'].append({
                    'condition': condition['condition'],
                    'severity': 'mild' if condition['similarity'] > 0.8 else 'moderate',
                    'confidence': condition['similarity']
                })
                
                # Add treatment recommendations
                analysis['recommendations'].extend(condition['treatment_recommendations'])
        
        # Remove duplicates from recommendations
        analysis['recommendations'] = list(set(analysis['recommendations']))
        
        return analysis
        
    except Exception as e:
        logger.error(f"Analysis generation error: {str(e)}")
        return {'error': 'Failed to generate analysis'}

@skin_analysis_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for the skin analysis service
    """
    return jsonify({
        'status': 'healthy',
        'service': 'skin_analysis',
        'version': '2.0'
    })

