import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  console.log('Login endpoint called');
  
  try {
    // Add CORS headers
    const response = NextResponse.next();
    response.headers.set('Access-Control-Allow-Origin', '*');
    response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');

    // Handle preflight requests
    if (request.method === 'OPTIONS') {
      return new NextResponse(null, { status: 200, headers: response.headers });
    }

    console.log('Processing POST request');
    
    // Parse request body
    let body;
    try {
      body = await request.json();
      console.log('Request body parsed successfully:', body);
    } catch (parseError) {
      console.error('Failed to parse request body:', parseError);
      return NextResponse.json(
        { error: 'Invalid JSON in request body' },
        { status: 400, headers: response.headers }
      );
    }

    const { client_type } = body;

    // Check environment variables
    const googleClientId = process.env.GOOGLE_CLIENT_ID;
    console.log('Google Client ID check:', googleClientId ? 'SET' : 'NOT SET');

    if (!googleClientId) {
      console.log('Google Client ID is missing');
      return NextResponse.json({
        message: 'OAuth service not configured',
        error: 'Missing Google OAuth configuration',
        googleClientId: false
      }, { 
        status: 503,
        headers: response.headers
      });
    }

    // Generate OAuth state for security
    const state = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    console.log('Generated state:', state);
    
    // Create Google OAuth URL with correct domain
    const redirectUri = `${process.env.NEXT_PUBLIC_VERCEL_URL || 'https://shine-skincare-1p3y4ew46-williamtflynn-2750s-projects.vercel.app'}/auth/callback`;
    const scope = 'openid email profile';
    
    console.log('Redirect URI:', redirectUri);
    
    const authorizationUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
      `client_id=${googleClientId}&` +
      `redirect_uri=${encodeURIComponent(redirectUri)}&` +
      `response_type=code&` +
      `scope=${encodeURIComponent(scope)}&` +
      `state=${state}&` +
      `access_type=offline&` +
      `prompt=consent`;

    console.log('Authorization URL generated successfully');

    const result = {
      authorization_url: authorizationUrl,
      state: state,
      expires_in: 3600,
      environment: {
        googleClientId: true,
        redirectUri: redirectUri
      }
    };

    console.log('Returning successful response');
    return NextResponse.json(result, {
      headers: response.headers
    });

  } catch (error) {
    console.error('Login endpoint error:', error);
    console.error('Error stack:', error instanceof Error ? error.stack : 'No stack trace');
    
    return NextResponse.json(
      { 
        error: 'Internal server error', 
        details: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString()
      },
      { 
        status: 500
      }
    );
  }
} 