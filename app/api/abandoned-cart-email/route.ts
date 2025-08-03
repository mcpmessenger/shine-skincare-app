import { NextRequest, NextResponse } from 'next/server'
import { CartService } from '@/lib/cart-service'

export const dynamic = 'force-dynamic'

export async function POST(request: NextRequest) {
  try {
    const { action, userId, userEmail, userName } = await request.json()

    switch (action) {
      case 'mark_abandoned':
        if (!userId || !userEmail || !userName) {
          return NextResponse.json(
            { error: 'Missing required parameters' },
            { status: 400 }
          )
        }

        await CartService.markCartAsAbandoned(userId, userEmail, userName)
        
        return NextResponse.json({ 
          success: true, 
          message: 'Cart marked as abandoned' 
        })

      case 'get_abandoned_carts':
        const abandonedCarts = await CartService.getAbandonedCartsForEmailCampaign()
        
        return NextResponse.json({ 
          success: true, 
          abandonedCarts 
        })

      case 'update_email_tracking':
        const { emailSentCount, nextEmailScheduledAt } = await request.json()
        
        if (!userId || emailSentCount === undefined) {
          return NextResponse.json(
            { error: 'Missing required parameters' },
            { status: 400 }
          )
        }

        await CartService.updateEmailCampaignTracking(
          userId, 
          emailSentCount, 
          nextEmailScheduledAt
        )
        
        return NextResponse.json({ 
          success: true, 
          message: 'Email tracking updated' 
        })

      case 'log_email_campaign':
        const { campaignType, subject, content } = await request.json()
        
        if (!userId || !userEmail || !campaignType || !subject || !content) {
          return NextResponse.json(
            { error: 'Missing required parameters' },
            { status: 400 }
          )
        }

        await CartService.logEmailCampaign(
          userId,
          userEmail,
          campaignType,
          subject,
          content
        )
        
        return NextResponse.json({ 
          success: true, 
          message: 'Email campaign logged' 
        })

      case 'recover_cart':
        if (!userId) {
          return NextResponse.json(
            { error: 'Missing user ID' },
            { status: 400 }
          )
        }

        await CartService.recoverAbandonedCart(userId)
        
        return NextResponse.json({ 
          success: true, 
          message: 'Cart recovered' 
        })

      default:
        return NextResponse.json(
          { error: 'Invalid action' },
          { status: 400 }
        )
    }
  } catch (error) {
    console.error('Abandoned cart email error:', error)
    return NextResponse.json(
      { 
        error: 'Internal server error',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
} 