import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

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