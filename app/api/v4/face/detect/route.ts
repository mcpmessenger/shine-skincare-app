import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://shine-backend-prod.eba-bfx39wvr.us-east-1.elasticbeanstalk.com';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    console.log('🔄 Face detection proxy - Backend URL:', BACKEND_URL);
    console.log('🔄 Face detection proxy - Request body keys:', Object.keys(body));
    
    const response = await fetch(`${BACKEND_URL}/api/v4/face/detect`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    
    console.log('✅ Face detection proxy - Backend response status:', response.status);
    console.log('✅ Face detection proxy - Backend response:', data);
    
    return NextResponse.json(data, { 
      status: response.status,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      }
    });
  } catch (error) {
    console.error('Face detection proxy error:', error);
    return NextResponse.json(
      { error: 'Face detection failed', details: error }, 
      { status: 500 }
    );
  }
}

export async function OPTIONS() {
  return NextResponse.json({}, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
