import { NextRequest, NextResponse } from 'next/server'

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
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:5000'
    
    try {
      // Add detailed logging for debugging
      console.log('🔍 Basic Analysis Proxy Debug');
      console.log('Backend URL:', `${backendUrl}/api/v3/skin/analyze-basic`);
      console.log('Request payload size:', JSON.stringify(requestBody).length);
      console.log('Request payload keys:', Object.keys(requestBody));
      
      // Forward the request to the Flask backend
      const response = await fetch(`${backendUrl}/api/v3/skin/analyze-basic`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      })

      console.log('Backend response status:', response.status);
      console.log('Backend response headers:', Object.fromEntries(response.headers.entries()));

      if (response.ok) {
        const data = await response.json()
        
        // Add frontend metadata
        data.frontend_metadata = {
          endpoint: '/api/v3/skin/analyze-basic',
          timestamp: new Date().toISOString(),
          integrated_system: true,
          proxy_to_backend: true
        };
        
        return NextResponse.json(data)
      } else {
        // If Flask backend fails, return a fallback response
        console.error('❌ Flask backend returned', response.status, 'using fallback')
        console.error('Backend error response:', await response.text())
        return NextResponse.json({
          error: 'Analysis service temporarily unavailable',
          fallback: true,
          timestamp: new Date().toISOString()
        }, { status: 503 })
      }
    } catch (fetchError) {
      // If fetch fails (backend not running), provide fallback
      console.error('❌ Flask backend connection failed:', fetchError)
      console.error('Error type:', typeof fetchError)
      console.error('Error message:', fetchError instanceof Error ? fetchError.message : 'Unknown error')
      return NextResponse.json({
        error: 'Analysis service unavailable',
        fallback: true,
        timestamp: new Date().toISOString()
      }, { status: 503 })
    }
  } catch (error) {
    console.error('Basic analysis error:', error)
    return NextResponse.json({
      error: 'Internal server error',
      fallback: true,
      timestamp: new Date().toISOString()
    }, { status: 500 })
  }
} 