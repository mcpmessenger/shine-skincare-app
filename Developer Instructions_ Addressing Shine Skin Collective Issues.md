# Developer Instructions: Addressing Shine Skin Collective Issues

This document outlines the identified issues within the Shine Skin Collective application, specifically focusing on the frontend hosted on AWS Amplify and the backend on Vercel. It provides detailed instructions for developers to resolve these problems, ensuring proper functionality and communication between the application components.

## 1. Resolving CORS Policy Block

**Problem**: The primary issue preventing the application from functioning correctly is the Cross-Origin Resource Sharing (CORS) policy block. The frontend, hosted at `https://main.d2wy4w2nf9bgxx.amplifyapp.com`, is unable to communicate with the backend API at `https://backend-7yqorv3fz-williamtflynn-2750s-projects.vercel.app` because the backend is not sending the necessary `Access-Control-Allow-Origin` header in its responses. This is a security measure enforced by web browsers to prevent malicious cross-site requests.

**Solution**: The backend application, which is a Flask application hosted on Vercel, needs to be configured to explicitly allow requests from the AWS Amplify frontend origin. This can be achieved by implementing CORS handling within the Flask application. The `flask-cors` library is a common and effective way to manage CORS in Flask applications.

### Steps to Implement CORS in Flask Backend:

1.  **Install `flask-cors`**: If not already installed, add the `flask-cors` package to your backend project's dependencies.

    ```bash
    pip install flask-cors
    ```

2.  **Initialize CORS in your Flask app**: Modify your Flask application's main file (e.g., `app.py` or `api.py` as suggested by the GitHub repository structure) to initialize CORS. You need to specify the allowed origins.

    ```python
    from flask import Flask
    from flask_cors import CORS

    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "https://main.d2wy4w2nf9bgxx.amplifyapp.com"}})

    # Your existing routes and logic go here
    ```

    **Explanation of `CORS` initialization**: 
    *   `app`: Your Flask application instance.
    *   `resources={r"/api/*": ...}`: This specifies that CORS should be applied to all routes under the `/api/` path. Adjust this regex if your API endpoints are structured differently.
    *   `"origins": "https://main.d2wy4w2nf9bgxx.amplifyapp.com"`: This is the crucial part. It explicitly tells the backend to allow requests originating from `https://main.d2wy4w2nf9bgxx.amplifyapp.com`. If you have other frontend environments (e.g., a development environment), you can add them as a list: `"origins": ["https://main.d2wy4w2nf9bgxx.amplifyapp.com", "http://localhost:3000"]`.

3.  **Deploy the updated Backend**: After making these changes, deploy the updated Flask backend to Vercel. As per the GitHub `README.md`, you can do this using the Vercel CLI:

    ```bash
    cd backend
    vercel --prod
    ```

    This will update your backend with the new CORS configuration, allowing the frontend to make successful requests.

## 2. Investigating Unauthorized API Access (401 Error)

**Problem**: Even after resolving the CORS issue, the screenshot indicates a `401 (Unauthorized)` error for the `/api/v2/analyze/guest` endpoint. The GitHub `README.md` states that 


guest access should be available for this endpoint. This suggests a potential misconfiguration in the backend's authentication logic or an unexpected requirement for guest access.

**Solution**: Once the CORS issue is resolved, the `401 Unauthorized` error for the guest analysis endpoint needs to be thoroughly investigated. Here's a systematic approach:

### Steps to Debug 401 Error for Guest Access:

1.  **Verify Backend Logs**: Check the Vercel deployment logs for the backend application. Look for any error messages or warnings related to authentication or authorization when the `/api/v2/analyze/guest` endpoint is accessed. These logs can provide crucial insights into why the request is being rejected.

2.  **Review Backend Authentication Logic**: Examine the Python code for the `/api/v2/analyze/guest` endpoint and any associated authentication middleware. Ensure that:
    *   There are no unintended authentication checks applied to this specific endpoint.
    *   If any API keys or tokens are expected even for guest access (e.g., a public API key), verify that the frontend is sending them correctly and the backend is validating them as expected.
    *   Confirm that the route is indeed configured to allow unauthenticated access as intended by the "Guest Access" feature.

3.  **Test Directly with `curl` or Postman**: Once CORS is resolved, try making a direct request to the `/api/v2/analyze/guest` endpoint using `curl` or a tool like Postman. This bypasses the frontend and helps isolate whether the issue is with the backend's handling of the request or something specific to the frontend's interaction.

    ```bash
    curl -X POST https://backend-7yqorv3fz-williamtflynn-2750s-projects.vercel.app/api/v2/analyze/guest -H "Content-Type: application/json" -d '{}'
    ```
    (Adjust the `-d` payload as per the actual expected request body for this endpoint.)

4.  **Examine Frontend Request**: In the browser's developer tools (Network tab), inspect the actual request being sent by the frontend to the `/api/v2/analyze/guest` endpoint. Verify the headers, payload, and any other parameters to ensure they match what the backend expects for guest access.

## 3. Addressing Missing `manifest.json`

**Problem**: The `manifest.json` file is not found, resulting in a 404 error. While this doesn't break the core functionality of the web application, it indicates that the application is not fully configured as a Progressive Web App (PWA). A `manifest.json` file is essential for defining app metadata, icons, and display modes, allowing users to install the web application to their home screen and providing an app-like experience.

**Solution**: To resolve the missing `manifest.json` error and enable PWA capabilities, you need to configure your Next.js application to generate and serve this file.

### Steps to Generate `manifest.json` in Next.js:

1.  **Install `next-pwa` (Recommended)**: The `next-pwa` package simplifies adding PWA capabilities to Next.js applications, including generating the `manifest.json` and service worker.

    ```bash
    npm install next-pwa
    ```

2.  **Configure `next.config.js`**: Modify your `next.config.js` file to include the `next-pwa` plugin.

    ```javascript
    const withPWA = require('next-pwa')({
      dest: 'public',
      disable: process.env.NODE_ENV === 'development',
    })

    module.exports = withPWA({
      // Your existing Next.js config
    })
    ```

    *   `dest: 'public'`: This tells `next-pwa` to output the `manifest.json` and service worker files to the `public` directory, which is served statically by Next.js.
    *   `disable: process.env.NODE_ENV === 'development'`: This is optional but recommended to disable PWA features during development for faster build times.

3.  **Create `public/manifest.json`**: Create a `manifest.json` file in your `public` directory. This file will define your PWA's properties. Here's a basic example:

    ```json
    {
      "name": "Shine - AI-Powered Skincare",
      "short_name": "Shine",
      "description": "AI-powered skin analysis and personalized skincare recommendations.",
      "start_url": "/",
      "display": "standalone",
      "background_color": "#ffffff",
      "theme_color": "#000000",
      "icons": [
        {
          "src": "/icons/icon-192x192.png",
          "sizes": "192x192",
          "type": "image/png"
        },
        {
          "src": "/icons/icon-512x512.png",
          "sizes": "512x512",
          "type": "image/png"
        }
      ]
    }
    ```

    *   **Important**: Ensure you have the specified icon files (e.g., `icon-192x192.png`, `icon-512x512.png`) in your `public/icons` directory. You'll need to create these icons.

4.  **Link `manifest.json` in `_document.js` or `layout.js`**: In your Next.js application, you need to link the `manifest.json` file in the `<head>` section of your HTML. If you're using the `app` directory, you can add it to your `layout.js` or a specific page's `head` component. If you're using the `pages` directory, it would typically go into `pages/_document.js`.

    ```javascript
    // In app/layout.js or a similar component
    import './styles/globals.css'; // Your global styles

    export default function RootLayout({ children }) {
      return (
        <html lang="en">
          <head>
            <link rel="manifest" href="/manifest.json" />
            {/* Other head elements */}
          </head>
          <body>{children}</body>
        </html>
      );
    }
    ```

5.  **Redeploy Frontend**: After implementing these changes, rebuild and redeploy your Next.js frontend application to AWS Amplify.

    ```bash
    npm run build
    # Then deploy via Amplify Console or CLI as per your setup
    ```

By following these instructions, the `manifest.json` file will be correctly generated and served, resolving the 404 error and enabling PWA features for your application.

## Summary of Actions:

1.  **Backend (Vercel)**: Implement CORS handling using `flask-cors` to allow requests from `https://main.d2wy4w2nf9bgxx.amplifyapp.com`.
2.  **Backend (Vercel)**: Investigate and debug the `401 Unauthorized` error for the `/api/v2/analyze/guest` endpoint, ensuring it allows unauthenticated access as intended.
3.  **Frontend (AWS Amplify)**: Configure Next.js to generate and serve `manifest.json` using `next-pwa` and create the necessary manifest file and icons.

These steps will address the critical communication issues between your frontend and backend, and enhance the overall user experience by enabling PWA features. Once these changes are implemented, thoroughly test the skin analysis functionality to ensure all issues are resolved.

