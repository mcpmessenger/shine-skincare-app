# Use official Python runtime with ML optimizations
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for ML libraries
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements_full_ml.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements_full_ml.txt

# Copy application code
COPY . .

# Create directory for models (will be downloaded from S3)
RUN mkdir -p models

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=run_fixed_model_server.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "300", "run_fixed_model_server:app"]
