import { NextRequest, NextResponse } from "next/server";
import http from 'http';

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  try {
    // Get the request body as JSON
    const requestBody = await request.json();
    
    // Check if image_data is provided
    if (!requestBody.image_data) {
      return NextResponse.json(
        { 
          error: 'Missing image_data',
          fallback_available: true
        },
        { status: 400 }
      );
    }

    // Get the backend URL from environment or use default
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:5000';
    
    try {
      // First try to forward the request to the Flask backend
      console.log(`🔍 Attempting to connect to Flask backend at: ${backendUrl}/api/v3/face/detect`);
      
      // Use direct HTTP request instead of fetch
      const url = new URL(`${backendUrl}/api/v3/face/detect`);
      const postData = JSON.stringify(requestBody);
      
      console.log(`🔍 URL parsed: hostname=${url.hostname}, port=${url.port}, path=${url.pathname}`);
      
      const response = await new Promise((resolve, reject) => {
        const req = http.request({
          hostname: url.hostname,
          port: url.port,
          path: url.pathname,
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(postData)
          }
        }, (res) => {
          console.log(`🔍 HTTP response received: status=${res.statusCode}`);
          let data = '';
          res.on('data', (chunk) => {
            data += chunk;
          });
          res.on('end', () => {
            console.log(`🔍 Response data: ${data.substring(0, 100)}`);
            resolve({
              ok: res.statusCode >= 200 && res.statusCode < 300,
              status: res.statusCode,
              json: () => JSON.parse(data)
            });
          });
        });
        
        req.on('error', (err) => {
          console.log(`❌ HTTP request error: ${err.message}`);
          reject(err);
        });
        
        req.write(postData);
        req.end();
      });

      if (response.ok) {
        console.log(`✅ Flask backend responded successfully`);
        const result = await response.json();
        
        // Add frontend metadata
        result.frontend_metadata = {
          endpoint: '/api/v3/face/detect',
          timestamp: new Date().toISOString(),
          proxy_to_backend: true
        };
        
        return NextResponse.json(result);
      } else {
        // If Flask backend fails, provide a fallback response
        console.log(`Flask backend returned ${response.status}, using fallback`);
        return NextResponse.json(
          { 
            error: 'Backend service unavailable',
            fallback_available: true,
            face_detected: false,
            face_bounds: { x: 0, y: 0, width: 0, height: 0 },
            confidence: 0.0,
            quality_metrics: {
              lighting: 'unknown',
              sharpness: 'unknown',
              positioning: 'unknown'
            },
            guidance: {
              message: 'Face detection service temporarily unavailable',
              suggestions: [
                'Please try again later',
                'Ensure your face is clearly visible',
                'Check lighting conditions'
              ]
            },
            frontend_metadata: {
              endpoint: '/api/v3/face/detect',
              timestamp: new Date().toISOString(),
              proxy_to_backend: false,
              fallback_used: true
            }
          },
          { status: 200 } // Return 200 with fallback data instead of 500
        );
      }
    } catch (fetchError) {
      // If fetch fails (backend not running), provide fallback
      console.log(`❌ Flask backend connection failed: ${fetchError.message}, using fallback`);
      return NextResponse.json(
        { 
          error: 'Backend service unavailable',
          fallback_available: true,
          face_detected: false,
          face_bounds: { x: 0, y: 0, width: 0, height: 0 },
          confidence: 0.0,
          quality_metrics: {
            lighting: 'unknown',
            sharpness: 'unknown',
            positioning: 'unknown'
          },
          guidance: {
            message: 'Face detection service temporarily unavailable',
            suggestions: [
              'Please try again later',
              'Ensure your face is clearly visible',
              'Check lighting conditions'
            ]
          },
          frontend_metadata: {
            endpoint: '/api/v3/face/detect',
            timestamp: new Date().toISOString(),
            proxy_to_backend: false,
            fallback_used: true
          }
        },
        { status: 200 } // Return 200 with fallback data instead of 500
      );
    }

  } catch (error) {
    console.error('Face detection error:', error);
    return NextResponse.json(
      { 
        error: 'Internal server error',
        fallback_available: true,
        face_detected: false,
        face_bounds: { x: 0, y: 0, width: 0, height: 0 },
        confidence: 0.0,
        quality_metrics: {
          lighting: 'unknown',
          sharpness: 'unknown',
          positioning: 'unknown'
        },
        guidance: {
          message: 'Face detection failed',
          suggestions: [
            'Please try again',
            'Check your internet connection',
            'Ensure image data is valid'
          ]
        },
        frontend_metadata: {
          endpoint: '/api/v3/face/detect',
          timestamp: new Date().toISOString(),
          proxy_to_backend: false,
          fallback_used: true
        }
      },
      { status: 200 } // Return 200 with fallback data instead of 500
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, { status: 200 });
} 