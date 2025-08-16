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
    const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || 'https://api.shineskincollective.com';
    
    try {
      // Add detailed logging for debugging
      console.log('🔍 Basic Analysis Proxy Debug');
      console.log('Backend URL:', `${backendUrl}/api/v3/skin/analyze-basic`);
      console.log('Request payload size:', JSON.stringify(requestBody).length);
      console.log('Request payload keys:', Object.keys(requestBody));
      
      // Log face detection result if provided
      if (requestBody.face_detection_result) {
        console.log('Frontend sending face_detection_result:', requestBody.face_detection_result);
      }
      
      // First try to forward the request to the Flask backend
      const response = await fetch(`${backendUrl}/api/v3/skin/analyze-basic`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
        // Add timeout to prevent hanging requests
        signal: AbortSignal.timeout(30000) // 30 second timeout
      });

      console.log('Backend response status:', response.status);
      console.log('Backend response headers:', Object.fromEntries(response.headers.entries()));

      if (response.ok) {
        const result = await response.json();
        
        // Add frontend metadata
        result.frontend_metadata = {
          endpoint: '/api/v3/skin/analyze-basic',
          timestamp: new Date().toISOString(),
          enhanced_system: true,
          proxy_to_backend: true
        };
        
        console.log('✅ Successfully proxied to backend');
        return NextResponse.json(result);
      } else {
        // If Flask backend fails, provide a fallback response
        console.log('❌ Flask backend failed with status:', response.status);
        const errorText = await response.text();
        console.log('Backend error response:', errorText);
        console.log('Flask backend unavailable, using fallback for basic analysis');
        return NextResponse.json(
          { 
            error: 'Analysis service temporarily unavailable',
            fallback_available: true,
            status: 'success',
            timestamp: new Date().toISOString(),
            analysis_type: 'basic',
            face_detection: {
              detected: false,
              confidence: 0.0,
              face_bounds: { x: 0, y: 0, width: 0, height: 0 },
              method: 'fallback',
              quality_metrics: {
                overall_quality: 'unknown',
                quality_score: 0.0
              }
            },
            skin_analysis: {
              texture: 'unknown',
              tone: 'unknown',
              conditions_detected: [],
              analysis_confidence: 0.0
            },
            recommendations: {
              immediate_care: ['Service temporarily unavailable'],
              long_term_care: ['Please try again later']
            },
            frontend_metadata: {
              endpoint: '/api/v3/skin/analyze-basic',
              timestamp: new Date().toISOString(),
              enhanced_system: true,
              proxy_to_backend: false,
              fallback_used: true
            }
          },
          { status: 503 }
        );
      }
    } catch (fetchError) {
      // If fetch fails (backend not running), provide fallback
      console.log('❌ Flask backend connection failed:', fetchError);
      console.log('Error type:', typeof fetchError);
      console.log('Error message:', fetchError instanceof Error ? fetchError.message : 'Unknown error');
      console.log('Flask backend connection failed, using fallback for basic analysis');
      return NextResponse.json(
        { 
          error: 'Analysis service temporarily unavailable',
          fallback_available: true,
          status: 'success',
          timestamp: new Date().toISOString(),
          analysis_type: 'basic',
          face_detection: {
            detected: false,
            confidence: 0.0,
            face_bounds: { x: 0, y: 0, width: 0, height: 0 },
            method: 'fallback',
            quality_metrics: {
              overall_quality: 'unknown',
              quality_score: 0.0
            }
          },
          skin_analysis: {
            texture: 'unknown',
            tone: 'unknown',
            conditions_detected: [],
            analysis_confidence: 0.0
          },
          recommendations: {
            immediate_care: ['Service temporarily unavailable'],
            long_term_care: ['Please try again later']
          },
          frontend_metadata: {
            endpoint: '/api/v3/skin/analyze-basic',
            timestamp: new Date().toISOString(),
            enhanced_system: true,
            proxy_to_backend: false,
            fallback_used: true
          }
        },
        { status: 503 }
      );
    }

  } catch (error) {
    console.error('Basic analysis error:', error);
    return NextResponse.json(
      { 
        error: 'Internal server error',
        fallback_available: true,
        status: 'success',
        timestamp: new Date().toISOString(),
        analysis_type: 'basic',
        face_detection: {
          detected: false,
          confidence: 0.0,
          face_bounds: { x: 0, y: 0, width: 0, height: 0 },
          method: 'fallback',
          quality_metrics: {
            overall_quality: 'unknown',
            quality_score: 0.0
          }
        },
        skin_analysis: {
          texture: 'unknown',
          tone: 'unknown',
          conditions_detected: [],
          analysis_confidence: 0.0
        },
        recommendations: {
          immediate_care: ['Service temporarily unavailable'],
          long_term_care: ['Please try again later']
        },
        frontend_metadata: {
          endpoint: '/api/v3/skin/analyze-basic',
          timestamp: new Date().toISOString(),
          enhanced_system: true,
          proxy_to_backend: false,
          fallback_used: true
        }
      },
      { status: 503 }
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, { status: 200 });
} 