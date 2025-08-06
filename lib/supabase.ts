import { createClient } from '@supabase/supabase-js'

// Environment variables with fallbacks for development
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder.supabase.co'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'placeholder-key'
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || 'placeholder-service-key'

// Check if we're in development mode and using placeholder values
const isDevelopment = process.env.NODE_ENV === 'development'
const isUsingPlaceholders = supabaseUrl === 'https://placeholder.supabase.co' || supabaseAnonKey === 'placeholder-key'

// Singleton pattern to prevent multiple instances
let supabaseClient: ReturnType<typeof createClient> | null = null
let supabaseAdminClient: ReturnType<typeof createClient> | null = null

// Client-side Supabase client (singleton)
export const createSupabaseClient = () => {
  if (!supabaseClient) {
    if (isDevelopment && isUsingPlaceholders) {
      console.warn('⚠️ Supabase: Using placeholder values for development. Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY for full functionality.')
    }
    
    supabaseClient = createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        persistSession: true,
        storageKey: 'shine-supabase-auth'
      }
    })
  }
  
  return supabaseClient
}

// Server-side Supabase client (singleton)
export const createSupabaseServerClient = () => {
  if (!supabaseClient) {
    if (isDevelopment && isUsingPlaceholders) {
      console.warn('⚠️ Supabase: Using placeholder values for development. Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY for full functionality.')
    }
    
    supabaseClient = createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        persistSession: false,
        autoRefreshToken: false
      }
    })
  }
  
  return supabaseClient
}

// Default client instance for use in services
export const supabase = createSupabaseClient()

// Admin client for server-side operations (singleton)
export const supabaseAdmin = () => {
  if (!supabaseAdminClient) {
    supabaseAdminClient = createClient(
      supabaseUrl,
      supabaseServiceKey,
      {
        auth: {
          autoRefreshToken: false,
          persistSession: false
        }
      }
    )
  }
  
  return supabaseAdminClient
}

// Helper function to check if Supabase is properly configured
export const isSupabaseConfigured = () => {
  return !isUsingPlaceholders
}

// Database types
export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          id: string
          google_id: string | null
          email: string
          name: string
          profile_picture_url: string | null
          phone_number: string | null
          date_of_birth: string | null
          subscription_tier: 'free' | 'premium' | 'enterprise'
          is_active: boolean
          shipping_address: any | null
          billing_address: any | null
          marketing_preferences: any
          last_login_at: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          google_id?: string | null
          email: string
          name: string
          profile_picture_url?: string | null
          phone_number?: string | null
          date_of_birth?: string | null
          subscription_tier?: 'free' | 'premium' | 'enterprise'
          is_active?: boolean
          shipping_address?: any | null
          billing_address?: any | null
          marketing_preferences?: any
          last_login_at?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          google_id?: string | null
          email?: string
          name?: string
          profile_picture_url?: string | null
          phone_number?: string | null
          date_of_birth?: string | null
          subscription_tier?: 'free' | 'premium' | 'enterprise'
          is_active?: boolean
          shipping_address?: any | null
          billing_address?: any | null
          marketing_preferences?: any
          last_login_at?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      products: {
        Row: {
          id: string
          name: string
          description: string | null
          price: number
          cost_price: number | null
          category: string
          brand: string | null
          sku: string | null
          barcode: string | null
          weight: number | null
          dimensions: any | null
          images: string[] | null
          ingredients: string[] | null
          usage_instructions: string | null
          skin_type_compatibility: string[] | null
          skin_concerns_addressed: string[] | null
          dermatologist_recommended: boolean
          is_active: boolean
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          name: string
          description?: string | null
          price: number
          cost_price?: number | null
          category: string
          brand?: string | null
          sku?: string | null
          barcode?: string | null
          weight?: number | null
          dimensions?: any | null
          images?: string[] | null
          ingredients?: string[] | null
          usage_instructions?: string | null
          skin_type_compatibility?: string[] | null
          skin_concerns_addressed?: string[] | null
          dermatologist_recommended?: boolean
          is_active?: boolean
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          name?: string
          description?: string | null
          price?: number
          cost_price?: number | null
          category?: string
          brand?: string | null
          sku?: string | null
          barcode?: string | null
          weight?: number | null
          dimensions?: any | null
          images?: string[] | null
          ingredients?: string[] | null
          usage_instructions?: string | null
          skin_type_compatibility?: string[] | null
          skin_concerns_addressed?: string[] | null
          dermatologist_recommended?: boolean
          is_active?: boolean
          created_at?: string
          updated_at?: string
        }
      }
      orders: {
        Row: {
          id: string
          user_id: string
          order_number: string
          status: 'pending' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'cancelled' | 'refunded'
          subtotal: number
          tax_amount: number
          shipping_amount: number
          discount_amount: number
          total_amount: number
          currency: string
          payment_status: 'pending' | 'paid' | 'failed' | 'refunded'
          payment_method: string | null
          payment_intent_id: string | null
          shipping_address: any
          billing_address: any
          estimated_delivery_date: string | null
          tracking_number: string | null
          notes: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          order_number: string
          status?: 'pending' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'cancelled' | 'refunded'
          subtotal: number
          tax_amount?: number
          shipping_amount?: number
          discount_amount?: number
          total_amount: number
          currency?: string
          payment_status?: 'pending' | 'paid' | 'failed' | 'refunded'
          payment_method?: string | null
          payment_intent_id?: string | null
          shipping_address: any
          billing_address: any
          estimated_delivery_date?: string | null
          tracking_number?: string | null
          notes?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          order_number?: string
          status?: 'pending' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'cancelled' | 'refunded'
          subtotal?: number
          tax_amount?: number
          shipping_amount?: number
          discount_amount?: number
          total_amount?: number
          currency?: string
          payment_status?: 'pending' | 'paid' | 'failed' | 'refunded'
          payment_method?: string | null
          payment_intent_id?: string | null
          shipping_address?: any
          billing_address?: any
          estimated_delivery_date?: string | null
          tracking_number?: string | null
          notes?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      carts: {
        Row: {
          id: string
          user_id: string | null
          session_id: string | null
          expires_at: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id?: string | null
          session_id?: string | null
          expires_at?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string | null
          session_id?: string | null
          expires_at?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      cart_items: {
        Row: {
          id: string
          cart_id: string
          product_id: string
          quantity: number
          added_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          cart_id: string
          product_id: string
          quantity: number
          added_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          cart_id?: string
          product_id?: string
          quantity?: number
          added_at?: string
          updated_at?: string
        }
      }
    }
  }
}

export type User = Database['public']['Tables']['users']['Row']
export type Product = Database['public']['Tables']['products']['Row']
export type Order = Database['public']['Tables']['orders']['Row']
export type Cart = Database['public']['Tables']['carts']['Row']
export type CartItem = Database['public']['Tables']['cart_items']['Row'] 