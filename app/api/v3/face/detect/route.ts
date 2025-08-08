import { NextRequest, NextResponse } from "next/server";

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
    // Force use port 5000 since backend is running there
    const backendUrl = 'http://localhost:5000';
    
    try {
      // First try to forward the request to the Flask backend
      console.log(`🔍 Attempting to connect to Flask backend at: ${backendUrl}/api/v3/face/detect`);
      
      const response = await fetch(`${backendUrl}/api/v3/face/detect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(requestBody),
        // Add timeout and better error handling
        signal: AbortSignal.timeout(10000) // 10 second timeout
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
      const errorMessage = fetchError instanceof Error ? fetchError.message : 'Unknown error';
      console.log(`❌ Flask backend connection failed: ${errorMessage}, using fallback`);
      console.log(`❌ Error details:`, fetchError);
      console.log(`❌ Backend URL: ${backendUrl}`);
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