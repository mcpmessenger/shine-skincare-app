# Backend Architecture Design for Shine Skincare Application

## 1. Introduction

This document outlines the proposed backend architecture for the Shine Skincare application, focusing on the integration of Google Vision API for advanced facial analysis, FAISS for efficient similarity search against a SCIN (Skin Condition Identification Network) dataset, and a robust product recommendation engine. The design considers the existing CI/CD pipeline, where the frontend is updated via GitHub triggers to Amplify, and the backend is manually updated via the Elastic Beanstalk (EB) console. The primary goal is to provide accurate skin condition identification, severity assessment, and personalized product recommendations, while optionally incorporating ethnicity and age.

## 2. Overall Architecture Overview

The backend architecture will be built upon the existing Flask/Python framework deployed on AWS Elastic Beanstalk, leveraging CloudFront as a CDN and HTTPS proxy. The core components will include:

- **API Gateway/Load Balancer (CloudFront/EB Load Balancer)**: Handles incoming requests, provides HTTPS termination, and distributes traffic to the backend instances.
- **Flask Application (Backend)**: The main application logic, responsible for orchestrating the various services, handling API requests, and managing data flow.
- **Google Vision API Integration**: For precise face detection and isolation from user-uploaded images.
- **Image Processing and Vectorization Module**: Converts isolated facial images into high-dimensional feature vectors suitable for similarity search.
- **FAISS (Facebook AI Similarity Search) Index**: Stores and enables rapid similarity search against the pre-computed SCIN dataset of skin condition vectors.
- **SCIN Dataset**: A comprehensive dataset containing vectorized representations of various skin conditions, along with associated metadata (e.g., condition type, severity, recommended ingredients).
- **Product Database**: Stores detailed information about skincare products, including their ingredients, categories, and other relevant attributes.
- **Product Recommendation Engine**: Matches identified skin conditions and recommended ingredients to available products, considering severity, ethnicity, and age.
- **Database (PostgreSQL/RDS)**: Stores user data, analysis results, product information, and potentially user feedback.
- **S3 (Simple Storage Service)**: For storing raw and processed images, as well as the FAISS index and SCIN dataset.

```mermaid
graph TD
    A[User] --> B(CloudFront CDN)
    B --> C(Elastic Beanstalk Load Balancer)
    C --> D{Flask Application}
    D --> E[Google Vision API]
    D --> F[Image Processing & Vectorization]
    D --> G[FAISS Index]
    D --> H[SCIN Dataset]
    D --> I[Product Database]
    D --> J[Product Recommendation Engine]
    D --> K[Database (RDS)]
    D --> L[S3 Storage]
    F --> G
    G --> H
    I --> J
    J --> K
    L --> F
    L --> G
    L --> I
```

## 3. Detailed Component Breakdown

### 3.1. Flask Application (Core Backend Service)

The Flask application will serve as the central hub, coordinating all operations. It will expose several API endpoints to the frontend, including:

- `/api/v2/analyze/guest`: Accepts user-uploaded images and optional demographic data (age, ethnicity). This will be the primary endpoint for initiating the skin analysis process.
- `/api/v2/recommendations/{analysis_id}`: Retrieves product recommendations based on a completed analysis.
- `/api/v2/products`: Provides access to product information.

**Key Responsibilities:**
- **Request Handling**: Receives and validates incoming requests from the frontend.
- **Orchestration**: Calls various internal and external services (Google Vision, image processing, FAISS, product recommendation).
- **Data Management**: Interacts with the database to store and retrieve analysis results, user profiles, and product data.
- **Error Handling**: Implements robust error handling and logging mechanisms.
- **Security**: Ensures secure communication and data handling, including proper authentication and authorization (though user authentication is a planned enhancement, not part of this immediate design).

### 3.2. Google Vision API Integration

Google Vision API will be used for its advanced image analysis capabilities, specifically for accurate face detection and landmark identification. This is crucial for isolating the face from the uploaded image.

**Process Flow:**
1.  **Image Upload**: User uploads an image to the Flask application.
2.  **API Call**: The Flask application sends the image to the Google Vision API.
3.  **Face Detection**: Google Vision API returns bounding box coordinates for detected faces and facial landmarks.
4.  **Face Isolation**: The Flask application uses these coordinates to crop and isolate the face from the original image. This ensures that only the relevant part of the image is used for subsequent analysis, improving accuracy and reducing noise.

### 3.3. Image Processing and Vectorization Module

This module will take the isolated facial image and transform it into a numerical representation (vector) that captures key skin features. This vector will then be used for similarity search.

**Process Flow:**
1.  **Pre-processing**: The isolated face image undergoes pre-processing steps such as resizing, normalization, and potentially enhancement to optimize it for the feature extraction model.
2.  **Feature Extraction (Vectorization)**: A pre-trained deep learning model (e.g., a Convolutional Neural Network trained on skin conditions) will extract a 2048-dimensional feature vector from the processed facial image. This vector represents the unique characteristics of the user's skin.
3.  **Storage**: The generated vector is stored temporarily or associated with the user's analysis session.

### 3.4. FAISS (Facebook AI Similarity Search) Index and SCIN Dataset

FAISS is a library for efficient similarity search and clustering of dense vectors. It will be used to quickly find the most similar skin profiles within our pre-built SCIN dataset.

**SCIN Dataset Structure:**
- The SCIN dataset will consist of a large collection of pre-computed 2048-dimensional vectors, each representing a specific skin condition (e.g., acne, dryness, hyperpigmentation) at various severity levels. Each vector will be associated with metadata, including:
    - `skin_condition_type`: (e.g., 


Acne, Dryness, Redness)
    - `severity_level`: (e.g., Mild, Moderate, Severe)
    - `associated_ingredients`: A list of beneficial ingredients for this condition.
    - `example_images`: References to images representing this condition.

**FAISS Implementation:**
1.  **Index Creation**: A FAISS index will be built offline using the vectors from the SCIN dataset. This index will be optimized for fast similarity search.
2.  **Vector Storage**: The FAISS index and the associated SCIN dataset metadata will be stored in S3 for easy access and versioning.
3.  **Similarity Search**: When a user uploads an image and their face vector is generated, this vector will be queried against the FAISS index. FAISS will return the `k` most similar vectors from the SCIN dataset, along with their distances (cosine similarity).
4.  **Condition Identification**: Based on the similarity search results, the system will identify the most probable skin conditions and their severity levels present in the user's image. The 


cosine similarity score will be converted into a percentage to indicate the confidence of the identification.

### 3.5. Product Recommendation Engine

This engine will be responsible for generating personalized product recommendations based on the identified skin conditions, their severity, and optionally, the user's age and ethnicity. The new product requirements document emphasizes the need for a product matching layer to connect ingredient-based recommendations to actual products.

**Process Flow:**
1.  **Input**: The engine receives the identified skin conditions (with severity and confidence percentages), and optional age and ethnicity data.
2.  **Ingredient Mapping**: For each identified skin condition, the engine will retrieve a list of beneficial ingredients from the SCIN dataset metadata. It will also consider ingredients to avoid based on the condition.
3.  **Product Filtering and Matching**: The engine will query the `Product Database` to find products that contain the beneficial ingredients and do not contain the ingredients to avoid. It will prioritize products based on:
    -   **Ingredient Match Score**: A score indicating how well a product's ingredients align with the recommended ingredients for the identified skin conditions.
    -   **Severity**: For severe conditions, products with higher concentrations of active ingredients or specialized formulations might be prioritized.
    -   **Optional Age and Ethnicity**: If provided, these factors can further refine recommendations. For example, certain ingredients or product types might be more suitable for specific age groups or ethnicities. This would require additional metadata in the `Product Database` or a separate knowledge base.
4.  **Ranking**: The matched products will be ranked based on their relevance and effectiveness for the user's specific skin profile. This ranking can incorporate factors like product ratings, popularity, and the overall match score.
5.  **Output**: A list of recommended products, each with a `match_score` (as specified in the `PRODUCT_REQUIREMENTS_DOCUMENT.md`), will be returned to the Flask application.

### 3.6. Product Database

The `Product Database` will be a critical component, storing comprehensive information about skincare products. The schema provided in the `PRODUCT_REQUIREMENTS_DOCUMENT.md` will be implemented.

**Schema (as per requirements document):**

```sql
-- Products table
CREATE TABLE products (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(255),
    category VARCHAR(100), -- cleanser, moisturizer, serum, etc.
    price DECIMAL(10,2),
    image_url VARCHAR(500),
    description TEXT,
    supplier_id UUID,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Product ingredients mapping
CREATE TABLE product_ingredients (
    product_id UUID REFERENCES products(id),
    ingredient_name VARCHAR(255),
    concentration DECIMAL(5,2), -- percentage
    is_primary BOOLEAN DEFAULT false,
    PRIMARY KEY (product_id, ingredient_name)
);

-- Suppliers table
CREATE TABLE suppliers (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    api_endpoint VARCHAR(500),
    api_key VARCHAR(255),
    is_active BOOLEAN DEFAULT true
);
```

**Data Population and Maintenance:**
- The database will be populated initially with a curated list of products. As per the `PRODUCT_REQUIREMENTS_DOCUMENT.md`, a basic product database with 50-100 products is an immediate next step.
- A `Supplier Integration Layer` (as described in the requirements document) will be developed to sync product catalogs from various suppliers, ensuring the database remains up-to-date. This layer will handle fetching product data, parsing it, and inserting/updating records in the `products` and `product_ingredients` tables.

### 3.7. Database (PostgreSQL/RDS)

PostgreSQL, managed by AWS RDS (Relational Database Service), will be used as the primary database. RDS provides a scalable, highly available, and secure database solution, reducing the operational overhead.

**Key Data Stored:**
- **User Data**: User profiles, authentication details (if user authentication is implemented).
- **Analysis Results**: Details of each skin analysis performed, including the identified skin conditions, severity, confidence scores, and the generated feature vectors.
- **Product Information**: All data from the `products`, `product_ingredients`, and `suppliers` tables.
- **User Feedback**: Data collected from user feedback on product effectiveness (as per `product_feedback` schema in requirements document).
- **User Skin Profiles**: For future ML enhancements and FAISS index updates, storing `user_skin_profiles` (as per requirements document) will be crucial.

### 3.8. S3 (Simple Storage Service)

AWS S3 will be utilized for efficient and cost-effective storage of various assets.

**Key Data Stored:**
- **Raw and Processed Images**: User-uploaded images and the isolated facial images.
- **FAISS Index**: The pre-built FAISS index for similarity search.
- **SCIN Dataset**: The raw SCIN dataset files and their metadata.
- **ML Models**: Any trained machine learning models used for feature extraction or recommendation.

## 4. CI/CD and Deployment Considerations

The updated CI/CD process, where GitHub pushes trigger Amplify for the frontend and backend updates are manual via the EB console, will be accommodated.

- **Frontend Deployment (Amplify)**: The frontend will continue to be deployed automatically via AWS Amplify upon pushes to the `main` branch of the GitHub repository. The frontend will communicate with the backend via the CloudFront URL.
- **Backend Deployment (Elastic Beanstalk)**: Backend updates will continue to be deployed manually via the EB console. This requires careful version control and coordination to ensure that the deployed backend code is compatible with the frontend and the latest architecture design. The `create-v2-deployment.py` script mentioned in the GitHub README will be used to create deployment packages.

## 5. Scalability and Performance

- **Elastic Beanstalk Auto-Scaling**: EB can be configured to automatically scale the backend instances based on traffic, ensuring high availability and performance.
- **RDS Scalability**: RDS allows for easy scaling of database resources (CPU, memory, storage) as needed.
- **FAISS Efficiency**: FAISS is highly optimized for similarity search on large datasets, providing near real-time responses.
- **CloudFront Caching**: CloudFront will cache static assets and API responses (where appropriate), reducing the load on the backend and improving response times.
- **Client-side Image Compression**: As noted in the GitHub README, client-side image compression significantly reduces the size of uploaded images, improving upload speed and reducing backend processing load.

## 6. Future Enhancements

Based on the `PRODUCT_REQUIREMENTS_DOCUMENT.md`, several future enhancements are planned:

- **User Feedback System**: Implementing schemas for `product_feedback` and `user_skin_profiles` to collect user feedback and update successful patterns in FAISS.
- **Advanced Recommendation Engine**: Training ML models on user feedback to predict product effectiveness and implementing A/B testing for recommendation variants.
- **Supplier Integration**: Expanding the `Supplier Integration Layer` to connect with multiple supplier APIs.
- **Authentication and User Profiles**: Implementing a full user authentication system and persistent user profiles.

## 7. Conclusion

This backend architecture design provides a robust and scalable solution for the Shine Skincare application, integrating advanced ML capabilities with a focus on accurate skin analysis and personalized product recommendations. By leveraging Google Vision API, FAISS, and a well-structured product database, the system will deliver a highly effective and user-centric experience. The design also takes into account the existing CI/CD processes, ensuring a smooth transition and continued development. The immediate next steps will involve implementing the core product system, including the product database and ingredient matching service, and addressing the 


critical "Analysis result not found" bug, as outlined in the `PRODUCT_REQUIREMENTS_DOCUMENT.md`.

