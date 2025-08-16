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
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'https://api.shineskincollective.com';
    
    try {
      // Add detailed logging for debugging
      console.log('🧠 Fixed ML Analysis - Starting...');
      console.log('Backend URL:', `${backendUrl}/api/v5/skin/analyze-fixed`);
      console.log('Request payload size:', JSON.stringify(requestBody).length);
      
      // Convert base64 image data to Blob for form data
      const imageData = requestBody.image_data;
      const imageBlob = new Blob([Buffer.from(imageData, 'base64')], { type: 'image/jpeg' });
      
      // Create FormData for the Flask backend
      const formData = new FormData();
      formData.append('image', imageBlob, 'image.jpg');
      
      // Add user demographics if provided
      if (requestBody.user_demographics) {
        formData.append('demographics', JSON.stringify(requestBody.user_demographics));
      }
      
      // Forward the request to the Flask backend with fixed ML model
      const response = await fetch(`${backendUrl}/api/v5/skin/analyze-fixed`, {
        method: 'POST',
        body: formData,
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
          fixed_ml_model: true,
          model_version: 'fixed_v1.0',
          accuracy: '62.50%'
        };
        
        console.log('✅ Fixed ML analysis completed successfully');
        return NextResponse.json(result);
      } else {
        // If Flask backend fails, provide a fallback response
        console.log('❌ Fixed ML backend failed with status:', response.status);
        const errorText = await response.text();
        console.log('Backend error response:', errorText);
        
        return NextResponse.json(
          { 
            error: 'Fixed ML backend service unavailable',
            fallback_available: true,
            status: 'error',
            message: 'Fixed ML model not available, please try again later',
            timestamp: new Date().toISOString(),
            model_version: 'fixed_v1.0',
            expected_accuracy: '62.50%'
          },
          { status: 503 }
        );
      }

    } catch (error) {
      console.error('Fixed ML analysis error:', error);
      return NextResponse.json(
        { 
          error: 'Fixed ML analysis failed',
          fallback_available: true,
          status: 'error',
          message: 'Fixed ML model temporarily unavailable',
          timestamp: new Date().toISOString(),
          model_version: 'fixed_v1.0'
        },
        { status: 500 }
      );
    }

  } catch (error) {
    console.error('Fixed ML route error:', error);
    return NextResponse.json(
      { 
        error: 'Internal server error',
        fallback_available: true,
        status: 'error',
        message: 'Failed to process fixed ML analysis request',
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
