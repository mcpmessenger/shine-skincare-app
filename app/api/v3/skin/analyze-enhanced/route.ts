import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    
    // Get the backend URL from environment or use default
    const backendUrl = process.env.BACKEND_URL || 'http://SHINE-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com';
    
    // Forward the request to the Flask backend
    const response = await fetch(`${backendUrl}/api/v3/skin/analyze-enhanced`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { error: errorData.error || 'Analysis failed' },
        { status: response.status }
      );
    }

    const result = await response.json();
    return NextResponse.json(result);

  } catch (error) {
    console.error('Enhanced skin analysis error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, { status: 200 });
} 