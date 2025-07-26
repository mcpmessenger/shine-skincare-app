import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    return NextResponse.json({
      message: 'Environment test',
      environment: {
        googleClientId: process.env.GOOGLE_CLIENT_ID ? 'SET' : 'NOT SET',
        googleClientSecret: process.env.GOOGLE_CLIENT_SECRET ? 'SET' : 'NOT SET',
        vercelUrl: process.env.NEXT_PUBLIC_VERCEL_URL || 'NOT SET',
        nodeEnv: process.env.NODE_ENV,
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Test failed', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 