import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = searchParams.get('limit') || '3';

    // For now, return mock trending products
    // We'll integrate with product database later
    return NextResponse.json({
      data: [
        {
          id: '1',
          name: 'HydraBoost Serum',
          brand: 'AquaGlow',
          price: 39.99,
          rating: 4.5,
          image_urls: ['/placeholder.svg?height=200&width=300'],
          description: 'A powerful hydrating serum infused with hyaluronic acid and ceramides.',
          category: 'serum',
          subcategory: 'hydrating',
          ingredients: ['Hyaluronic Acid', 'Ceramides', 'Niacinamide'],
          currency: 'USD',
          availability_status: 'available',
          review_count: 127
        },
        {
          id: '2',
          name: 'ClearSkin Acne Treatment',
          brand: 'DermPure',
          price: 24.5,
          rating: 4.0,
          image_urls: ['/placeholder.svg?height=200&width=300'],
          description: 'Target stubborn breakouts with this salicylic acid formula.',
          category: 'treatment',
          subcategory: 'acne',
          ingredients: ['Salicylic Acid', 'Tea Tree Oil', 'Zinc PCA'],
          currency: 'USD',
          availability_status: 'available',
          review_count: 89
        },
        {
          id: '3',
          name: 'Radiance Vitamin C Serum',
          brand: 'GlowEssence',
          price: 45.0,
          rating: 4.8,
          image_urls: ['/placeholder.svg?height=200&width=300'],
          description: 'Brighten and even skin tone with this potent vitamin C serum.',
          category: 'serum',
          subcategory: 'brightening',
          ingredients: ['Vitamin C', 'Ferulic Acid', 'Vitamin E'],
          currency: 'USD',
          availability_status: 'available',
          review_count: 203
        }
      ].slice(0, parseInt(limit)),
      success: true,
      message: 'Trending products retrieved successfully'
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal server error', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 