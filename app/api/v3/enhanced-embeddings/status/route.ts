import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  try {
    // Get the backend URL from environment or use default
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://shine-backend-light.eba-ueb7him5.us-east-1.elasticbeanstalk.com';
    
    // Get status from the Flask backend
    const response = await fetch(`${backendUrl}/api/v3/enhanced-embeddings/status`, {
      method: 'GET',
    });

    if (!response.ok) {
      return NextResponse.json(
        { 
          error: 'Failed to get enhanced embeddings status',
          status: 'unavailable'
        },
        { status: response.status }
      );
    }

    const result = await response.json();
    
    // Add frontend metadata
    result.frontend_metadata = {
      endpoint: '/api/v3/enhanced-embeddings/status',
      timestamp: new Date().toISOString(),
      frontend_available: true
    };
    
    return NextResponse.json(result);

  } catch (error) {
    console.error('Enhanced embeddings status error:', error);
    return NextResponse.json(
      { 
        error: 'Internal server error',
        status: 'unavailable'
      },
      { status: 500 }
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, { status: 200 });
} 