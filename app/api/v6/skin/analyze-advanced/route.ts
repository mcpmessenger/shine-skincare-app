import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  try {
    // Get the request body as JSON
    const requestBody = await request.json();
    
    // Check if image data is provided
    const imageData = requestBody.image_data || requestBody.image;
    if (!imageData) {
      return NextResponse.json(
        { 
          error: 'Missing image data (image_data or image field required)',
          fallback_available: true
        },
        { status: 400 }
      );
    }

    // Get the backend URL from environment or use default
    const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || 'https://api.shineskincollective.com';
    
    try {
      // Forward the request to the Flask backend Advanced endpoint
      console.log(`Attempting to connect to Flask backend at: ${backendUrl}/api/v6/skin/analyze-advanced`);
      
      // Prepare request body for backend
      const backendRequestBody = {
        image: imageData
      };
      
      const response = await fetch(`${backendUrl}/api/v6/skin/analyze-advanced`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(backendRequestBody),
        // Add timeout for ML analysis
        signal: AbortSignal.timeout(30000) // 30 second timeout
      });

      if (response.ok) {
        console.log(`Advanced backend responded successfully`);
        const result = await response.json();
        
        // Add frontend metadata
        result.frontend_metadata = {
          endpoint: '/api/v6/skin/analyze-advanced',
          timestamp: new Date().toISOString(),
          proxy_to_backend: true,
          model_version: 'Advanced_v1.0',
          analysis_type: 'advanced_skin_analysis'
        };
        
        return NextResponse.json(result);
      } else {
        // If Flask backend fails, provide a fallback response
        console.log(`Advanced backend returned ${response.status}, using fallback`);
        return NextResponse.json(
          { 
            error: 'Backend Advanced service unavailable',
            fallback_available: true,
            status: 'error',
            analysis_type: 'advanced_skin_analysis',
            model_info: {
              version: 'Advanced_v1.0',
              training_data: 'SCIN (340) + UTKFace (1,995)',
              model_size: '2.4M parameters',
              features: '468 MediaPipe landmarks + image quality metrics'
            },
            result: {
              detected_conditions: [],
              primary_condition: 'unknown',
              confidence: 0.0,
              severity: 'unknown',
              skin_health_score: 0.0
            },
            guidance: {
              message: 'Advanced analysis service temporarily unavailable',
              suggestions: [
                'Please try again later',
                'Check backend service status',
                'Ensure ML model is loaded'
              ]
            },
            frontend_metadata: {
              endpoint: '/api/v6/skin/analyze-advanced',
              timestamp: new Date().toISOString(),
              proxy_to_backend: false,
              fallback_used: true
            }
          },
          { status: 200 } // Return 200 with fallback data instead of 500
        );
      }
    } catch (fetchError) {
      console.error('Error connecting to backend:', fetchError);
      
      // Return fallback response if backend is unreachable
      return NextResponse.json(
        { 
          error: 'Backend service unreachable',
          fallback_available: true,
          status: 'error',
          analysis_type: 'advanced_skin_analysis',
          model_info: {
            version: 'Advanced_v1.0',
            training_data: 'SCIN (340) + UTKFace (1,995)',
            model_size: '2.4M parameters',
            features: '468 MediaPipe landmarks + image quality metrics'
          },
          result: {
            detected_conditions: [],
            primary_condition: 'unknown',
            confidence: 0.0,
            severity: 'unknown',
            skin_health_score: 0.0
          },
          guidance: {
            message: 'Advanced analysis service currently unavailable',
            suggestions: [
              'Please try again later',
              'Check your internet connection',
              'Ensure backend service is running'
            ]
          },
          frontend_metadata: {
            endpoint: '/api/v6/skin/analyze-advanced',
            timestamp: new Date().toISOString(),
            proxy_to_backend: false,
            fallback_used: true,
            error: fetchError instanceof Error ? fetchError.message : 'Unknown error'
          }
        },
        { status: 200 }
      );
    }
  } catch (error) {
    console.error('Error in advanced skin analysis API:', error);
    
    return NextResponse.json(
      { 
        error: 'Internal server error',
        status: 'error',
        analysis_type: 'advanced_skin_analysis',
        frontend_metadata: {
          endpoint: '/api/v6/skin/analyze-advanced',
          timestamp: new Date().toISOString(),
          proxy_to_backend: false,
          fallback_used: false,
          error: error instanceof Error ? error.message : 'Unknown error'
        }
      },
      { status: 500 }
    );
  }
}
