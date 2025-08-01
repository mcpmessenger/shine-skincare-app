#!/bin/bash

# Install system dependencies for Google Cloud Vision and FAISS
yum update -y
yum install -y gcc gcc-c++ make cmake
yum install -y python3-devel
yum install -y libffi-devel openssl-devel

# Install Python dependencies
source /var/app/venv/*/bin/activate
pip install --upgrade pip
pip install -r /var/app/staging/requirements.txt

