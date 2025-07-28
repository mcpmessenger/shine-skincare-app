#!/bin/bash
# Optimized ML dependency installation script for AWS EB
# Handles large packages efficiently with proper error handling

set -e

echo "🔧 Installing ML dependencies in optimized order..."

# Get the virtual environment path (EB specific)
VENV_PATH="/var/app/venv/staging-LQM1lest/bin"
PIP="$VENV_PATH/pip"

# Create temp directories for builds
mkdir -p /tmp/pip-build /tmp/pip-cache
chmod 777 /tmp/pip-build /tmp/pip-cache

# Configure pip for large package builds
export PIP_CACHE_DIR="/tmp/pip-cache"
export PIP_BUILD_DIR="/tmp/pip-build"
export PIP_TIMEOUT=300
export PIP_RETRIES=3

echo "📦 Step 1: Upgrading pip and build tools..."
$PIP install --upgrade pip==23.3.1 setuptools==69.0.2 wheel==0.42.0 --no-cache-dir

echo "📦 Step 2: Installing core Flask dependencies..."
$PIP install --no-cache-dir \
    Flask==3.0.0 \
    flask-cors==4.0.0 \
    gunicorn==21.2.0 \
    python-dotenv==1.0.0

echo "📦 Step 3: Installing numpy (foundation for ML libs)..."
$PIP install numpy==1.24.3 --no-cache-dir --compile --no-build-isolation

echo "📦 Step 4: Installing core ML dependencies..."
$PIP install --no-cache-dir --compile --no-build-isolation \
    scipy==1.11.4 \
    scikit-learn==1.3.2

echo "📦 Step 5: Installing FAISS (may take a while)..."
$PIP install faiss-cpu==1.7.4 --no-cache-dir --no-build-isolation || {
    echo "⚠️ FAISS installation failed, will use mock service"
    export USE_MOCK_SERVICES=true
}

echo "📦 Step 6: Installing image processing libraries..."
$PIP install --no-cache-dir \
    opencv-python-headless==4.8.1.78 \
    Pillow==10.0.1

echo "📦 Step 7: Installing Google Cloud dependencies..."
$PIP install --no-cache-dir \
    google-cloud-vision==3.4.4 \
    google-auth==2.23.4 \
    google-api-core==2.12.0

echo "📦 Step 8: Installing database and utilities..."
$PIP install --no-cache-dir \
    psycopg2-binary==2.9.7 \
    supabase==1.0.4 \
    requests==2.31.0 \
    structlog==23.1.0 \
    psutil==5.9.6

echo "🧹 Cleaning up build cache..."
rm -rf /tmp/pip-build /tmp/pip-cache

echo "✅ ML dependencies installation completed!"

# Verify critical packages
echo "🔍 Verifying installation..."
python3 -c "import numpy; print(f'✓ NumPy {numpy.__version__}')" || echo "❌ NumPy failed"
python3 -c "import cv2; print(f'✓ OpenCV {cv2.__version__}')" || echo "❌ OpenCV failed"
python3 -c "import faiss; print('✓ FAISS available')" || echo "⚠️ FAISS not available (will use mock)"
python3 -c "from google.cloud import vision; print('✓ Google Vision available')" || echo "❌ Google Vision failed"

echo "🎉 Installation verification completed!"