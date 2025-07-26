import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const skinType = searchParams.get('skinType');
    const concerns = searchParams.get('concerns');

    // For now, return mock recommendations
    // We'll integrate with product database later
    return NextResponse.json({
      message: 'Recommendations endpoint ready',
      recommendations: [
        {
          id: 1,
          name: 'Gentle Foaming Cleanser',
          brand: 'CeraVe',
          price: 15.99,
          category: 'cleanser',
          skinType: ['dry', 'sensitive'],
          concerns: ['acne', 'irritation']
        },
        {
          id: 2,
          name: 'Daily Moisturizer with SPF 30',
          brand: 'Neutrogena',
          price: 22.99,
          category: 'moisturizer',
          skinType: ['all'],
          concerns: ['sun damage', 'aging']
        }
      ]
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 