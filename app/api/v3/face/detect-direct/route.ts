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
    const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || 'https://shineskincollective.com';
    
    console.log(`🔍 Direct connection to backend at: ${backendUrl}/api/v3/face/detect`);
    
    try {
      // Direct connection to backend
      const response = await fetch(`${backendUrl}/api/v3/face/detect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(requestBody),
        signal: AbortSignal.timeout(15000) // 15 second timeout
      });

      console.log(`🔍 Backend response status: ${response.status}`);

      if (response.ok) {
        const result = await response.json();
        console.log(`✅ Backend response:`, result);
        
        // Add frontend metadata
        result.frontend_metadata = {
          endpoint: '/api/v3/face/detect-direct',
          timestamp: new Date().toISOString(),
          proxy_to_backend: true,
          method: 'direct'
        };
        
        return NextResponse.json(result);
      } else {
        console.log(`❌ Backend returned error status: ${response.status}`);
        const errorText = await response.text();
        console.log(`❌ Backend error response:`, errorText);
        
        return NextResponse.json(
          { 
            error: `Backend returned ${response.status}`,
            backend_error: errorText,
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
              message: 'Backend connection failed',
              suggestions: [
                'Check if backend server is running',
                'Verify network connectivity',
                'Check backend logs for errors'
              ]
            },
            frontend_metadata: {
              endpoint: '/api/v3/face/detect-direct',
              timestamp: new Date().toISOString(),
              proxy_to_backend: false,
              fallback_used: true,
              method: 'direct'
            }
          },
          { status: 200 }
        );
      }
    } catch (fetchError) {
      const errorMessage = fetchError instanceof Error ? fetchError.message : 'Unknown error';
      console.log(`❌ Direct backend connection failed: ${errorMessage}`);
      console.log(`❌ Error details:`, fetchError);
      console.log(`❌ Backend URL: ${backendUrl}`);
      
      return NextResponse.json(
        { 
          error: 'Direct backend connection failed',
          error_details: errorMessage,
          backend_url: backendUrl,
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
            message: 'Direct backend connection failed',
            suggestions: [
              'Backend server may not be running',
              'Check network connectivity',
              'Verify backend URL configuration'
            ]
          },
          frontend_metadata: {
            endpoint: '/api/v3/face/detect-direct',
            timestamp: new Date().toISOString(),
            proxy_to_backend: false,
            fallback_used: true,
            method: 'direct'
          }
        },
        { status: 200 }
      );
    }

  } catch (error) {
    console.error('Direct face detection error:', error);
    return NextResponse.json(
      { 
        error: 'Internal server error',
        error_details: error instanceof Error ? error.message : 'Unknown error',
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
          message: 'Internal server error',
          suggestions: [
            'Please try again',
            'Check server logs',
            'Contact support if issue persists'
          ]
        },
        frontend_metadata: {
          endpoint: '/api/v3/face/detect-direct',
          timestamp: new Date().toISOString(),
          proxy_to_backend: false,
          fallback_used: true,
          method: 'direct'
        }
      },
      { status: 200 }
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, { status: 200 });
} 