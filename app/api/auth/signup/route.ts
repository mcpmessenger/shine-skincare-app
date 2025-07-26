import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  try {
    const { email, password, name } = await request.json();

    // For now, return a mock response
    // We'll integrate with Supabase later
    return NextResponse.json({
      message: 'Signup endpoint ready',
      email,
      name
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 