# Shine Backend API

This is the backend API for the Shine skincare application, built with Flask and following a microservices architecture.

## Security & Environment Variables

- Never commit `.env`, `.env.local`, or any secret files to GitHub.
- All production secrets and environment variables should be set in the AWS Elastic Beanstalk Console (backend) and AWS Amplify Console (frontend).
- Ensure `.env*` files are listed in `.gitignore` and `.ebignore`.

## Pre-commit Checklist

- Run `git status` and `git diff` to ensure no secrets are staged.
- Optionally, run `npx trufflehog filesystem .` or `gitleaks detect` to scan for secrets.

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

### Production Deployment

1. Set environment variables for production in the AWS Console (do not commit secrets).
2. Use production database.
3. Configure reverse proxy (nginx) if needed.
4. Set up SSL certificates.
5. Configure monitoring and logging.

### Docker Deployment (Optional/Local Dev Only)

```bash
# Build Docker image
# (For local development only; not used in production)
docker build -t shine-backend .

# Run container
docker run -p 5000:5000 shine-backend
```

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

## What We've Tried (Security & Deployment)
- All secrets and environment variables are managed via the AWS Console (Elastic Beanstalk for backend, Amplify for frontend) and are never committed to GitHub.
- `.env*` files are included in `.gitignore` and `.ebignore` to prevent accidental leaks.
- We run pre-commit checks and recommend using tools like `trufflehog` or `gitleaks` to scan for secrets before pushing.
- The backend is deployed on AWS Elastic Beanstalk (Python platform, no Docker), and the frontend is deployed via AWS Amplify with GitHub integration.
- All dependencies are pinned and reviewed for security updates.
- We monitor deployment logs and health checks for anomalies.

If you discover a bug or vulnerability, please open an issue or email the maintainers directly. We appreciate responsible disclosure and will work with you to resolve any issues.

# Deployment Flow

## Frontend (AWS Amplify)
- Source code is managed in GitHub.
- On push to the main branch, AWS Amplify automatically builds and deploys the frontend.
- All frontend environment variables (e.g., `NEXT_PUBLIC_BACKEND_URL`) are set in the Amplify Console, not in the repo.
- No secrets are ever committed to GitHub.

## Backend (AWS Elastic Beanstalk)
- Source code is managed in GitHub.
- Backend is deployed using the EB CLI (`eb deploy`) to an Elastic Beanstalk environment (Python platform, no Docker).
- All backend environment variables and secrets are set in the AWS Console for the EB environment.
- Pre-commit checks and secret scans are run before every push.
- After deployment, health checks and logs are monitored to ensure the app is running correctly.

---

## Project Status (as of July 2025)

### ✅ Completed
- Enhanced FAISS service with cosine similarity and vector normalization
- Demographic-weighted search service
- Google Vision API integration service
- Production FAISS service with persistence and thread safety
- Enhanced skin type classifier service
- Updated API endpoints for enhanced analysis
- Integration of services with existing infrastructure
- Comprehensive error handling and logging
- Performance optimization and AWS deployment

### 🟡 In Progress / Remaining
- Validation and testing framework (cross-demographic, performance, accuracy)
- Gradual service replacement strategy (feature flags, health monitoring, rollback)
- Production environment and credentials setup (Google Vision, Supabase, secure creds, monitoring)
- Documentation and deployment configuration (API docs, deployment guide, troubleshooting, monitoring)
- Final integration and validation testing (end-to-end, performance, regression, backward compatibility)

---

**Note:**
- The backend is now fully migrated to AWS Elastic Beanstalk for scalable, production-grade deployment.
- The frontend is managed via AWS Amplify with GitHub integration for continuous deployment.
- See `.kiro/specs/backend-ai-upgrade/tasks.md` for the most granular and up-to-date task tracking. 

- If you see 'Cannot import setuptools.build_meta' or build backend errors during deployment, add a `pyproject.toml` file to your backend directory with:

```toml
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
```

This ensures pip can build source packages correctly in the AWS environment. 