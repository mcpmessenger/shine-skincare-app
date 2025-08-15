# Build and Push Hare Run V6 Container
Write-Host "Building Hare Run V6 Container..." -ForegroundColor Green

# Set variables
$ECR_REPO = "396608803476.dkr.ecr.us-east-1.amazonaws.com"
$IMAGE_NAME = "shine-api-gateway"
$IMAGE_TAG = "hare-run-v6"
$FULL_IMAGE = "$ECR_REPO/$IMAGE_NAME`:$IMAGE_TAG"

# Login to ECR
Write-Host "Logging into ECR..." -ForegroundColor Yellow
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_REPO

# Build the image
Write-Host "Building Docker image..." -ForegroundColor Yellow
docker build -f Dockerfile.hare-run-v6 -t "$IMAGE_NAME`:$IMAGE_TAG" .

# Tag for ECR
Write-Host "Tagging image for ECR..." -ForegroundColor Yellow
docker tag "$IMAGE_NAME`:$IMAGE_TAG" $FULL_IMAGE

# Push to ECR
Write-Host "Pushing to ECR..." -ForegroundColor Yellow
docker push $FULL_IMAGE

Write-Host "Hare Run V6 container built and pushed successfully!" -ForegroundColor Green
Write-Host "Image: $FULL_IMAGE" -ForegroundColor Cyan
