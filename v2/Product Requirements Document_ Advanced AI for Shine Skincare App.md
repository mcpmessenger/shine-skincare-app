# Product Requirements Document: Advanced AI for Shine Skincare App

## 1. Introduction

This Product Requirements Document (PRD) outlines the requirements for the Advanced AI Team to develop and integrate robust artificial intelligence capabilities into the Shine Skincare App. The primary goal is to transition the application from its current state of mock data analysis to a fully functional system capable of real-world facial analysis, accurate skin condition assessment, and personalized skincare recommendations. This will be achieved by leveraging the existing SCIN (Skin Condition Image Network) database, stored in Google Cloud Storage, and implementing advanced AI/ML techniques such as face vectorization and cosine similarity.

## 2. Goals and Objectives

### 2.1. Overall Goal

To enable the Shine Skincare App to provide highly accurate, AI-driven skin analysis and personalized product recommendations based on real user facial images, utilizing a comprehensive skin condition database.

### 2.2. Specific Objectives

*   **Integrate SCIN Database**: Fully activate and utilize the SCIN database as the primary source of ground truth data for skin analysis and model training.
*   **Real-time Facial Analysis**: Develop and integrate AI models capable of performing real-time, accurate facial analysis from user-uploaded images.
*   **Skin Condition Detection and Assessment**: Implement AI algorithms to reliably detect, classify, and assess the severity of various skin conditions (e.g., acne, hyperpigmentation, fine lines, dryness, oiliness, sensitivity).
*   **Face Vectorization**: Generate high-dimensional numerical representations (vectors/embeddings) of user faces that capture key skin characteristics.
*   **Cosine Similarity for Recommendations**: Utilize cosine similarity to compare user skin vectors with known skin profiles and product efficacy data to provide highly relevant and personalized recommendations.
*   **Scalable and Performant Solution**: Ensure the AI components are optimized for performance and can scale to handle a growing user base and increasing analysis requests.
*   **Seamless Backend Integration**: Integrate the new AI capabilities into the existing Flask backend, specifically replacing the current mock analysis logic in the `/api/v2/analyze/guest` and potentially other analysis endpoints.

## 3. Scope

This PRD focuses on the AI/ML components and their integration into the backend. It does not cover frontend UI/UX changes unless directly necessitated by the AI functionality. The scope includes:

*   Development and training of AI models for facial analysis and skin condition detection.
*   Implementation of face vectorization techniques.
*   Integration of FAISS or similar libraries for efficient similarity search.
*   Development of data pipelines for accessing and utilizing the SCIN database from Google Cloud Storage.
*   Refactoring of existing backend analysis endpoints to incorporate real AI inference.
*   Establishment of monitoring and feedback mechanisms for AI model performance.

## 4. Stakeholders

*   **Product Owner**: Defines the overall vision and priorities.
*   **Advanced AI Team (Primary)**: Responsible for the design, development, and deployment of AI models and algorithms.
*   **Backend Development Team**: Responsible for integrating AI components into the Flask backend and maintaining API endpoints.
*   **Frontend Development Team**: Consumes the AI-powered API endpoints and displays results to users.
*   **DevOps/Infrastructure Team**: Ensures the necessary infrastructure (e.g., GPU instances, storage) is available and configured for AI workloads.
*   **Data Annotation Team**: Provides high-quality, labeled data for model training and validation.

## 5. User Stories

### 5.1. Guest User Analysis

*   **As a guest user**, I want to upload a photo of my face so that I can receive an immediate, AI-powered analysis of my skin type and primary concerns.
*   **As a guest user**, I want to receive personalized skincare recommendations based on my skin analysis so that I can find suitable products.

### 5.2. Authenticated User Analysis (Future)

*   **As an authenticated user**, I want to save my skin analysis results over time so that I can track my skin health progress.
*   **As an authenticated user**, I want to compare my current skin condition to historical data or ideal skin profiles so that I can understand changes and improvements.

## 6. Functional Requirements

### 6.1. SCIN Database Integration

*   **FR1.1**: The backend shall be able to securely connect to and authenticate with Google Cloud Storage.
*   **FR1.2**: The backend shall be able to load and parse the SCIN dataset metadata (e.g., CSV, JSON files) from a specified Google Cloud Storage bucket.
*   **FR1.3**: The backend shall be able to efficiently retrieve individual image files from the Google Cloud Storage bucket based on paths or filenames provided in the SCIN dataset.
*   **FR1.4**: The backend shall be able to filter and query the SCIN dataset based on various attributes (e.g., skin type, condition, demographics) for model training and similarity search.

### 6.2. Facial Analysis and Feature Extraction

*   **FR2.1**: The system shall accurately detect human faces within uploaded images.
*   **FR2.2**: The system shall extract key facial landmarks (e.g., eyes, nose, mouth, jawline) to enable precise alignment and cropping.
*   **FR2.3**: The system shall perform robust image preprocessing on detected faces, including normalization of lighting, color, and resolution.
*   **FR2.4**: The system shall extract a comprehensive set of skin-specific features from the preprocessed facial images, including but not limited to:
    *   Skin texture (e.g., smoothness, roughness, pore size)
    *   Pigmentation irregularities (e.g., hyperpigmentation, dark spots)
    *   Redness and inflammation (e.g., acne, rosacea)
    *   Fine lines and wrinkles
    *   Oiliness/shine
    *   Hydration indicators

### 6.3. Skin Condition Detection and Classification

*   **FR3.1**: The system shall classify the user's overall skin type (e.g., oily, dry, combination, normal, sensitive).
*   **FR3.2**: The system shall detect and classify the presence of primary skin concerns (e.g., acne, hyperpigmentation, fine lines, dehydration, enlarged pores).
*   **FR3.3**: For each detected skin concern, the system shall provide a severity assessment (e.g., mild, moderate, severe).
*   **FR3.4**: The system shall provide a confidence score for each detected skin type and concern.

### 6.4. Face Vectorization and Similarity Search

*   **FR4.1**: The system shall generate a high-dimensional vector (embedding) for each analyzed face, representing its unique skin characteristics.
*   **FR4.2**: The system shall build and maintain an efficient similarity search index (e.g., using FAISS) from the vectorized SCIN dataset.
*   **FR4.3**: The system shall perform cosine similarity calculations between a user's skin vector and vectors in the SCIN database to find similar skin profiles.

### 6.5. Personalized Recommendations

*   **FR5.1**: The system shall generate personalized skincare product recommendations based on the detected skin type, concerns, and severity.
*   **FR5.2**: Recommendations shall prioritize products known to be effective for similar skin profiles found via cosine similarity in the SCIN database.
*   **FR5.3**: The system shall provide a rationale or explanation for each recommendation.

### 6.6. API Integration

*   **FR6.1**: The `/api/v2/analyze/guest` endpoint shall be updated to perform real AI-driven analysis instead of mock analysis.
*   **FR6.2**: The API response for analysis shall include `skin_type`, `concerns` (with severity), `recommendations` (with rationale), and `confidence` scores.
*   **FR6.3**: The API shall handle image uploads efficiently, supporting common image formats (e.g., JPEG, PNG).

## 7. Non-Functional Requirements

### 7.1. Performance

*   **NFR7.1.1**: Facial analysis and recommendation generation for a single image shall complete within 5 seconds (target: 2 seconds).
*   **NFR7.1.2**: The similarity search (FAISS) on the SCIN dataset shall return results within 1 second.
*   **NFR7.1.3**: The backend AI services shall be able to handle 10 concurrent analysis requests without significant degradation in response time.

### 7.2. Scalability

*   **NFR7.2.1**: The AI models and services shall be deployable on scalable infrastructure (e.g., AWS Elastic Beanstalk with auto-scaling, potentially GPU instances).
*   **NFR7.2.2**: The SCIN database access and similarity search index shall be able to scale to accommodate millions of entries.

### 7.3. Reliability and Availability

*   **NFR7.3.1**: The AI analysis service shall have an uptime of 99.9%.
*   **NFR7.3.2**: The system shall gracefully handle invalid image inputs or analysis failures, returning informative error messages.

### 7.4. Security

*   **NFR7.4.1**: All communication with Google Cloud Storage shall be encrypted (HTTPS).
*   **NFR7.4.2**: User image data shall be handled securely, with appropriate access controls and retention policies.
*   **NFR7.4.3**: AI models shall be protected against adversarial attacks where feasible.

### 7.5. Maintainability

*   **NFR7.5.1**: The AI codebase shall be modular, well-documented, and follow best practices for machine learning engineering.
*   **NFR7.5.2**: The AI models shall be easily retrainable with new data.

## 8. Technical Considerations

### 8.1. AI/ML Frameworks

*   **PyTorch/TensorFlow**: Continue using these frameworks for developing and deploying deep learning models for facial analysis and skin condition classification.
*   **FAISS**: Leverage FAISS for efficient similarity search on high-dimensional skin vectors. Consider integrating it with the `scin_dataset_service` and `scin_integration_manager`.

### 8.2. Data Management

*   **Google Cloud Storage**: Continue using GCS for storing the raw SCIN image data and potentially preprocessed features or model checkpoints.
*   **SCIN Dataset Structure**: Ensure the SCIN dataset (metadata and images) is well-structured and easily queryable for training and inference.

### 8.3. Backend Integration

*   **Flask**: The AI components should integrate seamlessly with the existing Flask backend. This may involve creating new Flask blueprints or services to expose AI functionalities.
*   **API Design**: Maintain consistency with existing API design principles.

### 8.4. Deployment

*   **AWS Elastic Beanstalk**: Explore options for deploying AI models on Elastic Beanstalk, potentially utilizing GPU-enabled instances for inference if computational demands are high.
*   **Containerization (Docker)**: Consider containerizing AI services for easier deployment and environment consistency.

## 9. Open Questions and Dependencies

*   **SCIN Dataset Availability**: Is the SCIN dataset fully curated, labeled, and accessible in Google Cloud Storage? What is its size and quality?
*   **Data Annotation Pipeline**: Is there an established process for annotating new skin images with ground truth data for model training?
*   **Model Training Infrastructure**: What resources are available for training large-scale deep learning models (e.g., GPU clusters)?
*   **Performance Benchmarks**: What are the specific performance targets for each AI component (e.g., inference time per image)?
*   **Ethical AI Considerations**: How will bias in data or models be addressed? What are the privacy implications of facial analysis?

## 10. Success Metrics

*   **Accuracy of Skin Type Classification**: >90% accuracy on a held-out test set.
*   **Accuracy of Primary Concern Detection**: >85% F1-score for each primary concern.
*   **Recommendation Relevance**: Measured by user feedback and conversion rates (if applicable).
*   **API Response Time**: Average response time for `/api/v2/analyze/guest` (with AI) < 3 seconds.
*   **SCIN Integration**: Successful loading and querying of the full SCIN dataset.

## 11. Future Considerations

*   **Personalized Skincare Routines**: Beyond product recommendations, offer full skincare routines.
*   **Progress Tracking**: Allow users to track their skin health progress over time with visual comparisons.
*   **Integration with Wearables/IoT**: Connect with devices for real-time skin data.
*   **Dermatologist Consultation Integration**: Offer tele-consultations based on AI analysis.

## 12. Appendix

### 12.1. Relevant Codebase Files

*   `backend/app/models/scin_integration.py`
*   `backend/app/routes/scin_integration.py`
*   `backend/app/services/scin_dataset_service.py`
*   `backend/app/services/scin_demographic_search_service.py`
*   `backend/app/services/scin_integration_manager.py`
*   `backend/app/services/scin_skin_condition_service.py`
*   `backend/enhanced-image-analysis.py`
*   `backend/app/enhanced_analysis_router.py`

## References

[1] mcpmessenger/shine-skincare-app GitHub Repository: `https://github.com/mcpmessenger/shine-skincare-app`

---

**Author**: Manus AI
**Date**: July 29, 2025




## 6.7. User Experience and Transparency (New Section)

*   **FR6.7.1**: The application shall provide clear visual and textual feedback to the user during the facial scanning process, indicating that their face is being analyzed.
*   **FR6.7.2**: The application shall explicitly inform the user that their facial image is being compared against the SCIN database using AI-driven similarity search (cosine similarity).
*   **FR6.7.3**: Upon completion of the analysis, the application shall visually present examples of similar skin conditions from the SCIN database that closely match the user's analyzed profile, along with their corresponding case IDs or relevant metadata.
*   **FR6.7.4**: The application shall provide a confirmation to the user when a face has been successfully detected in the uploaded image, ideally leveraging the Google Vision API's face detection capabilities.

## 6.8. Image Preprocessing with Google Vision API (New Section)

*   **FR6.8.1**: The system shall utilize the Google Vision API to accurately detect and isolate the primary human face within an uploaded image.
*   **FR6.8.2**: Only the isolated facial region shall be passed to subsequent AI/ML models for detailed skin analysis and vectorization, optimizing processing and focusing on relevant areas.
*   **FR6.8.3**: The system shall handle cases where no face is detected or multiple faces are detected, providing appropriate user feedback and guidance.

## 7. Non-Functional Requirements (Updates)

### 7.1. Performance

*   **NFR7.1.1**: Facial analysis and recommendation generation for a single image shall complete within 5 seconds (target: 2 seconds), including Google Vision API processing.

### 7.3. Reliability and Availability

*   **NFR7.3.3**: The system shall gracefully handle cases where Google Vision API fails to detect a face or returns an error, providing user-friendly messages and alternative options.

## 9. Open Questions and Dependencies (Updates)

*   **Google Vision API Integration**: What are the cost implications and rate limits for extensive use of Google Vision API for face detection and isolation?



