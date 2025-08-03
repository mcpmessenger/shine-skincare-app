import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder.supabase.co'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'placeholder-key'

// Only create client if we have valid credentials
export const supabase = supabaseUrl !== 'https://placeholder.supabase.co' && supabaseAnonKey !== 'placeholder-key'
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null

// Database types for TypeScript
export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          id: string
          email: string
          name: string
          profile_picture_url?: string
          created_at: string
          updated_at: string
          last_login_at?: string
          is_active: boolean
          subscription_tier: string
          google_id?: string
        }
        Insert: {
          id?: string
          email: string
          name: string
          profile_picture_url?: string
          created_at?: string
          updated_at?: string
          last_login_at?: string
          is_active?: boolean
          subscription_tier?: string
          google_id?: string
        }
        Update: {
          id?: string
          email?: string
          name?: string
          profile_picture_url?: string
          created_at?: string
          updated_at?: string
          last_login_at?: string
          is_active?: boolean
          subscription_tier?: string
          google_id?: string
        }
      }
      carts: {
        Row: {
          id: string
          user_id: string
          items: any[] // JSON array of cart items
          total: number
          created_at: string
          updated_at: string
          is_abandoned: boolean
          abandoned_at?: string
          email_sent_count: number
          last_email_sent_at?: string
        }
        Insert: {
          id?: string
          user_id: string
          items: any[]
          total: number
          created_at?: string
          updated_at?: string
          is_abandoned?: boolean
          abandoned_at?: string
          email_sent_count?: number
          last_email_sent_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          items?: any[]
          total?: number
          created_at?: string
          updated_at?: string
          is_abandoned?: boolean
          abandoned_at?: string
          email_sent_count?: number
          last_email_sent_at?: string
        }
      }
      abandoned_carts: {
        Row: {
          id: string
          user_id: string
          user_email: string
          user_name: string
          cart_items: any[]
          cart_total: number
          abandoned_at: string
          email_sent_count: number
          last_email_sent_at?: string
          next_email_scheduled_at?: string
          is_recovered: boolean
          recovered_at?: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          user_email: string
          user_name: string
          cart_items: any[]
          cart_total: number
          abandoned_at: string
          email_sent_count?: number
          last_email_sent_at?: string
          next_email_scheduled_at?: string
          is_recovered?: boolean
          recovered_at?: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          user_email?: string
          user_name?: string
          cart_items?: any[]
          cart_total?: number
          abandoned_at?: string
          email_sent_count?: number
          last_email_sent_at?: string
          next_email_scheduled_at?: string
          is_recovered?: boolean
          recovered_at?: string
          created_at?: string
          updated_at?: string
        }
      }
      email_campaigns: {
        Row: {
          id: string
          user_id: string
          user_email: string
          campaign_type: string // 'abandoned_cart', 'welcome', 'recommendations'
          subject: string
          content: string
          sent_at: string
          opened_at?: string
          clicked_at?: string
          unsubscribed_at?: string
          created_at: string
        }
        Insert: {
          id?: string
          user_id: string
          user_email: string
          campaign_type: string
          subject: string
          content: string
          sent_at: string
          opened_at?: string
          clicked_at?: string
          unsubscribed_at?: string
          created_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          user_email?: string
          campaign_type?: string
          subject?: string
          content?: string
          sent_at?: string
          opened_at?: string
          clicked_at?: string
          unsubscribed_at?: string
          created_at?: string
        }
      }
      images: {
        Row: {
          id: string
          user_id: string
          image_url: string
          faiss_index_id?: number
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          image_url: string
          faiss_index_id?: number
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          image_url?: string
          faiss_index_id?: number
          created_at?: string
          updated_at?: string
        }
      }
      analyses: {
        Row: {
          id: string
          image_id: string
          google_vision_result: any
          created_at: string
        }
        Insert: {
          id?: string
          image_id: string
          google_vision_result: any
          created_at?: string
        }
        Update: {
          id?: string
          image_id?: string
          google_vision_result?: any
          created_at?: string
        }
      }
      medical_analyses: {
        Row: {
          id: string
          user_id: string
          image_id: string
          condition_identified: string
          confidence_score: number
          detailed_description: string
          recommended_treatments: string[]
          similar_conditions: any[]
          created_at: string
        }
        Insert: {
          id?: string
          user_id: string
          image_id: string
          condition_identified: string
          confidence_score: number
          detailed_description: string
          recommended_treatments: string[]
          similar_conditions: any[]
          created_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          image_id?: string
          condition_identified?: string
          confidence_score?: number
          detailed_description?: string
          recommended_treatments?: string[]
          similar_conditions?: any[]
          created_at?: string
        }
      }
    }
  }
} 