# Developer Instructions for Shine Skin Collective

This document outlines the new development path for the Shine Skin Collective project, provides a systematic approach to resolving common development errors, and guides the team towards achieving a Maximum Viable Product (MVP) and successful deployment. These instructions are based on the updated `README.md` in the `mcpmessenger/shine-skin-collective` GitHub repository.

## 1. Understanding the New Development Path

The Shine Skin Collective project has evolved into a full-stack application with a clear separation of concerns and modern deployment strategies. The core components and their interactions are as follows:

### 1.1 Project Overview

Shine is an AI-powered web application designed for skin analysis and personalized skincare recommendations. It leverages advanced computer vision and machine learning to provide professional features and a user-friendly experience.

### 1.2 Technology Stack

*   **Frontend**: Built with **Next.js**, deployed on **AWS Amplify**.
*   **Backend**: A **Flask** application, deployed on **Vercel**.
*   **AI & ML**: Utilizes advanced computer vision and machine learning, likely involving custom models for skin analysis and potentially vector databases (like Milvus, as discussed previously) for similarity search.
*   **Database**: **Supabase** is used for the database, providing a backend-as-a-service solution.
*   **Authentication**: Implemented using **Google OAuth**.
*   **Payments**: Integrated with **Stripe**.
*   **Cloud Integration**: Leverages **Google Cloud Platform** for AI/ML services (e.g., Google Vision API, custom model hosting) and potentially data storage.

### 1.3 Key Development Areas

Based on the project structure and technologies, the primary development areas are:

*   **Frontend Development (`app/`, `components/`, `lib/`, `hooks/`)**: Focuses on the user interface, user experience, and interaction with the backend API. This includes pages for authentication, skin analysis, and similarity search.
*   **Backend Development (`backend/`)**: Handles API endpoints, business logic, database interactions (Supabase), authentication (Google OAuth), and payment processing (Stripe). This is where the core AI/ML model inference will likely reside or be orchestrated.
*   **AI/ML Integration**: This involves integrating custom computer vision models for skin analysis, potentially leveraging vector databases for efficient similarity search, and possibly RAG (Retrieval Augmented Generation) for enhanced recommendations.
*   **Deployment & Infrastructure**: Managing deployments on AWS Amplify (frontend) and Vercel (backend), and configuring environment variables for both platforms.

### 1.4 Communication Flow

*   The **Frontend (AWS Amplify)** communicates with the **Backend API (Vercel)**.
*   The Backend interacts with **Supabase** for data persistence, **Google OAuth** for authentication, **Stripe** for payments, and **Google Cloud Platform** services for AI/ML operations.

This new path emphasizes a modular, cloud-native approach, allowing for scalable development and deployment of both frontend and backend services independently.



## 2. Systematic Error Resolution and Debugging Guide

Development errors are inevitable, but a systematic approach can significantly reduce debugging time and frustration. This section provides a guide to identifying, diagnosing, and resolving common issues in the Shine Skin Collective project.

### 2.1 Common Error Categories

Errors in a full-stack application like Shine can originate from various layers. Understanding these categories helps in narrowing down the problem:

*   **Frontend Errors**: Issues related to the Next.js application, including UI rendering problems, JavaScript runtime errors, incorrect data display, or failed API calls from the client side.
*   **Backend Errors**: Problems within the Flask API, such as server startup failures, incorrect API responses, database connection issues, authentication/authorization failures, or errors in AI/ML model inference.
*   **API Integration Errors**: Mismatches or failures in communication between the frontend and backend, or between the backend and external services (Supabase, Google OAuth, Stripe, Google Cloud Vision API, Milvus).
*   **Environment Variable Configuration Errors**: Incorrectly set or missing environment variables leading to authentication failures, incorrect API endpoints, or service misconfigurations.
*   **External Service Errors**: Issues with third-party services like Supabase (database connectivity, schema, Row Level Security), Google OAuth (client ID/secret, redirect URIs, scope issues), Stripe (API keys, webhook setup), or Google Cloud Platform (API enablement, credentials, quotas).
*   **Deployment Errors**: Problems occurring during the build or deployment process on AWS Amplify (frontend) or Vercel (backend), often related to build dependencies, environment variables, or configuration files.

### 2.2 Systematic Debugging Steps

When an error occurs, follow these steps to systematically diagnose and resolve the issue:

1.  **Observe and Document**: What is the exact error message? Where does it appear (browser console, server logs, build logs)? What actions led to the error? Documenting these details is crucial for effective troubleshooting and for seeking help if needed.

2.  **Check Logs**: Logs are your first line of defense. They provide detailed information about what went wrong.
    *   **Frontend (Browser Console)**: Open your browser's developer tools (usually F12 or Cmd+Option+I) and check the `Console` tab for JavaScript errors, network request failures, and `console.log` messages.
    *   **Frontend (AWS Amplify Build Logs)**: If the frontend fails to deploy, check the build logs in the AWS Amplify Console for errors during `npm ci` or `npm run build` phases.
    *   **Backend (Local Terminal)**: If running locally, check the terminal where your Flask backend (`python run.py`) is running for Python tracebacks or Flask-specific error messages.
    *   **Backend (Vercel Function Logs)**: For deployed backend issues, go to your Vercel Dashboard, navigate to your project, and check the `Logs` tab for serverless function execution errors.

3.  **Verify Environment Variables**: Many issues stem from incorrect or missing environment variables. Double-check that all required environment variables are correctly set in:
    *   **Frontend**: AWS Amplify Console (for deployed app) and `.env.local` (for local development).
    *   **Backend**: Vercel Dashboard (for deployed API) and `.env` (for local development).
    *   Ensure there are no typos, leading/trailing spaces, or incorrect values.
    *   Remember that `GOOGLE_APPLICATION_CREDENTIALS` for the backend should point to the *path* of your service account JSON key file, not the JSON content itself.

4.  **Isolate the Problem**: Determine which part of the system is failing.
    *   **Frontend vs. Backend**: If the frontend is displaying an error related to an API call, try testing the backend API endpoint directly using tools like `curl`, Postman, or Insomnia. If the backend API works correctly when tested directly, the problem is likely in the frontend's API integration or data handling. If the backend API fails, the problem is in the backend or its dependencies.
    *   **Backend vs. External Service**: If the backend is failing, check if it's due to a connection issue with Supabase, Google OAuth, Stripe, or Google Cloud services. Look for specific error messages related to these integrations in the backend logs.

5.  **Test API Endpoints Directly**: Use `curl` or a tool like Postman/Insomnia to send requests directly to your backend API endpoints. This helps confirm if the backend is functioning as expected, independent of the frontend.

    ```bash
    # Example: Test a GET endpoint
    curl -X GET https://shine-skincare-rdrp39n2c-williamtflynn-2750s-projects.vercel.app/api/some-endpoint

    # Example: Test a POST endpoint with JSON data
    curl -X POST -H "Content-Type: application/json" \
         -d '{"key": "value"}' \
         https://shine-skincare-rdrp39n2c-williamtflynn-2750s-projects.vercel.app/api/another-endpoint
    ```

6.  **Use Browser Developer Tools (for Frontend)**: Beyond the console, the `Network` tab can show you the status codes and responses of API calls. The `Elements` tab can help inspect the DOM and identify rendering issues. The `Sources` tab allows you to set breakpoints and step through your JavaScript code.

7.  **Review Recent Code Changes**: If the error recently appeared, review the latest code changes. Use `git log` or your GitHub repository's commit history to identify commits that might have introduced the bug. Revert to a previous working version if necessary to confirm the source of the problem.

8.  **Simplify and Reproduce**: Try to create the simplest possible scenario that reproduces the error. This helps in isolating the problematic code section.

### 2.3 Troubleshooting Specific Areas

#### 2.3.1 Frontend (Next.js/React) Issues

*   **"Hydration Mismatch" Errors**: Often occur when the server-rendered HTML doesn't match the client-rendered HTML. Ensure dynamic content or client-side only components are correctly handled (e.g., using `useEffect` or `typeof window !== 'undefined'` checks).
*   **API Call Failures**: Check the `Network` tab in browser dev tools. Look for 4xx (client-side errors like 401 Unauthorized, 404 Not Found) or 5xx (server-side errors). Verify the `NEXT_PUBLIC_API_URL` environment variable.
*   **Component Rendering Issues**: Use React Developer Tools (browser extension) to inspect component state and props.

#### 2.3.2 Backend (Flask) Issues

*   **`ModuleNotFoundError` or `ImportError`**: Ensure all dependencies are listed in `requirements.txt` and installed (`pip install -r requirements.txt`). Check your Python environment and virtual environment activation.
*   **`AttributeError` or `TypeError`**: These usually indicate issues with object properties or data types. Inspect the data being passed to functions or methods.
*   **Database Connection Errors (Supabase)**: Verify `DATABASE_URL`, `SUPABASE_URL`, and `SUPABASE_KEY` environment variables. Check if your Supabase database is running and accessible. Ensure your database schema matches what your Flask app expects.
*   **API Key/Credential Issues**: For Google Cloud Vision API, Google OAuth, or Stripe, ensure the correct API keys, client IDs, and secrets are loaded from environment variables and are valid.
*   **Vercel Deployment Failures**: Check `vercel.json` for correct configuration, especially the `build` and `routes` sections. Ensure `api.py` is correctly set as the entry point.

#### 2.3.3 Google Cloud / OAuth Integration Issues

*   **`GOOGLE_APPLICATION_CREDENTIALS`**: This environment variable must point to the *absolute path* of your Google service account JSON key file, not the content of the file itself. Ensure the service account has the necessary roles (e.g., `Vision AI User`, `Storage Object Viewer`).
*   **OAuth Client ID/Secret**: Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are correct. Ensure the authorized redirect URIs in your Google Cloud Console OAuth consent screen match your application's redirect URIs (e.g., `http://localhost:3000/auth/callback/google` for local development, and your deployed Amplify URL for production).
*   **API Enablement**: Confirm that the necessary Google Cloud APIs (e.g., Cloud Vision API) are enabled in your Google Cloud project.

#### 2.3.4 Supabase Issues

*   **Row Level Security (RLS)**: If you're getting unexpected permission errors when accessing data, check your RLS policies in Supabase. They might be preventing your application from reading or writing data.
*   **Schema Mismatches**: Ensure your application's data models or queries align with your Supabase table schemas.

By systematically applying these debugging strategies, your development team can efficiently identify and resolve errors, leading to a smoother development process and a more stable application.



## 3. MVP Definition and AWS Elastic Beanstalk Deployment Strategy

Defining a clear Minimum Viable Product (MVP) is crucial for focused development and rapid iteration. This section outlines the MVP for the Shine Skin Collective and details the new backend deployment strategy using AWS Elastic Beanstalk (EB) via the AWS CLI.

### 3.1 Defining the Maximum Viable Product (MVP)

Given the project's complexity and the goal of rapid deployment, the MVP should focus on the core value proposition: AI-powered skin analysis and personalized recommendations. A potential MVP could include:

*   **User Authentication**: Google OAuth for user login and registration.
*   **Image Upload**: Frontend functionality to allow users to upload skin images.
*   **Basic Skin Analysis**: Backend processing of uploaded images using the AI model (initially, this could be a simplified model or a pre-trained one) to identify general skin conditions (e.g., acne, dryness, redness).
*   **Personalized Recommendations**: Displaying basic skincare product or routine recommendations based on the identified skin condition.
*   **User Profile**: A simple user profile to view past analyses.
*   **Responsive Design**: Ensuring the application is usable across desktop and mobile devices.

**Features to defer for post-MVP**: Advanced severity assessment, detailed racial analysis (beyond basic Fitzpatrick/Monk tones), comprehensive RAG-based recommendations, Stripe integration for payments, and extensive historical data tracking.

### 3.2 Backend Deployment with AWS Elastic Beanstalk (EB) via CLI

The backend will now be deployed to AWS Elastic Beanstalk, providing a robust and scalable environment. This approach offers more control and flexibility compared to Vercel for complex Python applications. The deployment will be managed via the AWS Command Line Interface (CLI).

#### 3.2.1 Prerequisites for EB Deployment

Before deploying, ensure the following are set up:

1.  **AWS Account and IAM User**: You need an active AWS account and an IAM user with programmatic access (Access Key ID and Secret Access Key) and permissions to create and manage Elastic Beanstalk applications, environments, EC2 instances, S3 buckets, and CloudWatch logs.
2.  **AWS CLI Installed and Configured**: If not already installed, follow the official AWS CLI installation guide: [Install the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html). After installation, configure it with your IAM user credentials:
    ```bash
    aws configure
    ```
    Provide your AWS Access Key ID, Secret Access Key, default region (e.g., `us-east-1`), and default output format (e.g., `json`).
3.  **Elastic Beanstalk CLI (EB CLI) Installed**: The EB CLI is a command-line client that simplifies creating, updating, and managing Elastic Beanstalk environments. Install it using `pip`:
    ```bash
    pip install awsebcli --upgrade --user
    ```
    Ensure `~/.local/bin` is in your system's PATH if you installed with `--user`.
4.  **Python Application Structure**: Your Flask backend should be structured appropriately for Elastic Beanstalk. The `application.py` file (or `wsgi.py` pointing to your Flask app instance) should be at the root of your backend directory, or you need to specify its location in `.ebextensions`.
5.  **`requirements.txt`**: Ensure your `backend/requirements.txt` file lists all Python dependencies required by your Flask application.
6.  **`.ebextensions` Folder**: This folder at the root of your backend directory (`shine-skin-collective/backend/.ebextensions/`) is used for custom Elastic Beanstalk configurations. It can contain `.config` files to install packages, set environment variables, or run commands during deployment.

#### 3.2.2 Backend Preparation for EB

Navigate to your backend directory:

```bash
cd backend
```

Initialize your Elastic Beanstalk application:

```bash
eb init -p python-3.9 shine-backend-app --region us-east-1
```

*   `-p python-3.9`: Specifies the Python platform version. Adjust if your Flask app uses a different version.
*   `shine-backend-app`: The name of your Elastic Beanstalk application.
*   `--region us-east-1`: Your desired AWS region.

This command creates the `.elasticbeanstalk/config.yml` file, which stores your EB CLI settings.

#### 3.2.3 Configuring Environment Variables for EB

Environment variables for your backend (e.g., `DATABASE_URL`, `GOOGLE_CLIENT_ID`, `JWT_SECRET_KEY`, `GOOGLE_CLOUD_PROJECT_ID`, `GOOGLE_APPLICATION_CREDENTIALS`) should be set directly in the Elastic Beanstalk environment. **Do NOT commit sensitive credentials to your repository.**

You can set environment variables using the EB CLI:

```bash
eb setenv DATABASE_URL=your_supabase_database_url \
             GOOGLE_CLIENT_ID=your_google_client_id \
             GOOGLE_CLIENT_SECRET=your_google_client_secret \
             JWT_SECRET_KEY=your_jwt_secret \
             STRIPE_SECRET_KEY=your_stripe_secret \
             SUPABASE_URL=your_supabase_url \
             SUPABASE_KEY=your_supabase_service_key \
             SUPABASE_ANON_KEY=your_supabase_anon_key \
             GOOGLE_CLOUD_PROJECT_ID=your_google_cloud_project_id
```

For `GOOGLE_APPLICATION_CREDENTIALS`, you should upload your service account JSON key file to a secure S3 bucket (created manually or via EB configuration) and then reference its path or content securely. A common approach is to store the JSON content as an environment variable, but this can be risky for very large JSONs or if not handled securely. Alternatively, you can use `.ebextensions` to download the key from S3 during deployment.

**Example `.ebextensions/01_setup.config` for `GOOGLE_APPLICATION_CREDENTIALS` (if stored in S3):**

```yaml
files:
  "/tmp/google-credentials.json":
    mode: "000600"
    owner: root
    group: root
    content: |-
      # Replace with your actual JSON content or use a secure S3 download
      # This is a placeholder. For production, consider fetching from S3 or AWS Secrets Manager.
      {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "...",
        "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
        "client_email": "...",
        "client_id": "...",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "...",
        "universe_domain": "googleapis.com"
      }

container_commands:
  01_set_google_credentials:
    command: "export GOOGLE_APPLICATION_CREDENTIALS=/tmp/google-credentials.json"
    leader_only: true
```

**Note**: Storing the entire JSON content directly in `.ebextensions` is generally not recommended for production due to security concerns and size limits. A more secure approach involves storing the key in AWS Secrets Manager and fetching it during application startup, or securely downloading it from a private S3 bucket using an IAM role attached to the EC2 instances.

#### 3.2.4 Deploying the Backend

Once initialized and configured, deploy your backend to a new Elastic Beanstalk environment:

```bash
eb create shine-backend-dev
```

*   `shine-backend-dev`: The name of your Elastic Beanstalk environment (e.g., `dev`, `staging`, `prod`).

To update an existing environment:

```bash
eb deploy
```

This command zips your backend directory, uploads it to S3, and deploys it to your Elastic Beanstalk environment. You can monitor the deployment status in the AWS Elastic Beanstalk console or by running `eb status`.

#### 3.2.5 Updating Backend URL in Frontend

After successful deployment, obtain the URL of your Elastic Beanstalk environment. This will be the new `NEXT_PUBLIC_API_URL` for your frontend.

1.  Get the environment URL:
    ```bash
    eb status
    ```
    Look for the `CNAME` field in the output.
2.  Update `NEXT_PUBLIC_API_URL` in your AWS Amplify Console for the frontend. No code push is required for the frontend after this change.

This new deployment strategy provides a robust and scalable foundation for your backend, allowing for more complex AI/ML integrations and better management of your application's infrastructure.



## 4. Overall Deployment Strategy

The Shine Skin Collective project utilizes a modern, decoupled deployment strategy, with the frontend hosted on AWS Amplify and the backend on AWS Elastic Beanstalk. This setup provides flexibility, scalability, and independent deployment cycles for each component.

### 4.1 Frontend Deployment (AWS Amplify)

AWS Amplify provides a robust platform for hosting Next.js applications, offering continuous deployment from your GitHub repository. Any push to the `main` branch (or configured branch) will automatically trigger a build and redeploy.

**Key Steps:**

1.  **Connect Repository**: Link your `shine-skin-collective` GitHub repository to AWS Amplify.
2.  **Configure Build Settings**: Use the provided `amplify.yml` (or similar) configuration to define build commands and artifact locations. The `README.md` provides a basic example:
    ```yaml
    version: 1
    frontend:
      phases:
        preBuild:
          commands:
            - npm ci
        build:
          commands:
            - npm run build
      artifacts:
        baseDirectory: .next
        files:
          - '**/*'
    ```
3.  **Set Environment Variables**: Crucially, set `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_APP_URL` in the Amplify Console under Environment Variables. The `NEXT_PUBLIC_API_URL` should point to your deployed Elastic Beanstalk backend URL.
4.  **Automated Deployment**: Configure Amplify to automatically deploy on pushes to your main branch.

### 4.2 Backend Deployment (AWS Elastic Beanstalk)

As detailed in Section 3.2, the Flask backend is deployed to AWS Elastic Beanstalk. This provides a managed environment for running Python applications, handling server provisioning, load balancing, and scaling.

**Key Steps:**

1.  **Initialize EB Application**: Use `eb init` in your `backend/` directory to set up the EB application and environment configuration.
2.  **Configure Environment Variables**: Set all sensitive and configuration-dependent environment variables (e.g., `DATABASE_URL`, `GOOGLE_CLIENT_ID`, `JWT_SECRET_KEY`, `GOOGLE_CLOUD_PROJECT_ID`, `GOOGLE_APPLICATION_CREDENTIALS`) directly in the Elastic Beanstalk environment using `eb setenv` or through the AWS Management Console. **Avoid hardcoding these in your code or committing them to Git.**
3.  **Deploy**: Use `eb create` for initial deployment and `eb deploy` for subsequent updates. The EB CLI handles packaging your application and deploying it to the configured environment.
4.  **Update Frontend API URL**: After each backend deployment, retrieve the new Elastic Beanstalk environment URL (CNAME) using `eb status` and update the `NEXT_PUBLIC_API_URL` in the AWS Amplify Console. This ensures the frontend always points to the correct backend endpoint.

### 4.3 Development Workflow Integration

*   **Local Development**: Developers can run the frontend and backend locally as described in the "Quick Start" section of the `README.md`. This allows for rapid iteration and testing without affecting deployed environments.
*   **Feature Branches**: All new features and bug fixes should be developed in separate feature branches.
*   **Code Reviews**: Implement a robust code review process before merging changes to the `main` branch.
*   **Staging Environments**: Consider setting up staging environments for both frontend and backend (e.g., `shine-frontend-staging` on Amplify, `shine-backend-staging` on EB) to test new features in a production-like environment before deploying to production.

This deployment strategy ensures a robust, scalable, and maintainable architecture for the Shine Skin Collective application.



## 5. Codebase Cleanup and Maintenance

Maintaining a clean and organized codebase is crucial for long-term project health, developer productivity, and efficient deployments. This section outlines best practices for identifying and removing old and unnecessary files.

### 5.1 Why Cleanup is Important

*   **Reduced Repository Size**: Smaller repositories are faster to clone, pull, and push, improving developer workflow.
*   **Faster Builds**: Unnecessary files can sometimes be included in build processes, slowing them down.
*   **Improved Clarity**: A clean codebase is easier to navigate and understand, reducing cognitive load for developers.
*   **Security**: Old configuration files or forgotten credentials can pose security risks if not properly managed.
*   **Deployment Efficiency**: Smaller deployment packages lead to faster uploads and deployments to platforms like AWS Amplify and Elastic Beanstalk.

### 5.2 Identifying Unnecessary Files

Common categories of files that often become unnecessary include:

*   **Temporary Files**: Files generated during development or testing that are not part of the final build (e.g., `.log`, `.tmp`, `.bak` files).
*   **Build Artifacts**: Files generated by build tools that are not intended for version control (e.g., `dist/`, `build/` directories, `node_modules/`, `__pycache__/`). These should typically be excluded via `.gitignore`.
*   **Old Configuration Files**: Configuration files from previous deployment strategies or unused services.
*   **Unused Code/Assets**: Code files, images, or other assets that are no longer referenced or used by the application.
*   **Personal Development Files**: Files created by individual developers for testing or experimentation that were accidentally committed.
*   **Dependency Caches**: Directories like `node_modules` (for Node.js) or virtual environment folders (for Python) should generally not be committed to the repository.

### 5.3 Cleanup Process

Follow these steps to systematically clean up your codebase:

1.  **Review `.gitignore` and `.dockerignore`**: Ensure that all build artifacts, temporary files, and dependency directories are correctly listed in your `.gitignore` (for Git) and `.dockerignore` (if using Docker) files. This prevents them from being committed to the repository.

    *   **Example `.gitignore` entries:**
        ```
        # Node.js
        node_modules/
        .next/
        .env.local

        # Python
        __pycache__/
        *.pyc
        .venv/
        .env

        # AWS Elastic Beanstalk
        .elasticbeanstalk/
        *.zip

        # General
        *.log
        *.tmp
        *.bak
        ```

2.  **Run Cleanup Commands**: Many build tools and package managers offer cleanup commands.

    *   **Frontend (Next.js/npm)**:
        ```bash
        # Remove node_modules and reinstall to ensure clean dependencies
        rm -rf node_modules
        npm install

        # Clean Next.js build cache
        rm -rf .next
        ```

    *   **Backend (Python/pip)**:
        ```bash
        # Remove Python bytecode files
        find . -name "__pycache__" -exec rm -rf {} +
        find . -name "*.pyc" -delete

        # Remove virtual environment (if present in repo, though it shouldn't be)
        rm -rf .venv
        ```

3.  **Identify Unused Files/Code**: This is often the most challenging part and may require manual review or static analysis tools.

    *   **Manual Review**: Regularly review directories and files, especially those that haven't been touched recently. If a file's purpose is unclear, investigate its usage.
    *   **Static Analysis Tools**: Tools like ESLint (for JavaScript/TypeScript) or Pylint (for Python) can sometimes identify unused variables or functions, which might point to unused files.
    *   **Code Coverage Tools**: Running tests with code coverage can highlight parts of the codebase that are never executed, potentially indicating dead code.

4.  **Remove Old Branches**: Encourage developers to regularly delete merged or stale feature branches from the remote repository to keep the Git history clean.

5.  **Periodically Audit Dependencies**: Review `package.json` and `requirements.txt` for unused or outdated dependencies. Remove those that are no longer needed.

6.  **Review Deployment Artifacts**: Ensure that your deployment pipelines (AWS Amplify, Elastic Beanstalk) are only packaging necessary files. For example, Elastic Beanstalk deploys the contents of your `backend/` directory. Ensure this directory only contains what's needed for the application to run.

By integrating these cleanup practices into your development workflow, the Shine Skin Collective project will remain agile, efficient, and easy to maintain.



## Conclusion

This document serves as a comprehensive guide for the development team of the Shine Skin Collective project. By understanding the new development path, adopting a systematic approach to error resolution, focusing on the defined MVP, and adhering to the AWS Elastic Beanstalk deployment strategy, your team can efficiently build and deploy a robust AI-powered skincare analysis application. Furthermore, consistent codebase cleanup and maintenance will ensure the project remains agile and scalable for future enhancements.

Remember to leverage the provided resources and best practices to streamline your development workflow and achieve successful deployments. Continuous communication and collaboration within the team will be key to overcoming challenges and delivering a high-quality product.

---

**Author**: Manus AI

**Date**: July 27, 2025


