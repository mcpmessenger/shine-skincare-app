import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  try {
    // Get the request body as JSON
    const requestBody = await request.json();
    
    // Check if image data is provided (accept both field names)
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

    // Get the backend URL from environment or use localhost for development
    const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    
    try {
      // Forward the request to the Flask backend Hare Run V6 endpoint
      console.log(`🔍 Attempting to connect to Flask backend at: ${backendUrl}/api/v6/skin/analyze-hare-run`);
      
      // Prepare request body for backend (use image_data field to match backend expectations)
      const backendRequestBody = {
        image_data: imageData
      };
      
      const response = await fetch(`${backendUrl}/api/v6/skin/analyze-hare-run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(backendRequestBody),
        // Add timeout and better error handling
        signal: AbortSignal.timeout(30000) // 30 second timeout for ML analysis
      });

      if (response.ok) {
        console.log(`✅ Hare Run V6 backend responded successfully`);
        const result = await response.json();
        
        // Add frontend metadata
        result.frontend_metadata = {
          endpoint: '/api/v6/skin/analyze-hare-run',
          timestamp: new Date().toISOString(),
          proxy_to_backend: true
        };
        
        return NextResponse.json(result);
      } else {
        // If Flask backend fails, provide a fallback response
        console.log(`Hare Run V6 backend returned ${response.status}, using fallback`);
        return NextResponse.json(
          { 
            error: 'Backend Hare Run V6 service unavailable',
            fallback_available: true,
            status: 'error',
            analysis_type: 'hare_run_v6_facial',
            model_info: {
              version: 'Hare_Run_V6_Facial_v1.0',
              accuracy: '97.13%',
              classes: 8,
              model_size: '128MB'
            },
            result: {
              detected_conditions: [],
              primary_condition: 'unknown',
              confidence: 0.0,
              severity: 'unknown'
            },
            guidance: {
              message: 'Hare Run V6 analysis service temporarily unavailable',
              suggestions: [
                'Please try again later',
                'Check backend service status',
                'Ensure ML model is loaded'
              ]
            },
            frontend_metadata: {
              endpoint: '/api/v6/skin/analyze-hare-run',
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
      console.log(`❌ Hare Run V6 backend connection failed: ${errorMessage}, using fallback`);
      console.log(`❌ Error details:`, fetchError);
      console.log(`❌ Backend URL: ${backendUrl}`);
      return NextResponse.json(
        { 
          error: 'Backend Hare Run V6 service unavailable',
          fallback_available: true,
          status: 'error',
          analysis_type: 'hare_run_v6_facial',
          model_info: {
            version: 'Hare_Run_V6_Facial_v1.0',
            accuracy: '97.13%',
            classes: 8,
            model_size: '128MB'
          },
          result: {
            detected_conditions: [],
            primary_condition: 'unknown',
            confidence: 0.0,
            severity: 'unknown'
          },
          guidance: {
            message: 'Hare Run V6 analysis service temporarily unavailable',
            suggestions: [
              'Please try again later',
              'Check backend service status',
              'Ensure ML model is loaded'
            ]
          },
          frontend_metadata: {
            endpoint: '/api/v6/skin/analyze-hare-run',
            timestamp: new Date().toISOString(),
            proxy_to_backend: false,
            fallback_used: true
          }
        },
        { status: 200 } // Return 200 with fallback data instead of 500
      );
    }

  } catch (error) {
    console.error('Hare Run V6 analysis error:', error);
    return NextResponse.json(
      { 
        error: 'Internal server error',
        fallback_available: true,
        status: 'error',
        analysis_type: 'hare_run_v6_facial',
        model_info: {
          version: 'Hare_Run_V6_Facial_v1.0',
          accuracy: '97.13%',
          classes: 8,
          model_size: '128MB'
        },
        result: {
          detected_conditions: [],
          primary_condition: 'unknown',
          confidence: 0.0,
          severity: 'unknown'
        },
        guidance: {
          message: 'Hare Run V6 analysis failed',
          suggestions: [
            'Please try again',
            'Check your internet connection',
            'Ensure image data is valid'
          ]
        },
        frontend_metadata: {
          endpoint: '/api/v6/skin/analyze-hare-run',
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
