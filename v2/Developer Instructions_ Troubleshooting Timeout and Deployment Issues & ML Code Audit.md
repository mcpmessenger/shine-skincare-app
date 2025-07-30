# Developer Instructions: Troubleshooting Timeout and Deployment Issues & ML Code Audit

## 1. Introduction

This document provides comprehensive instructions for developers to systematically address timeout and deployment issues within the Shine Skincare App backend, particularly focusing on the integration of real Machine Learning (ML) algorithms and capabilities. It also outlines a code audit process to ensure that the intended AI functionalities are correctly implemented and utilized.

This guide builds upon the existing project documentation, including the Product Requirements Document, SCIN Database Integration Analysis, and the AWS Infrastructure documentation. It aims to provide actionable steps for debugging, optimizing, and verifying the AI-powered features.

## 2. Addressing Timeout Issues

Timeout issues in the Shine Skincare App backend can stem from various sources, especially with the introduction of computationally intensive AI/ML processes and external API calls (e.g., Google Vision API, GCS access). This section outlines common causes and solutions.

### 2.1. Long-Running AI/ML Inference

**Problem**: Facial analysis, image vectorization, and similarity searches can be time-consuming, potentially exceeding typical API gateway or load balancer timeouts (e.g., 30-60 seconds).

**Solutions**:

1.  **Optimize ML Models**: 
    *   **Model Quantization/Pruning**: Reduce model size and computational requirements without significant loss in accuracy. Libraries like TensorFlow Lite or ONNX Runtime can help with this.
    *   **Efficient Architectures**: Ensure the chosen models (e.g., for skin classification, vectorization) are optimized for inference speed. Consider MobileNet or EfficientNet variants for mobile-first applications.
    *   **Batch Processing**: If multiple images are processed in a single request (less likely for a single user upload, but relevant for internal processes), batching can improve throughput.

2.  **Hardware Acceleration (GPU)**:
    *   **Problem**: CPU-only instances on Elastic Beanstalk may not be sufficient for real-time AI inference, leading to slow processing.
    *   **Solution**: Deploy the Flask backend on AWS Elastic Beanstalk environments configured with GPU-enabled EC2 instances (e.g., `g4dn` or `p3` instance types). This requires updating the `cloudformation-template.yaml` and potentially the `Procfile` or Dockerfile to utilize GPU resources.
    *   **Action**: If using `faiss-gpu`, ensure the Elastic Beanstalk environment has NVIDIA drivers and CUDA installed, or use a pre-built Docker image with these dependencies.

3.  **Increase Timeout Settings**:
    *   **Problem**: Default timeouts on load balancers (e.g., AWS Application Load Balancer - ALB) or web servers (e.g., Gunicorn/Nginx within Elastic Beanstalk) might be too low.
    *   **Solution**: Increase the idle timeout for the ALB and the Gunicorn/Nginx worker timeouts in your Elastic Beanstalk configuration. While this can mitigate immediate timeouts, it's a workaround and not a solution for slow processing.
    *   **Action (ALB)**: In the AWS Console, navigate to EC2 -> Load Balancers, select your ALB, and modify the `Idle timeout` attribute (e.g., to 120 seconds).
    *   **Action (Elastic Beanstalk)**: Add or modify configuration files (`.ebextensions/*.config`) to set Gunicorn/Nginx timeouts. For example, for Gunicorn:
        ```yaml
        option_settings:
          aws:elasticbeanstalk:container:python:
            WSGIPath: application:app
            NumProcesses: 1
            NumThreads: 15
          aws:elasticbeanstalk:application:environment:
            PYTHONUNBUFFERED: 1
          aws:elasticbeanstalk:environment:proxy:staticfiles:
            /static: static
          aws:elasticbeanstalk:container:python:platform:
            # Set Gunicorn timeout to 120 seconds
            GUNICORN_TIMEOUT: 120
        ```

4.  **Asynchronous Processing (Long-Term Solution)**:
    *   **Problem**: Synchronous API calls block the client until the AI analysis is complete, leading to perceived slowness and potential timeouts for the user.
    *   **Solution**: Implement an asynchronous processing pattern using message queues (e.g., AWS SQS, Celery with Redis/RabbitMQ). The `/api/v2/analyze/guest` endpoint would quickly return an `analysis_id`, and the actual AI processing would happen in a background worker. The frontend would then poll a status endpoint (`/api/enhanced-analysis/status/<analysis_id>`) or receive a webhook notification when the analysis is complete.
    *   **Action**: This requires significant architectural changes, including introducing a task queue, worker processes, and a mechanism for storing and retrieving analysis results (e.g., a database or cache).

### 2.2. Google Cloud Storage (GCS) Access Issues

**Problem**: Slow or failed access to the SCIN dataset in GCS can cause delays and timeouts.

**Solutions**:

1.  **Verify Network Connectivity**: Ensure the Elastic Beanstalk instances have proper network access to Google Cloud Storage. This typically involves outbound internet access from the VPC subnets.

2.  **Optimize GCS Access**: 
    *   **Regional Proximity**: If possible, host the GCS bucket in a region geographically close to your AWS Elastic Beanstalk deployment (e.g., `us-east-1` for AWS and a `us-east` region for GCP).
    *   **Caching**: Implement local caching for frequently accessed SCIN metadata or smaller image files to reduce repeated GCS calls. The `SCINIntegrationManager` already has some caching mechanisms for vectors.
    *   **Parallel Downloads**: If loading multiple images, use concurrent downloads where appropriate.

3.  **Authentication and Authorization**: 
    *   **Problem**: Incorrect IAM roles or service account configurations can lead to access denied errors or slow authentication.
    *   **Solution**: Double-check that the GCP service account used by the Flask app has `storage.objects.get` and `storage.objects.list` permissions on the SCIN bucket. Ensure the AWS IAM role attached to the Elastic Beanstalk instances has permissions to retrieve the GCP credentials securely.
    *   **Action**: Review the `load_gcp_credentials` function (or similar mechanism) in your Flask app to ensure it correctly loads and applies the GCP credentials.

## 3. Resolving Deployment Issues

Deployment issues often manifest as failed builds, services not starting, or applications not responding after deployment. This section provides a systematic approach to troubleshooting and resolving these problems.

### 3.1. Common Deployment Failures and Solutions

1.  **Missing Dependencies**: 
    *   **Problem**: The application fails to start because required Python packages are not installed in the Elastic Beanstalk environment.
    *   **Solution**: Ensure `backend/requirements.txt` is comprehensive and up-to-date. Elastic Beanstalk automatically installs packages listed in this file during deployment.
    *   **Action**: Verify that all necessary ML libraries (`numpy`, `opencv-python`, `Pillow`, `gcsfs`, `pandas`, `tqdm`, `scikit-learn`, `faiss-cpu`/`faiss-gpu`) are explicitly listed.

2.  **Incorrect `Procfile` or WSGI Path**: 
    *   **Problem**: Elastic Beanstalk cannot find or start the Flask application.
    *   **Solution**: Confirm that your `Procfile` (if used) or the `WSGIPath` in `.ebextensions` correctly points to your Flask application instance (e.g., `application:app` or `port-fixed-backend:app`).
    *   **Action**: For the `port-fixed-backend.py` file, ensure the `app` object is correctly exposed and the WSGI path points to it.

3.  **Environment Variable Issues**: 
    *   **Problem**: The application fails due to missing or incorrect environment variables (e.g., `GOOGLE_APPLICATION_CREDENTIALS`, database URLs).
    *   **Solution**: Set environment variables in the Elastic Beanstalk configuration (Software -> Environment properties) or via `.ebextensions`.
    *   **Action**: Ensure `GOOGLE_APPLICATION_CREDENTIALS` is set if you are loading GCP credentials from a file. Verify other critical variables like `DATABASE_URL`, `JWT_SECRET_KEY`, etc.

4.  **Security Group / Network Configuration**: 
    *   **Problem**: The application deploys but is unreachable, or cannot connect to external services (e.g., GCS, RDS).
    *   **Solution**: Check the security groups associated with your Elastic Beanstalk instances and the ALB. Ensure inbound rules allow traffic on necessary ports (e.g., 80/443 for HTTP/HTTPS) and outbound rules allow connections to external services.
    *   **Action**: Verify that the Elastic Beanstalk instances are in public subnets or have a NAT Gateway for outbound internet access if in private subnets.

5.  **Insufficient Permissions**: 
    *   **Problem**: The Elastic Beanstalk instance role lacks permissions to perform AWS actions (e.g., writing logs to CloudWatch, accessing S3).
    *   **Solution**: Review the IAM role attached to your Elastic Beanstalk environment and add any missing permissions.
    *   **Action**: Ensure the role has `AWSElasticBeanstalkWebTier` and `AWSElasticBeanstalkWorkerTier` managed policies, plus any custom policies for GCS access or other AWS services.

### 3.2. Using the Provided Deployment Scripts

The `aws-infrastructure` directory contains PowerShell scripts for deployment. While they are PowerShell-based, the underlying AWS CLI commands can be adapted for other shell environments.

*   **`deploy-simple.ps1`**: For initial setup. This script likely sets up the basic Elastic Beanstalk environment.
*   **`update-ecs-service.ps1`**: **Crucial for updates.** This script handles building a new Docker image from your `backend/` directory, pushing it to ECR, and updating the ECS service to use the new image. This is the primary script to use after making code changes.

    *   **Key Parameter**: Use `-BuildImage` to ensure your latest code changes are built into a new Docker image and deployed.
    *   **Monitoring**: Always monitor CloudWatch logs (`/ecs/production-shine-api`) during and after deployment to catch application-level errors.

**Action**: After making changes to the backend code (e.g., updating `requirements.txt`, modifying Python files), navigate to the `aws-infrastructure` directory and run:

```powershell
.\update-ecs-service.ps1 -BuildImage
```

Or, if you are not on a PowerShell environment, you would need to manually execute the steps outlined in `ECS_SERVICE_UPDATE_GUIDE.md` (Docker build, ECR push, ECS service update via AWS CLI).

## 4. Code Audit for Real Machine Learning Algorithms and Capabilities

The project aims to move from mock analysis to real AI. This section guides you through auditing the backend code to ensure that real ML algorithms are being used and their capabilities are fully leveraged.

### 4.1. Verify ML Library Usage

**Objective**: Confirm that `numpy`, `opencv-python` (`cv2`), `Pillow` (`PIL.Image`), and potentially `PyTorch`/`TensorFlow` are actively used for image processing and ML inference, not just imported.

**Audit Steps**:

1.  **Examine `backend/enhanced-image-analysis.py`**: 
    *   Look for the `ML_AVAILABLE` flag. Ensure it evaluates to `True` in the deployed environment. If it's `False`, it indicates missing dependencies or an environment issue.
    *   Trace the calls to `analyze_skin_tone`, `detect_imperfections`, and `analyze_skin_texture`. These functions contain `cv2` and `numpy` operations. Verify that these are the functions being called by the `/api/v2/analyze/guest` endpoint, and not a mock fallback.

2.  **Examine `backend/app/enhanced_analysis_router.py`**: 
    *   This file defines the `EnhancedAnalysisRouter` which orchestrates calls to various services (`google_vision`, `skin_classifier`, `demographic_search`).
    *   Verify that `service_manager.get_service()` calls are correctly retrieving instances of `SCINDatasetService`, `EnhancedImageVectorizationService`, `FAISSService`, `GoogleVisionService`, `SkinClassifierService`, and `DemographicSearchService`.

3.  **Inspect Service Implementations**: 
    *   **`backend/app/services/enhanced_image_vectorization_service.py`**: This service should contain the actual logic for generating face embeddings using deep learning models (e.g., a pre-trained CNN). Verify that it's not returning mock vectors.
    *   **`backend/app/services/faiss_service.py`**: Confirm that this service is correctly initializing and interacting with a FAISS index, and performing real similarity searches, not just returning dummy results.
    *   **`backend/app/services/scin_dataset_service.py`**: Ensure this service is successfully loading data from the real GCS bucket and providing actual image data for vectorization.
    *   **`backend/app/services/skin_classifier_service.py`**: This service should implement or call a real ML model for skin type and condition classification.

**Action**: For each of these services, add logging statements to confirm that real data is being processed and that ML models are being loaded and used. For example, log the shape of vectors, confidence scores from models, or the number of items in the FAISS index.

### 4.2. Verify SCIN Dataset Integration

**Objective**: Ensure the SCIN dataset is actively used for analysis and recommendations.

**Audit Steps**:

1.  **SCIN Data Loading**: 
    *   Verify that `SCINDatasetService.load_metadata()` is successfully called during application startup (or initialization of `SCINIntegrationManager`).
    *   Check logs for messages indicating successful loading of `scin_cases.csv` and `scin_labels.csv` from GCS.

2.  **Image Retrieval from GCS**: 
    *   Confirm that `SCINDatasetService.load_image_from_gcs()` is being called when building the FAISS index or retrieving similar images.
    *   Ensure there are no errors related to GCS access in the logs.

3.  **FAISS Index Population**: 
    *   Verify that `SCINIntegrationManager.build_similarity_index()` is successfully executed. This process involves vectorizing SCIN images and adding them to the FAISS index.
    *   Check the `faiss_service.get_index_info()` to confirm that the index is populated with a significant number of vectors.

4.  **Similarity Search in Recommendations**: 
    *   Trace the `get_smart_recommendations` function. It should be receiving `similar_scin_images` from the `scin_integration_manager.search_similar_images_by_vector` call.
    *   Confirm that the recommendation logic actually uses the `case_id`, `condition`, `skin_type`, etc., from the `similar_scin_images` to generate personalized recommendations, rather than generic ones.

**Action**: Implement a dedicated health check endpoint (e.g., `/api/scin/health`) that reports the status of SCIN dataset loading, vector generation, and FAISS index population. This endpoint should return `True` for `scin_loaded`, `vectors_generated`, and `faiss_populated` once the system is fully operational.

### 4.3. Code Quality and Best Practices for ML

**Objective**: Ensure the ML code adheres to best practices for maintainability, performance, and reliability.

**Audit Steps**:

1.  **Error Handling**: 
    *   Verify that all ML-related functions and service calls have robust `try-except` blocks to gracefully handle exceptions (e.g., image processing errors, model loading failures, GCS connection issues).
    *   Ensure informative error messages are logged and returned to the client when appropriate.

2.  **Logging**: 
    *   Implement detailed logging at various stages of the AI pipeline: input validation, model inference start/end, service calls, and result formatting.
    *   Use appropriate logging levels (INFO, WARNING, ERROR) to distinguish between normal operation and issues.

3.  **Resource Management**: 
    *   Ensure that image files and other resources are properly closed or released after use to prevent memory leaks.
    *   If using GPU resources, ensure they are correctly allocated and deallocated.

4.  **Configuration Management**: 
    *   Externalize configurable parameters (e.g., model paths, GCS bucket names, FAISS index paths, confidence thresholds) using environment variables or a dedicated configuration file. Avoid hardcoding these values.

5.  **Modularity**: 
    *   Confirm that the AI logic is well-separated into distinct services and modules, as observed in `backend/app/services/`.
    *   This promotes reusability, testability, and easier updates.

## 5. Conclusion

By systematically following these instructions, developers can effectively troubleshoot and resolve timeout and deployment challenges, and ensure the full activation and optimal performance of the Shine Skincare App's advanced AI features. The code audit steps will help verify that real ML algorithms are correctly integrated and leveraging the crucial SCIN dataset for accurate and personalized skin analysis.

---

**Author**: Manus AI
**Date**: July 29, 2025





## 6. Enhancing User Experience with Transparent AI and Visual Feedback

To improve user trust and understanding, the application should provide clear feedback on the AI analysis process, especially regarding facial scanning and SCIN database comparison.

### 6.1. Real-time Feedback During Facial Scanning

**Objective**: Inform the user that their face is being analyzed and that the process is active.

**Implementation Details (Frontend)**:

1.  **Visual Cues**: During the image upload and processing phase, display an animation (e.g., a scanning effect over the uploaded image, a progress bar, or a subtle glow around the face area) to indicate active analysis.
2.  **Textual Prompts**: Show messages like "Analyzing your skin...", "Scanning for key features...", or "Comparing with thousands of skin profiles..." to keep the user informed.

### 6.2. Explicit Communication of SCIN Database Comparison

**Objective**: Clearly communicate to the user that their facial data is being compared against the SCIN database using advanced AI techniques.

**Implementation Details (Frontend/Backend)**:

1.  **Post-Analysis Message**: After the analysis is complete, but before displaying detailed results, present a brief message to the user, for example:
    > "Your unique skin profile has been analyzed and compared to over [Number] entries in our comprehensive SCIN database using advanced AI similarity search to find the most relevant insights for you."
2.  **Terminology**: Use terms like "AI-driven similarity search" and "cosine similarity" in user-facing explanations where appropriate, but ensure they are accompanied by clear, non-technical explanations.

### 6.3. Visual Presentation of Similar SCIN Conditions

**Objective**: Provide tangible evidence of the AI's work by showing similar cases from the SCIN database.

**Implementation Details (Frontend/Backend)**:

1.  **API Enhancement**: The `/api/v2/analyze/guest` endpoint (or a new dedicated endpoint) should return not only the `similar_scin_profiles` data (as outlined in the updated PRD) but also the corresponding image URLs from GCS for these similar profiles.
2.  **Frontend Display**: 
    *   **Carousel/Gallery**: Display a carousel or gallery of 3-5 images from the `similar_scin_profiles` returned by the backend.
    *   **Contextual Information**: For each image, display relevant metadata such as the `condition`, `skin_type`, and the `distance` (similarity score) to the user's profile. Explain that a lower distance means higher similarity.
    *   **User Consent**: Consider adding a prompt asking for user consent before displaying these images, especially if they are real patient images (even if anonymized).

**Action (Backend)**: In the `analyze_skin_guest` function (or the function handling `/api/v2/analyze/guest`), ensure that when `similar_scin_images` are retrieved, the `image_path` (which is a GCS URL) is included in the response for each similar profile. The `SCINDatasetService`'s `load_image_from_gcs` can provide these URLs.

### 6.4. Google Vision API for Face Isolation and Confirmation

**Objective**: Improve the accuracy of analysis and provide user confidence by isolating the face and confirming its detection.

**Implementation Details (Backend)**:

1.  **Pre-processing with Google Vision API**: Before passing the image to the `EnhancedImageVectorizationService` or `SkinClassifierService`, use the Google Vision API to detect faces and extract the bounding box of the primary face.

    **Action (Backend)**: Modify the `analyze_skin_guest` function in `backend/enhanced-image-analysis.py` (or `backend/app/enhanced_analysis_router.py`) to include the following steps:

    *   **Call Google Vision API for Face Detection**: 
        ```python
        google_vision_service = service_manager.get_service("google_vision")
        vision_response = google_vision_service.detect_faces_from_bytes(image_data)

        if not vision_response or not vision_response.get("face_found"):
            # Handle no face detected: return error or prompt user
            return jsonify({"success": False, "message": "No face detected in the image. Please upload a clear photo of your face."}), 400

        face_bounding_box = vision_response.get("bounding_box") # { 'x': ..., 'y': ..., 'width': ..., 'height': ... }
        # Extract face image using PIL
        from PIL import Image
        from io import BytesIO
        original_image = Image.open(BytesIO(image_data))
        cropped_face_image = original_image.crop((
            face_bounding_box["x"],
            face_bounding_box["y"],
            face_bounding_box["x"] + face_bounding_box["width"],
            face_bounding_box["y"] + face_bounding_box["height"]
        ))

        # Convert cropped_face_image back to bytes if needed for other services
        cropped_face_bytes_io = BytesIO()
        cropped_face_image.save(cropped_face_bytes_io, format=original_image.format)
        cropped_face_data = cropped_face_bytes_io.getvalue()
        ```

    *   **Pass Cropped Face to Subsequent Services**: Ensure that `cropped_face_data` (or `cropped_face_image` if the service accepts PIL Image objects) is passed to `enhanced_image_vectorization_service.vectorize_image` and `skin_classifier_service.classify_skin_type`.

2.  **Face Detected Confirmation (Frontend)**:
    *   **Visual Confirmation**: Once the backend confirms face detection (e.g., by returning a `face_detected: true` flag in the initial response or a specific status), display a visual cue to the user, such as a checkmark or a brief animation indicating successful face capture.
    *   **Textual Confirmation**: A message like "Face detected! Analyzing your skin..." can be shown.

**Action (Backend)**: Update the `/api/v2/analyze/guest` response to include a `face_detected: true/false` flag and potentially the bounding box coordinates if the frontend needs to highlight the detected face.

### 6.5. Error Handling for Face Detection

**Objective**: Gracefully handle scenarios where no face is detected or multiple faces are present.

**Implementation Details (Backend/Frontend)**:

1.  **Backend Response**: If `google_vision_service.detect_faces_from_bytes` indicates no face found, the backend should return a specific error message (e.g., `{"success": false, "message": "No face detected. Please ensure your face is clearly visible in the photo."}`).
2.  **Frontend Guidance**: The frontend should interpret this error and provide clear instructions to the user on how to take a better photo (e.g., "Make sure your face is well-lit and centered", "Only one face should be in the photo").

## 7. Updated API Specification for `/api/v2/analyze/guest` (Additions)

**Response (200 OK) - Additions to `ml_analysis` section**:

```json
{
  "data": {
    "results": {
      // ... existing fields
    },
    "ml_analysis": {
      // ... existing fields
      "face_detection": {
        "face_detected": "boolean",
        "bounding_box": {
          "x": "number",
          "y": "number",
          "width": "number",
          "height": "number"
        },
        "confidence": "number" // Confidence score from Google Vision API
      },
      "similar_scin_profiles": [
        {
          // ... existing fields
          "image_url": "string" // URL to the similar SCIN image in GCS
        }
      ]
    },
    // ... existing fields
  }
}
```

**Error Responses (400 Bad Request) - New Error Type**:

```json
{
  "success": false,
  "message": "No face detected. Please ensure your face is clearly visible in the photo.",
  "error_type": "face_detection_error"
}
```



