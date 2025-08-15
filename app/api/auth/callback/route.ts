import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  // Add CORS headers
  const response = NextResponse.next();
  response.headers.set('Access-Control-Allow-Origin', '*');
  response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // Handle preflight requests
  if (request.method === 'OPTIONS') {
    return new NextResponse(null, { status: 200, headers: response.headers });
  }

  try {
    const { code, state } = await request.json();

    if (!code || !state) {
      return NextResponse.json(
        { error: 'Missing code or state parameter' },
        { 
          status: 400,
          headers: response.headers
        }
      );
    }

    // Check if environment variables are available
    const googleClientId = process.env.GOOGLE_CLIENT_ID;
    const googleClientSecret = process.env.GOOGLE_CLIENT_SECRET;

    if (!googleClientId || !googleClientSecret) {
      return NextResponse.json({
        message: 'OAuth service not configured',
        error: 'Missing Google OAuth configuration',
        googleClientId: !!googleClientId,
        googleClientSecret: !!googleClientSecret
      }, { 
        status: 503,
        headers: response.headers
      });
    }

    // Exchange authorization code for tokens
    const redirectUri = `${process.env.NEXT_PUBLIC_VERCEL_URL || 'https://shine-skincare-1p3y4ew46-williamtflynn-2750s-projects.vercel.app'}/auth/callback`;
    
    const tokenResponse = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        client_id: googleClientId,
        client_secret: googleClientSecret,
        code: code,
        grant_type: 'authorization_code',
        redirect_uri: redirectUri,
      }),
    });

    if (!tokenResponse.ok) {
      const errorData = await tokenResponse.text();
      console.error('Token exchange failed:', errorData);
      return NextResponse.json(
        { error: 'Failed to exchange authorization code for tokens' },
        { 
          status: 400,
          headers: response.headers
        }
      );
    }

    const tokens = await tokenResponse.json();

    // Get user info from Google
    const userInfoResponse = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
      headers: {
        'Authorization': `Bearer ${tokens.access_token}`,
      },
    });

    if (!userInfoResponse.ok) {
      return NextResponse.json(
        { error: 'Failed to get user information from Google' },
        { 
          status: 400,
          headers: response.headers
        }
      );
    }

    const userInfo = await userInfoResponse.json();

    // Create a simple JWT-like token (in production, use a proper JWT library)
    const accessToken = Buffer.from(JSON.stringify({
      sub: userInfo.id,
      email: userInfo.email,
      name: userInfo.name,
      picture: userInfo.picture,
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + 3600, // 1 hour
    })).toString('base64');

    return NextResponse.json({
      access_token: accessToken,
      refresh_token: tokens.refresh_token || 'mock_refresh_token_' + Date.now(),
      user_profile: {
        id: userInfo.id,
        email: userInfo.email,
        name: userInfo.name,
        profile_picture_url: userInfo.picture,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      user_info: {
        id: userInfo.id,
        email: userInfo.email,
        name: userInfo.name,
        picture: userInfo.picture,
        access_token: accessToken
      },
      expires_in: 3600,
      environment: {
        googleClientId: googleClientId ? 'SET' : 'NOT SET',
        googleClientSecret: googleClientSecret ? 'SET' : 'NOT SET'
      }
    }, {
      headers: response.headers
    });
  } catch (error) {
    console.error('OAuth callback error:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error instanceof Error ? error.message : 'Unknown error' },
      { 
        status: 500,
        headers: response.headers
      }
    );
  }
} 