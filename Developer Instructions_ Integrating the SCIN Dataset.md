
# Developer Instructions: Integrating the SCIN Dataset

This document provides comprehensive instructions for developers to integrate the SCIN (Skin Condition Image Network) dataset into their projects. The SCIN dataset is stored in a public Google Cloud Storage (GCS) bucket and offers rich annotations for skin conditions, severity, and race, making it highly valuable for building robust AI models for skincare analysis.

## 1. Understanding the SCIN Dataset Structure and Schema

The SCIN dataset is organized within the `dx-scin-public-data` GCS bucket. The primary data and metadata are located within the `dataset/` folder. Here's a breakdown of the key components:

*   **`images/` folder**: Contains all the image files. The images are named with a unique identifier (e.g., `image_id.jpg`).
*   **`scin_cases.csv`**: This CSV file contains core information about each case (contributed image set), including self-reported demographic and symptom information. Key columns include:
    *   `case_id`: Unique identifier for each case.
    *   `image_file_name`: The filename of the image associated with the case (e.g., `12345.jpg`).
    *   Self-reported fields such as `age`, `gender`, `race_ethnicity`, `skin_type`, `symptom_duration`, etc.
*   **`scin_labels.csv`**: This CSV file contains the dermatologist labels and estimated skin tone labels for each case. Key columns include:
    *   `case_id`: Links to `scin_cases.csv`.
    *   `dermatologist_condition_label`: The primary skin condition diagnosis provided by dermatologists.
    *   `estimated_fitzpatrick_skin_type`: Dermatologist's estimation of Fitzpatrick skin type.
    *   `estimated_monk_skin_tone`: Layperson's estimation of Monk Skin Tone.
    *   Other label-related fields.
*   **`scin_app_questions.csv`**: Contains the questions asked to contributors via the app.
*   **`scin_label_questions.csv`**: Contains the questions asked to labelers.

**Schema Overview**: The `scin_cases.csv` and `scin_labels.csv` files are the most crucial for integrating image data with its annotations. They can be joined using the `case_id` column. The `image_file_name` in `scin_cases.csv` allows you to construct the full GCS path to retrieve the corresponding image.

For a detailed and up-to-date overview of the dataset schema, always refer to the official [Dataset Documentation](https://github.com/google-research-datasets/scin/blob/main/dataset_schema.md) on the SCIN GitHub repository. This document will provide the most accurate and granular details about each field and its possible values.

## 2. Setting Up Your Google Cloud Environment and Access

To access the SCIN dataset from Google Cloud Storage, you need to set up your environment with the necessary tools and authentication. This section assumes you have a Google Cloud Platform (GCP) project and appropriate permissions to access public GCS buckets.

### 2.1 Install Google Cloud SDK

The Google Cloud SDK provides a set of tools for interacting with Google Cloud services, including `gsutil` for Cloud Storage operations. If you don't have it installed, follow the official installation guide:

*   **Linux/macOS**: [Install Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
*   **Windows**: [Install Google Cloud SDK](https://cloud.google.com/sdk/docs/install-windows)

After installation, initialize the SDK:

```bash
gcloud init
```

Follow the prompts to log in with your Google account and select a default GCP project. While the SCIN bucket is public, having a configured project is good practice for other GCP interactions.

### 2.2 Authenticate for GCS Access

Although the `dx-scin-public-data` bucket is publicly accessible, it's often convenient to authenticate your environment for seamless access, especially if you plan to use client libraries that leverage application default credentials. You can authenticate using:

*   **User Application Default Credentials (Recommended for Development)**:
    ```bash
gcloud auth application-default login
    ```
    This command opens a browser window for you to log in with your Google account. It sets up credentials that your applications can use to authenticate to Google Cloud APIs.

*   **Service Account Key (Recommended for Production/Automated Workflows)**:
    For production environments or automated scripts, it's best to use a service account. Create a service account in your GCP project with the `Storage Object Viewer` role (or a custom role with `storage.objects.get` and `storage.objects.list` permissions). Download the JSON key file and set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable:

    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/keyfile.json"
    ```
    Replace `/path/to/your/keyfile.json` with the actual path to your downloaded service account key file.

### 2.3 Install Python Libraries

For programmatic access to GCS and data manipulation in Python, you'll need the `google-cloud-storage` and `gcsfs` libraries, along with `pandas` for CSV file handling and `Pillow` (PIL) for image processing.

```bash
pip install google-cloud-storage gcsfs pandas Pillow
```

These libraries will allow you to interact with the GCS bucket, read CSV files directly from GCS, and process images without necessarily downloading them all locally first.

With your environment set up, you are now ready to develop scripts for data ingestion and pre-processing.



## 3. Developing Data Ingestion and Pre-processing Scripts

This section provides Python code examples and guidance for ingesting the SCIN dataset from Google Cloud Storage, merging metadata, and performing basic pre-processing steps. These scripts will form the foundation of your data pipeline.

### 3.1 Accessing Metadata CSV Files

The `gcsfs` library allows you to treat GCS buckets like a local filesystem, enabling `pandas` to directly read CSV files from the bucket.

```python
import gcsfs
import pandas as pd

# Define the GCS bucket path where the dataset CSVs are located
BUCKET_PATH = 'gs://dx-scin-public-data/dataset/'

# Initialize a GCS filesystem client
fs = gcsfs.GCSFileSystem()

# Read scin_cases.csv
# This file contains self-reported demographic and symptom information, and image filenames.
with fs.open(BUCKET_PATH + 'scin_cases.csv') as f:
    cases_df = pd.read_csv(f)
print('scin_cases.csv head:')
print(cases_df.head())

# Read scin_labels.csv
# This file contains dermatologist labels for conditions and estimated skin tone.
with fs.open(BUCKET_PATH + 'scin_labels.csv') as f:
    labels_df = pd.read_csv(f)
print('\nscin_labels.csv head:')
print(labels_df.head())

# Read scin_app_questions.csv (optional, for understanding survey context)
with fs.open(BUCKET_PATH + 'scin_app_questions.csv') as f:
    app_questions_df = pd.read_csv(f)
print('\nscin_app_questions.csv head:')
print(app_questions_df.head())

# Read scin_label_questions.csv (optional, for understanding labeling context)
with fs.open(BUCKET_PATH + 'scin_label_questions.csv') as f:
    label_questions_df = pd.read_csv(f)
print('\nscin_label_questions.csv head:')
print(label_questions_df.head())
```

### 3.2 Merging Metadata for Comprehensive Records

To get a complete record for each image, you will typically merge `cases_df` and `labels_df` using the common `case_id` column.

```python
# Merge the two dataframes on 'case_id'
# A left merge ensures all cases from cases_df are kept, even if a label is missing.
merged_df = pd.merge(cases_df, labels_df, on='case_id', how='left')
print('\nMerged DataFrame head:')
print(merged_df.head())

# Display information about the merged DataFrame, including data types and non-null counts
print('\nMerged DataFrame Info:')
merged_df.info()

# Check for missing values in critical columns
print('\nMissing values in key columns:')
print(merged_df[['dermatologist_condition_label', 'estimated_fitzpatrick_skin_type', 'estimated_monk_skin_tone', 'image_file_name']].isnull().sum())
```

### 3.3 Accessing and Pre-processing Images

Images are stored in the `images/` subdirectory within the `dataset/` folder. You can construct the full GCS path for each image using the `image_file_name` from your merged DataFrame. For image processing, `Pillow` (PIL) is a common choice.

```python
from PIL import Image
import io

# Example: Get the GCS path for the first image
first_image_file = merged_df['image_file_name'].iloc[0]
first_image_gcs_path = BUCKET_PATH + 'images/' + first_image_file
print(f'\nFirst image GCS path: {first_image_gcs_path}')

# Function to load an image from GCS
def load_image_from_gcs(gcs_path, fs_client):
    try:
        with fs_client.open(gcs_path, 'rb') as f:
            img_bytes = f.read()
        img = Image.open(io.BytesIO(img_bytes))
        return img
    except Exception as e:
        print(f"Error loading image {gcs_path}: {e}")
        return None

# Load the first image
example_image = load_image_from_gcs(first_image_gcs_path, fs)
if example_image:
    print(f"Loaded image: {example_image.size} (width, height), {example_image.mode} (mode)")
    # Example pre-processing: resize image
    resized_image = example_image.resize((224, 224)) # Common size for CNNs
    print(f"Resized image: {resized_image.size}")
    # You can add more pre-processing steps here, e.g., normalization, cropping

# Example: Iterate and process a subset of images
# For large datasets, consider batch processing and parallelization.
# This example processes the first 5 images.

# Create a list of GCS paths for the first 5 images
sample_image_paths = [BUCKET_PATH + 'images/' + f for f in merged_df['image_file_name'].head(5)]

processed_images = []
for path in sample_image_paths:
    img = load_image_from_gcs(path, fs)
    if img:
        # Perform your desired pre-processing (e.g., resize, convert to RGB)
        img = img.resize((224, 224)).convert('RGB')
        processed_images.append(img)

print(f"Successfully processed {len(processed_images)} sample images.")
```

### 3.4 Data Filtering and Analysis Examples

Leverage `pandas` to filter and analyze the dataset based on the rich annotations provided. This is crucial for creating balanced training datasets and understanding data distributions.

```python
# Example: Filter for cases with 'Acne' condition
acne_cases = merged_df[merged_df['dermatologist_condition_label'] == 'Acne']
print('\nAcne cases head (selected columns):')
print(acne_cases[['case_id', 'dermatologist_condition_label', 'estimated_fitzpatrick_skin_type', 'estimated_monk_skin_tone', 'image_file_name']].head())

# Example: Analyze distribution of Estimated Fitzpatrick Skin Type
print('\nDistribution of Estimated Fitzpatrick Skin Type:')
print(merged_df['estimated_fitzpatrick_skin_type'].value_counts())

# Example: Analyze distribution of Estimated Monk Skin Tone
print('\nDistribution of Estimated Monk Skin Tone:')
print(merged_df['estimated_monk_skin_tone'].value_counts())

# Example: Analyze distribution of Dermatologist Condition Labels
print('\nDistribution of Dermatologist Condition Labels (Top 10):')
print(merged_df['dermatologist_condition_label'].value_counts().head(10))

# Example: Filter for specific race/skin tone and condition
# Find cases of 'Eczema' in 'Fitzpatrick Skin Type IV'
eczema_ft4_cases = merged_df[
    (merged_df['dermatologist_condition_label'] == 'Eczema') &
    (merged_df['estimated_fitzpatrick_skin_type'] == 'IV')
]
print('\nEczema cases in Fitzpatrick Skin Type IV (head):')
print(eczema_ft4_cases[['case_id', 'dermatologist_condition_label', 'estimated_fitzpatrick_skin_type', 'image_file_name']].head())
```

These scripts provide a foundation for interacting with the SCIN dataset. You can adapt and extend them to fit your specific model training, analysis, and application needs. Remember to handle large datasets efficiently by implementing batch processing, parallelization, and potentially using distributed computing frameworks if necessary.



## 4. Integrating with Your AI Model and Application

Once you have successfully ingested and pre-processed the SCIN dataset, the next step is to integrate this data into your AI model training pipeline and, subsequently, into your application for tasks like image embedding, similarity search, and RAG (Retrieval Augmented Generation).

### 4.1 Training Your Image Embedding Model

The pre-processed images and their associated metadata from the SCIN dataset will serve as the training data for your image embedding model. This model (e.g., a fine-tuned CNN) will learn to generate vector representations (embeddings) of skin images that capture their key visual characteristics, including condition, severity, and racial features.

*   **Data Loading**: Use the `merged_df` (or a filtered/sampled version of it) to get image file paths and corresponding labels.
*   **Image Augmentation**: Apply data augmentation techniques (e.g., rotation, flipping, color jittering) to increase the diversity of your training data and improve model generalization.
*   **Model Architecture**: Choose an appropriate deep learning architecture (e.g., ResNet, EfficientNet, Vision Transformer) and fine-tune it on your SCIN data. The last layer of the model should output the desired embedding vector.
*   **Loss Function**: Consider using contrastive or triplet loss functions to encourage the model to produce embeddings where similar images are close together and dissimilar images are far apart in the embedding space.
*   **Evaluation**: Evaluate your embedding model using metrics relevant to similarity search, such as recall@k, precision@k, and mean average precision (mAP).

### 4.2 Populating Milvus with Embeddings

After training your embedding model, you will use it to generate embeddings for all images in your dataset. These embeddings, along with relevant metadata, will then be inserted into Milvus for efficient vector similarity search.

```python
# Assuming you have a trained embedding_model that takes a PIL Image and returns a numpy array embedding
# from your_model_library import EmbeddingModel
# embedding_model = EmbeddingModel()

# Example function to get embedding (replace with your actual model inference)
def get_image_embedding(pil_image):
    # Placeholder: In a real scenario, this would involve model inference
    # Ensure the output dimension matches your Milvus schema (e.g., 128)
    return [random.uniform(-1, 1) for _ in range(128)] # Example random embedding

# Prepare data for Milvus insertion
# This is a conceptual loop; for large datasets, use batch processing.

# Lists to hold data for Milvus insertion (column-wise)
case_ids_milvus = []
embeddings_milvus = []
conditions_milvus = []
severities_milvus = [] # You might need to map severity labels to numerical values
races_milvus = []
genders_milvus = []
age_groups_milvus = []
image_urls_milvus = []

# Iterate through your merged_df (or a subset)
for index, row in merged_df.iterrows():
    gcs_image_path = BUCKET_PATH + 'images/' + row['image_file_name']
    pil_image = load_image_from_gcs(gcs_image_path, fs) # Use the load_image_from_gcs function from Section 3.3

    if pil_image:
        embedding = get_image_embedding(pil_image.resize((224, 224)).convert('RGB'))

        case_ids_milvus.append(row['case_id'])
        embeddings_milvus.append(embedding)
        conditions_milvus.append(row['dermatologist_condition_label'])
        # Example: Simple mapping for severity (adjust based on your data)
        # For SCIN, severity might be inferred from symptom_duration or other fields
        severities_milvus.append(0) # Placeholder, replace with actual severity logic
        races_milvus.append(row['estimated_fitzpatrick_skin_type']) # Using FST as race proxy
        genders_milvus.append(row['gender']) # Assuming 'gender' is in cases_df
        age_groups_milvus.append(row['age_group']) # Assuming 'age_group' is in cases_df
        image_urls_milvus.append(gcs_image_path)

# Insert into Milvus (refer to Section 3.2 of previous report for Milvus connection and schema)
# collection.insert([
#     case_ids_milvus,
#     embeddings_milvus,
#     conditions_milvus,
#     severities_milvus,
#     races_milvus,
#     genders_milvus,
#     age_groups_milvus,
#     image_urls_milvus
# ])
# collection.flush()
# print(f"Inserted {len(case_ids_milvus)} entities into Milvus.")
```

### 4.3 Implementing Similarity Search and RAG

With Milvus populated, you can implement the core similarity search functionality and integrate it with a RAG system.

*   **Similarity Search API**: Create an API endpoint that receives a new skin image, generates its embedding using your trained model, and queries Milvus for the most similar images. The results should include the `case_id`, `distance`, and relevant metadata (condition, skin tone, image URL).
*   **RAG Integration**: For a RAG system, the retrieved similar cases (and their associated textual metadata/explanations) can be used as context for a large language model (LLM). The LLM can then generate more detailed and personalized skincare recommendations or explanations based on the visual similarity and the textual information from the retrieved cases.

### 4.4 Continuous Improvement and Maintenance

*   **Data Refresh**: Periodically check for updates to the SCIN dataset or integrate new datasets to keep your model current and comprehensive.
*   **Model Retraining**: As new data becomes available or as your understanding of skin conditions evolves, retrain your embedding model to maintain and improve its accuracy.
*   **Milvus Maintenance**: Monitor Milvus performance, optimize indexes, and scale your Milvus instance as your dataset grows and query load increases.

By following these instructions, you can effectively integrate the SCIN dataset into your Shine project, enabling advanced AI-powered skin analysis capabilities. This dataset, with its focus on diversity and rich annotations, will be a cornerstone for building an accurate, fair, and impactful skincare solution.

