# Requirements Document

## Introduction

This specification defines the requirements for upgrading the Shine Skincare mobile application from its current basic color-scanning functionality to an advanced AI-powered skin analysis system. The upgrade will integrate Google Vision API for facial detection, FAISS similarity search using a database of known skin conditions (SCIN dataset), and machine learning models to provide intelligent diagnoses and personalized product recommendations. This transformation moves the application from mock data to real-world AI inference, significantly enhancing accuracy and user value.

## Requirements

### Requirement 1: Google Vision API Integration for Face Detection

**User Story:** As a user uploading a selfie for skin analysis, I want the system to automatically detect and isolate my face from the image, so that the analysis focuses on the relevant facial area and provides accurate results.

#### Acceptance Criteria

1. WHEN a user uploads an image THEN the system SHALL call the Google Vision API to detect faces in the image
2. WHEN no face is detected in the uploaded image THEN the system SHALL return an error message "No face detected" and prompt the user to retry
3. WHEN multiple faces are detected in the uploaded image THEN the system SHALL return an error message "Multiple faces detected. Please upload an image with a single face"
4. WHEN exactly one face is detected THEN the system SHALL crop the image to the face's bounding box coordinates
5. WHEN the Google Vision API call fails THEN the system SHALL handle the error gracefully and return an appropriate error message to the user

### Requirement 2: Enhanced Image Vectorization and FAISS Similarity Search

**User Story:** As a user seeking skin analysis, I want the system to compare my facial features with a database of known skin conditions, so that I receive accurate diagnoses based on similar cases.

#### Acceptance Criteria

1. WHEN a face is successfully cropped THEN the system SHALL convert the cropped facial image into a high-dimensional numerical vector using a pre-trained deep learning model
2. WHEN the face vector is generated THEN the system SHALL query the FAISS index to find the k most similar SCIN profiles (where k=5 by default)
3. WHEN the FAISS search is performed THEN the system SHALL return similarity distances and indices of the nearest neighbors
4. WHEN similar profiles are found THEN the system SHALL retrieve the corresponding metadata including skin condition labels, severity levels, and associated recommendations
5. WHEN the FAISS index is unavailable or corrupted THEN the system SHALL handle the error and provide fallback functionality

### Requirement 3: AI-Powered Skin Condition Classification

**User Story:** As a user receiving skin analysis results, I want the system to classify my skin type and identify specific concerns with confidence scores, so that I understand my skin condition and its severity level.

#### Acceptance Criteria

1. WHEN similar SCIN profiles are retrieved THEN the system SHALL classify the user's overall skin type based on the aggregated data from nearest neighbors
2. WHEN skin classification is performed THEN the system SHALL identify specific skin concerns (acne, dryness, sensitivity, aging, etc.) with individual confidence scores
3. WHEN each concern is identified THEN the system SHALL assign a severity level of mild, moderate, or severe
4. WHEN classification results are generated THEN the system SHALL include confidence scores ranging from 0.0 to 1.0 for each identified concern
5. WHEN the classification model fails THEN the system SHALL provide a graceful fallback with basic skin type detection

### Requirement 4: Personalized Product Recommendation Engine

**User Story:** As a user who has received skin analysis results, I want to see personalized product recommendations with clear rationales, so that I can make informed decisions about skincare products that address my specific concerns.

#### Acceptance Criteria

1. WHEN skin conditions are classified THEN the system SHALL generate personalized product recommendations based on the identified concerns and their severity levels
2. WHEN recommendations are generated THEN the system SHALL prioritize products that have proven efficacy for the identified skin conditions
3. WHEN each recommendation is provided THEN the system SHALL include a clear rationale explaining why the product is suitable for the user's specific skin profile
4. WHEN similar SCIN profiles have associated product data THEN the system SHALL incorporate this information into the recommendation logic
5. WHEN no suitable products are found for a specific concern THEN the system SHALL provide general skincare advice or suggest consulting a dermatologist

### Requirement 5: Enhanced Frontend User Experience

**User Story:** As a user interacting with the skin analysis feature, I want clear feedback throughout the process and comprehensive results display, so that I understand what's happening and can easily interpret my results.

#### Acceptance Criteria

1. WHEN an image is being processed THEN the system SHALL display clear loading indicators with progress messages such as "Detecting face..." and "Analyzing skin..."
2. WHEN a face is successfully detected THEN the system SHALL display a confirmation message "Face detected, analyzing your skin..."
3. WHEN analysis results are ready THEN the system SHALL display the diagnosed skin conditions with their severity levels and confidence scores
4. WHEN similar SCIN profiles are found THEN the system SHALL display visual examples of similar skin conditions with relevant metadata
5. WHEN product recommendations are generated THEN the system SHALL present them clearly with rationales and easy-to-understand formatting
6. WHEN any error occurs during the process THEN the system SHALL provide user-friendly error messages with options to retry or adjust their approach

### Requirement 6: API Endpoint Enhancement and Data Structure

**User Story:** As a frontend application, I want to interact with a robust API endpoint that provides comprehensive analysis results in a structured format, so that I can display rich information to users effectively.

#### Acceptance Criteria

1. WHEN the frontend calls the `/api/v2/analyze/guest` endpoint with an image THEN the system SHALL orchestrate the complete AI pipeline and return structured results
2. WHEN the API response is generated THEN it SHALL include `skin_type`, `concerns`, `recommendations`, and `similar_scin_profiles` fields
3. WHEN image uploads are processed THEN the system SHALL support common formats including JPEG and PNG with efficient handling
4. WHEN the API processes requests THEN it SHALL handle concurrent users and maintain response times under 30 seconds for 95% of requests
5. WHEN API errors occur THEN the system SHALL return appropriate HTTP status codes with descriptive error messages in JSON format

### Requirement 7: Performance and Scalability Requirements

**User Story:** As a user of the application, I want fast and reliable skin analysis results even during peak usage times, so that I have a smooth experience regardless of system load.

#### Acceptance Criteria

1. WHEN the system processes skin analysis requests THEN 95% of requests SHALL complete within 30 seconds
2. WHEN the system experiences concurrent usage THEN it SHALL support at least 50 simultaneous users without degradation
3. WHEN the FAISS index is loaded THEN it SHALL be optimized for fast similarity searches with sub-second query times
4. WHEN the system starts up THEN the FAISS index and ML models SHALL be loaded efficiently to minimize initialization time
5. WHEN system resources are constrained THEN the application SHALL gracefully handle resource limitations and provide appropriate user feedback

### Requirement 8: Data Management and Storage Integration

**User Story:** As a system administrator, I want the AI models and SCIN dataset to be properly managed and accessible, so that the analysis pipeline has reliable access to the necessary data and models.

#### Acceptance Criteria

1. WHEN the system initializes THEN it SHALL load the pre-vectorized SCIN dataset from Google Cloud Storage
2. WHEN the FAISS index is built THEN it SHALL be persisted to storage for efficient loading on subsequent startups
3. WHEN ML models are needed THEN they SHALL be loaded from the appropriate storage location (PyTorch/TensorFlow models)
4. WHEN the system accesses the product database THEN it SHALL retrieve current product information for recommendations
5. WHEN data updates are available THEN the system SHALL support updating the FAISS index and models without requiring full system restart