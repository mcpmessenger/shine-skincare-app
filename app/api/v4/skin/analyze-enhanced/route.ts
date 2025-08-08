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
      // Add detailed logging for debugging
      console.log('🧠 Enhanced ML Analysis - Starting...');
      console.log('Backend URL:', `${backendUrl}/api/v4/skin/analyze-enhanced`);
      console.log('Request payload size:', JSON.stringify(requestBody).length);
      
              // Forward the request to the Flask backend with enhanced ML model
        const response = await fetch(`${backendUrl}/api/v4/skin/analyze-enhanced`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody),
          // Add timeout to prevent hanging requests
          signal: AbortSignal.timeout(60000) // 60 second timeout for ML processing
        });

      console.log('Backend response status:', response.status);

      if (response.ok) {
        const result = await response.json();
        
        // Add frontend metadata
        result.frontend_metadata = {
          endpoint: '/api/v4/skin/analyze-enhanced',
          timestamp: new Date().toISOString(),
          enhanced_ml_model: true,
          model_version: 'enhanced_v1.0',
          accuracy: '60.2%'
        };
        
        console.log('✅ Enhanced ML analysis completed successfully');
        return NextResponse.json(result);
      } else {
        // If Flask backend fails, provide a fallback response
        console.log('❌ Enhanced ML backend failed with status:', response.status);
        const errorText = await response.text();
        console.log('Backend error response:', errorText);
        
        return NextResponse.json(
          { 
            error: 'Enhanced ML backend service unavailable',
            fallback_available: true,
            status: 'error',
            message: 'Enhanced ML model not available, please try again later',
            timestamp: new Date().toISOString(),
            model_version: 'enhanced_v1.0',
            expected_accuracy: '60.2%'
          },
          { status: 503 }
        );
      }

    } catch (error) {
      console.error('Enhanced ML analysis error:', error);
      return NextResponse.json(
        { 
          error: 'Enhanced ML analysis failed',
          fallback_available: true,
          status: 'error',
          message: 'Enhanced ML model temporarily unavailable',
          timestamp: new Date().toISOString(),
          model_version: 'enhanced_v1.0'
        },
        { status: 500 }
      );
    }

  } catch (error) {
    console.error('Enhanced ML route error:', error);
    return NextResponse.json(
      { 
        error: 'Internal server error',
        fallback_available: true,
        status: 'error',
        message: 'Failed to process enhanced ML analysis request',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}
