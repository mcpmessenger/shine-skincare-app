# Shine App Backend Enhancement: Developer Instructions

## Objective

To enhance the Shine app backend to include skin analysis using Google Vision AI and selfie similarity search using FAISS, with Supabase as the database.

## Technology Stack

- **Backend**: Flask (existing)
- **Database**: Supabase (PostgreSQL)
- **Image Analysis**: Google Cloud Vision AI (pre-trained models)
- **Similarity Search**: FAISS
- **Image Vectorization**: A pre-trained CNN model (e.g., ResNet-50)

## Implementation Steps

### 1. Google Vision AI Integration

- **Set up Google Cloud Project**:
    - Create a new project in the Google Cloud Console.
    - Enable the Cloud Vision API.
    - Create and download API credentials (JSON file).
- **Backend Service**:
    - Create a new service/module in the Flask app to handle interactions with the Google Vision API.
    - Use the `google-cloud-vision` Python library.
    - Implement a function that takes an image file path and sends it to the Vision API.
    - The function should handle `FACE_DETECTION` and `IMAGE_PROPERTIES` features.
    - Parse the JSON response from the API and store it.

### 2. Image Vectorization for FAISS

- **Choose a Pre-trained Model**:
    - Use a library like `timm` or `torchvision` to load a pre-trained CNN model (e.g., `resnet50`).
    - The model will be used to convert images into vector embeddings.
- **Vectorization Function**:
    - Create a function that takes an image, preprocesses it to fit the model's input requirements (resizing, normalization), and returns a feature vector.
    - This vector will be used for the similarity search.

### 3. FAISS Similarity Search

- **FAISS Index Management**:
    - Since the dataset is small, the FAISS index can be built and kept in memory.
    - On application startup, load all existing image vectors from the database and build the FAISS index.
    - Use `faiss.IndexFlatL2` for simplicity.
- **Indexing New Images**:
    - When a new image is uploaded, vectorize it using the function from step 2.
    - Add the new vector to the in-memory FAISS index.
- **Search Functionality**:
    - Create an API endpoint that takes an image ID as input.
    - Retrieve the vector for that image.
    - Use the vector to search the FAISS index for the `k` nearest neighbors.
    - Return the IDs of the similar images.

### 4. Supabase Database Schema

- **`images` table**:
    - `id` (PK)
    - `user_id` (FK to `users` table)
    - `image_url` (text) - URL to the image in Supabase Storage
    - `faiss_index_id` (integer) - The ID of the image in the FAISS index
    - `created_at` (timestamp)
- **`analyses` table**:
    - `id` (PK)
    - `image_id` (FK to `images` table)
    - `google_vision_result` (jsonb) - The full JSON response from Google Vision AI
    - `created_at` (timestamp)

### 5. API Endpoints

- **`POST /api/v2/analyze`**:
    - Takes an image file in the request.
    - Saves the image to Supabase Storage.
    - Calls the Google Vision AI service to analyze the image.
    - Vectorizes the image.
    - Adds the image metadata to the `images` table and the analysis result to the `analyses` table.
    - Adds the vector to the FAISS index.
    - Returns the analysis result.
- **`GET /api/v2/similar/:image_id`**:
    - Takes an `image_id` as a parameter.
    - Retrieves the corresponding vector.
    - Searches FAISS for similar images.
    - Returns a list of similar image URLs.

## Getting Started

1.  **Clone the repository**.
2.  **Set up environment variables**: Include Supabase and Google Cloud credentials.
3.  **Install dependencies**: `pip install -r requirements.txt` (make sure to add `faiss-cpu`, `google-cloud-vision`, and a deep learning library like `torch` and `timm`).
4.  **Run the database migrations** to create the new tables.
5.  **Implement the new services and endpoints** as described above.


