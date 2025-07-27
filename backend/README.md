# Shine Backend API

This is the backend API for the Shine skincare application, built with Flask and following a microservices architecture.

## Features

- **Authentication Service**: Google OAuth integration with JWT tokens
- **Image Analysis Service**: Computer vision for skin analysis
- **Product Recommendation Service**: AI-powered product suggestions
- **Payment Processing Service**: Stripe integration for payments
- **MCP Integration Service**: Firecrawl integration for web discovery

## Prerequisites

- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- Docker (optional)

## Quick Start

### 1. Clone and Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env file with your configuration
# See Configuration section below
```

### 3. Database Setup

```bash
# Create PostgreSQL databases
createdb shine_dev
createdb shine_test

# Run database migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 4. Start Services

```bash
# Start Redis (if not running)
redis-server

# Start the Flask application
python run.py
```

The API will be available at `http://localhost:5000`

## Configuration

### Required Environment Variables

Copy `env.example` to `.env` and configure the following:

#### Database
- `DEV_DATABASE_URL`: PostgreSQL connection string for development
- `TEST_DATABASE_URL`: PostgreSQL connection string for testing
- `DATABASE_URL`: PostgreSQL connection string for production

#### Authentication
- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret
- `GOOGLE_REDIRECT_URI`: OAuth callback URL

#### Redis
- `REDIS_URL`: Redis connection string
- `CELERY_BROKER_URL`: Celery broker URL
- `CELERY_RESULT_BACKEND`: Celery result backend URL

#### Stripe (for payments)
- `STRIPE_SECRET_KEY`: Stripe secret key
- `STRIPE_PUBLISHABLE_KEY`: Stripe publishable key

#### MCP Integration
- `MCP_SERVER_URL`: Firecrawl MCP server URL
- `MCP_API_KEY`: MCP API key

## API Endpoints

### Authentication
- `POST /api/auth/login` - Initiate Google OAuth login
- `POST /api/auth/callback` - Handle OAuth callback
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile
- `POST /api/auth/logout` - Logout user
- `POST /api/auth/refresh` - Refresh access token

### Image Analysis
- `POST /api/analysis/upload` - Upload image for analysis
- `GET /api/analysis/results/{upload_id}` - Get analysis results
- `GET /api/analysis/history` - Get analysis history

### Product Recommendations
- `GET /api/recommendations/{analysis_id}` - Get product recommendations
- `POST /api/recommendations/feedback` - Submit recommendation feedback
- `GET /api/recommendations/trending` - Get trending products

### Payments
- `POST /api/payments/create-intent` - Create payment intent
- `POST /api/payments/confirm` - Confirm payment
- `GET /api/payments/history` - Get payment history

### MCP Integration
- `POST /api/mcp/discover-similar` - Discover similar images
- `GET /api/mcp/discovery-results/{discovery_id}` - Get discovery results
- `GET /api/mcp/discovery-progress/{discovery_id}` - Get discovery progress

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8

# Type checking
mypy app/
```

### Database Migrations

```bash
# Create new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── auth/                # Authentication service
│   ├── image_analysis/      # Image analysis service
│   ├── recommendations/     # Product recommendations
│   ├── payments/            # Payment processing
│   ├── mcp/                 # MCP integration
│   └── models/              # Database models
├── config.py               # Configuration classes
├── requirements.txt        # Python dependencies
├── run.py                 # Application entry point
└── README.md              # This file
```

## Deployment

### Docker Deployment

```bash
# Build Docker image
docker build -t shine-backend .

# Run container
docker run -p 5000:5000 shine-backend
```

### Production Deployment

1. Set environment variables for production
2. Use production database
3. Configure reverse proxy (nginx)
4. Set up SSL certificates
5. Configure monitoring and logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License. 

# Bug Bounty

We welcome security researchers and contributors! If you find a vulnerability or security issue, please report it responsibly. Do not publicly disclose vulnerabilities without first contacting the maintainers. Responsible disclosures may be eligible for a reward.

To report a bug or vulnerability, please open an issue or email the maintainers directly.

# Deployment (No Docker)

## Recommended: AWS Elastic Beanstalk (Python Platform)
- Remove any Dockerfile from the backend directory.
- Ensure you have a `requirements.txt` and a `Procfile` (should be: `web: gunicorn api:app`).
- Zip your backend directory (excluding venv, .git, .pytest_cache, __pycache__, and any secrets).
- Deploy to AWS Elastic Beanstalk using the Python 3.11 platform.
- Set all required environment variables in the AWS Console.

## Security Best Practices
- **Never commit secrets or credentials** (API keys, service account JSON, etc.) to version control.
- Add all secrets to your `.gitignore` and `.ebignore` files.
- Use environment variables for all sensitive information. 

## Known Deployment Issue (July 2025)

**Issue:**
- AWS Elastic Beanstalk deployment fails at the dependency installation step.
- This is likely due to heavy ML dependencies (torch, torchvision, faiss-cpu) failing to build or install on the default Python environment.
- Increasing the disk size (e.g., to 30GB) is required, but sometimes the environment upgrade can take a long time or get stuck.

**Troubleshooting Steps:**
- Check Beanstalk logs for pip errors or missing system packages.
- Try pinning torch, torchvision, and faiss-cpu to specific versions in requirements.txt.
- If faiss-cpu fails, add a .ebextensions/python.config file to install system packages (e.g., libomp, gcc, python3-devel).
- If the instance runs out of memory or disk, try a larger instance type and/or increase the root volume size.
- If the environment upgrade (disk size increase) takes too long or fails, consider terminating the environment and creating a new one with the desired disk size from the start.

**Next:**
- See the logs for the exact error and adjust requirements or system packages as needed.
- If stuck, start a fresh environment with the correct settings. 

- If you see 'Cannot import setuptools.build_meta' or build backend errors during deployment, add a `pyproject.toml` file to your backend directory with:

```toml
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
```

This ensures pip can build source packages correctly in the AWS environment. 