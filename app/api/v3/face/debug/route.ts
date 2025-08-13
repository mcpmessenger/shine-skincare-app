import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  try {
    // Get all environment variables
    const envVars = {
      BACKEND_URL: process.env.BACKEND_URL,
      NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
      NODE_ENV: process.env.NODE_ENV,
      PORT: process.env.PORT,
    };
    
    // Test backend connectivity
    const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || 'https://awseb--AWSEB-ydAUJ3jj2fwA-1083929952.us-east-1.elb.amazonaws.com';
    let backendStatus = 'unknown';
    let backendResponse = null;
    
    try {
      const response = await fetch(`${backendUrl}/api/v3/system/health`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
        signal: AbortSignal.timeout(5000)
      });
      
      backendStatus = response.ok ? 'connected' : `error_${response.status}`;
      if (response.ok) {
        backendResponse = await response.json();
      }
    } catch (error) {
      backendStatus = `failed: ${error instanceof Error ? error.message : 'unknown error'}`;
    }
    
    return NextResponse.json({
      environment: envVars,
      backend_url: backendUrl,
      backend_status: backendStatus,
      backend_response: backendResponse,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    return NextResponse.json({
      error: 'Debug route error',
      details: error instanceof Error ? error.message : 'unknown error',
      timestamp: new Date().toISOString()
    }, { status: 500 });
  }
} 