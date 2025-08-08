import { supabase } from './supabase'
import { CartItem } from '@/hooks/useCart'

export interface CartData {
  id?: string
  user_id: string
  items: CartItem[]
  total: number
  created_at?: string
  updated_at?: string
  is_abandoned?: boolean
  abandoned_at?: string
  email_sent_count?: number
  last_email_sent_at?: string
}

export interface AbandonedCartData {
  id?: string
  user_id: string
  user_email: string
  user_name: string
  cart_items: CartItem[]
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

export class CartService {
  // Save or update user's cart
  static async saveCart(userId: string, items: CartItem[], total: number): Promise<void> {
    if (!supabase) {
      console.warn('Supabase not configured, skipping cart save')
      return
    }

    try {
      const { data: existingCart } = await supabase
        .from('carts')
        .select('id')
        .eq('user_id', userId)
        .eq('is_abandoned', false)
        .single()

      const cartData: CartData = {
        user_id: userId,
        items,
        total,
        updated_at: new Date().toISOString(),
        is_abandoned: false
      }

      if (existingCart) {
        // Update existing cart
        await supabase
          .from('carts')
          .update(cartData as any)
          .eq('id', existingCart.id as string)
      } else {
        // Create new cart
        cartData.created_at = new Date().toISOString()
        await supabase
          .from('carts')
          .insert(cartData as any)
      }
    } catch (error) {
      console.error('Error saving cart:', error)
    }
  }

  // Mark cart as abandoned
  static async markCartAsAbandoned(userId: string, userEmail: string, userName: string): Promise<void> {
    if (!supabase) {
      console.warn('Supabase not configured, skipping abandoned cart tracking')
      return
    }

    try {
      // Get current cart
      const { data: cart } = await supabase
        .from('carts')
        .select('*')
        .eq('user_id', userId)
        .eq('is_abandoned', false)
        .single()

      if (cart && (cart as any).items && (cart as any).items.length > 0) {
        // Mark cart as abandoned
        await supabase
          .from('carts')
          .update({
            is_abandoned: true,
            abandoned_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          })
          .eq('id', cart.id as string)

        // Create abandoned cart record
        const abandonedCartData: AbandonedCartData = {
          user_id: userId,
          user_email: userEmail,
          user_name: userName,
          cart_items: (cart as any).items,
          cart_total: (cart as any).total,
          abandoned_at: new Date().toISOString(),
          email_sent_count: 0,
          is_recovered: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }

        await supabase
          .from('abandoned_carts')
          .insert(abandonedCartData as any)
      }
    } catch (error) {
      console.error('Error marking cart as abandoned:', error)
    }
  }

  // Recover abandoned cart
  static async recoverAbandonedCart(userId: string): Promise<void> {
    if (!supabase) {
      console.warn('Supabase not configured, skipping cart recovery')
      return
    }

    try {
      // Mark abandoned cart as recovered
      await supabase
        .from('abandoned_carts')
        .update({
          is_recovered: true,
          recovered_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        })
        .eq('user_id', userId)
        .eq('is_recovered', false)

      // Clear the abandoned cart
      await supabase
        .from('carts')
        .update({
          is_abandoned: true,
          updated_at: new Date().toISOString()
        })
        .eq('user_id', userId)
        .eq('is_abandoned', false)
    } catch (error) {
      console.error('Error recovering abandoned cart:', error)
    }
  }

  // Get abandoned carts for email campaigns
  static async getAbandonedCartsForEmailCampaign(): Promise<AbandonedCartData[]> {
    if (!supabase) {
      console.warn('Supabase not configured, returning empty abandoned carts')
      return []
    }

    try {
      const { data, error } = await supabase
        .from('abandoned_carts')
        .select('*')
        .eq('is_recovered', false)
        .lte('email_sent_count', 3) // Max 3 emails per cart
        .order('abandoned_at', { ascending: true })

      if (error) {
        console.error('Error fetching abandoned carts:', error)
        return []
      }

      return (data as unknown as AbandonedCartData[]) || []
    } catch (error) {
      console.error('Error getting abandoned carts:', error)
      return []
    }
  }

  // Update email campaign tracking
  static async updateEmailCampaignTracking(
    userId: string,
    emailSentCount: number,
    nextEmailScheduledAt?: string
  ): Promise<void> {
    if (!supabase) {
      console.warn('Supabase not configured, skipping email tracking update')
      return
    }

    try {
      await supabase
        .from('abandoned_carts')
        .update({
          email_sent_count: emailSentCount,
          last_email_sent_at: new Date().toISOString(),
          next_email_scheduled_at: nextEmailScheduledAt,
          updated_at: new Date().toISOString()
        })
        .eq('user_id', userId)
        .eq('is_recovered', false)
    } catch (error) {
      console.error('Error updating email campaign tracking:', error)
    }
  }

  // Log email campaign
  static async logEmailCampaign(
    userId: string,
    userEmail: string,
    campaignType: string,
    subject: string,
    content: string
  ): Promise<void> {
    if (!supabase) {
      console.warn('Supabase not configured, skipping email campaign logging')
      return
    }

    try {
      await supabase
        .from('email_campaigns')
        .insert({
          user_id: userId,
          user_email: userEmail,
          campaign_type: campaignType,
          subject,
          content,
          sent_at: new Date().toISOString(),
          created_at: new Date().toISOString()
        })
    } catch (error) {
      console.error('Error logging email campaign:', error)
    }
  }

  // Get user's current cart
  static async getUserCart(userId: string): Promise<CartData | null> {
    if (!supabase) {
      console.warn('Supabase not configured, returning null cart')
      return null
    }

    try {
      const { data, error } = await supabase
        .from('carts')
        .select('*')
        .eq('user_id', userId)
        .eq('is_abandoned', false)
        .single()

      if (error) {
        console.error('Error fetching user cart:', error)
        return null
      }

      return data as unknown as CartData
    } catch (error) {
      console.error('Error getting user cart:', error)
      return null
    }
  }

  // Clear user's cart
  static async clearUserCart(userId: string): Promise<void> {
    if (!supabase) {
      console.warn('Supabase not configured, skipping cart clear')
      return
    }

    try {
      await supabase
        .from('carts')
        .update({
          items: [],
          total: 0,
          updated_at: new Date().toISOString()
        })
        .eq('user_id', userId)
        .eq('is_abandoned', false)
    } catch (error) {
      console.error('Error clearing user cart:', error)
    }
  }
} 