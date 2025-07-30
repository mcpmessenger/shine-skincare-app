# Developer Instructions: Shine Skincare App v2 Upgrade

## 1. Introduction

This document provides comprehensive instructions for upgrading the Shine Skincare mobile application from its current color-scanning functionality to an advanced AI-powered system. Version 2 will leverage the Google Vision API for precise facial detection and isolation, followed by a cosine similarity search using a FAISS database of known skin conditions to provide intelligent diagnoses and personalized recommendations. This upgrade aims to significantly enhance the accuracy and utility of the skin analysis feature, moving from mock data to real-world AI inference.

## 2. Overview of Changes

The core of this upgrade involves shifting from a basic image analysis to a sophisticated AI pipeline. This requires significant modifications to both the frontend (user interaction and display) and the backend (image processing, AI inference, and data management).

### 2.1. Updated User Flow

The user flow will be enhanced to incorporate facial detection and feedback. The key steps are:

1.  **User Starts Analysis**: User initiates the skin analysis process.
2.  **Upload Photo**: User uploads a selfie.
3.  **Backend: Receive Image**: The backend receives the uploaded image.
4.  **Google Vision API: Detect Face**: The backend calls the Google Vision API to detect faces.
5.  **Face Detected?**: Conditional check:
    *   **No**: Frontend displays a "No Face Detected" error, and the user retries/exits.
    *   **Yes**: Backend proceeds to crop the detected face.
6.  **Backend: Crop Face**: The detected face region is isolated.
7.  **Backend: Vectorize Cropped Face**: The cropped face is converted into a high-dimensional vector (embedding).
8.  **Backend: Search FAISS for Similar SCIN Profiles**: The vectorized face is used to query the FAISS database for similar skin profiles from the SCIN dataset.
9.  **Backend: Classify Skin Conditions**: Based on the similar profiles, skin conditions are classified.
10. **Backend: Generate Recommendations**: Personalized recommendations are generated.
11. **Backend: Return Analysis Results + Similar SCIN Profiles**: The analysis results, including detected conditions, confidence scores, and similar SCIN profiles, are returned to the frontend.
12. **Frontend: Display Face Detected/Processing Message**: User receives feedback that their face was detected and analysis is in progress.
13. **Frontend: Display Analysis Results**: The diagnosed skin conditions and their severity are displayed.
14. **Frontend: Display Similar SCIN Images with Metadata**: Visual examples of similar skin conditions from the SCIN database are shown.
15. **Frontend: Display Personalized Recommendations**: The final product recommendations are presented.

### 2.2. Architectural Changes

The updated architecture introduces new components and modifies existing ones to support the advanced AI capabilities. Key changes include:

*   **Google Vision API Integration**: A new service or module within the backend will be responsible for interacting with the Google Vision API for face detection and cropping.
*   **Enhanced Image Vectorization Service**: This service will be responsible for converting cropped facial images into numerical vectors suitable for FAISS.
*   **FAISS Similarity Search Index**: The SCIN dataset will be indexed using FAISS for efficient similarity searches. This will likely reside alongside the existing `SCIN Dataset Service` and `SCIN Demographic Search Service`.
*   **Skin Classifier Service**: This service will leverage the vectorized face and FAISS search results to classify specific skin conditions.
*   **Recommendation Engine**: This component will generate personalized product recommendations based on the classified skin conditions and similar SCIN profiles.
*   **Enhanced Analysis Router**: This will orchestrate the flow between the new and existing backend services.

These services will interact with the existing `Google Cloud Storage (SCIN Dataset)` and `PyTorch/TensorFlow Models` for vectorization and classification, and the `Product Database` for recommendations. The frontend (Next.js/TypeScript) will continue to interact with the backend (Flask/Python) via the `/api/v2/analyze/guest` endpoint, which will now trigger the full AI pipeline.

## 3. Frontend Development Instructions

### 3.1. User Interface Updates

*   **Loading States**: Implement clear loading indicators while the image is being processed and analyzed by the backend, especially during the Google Vision API call and FAISS search.
*   **Error Handling**: Display user-friendly error messages if no face is detected, multiple faces are detected, or if there are other issues with the image upload or analysis. Provide options for the user to retry or adjust their photo.
*   **Feedback Messages**: Provide explicit feedback to the user, such as "Face Detected, Analyzing Your Skin..." after successful facial detection.
*   **Display Similar SCIN Profiles**: Design a section to display images of similar skin conditions from the SCIN database, along with relevant metadata (e.g., condition type, severity). This will enhance transparency and user understanding.
*   **Recommendation Display**: Ensure the personalized product recommendations are clearly presented, potentially with a rationale for each recommendation as per FR5.3 [1].

### 3.2. API Interaction

*   The frontend will continue to use the `/api/v2/analyze/guest` endpoint for submitting images and receiving analysis results. The structure of the response from this endpoint will be updated to include the new AI-driven data.
*   Expect the API response to include:
    *   `skin_type`: Overall skin type classification.
    *   `concerns`: A list of detected skin concerns with their severity and confidence scores.
    *   `recommendations`: A list of personalized product recommendations, each with a rationale.
    *   `similar_scin_profiles`: Data (e.g., image URLs, metadata) for similar profiles found in the SCIN database.

## 4. Backend Development Instructions

The backend (Flask/Python) will undergo the most significant changes to integrate the new AI capabilities. The existing `/api/v2/analyze/guest` endpoint will be refactored to orchestrate the following steps:

### 4.1. Google Vision API Integration (FR6.8.1, FR6.8.2, FR6.8.3)

1.  **Client Setup**: Install the Google Cloud Vision API client library for Python (`google-cloud-vision`).
2.  **Authentication**: Ensure the Flask application is authenticated to use the Google Vision API. This typically involves setting up a service account and providing its credentials to the application environment.
3.  **Face Detection**: Upon receiving an image from the frontend, call the Google Vision API's `face_detection` feature. The API will return bounding box coordinates for detected faces [2].
    ```python
    from google.cloud import vision
    import io
    from PIL import Image

    def detect_and_crop_face(image_content):
        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=image_content)

        response = client.face_detection(image=image)
        faces = response.face_annotations

        if not faces:
            return None, "No face detected."
        if len(faces) > 1:
            # Optionally, select the largest face or return an error
            return None, "Multiple faces detected. Please upload an image with a single face."

        face = faces[0]
        vertices = face.bounding_poly.vertices

        # Get original image dimensions
        img = Image.open(io.BytesIO(image_content))
        img_width, img_height = img.size

        # Unnormalize coordinates and crop
        # The vertices are in pixel coordinates, no unnormalization needed if using bounding_poly.vertices
        # Bounding box coordinates are (x, y) for top-left, top-right, bottom-right, bottom-left
        x_min = min(v.x for v in vertices)
        y_min = min(v.y for v in vertices)
        x_max = max(v.x for v in vertices)
        y_max = max(v.y for v in vertices)

        cropped_img = img.crop((x_min, y_min, x_max, y_max))
        
        # Convert cropped image back to bytes for further processing
        buffered = io.BytesIO()
        cropped_img.save(buffered, format="PNG") # Or JPEG, depending on downstream needs
        return buffered.getvalue(), None
    ```
4.  **Error Handling**: Implement robust error handling for cases where no face is detected or multiple faces are present, returning appropriate messages to the frontend [1, NFR7.3.3].
5.  **Image Cropping**: Crop the original image to the detected face's bounding box. This cropped image will be used for subsequent AI/ML analysis.

### 4.2. Face Vectorization (FR4.1)

*   The cropped facial image needs to be converted into a high-dimensional numerical vector (embedding). This will likely involve a pre-trained deep learning model (e.g., a CNN-based face embedding model like FaceNet or a custom model trained on skin features).
*   Integrate this vectorization logic into a dedicated service (e.g., `Enhanced Image Vectorization Service`) that takes the cropped image as input and returns its vector representation.

### 4.3. FAISS Integration (FR4.2, FR4.3)

1.  **Install FAISS**: Install the FAISS library (`faiss-cpu` or `faiss-gpu` depending on your environment) in the backend environment.
2.  **SCIN Dataset Vectorization**: Ensure that all images in the SCIN database (stored in Google Cloud Storage) are pre-processed and vectorized. These vectors will form the FAISS index.
3.  **Build and Load FAISS Index**: On application startup or as part of a data loading process, build a FAISS index from the vectorized SCIN dataset. For production, this index should be persisted and loaded efficiently.
    ```python
    import faiss
    import numpy as np

    def build_faiss_index(scin_vectors):
        dimension = scin_vectors.shape[1] # Dimension of your vectors
        index = faiss.IndexFlatL2(dimension) # Or other index types like IndexIVFFlat
        index.add(scin_vectors)
        return index

    # Example usage:
    # scin_vectors = np.array([...]) # Load your pre-vectorized SCIN data
    # faiss_index = build_faiss_index(scin_vectors)
    # faiss.write_index(faiss_index, "scin_faiss_index.bin") # Save the index
    # loaded_index = faiss.read_index("scin_faiss_index.bin") # Load the index
    ```
4.  **Similarity Search**: When a user's face vector is generated, query the FAISS index to find the `k` most similar SCIN profiles. This will return the distances and indices of the nearest neighbors.
    ```python
    def search_similar_profiles(user_vector, faiss_index, k=5):
        distances, indices = faiss_index.search(np.array([user_vector]), k)
        return distances, indices
    ```
5.  **Retrieve SCIN Metadata**: Use the returned indices to retrieve the corresponding metadata (e.g., skin condition labels, associated recommendations, image URLs) from your SCIN dataset management system (e.g., `scin_dataset_service`).

### 4.4. Skin Condition Classification (FR3.1, FR3.2, FR3.3, FR3.4)

*   Based on the similar SCIN profiles found via FAISS, the `Skin Classifier Service` will classify the user's skin type and primary concerns. This might involve aggregating labels from the nearest neighbors or using a separate classification model that takes the user's vector and/or similar profiles as input.
*   Assign a severity level (mild, moderate, severe) and a confidence score for each detected condition.

### 4.5. Recommendation Generation (FR5.1, FR5.2, FR5.3)

*   The `Recommendation Engine` will generate personalized product recommendations. This should consider the classified skin conditions, their severity, and the specific products associated with the similar SCIN profiles.
*   Prioritize products that have proven efficacy for the identified conditions or similar skin types.
*   Provide a clear rationale for each recommendation to the user.

### 4.6. API Endpoint Refactoring (FR6.1, FR6.2, FR6.3)

*   Modify the `/api/v2/analyze/guest` endpoint in `backend/app/enhanced_analysis_router.py` to orchestrate the entire pipeline:
    1.  Receive image.
    2.  Call Google Vision API for face detection and cropping.
    3.  If face detected, vectorize the cropped face.
    4.  Perform FAISS similarity search.
    5.  Classify skin conditions.
    6.  Generate recommendations.
    7.  Construct and return the comprehensive JSON response including `skin_type`, `concerns`, `recommendations`, and `similar_scin_profiles`.
*   Ensure the API can handle image uploads efficiently (FR6.3) and supports common formats like JPEG and PNG.

## 5. Deployment and Testing Considerations

### 5.1. Environment Setup

*   **Google Cloud Credentials**: Ensure the AWS Elastic Beanstalk environment has access to the necessary Google Cloud credentials for the Vision API and Google Cloud Storage.
*   **FAISS Dependencies**: The deployment environment must have the FAISS library installed. If using `faiss-gpu`, ensure appropriate GPU drivers and CUDA are configured on the Elastic Beanstalk instances.
*   **Increased Resources**: Given the computational demands of AI models and FAISS, consider upgrading the Elastic Beanstalk instance type (e.g., to `m5.2xlarge` or GPU-enabled instances if needed) and increasing Gunicorn workers and timeouts [GitHub Readme, Issue 5, NFR7.2.1].

### 5.2. Testing

*   **Unit Tests**: Develop unit tests for each new service and component (e.g., `detect_and_crop_face` function, vectorization logic, FAISS search function).
*   **Integration Tests**: Test the full `/api/v2/analyze/guest` pipeline to ensure all components interact correctly.
*   **Performance Testing**: Conduct performance tests to ensure the NFRs for response time and concurrency are met [1, NFR7.1.1, NFR7.1.2, NFR7.1.3].
*   **Edge Cases**: Thoroughly test with images containing no faces, multiple faces, poor lighting, and various skin tones and conditions.

## 6. References

[1] ProductRequirementsDocument_AdvancedAIforShineSkincareApp.md (Provided by user)
[2] [Detect faces | Cloud Vision API - Google Cloud](https://cloud.google.com/vision/docs/detecting-faces)
[3] [How to Crop Image Based on Google Vision API Bounding Poly - Stack Overflow](https://stackoverflow.com/questions/72540247/how-to-crop-image-based-on-google-vision-api-bounding-poly-normalized-vertices-u)
[4] [facebookresearch/faiss: A library for efficient similarity search - GitHub](https://github.com/facebookresearch/faiss)
[5] [Building a Text Similarity Search App with Flask, BERT, and FAISS - Red and Green](https://redandgreen.co.uk/text-similarity-search-app-with-faiss/ai-ml/)

---

**Author**: Manus AI
**Date**: July 30, 2025




## 7. Fitzpatrick Scale Integration (Optional Age and Ethnicity Input)

To provide more precise results and personalized recommendations, users will have the option to input their age and ethnicity. This information will be used in conjunction with the AI analysis to refine recommendations, particularly in the context of the Fitzpatrick Skin Type (FST) scale.

### 7.1. Frontend Changes

*   **Optional Input Fields**: Add optional input fields on the user interface for `age` (e.g., a numerical input or a dropdown for age ranges) and `ethnicity` (e.g., a dropdown with common ethnic categories or a free-text field). Clearly label these fields as optional and explain their purpose (e.g., "Optional: Help us refine your results").
*   **Data Transmission**: Ensure that these new `age` and `ethnicity` fields are included in the payload sent to the `/api/v2/analyze/guest` endpoint when the user submits their photo for analysis.

### 7.2. Backend Changes

*   **API Endpoint Update**: Modify the `/api/v2/analyze/guest` endpoint to accept `age` and `ethnicity` as optional parameters in the request payload.
*   **Data Utilization**: The `age` and `ethnicity` data should be passed to the `Recommendation Engine` (FR5.1, FR5.2, FR5.3) and potentially the `Skin Classifier Service` (FR3.1, FR3.2, FR3.3, FR3.4) for contextualization.
    *   **Recommendation Engine Refinement**: The recommendation engine can use age and ethnicity to fine-tune product suggestions. For example, certain product ingredients or routines might be more suitable for specific age groups (e.g., anti-aging products for older users) or ethnic skin types (e.g., products addressing hyperpigmentation common in certain ethnicities).
    *   **SCIN Database Search (Optional Enhancement)**: If the SCIN database contains demographic information (age, ethnicity, or even pre-assigned Fitzpatrick types) for its profiles, this user-provided data can be used to narrow down the FAISS search space or to give more weight to similar profiles within the same demographic. This would involve modifying the `search_similar_profiles` logic or the data preparation for the FAISS index.
*   **Fitzpatrick Scale Inference (Optional)**: While the Fitzpatrick scale is primarily determined by sun sensitivity, a basic FST can be inferred or suggested based on a combination of skin tone (from image analysis) and self-reported ethnicity. This inferred FST can be returned to the frontend for user information and education, but it should be clearly stated that this is an estimation and not a clinical diagnosis.

### 7.3. Data Management Considerations

*   **SCIN Dataset Enrichment**: Consider enriching the SCIN dataset with age and ethnicity metadata if it's not already present. This would significantly enhance the ability to provide demographically-tailored recommendations and improve the FAISS search relevance.

### 7.4. References

[6] [Fitzpatrick Skin Type Scale – Bang-on or Bunk-off? Understanding ... - LVSCC](https://lvscc.dev.westderm.com/fitzpatrick-skin-type-scale-bang-on-or-bunk-off-understanding-your-skin-cancer-risk/)
[7] [Self-Reported Pigmentary Phenotypes and Race are Significant but ... - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC4165764/)


