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
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:5000';
    
    try {
      // Forward the request to the Flask backend
      const response = await fetch(`${backendUrl}/api/v3/skin/analyze-real-database`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (response.ok) {
        const result = await response.json();
        
        // Add frontend metadata
        result.frontend_metadata = {
          endpoint: '/api/v3/skin/analyze-real-database',
          timestamp: new Date().toISOString(),
          real_database_system: true,
          proxy_to_backend: true
        };
        
        return NextResponse.json(result);
      } else {
        // If Flask backend fails, provide a fallback response
        console.log('Real database backend unavailable, using fallback for skin analysis');
        return NextResponse.json(
          { 
            error: 'Real database service unavailable',
            fallback_available: true,
            status: 'success',
            timestamp: new Date().toISOString(),
            analysis_type: 'real_database_fallback',
            demographics: {
              age_category: null,
              race_category: null
            },
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
              overall_health_score: 0.0,
              texture: 'unknown',
              tone: 'unknown',
              conditions_detected: [],
              analysis_confidence: 0.0
            },
            similarity_search: {
              dataset_used: 'fallback',
              similar_cases: []
            },
            recommendations: {
              immediate_care: ['Real database service temporarily unavailable'],
              long_term_care: ['Please try again later'],
              professional_consultation: false
            },
            quality_assessment: {
              image_quality: 'unknown',
              confidence_reliability: 'low'
            },
            frontend_metadata: {
              endpoint: '/api/v3/skin/analyze-real-database',
              timestamp: new Date().toISOString(),
              real_database_system: true,
              proxy_to_backend: false,
              fallback_used: true
            }
          },
          { status: 200 } // Return 200 with fallback data instead of 500
        );
      }
    } catch (fetchError) {
      // If fetch fails (backend not running), provide fallback
      console.log('Real database backend connection failed, using fallback for skin analysis');
      return NextResponse.json(
        { 
          error: 'Real database service unavailable',
          fallback_available: true,
          status: 'success',
          timestamp: new Date().toISOString(),
          analysis_type: 'real_database_fallback',
          demographics: {
            age_category: null,
            race_category: null
          },
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
            overall_health_score: 0.0,
            texture: 'unknown',
            tone: 'unknown',
            conditions_detected: [],
            analysis_confidence: 0.0
          },
          similarity_search: {
            dataset_used: 'fallback',
            similar_cases: []
          },
          recommendations: {
            immediate_care: ['Real database service temporarily unavailable'],
            long_term_care: ['Please try again later'],
            professional_consultation: false
          },
          quality_assessment: {
            image_quality: 'unknown',
            confidence_reliability: 'low'
          },
          frontend_metadata: {
            endpoint: '/api/v3/skin/analyze-real-database',
            timestamp: new Date().toISOString(),
            real_database_system: true,
            proxy_to_backend: false,
            fallback_used: true
          }
        },
        { status: 200 } // Return 200 with fallback data instead of 500
      );
    }

  } catch (error) {
    console.error('Real database analysis error:', error);
    return NextResponse.json(
      { 
        error: 'Internal server error',
        fallback_available: true,
        status: 'success',
        timestamp: new Date().toISOString(),
        analysis_type: 'real_database_fallback',
        demographics: {
          age_category: null,
          race_category: null
        },
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
          overall_health_score: 0.0,
          texture: 'unknown',
          tone: 'unknown',
          conditions_detected: [],
          analysis_confidence: 0.0
        },
        similarity_search: {
          dataset_used: 'fallback',
          similar_cases: []
        },
        recommendations: {
          immediate_care: ['Real database service temporarily unavailable'],
          long_term_care: ['Please try again later'],
          professional_consultation: false
        },
        quality_assessment: {
          image_quality: 'unknown',
          confidence_reliability: 'low'
        },
        frontend_metadata: {
          endpoint: '/api/v3/skin/analyze-real-database',
          timestamp: new Date().toISOString(),
          real_database_system: true,
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