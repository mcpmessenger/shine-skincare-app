import { createSupabaseServerClient } from '@/lib/supabase'
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const supabase = createSupabaseServerClient()
    
    // Test basic connection
    const { data: products, error: productsError } = await supabase
      .from('products')
      .select('*')
      .limit(5)
    
    if (productsError) {
      return NextResponse.json({
        success: false,
        error: 'Database connection failed',
        details: productsError.message
      }, { status: 500 })
    }
    
    // Test user table structure
    const { data: users, error: usersError } = await supabase
      .from('users')
      .select('id, email, name')
      .limit(1)
    
    return NextResponse.json({
      success: true,
      message: 'Supabase connection successful',
      data: {
        productsCount: products?.length || 0,
        usersCount: users?.length || 0,
        sampleProducts: products?.slice(0, 2) || []
      }
    })
    
  } catch (error) {
    console.error('Supabase test error:', error)
    return NextResponse.json({
      success: false,
      error: 'Unexpected error',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
} 