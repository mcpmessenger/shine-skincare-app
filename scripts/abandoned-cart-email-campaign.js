const nodemailer = require('nodemailer')

// Email configuration
const transporter = nodemailer.createTransporter({
  service: 'gmail', // or your email service
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASSWORD
  }
})

// Email templates
const emailTemplates = {
  abandoned_cart_1: {
    subject: 'Your cart is waiting for you! 🛒',
    template: (userName, cartItems, cartTotal) => `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #3b82f6;">Hi ${userName}!</h2>
        <p>We noticed you left some amazing products in your cart. Don't let them get away!</p>
        
        <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
          <h3 style="margin-top: 0;">Your Cart Items:</h3>
          ${cartItems.map(item => `
            <div style="display: flex; justify-content: space-between; margin: 10px 0; padding: 10px; background: white; border-radius: 4px;">
              <span>${item.name}</span>
              <span style="font-weight: bold;">$${item.price.toFixed(2)}</span>
            </div>
          `).join('')}
          <div style="border-top: 2px solid #e5e7eb; padding-top: 10px; margin-top: 10px;">
            <strong>Total: $${cartTotal.toFixed(2)}</strong>
          </div>
        </div>
        
        <a href="${process.env.NEXT_PUBLIC_APP_URL}/catalog" style="background-color: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
          Complete Your Purchase
        </a>
        
        <p style="margin-top: 20px; font-size: 14px; color: #6b7280;">
          This offer expires in 24 hours!
        </p>
      </div>
    `
  },
  
  abandoned_cart_2: {
    subject: 'Still thinking about it? Here\'s 10% off! 💫',
    template: (userName, cartItems, cartTotal) => `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #3b82f6;">Hi ${userName}!</h2>
        <p>We know you're busy, but great skincare shouldn't wait! Here's a special offer just for you:</p>
        
        <div style="background-color: #fef3c7; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f59e0b;">
          <h3 style="margin-top: 0; color: #92400e;">🎉 10% OFF YOUR CART!</h3>
          <p style="margin-bottom: 0;">Use code: <strong>COMEBACK10</strong></p>
        </div>
        
        <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
          <h3 style="margin-top: 0;">Your Cart Items:</h3>
          ${cartItems.map(item => `
            <div style="display: flex; justify-content: space-between; margin: 10px 0; padding: 10px; background: white; border-radius: 4px;">
              <span>${item.name}</span>
              <span style="font-weight: bold;">$${item.price.toFixed(2)}</span>
            </div>
          `).join('')}
          <div style="border-top: 2px solid #e5e7eb; padding-top: 10px; margin-top: 10px;">
            <strong>Total: $${cartTotal.toFixed(2)}</strong>
          </div>
        </div>
        
        <a href="${process.env.NEXT_PUBLIC_APP_URL}/catalog" style="background-color: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
          Claim Your Discount
        </a>
        
        <p style="margin-top: 20px; font-size: 14px; color: #6b7280;">
          This offer expires in 48 hours!
        </p>
      </div>
    `
  },
  
  abandoned_cart_3: {
    subject: 'Last chance: Your cart expires tomorrow! ⏰',
    template: (userName, cartItems, cartTotal) => `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #3b82f6;">Hi ${userName}!</h2>
        <p>This is your final reminder - your cart will be cleared tomorrow. Don't miss out on these amazing products!</p>
        
        <div style="background-color: #fef2f2; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ef4444;">
          <h3 style="margin-top: 0; color: #dc2626;">⚠️ FINAL REMINDER</h3>
          <p style="margin-bottom: 0;">Your cart expires in 24 hours!</p>
        </div>
        
        <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
          <h3 style="margin-top: 0;">Your Cart Items:</h3>
          ${cartItems.map(item => `
            <div style="display: flex; justify-content: space-between; margin: 10px 0; padding: 10px; background: white; border-radius: 4px;">
              <span>${item.name}</span>
              <span style="font-weight: bold;">$${item.price.toFixed(2)}</span>
            </div>
          `).join('')}
          <div style="border-top: 2px solid #e5e7eb; padding-top: 10px; margin-top: 10px;">
            <strong>Total: $${cartTotal.toFixed(2)}</strong>
          </div>
        </div>
        
        <a href="${process.env.NEXT_PUBLIC_APP_URL}/catalog" style="background-color: #ef4444; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
          Complete Purchase Now
        </a>
        
        <p style="margin-top: 20px; font-size: 14px; color: #6b7280;">
          This is your last chance to complete your purchase!
        </p>
      </div>
    `
  }
}

// Send abandoned cart email
async function sendAbandonedCartEmail(abandonedCart, emailNumber) {
  try {
    const template = emailTemplates[`abandoned_cart_${emailNumber}`]
    if (!template) {
      throw new Error(`No template found for email number ${emailNumber}`)
    }

    const htmlContent = template.template(
      abandonedCart.user_name,
      abandonedCart.cart_items,
      abandonedCart.cart_total
    )

    const mailOptions = {
      from: process.env.EMAIL_USER,
      to: abandonedCart.user_email,
      subject: template.subject,
      html: htmlContent
    }

    await transporter.sendMail(mailOptions)

    // Log the email campaign
    await fetch(`${process.env.NEXT_PUBLIC_APP_URL}/api/abandoned-cart-email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        action: 'log_email_campaign',
        userId: abandonedCart.user_id,
        userEmail: abandonedCart.user_email,
        campaignType: `abandoned_cart_${emailNumber}`,
        subject: template.subject,
        content: htmlContent
      })
    })

    // Update email tracking
    await fetch(`${process.env.NEXT_PUBLIC_APP_URL}/api/abandoned-cart-email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        action: 'update_email_tracking',
        userId: abandonedCart.user_id,
        emailSentCount: abandonedCart.email_sent_count + 1,
        nextEmailScheduledAt: getNextEmailSchedule(emailNumber)
      })
    })

    console.log(`Sent abandoned cart email ${emailNumber} to ${abandonedCart.user_email}`)
  } catch (error) {
    console.error(`Error sending abandoned cart email to ${abandonedCart.user_email}:`, error)
  }
}

// Get next email schedule based on email number
function getNextEmailSchedule(emailNumber) {
  const now = new Date()
  
  switch (emailNumber) {
    case 1:
      // Send second email after 24 hours
      return new Date(now.getTime() + 24 * 60 * 60 * 1000).toISOString()
    case 2:
      // Send third email after 48 hours
      return new Date(now.getTime() + 48 * 60 * 60 * 1000).toISOString()
    default:
      return null
  }
}

// Main function to process abandoned carts
async function processAbandonedCarts() {
  try {
    console.log('Starting abandoned cart email campaign...')

    // Get abandoned carts from API
    const response = await fetch(`${process.env.NEXT_PUBLIC_APP_URL}/api/abandoned-cart-email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        action: 'get_abandoned_carts'
      })
    })

    if (!response.ok) {
      throw new Error('Failed to fetch abandoned carts')
    }

    const { abandonedCarts } = await response.json()
    console.log(`Found ${abandonedCarts.length} abandoned carts`)

    // Process each abandoned cart
    for (const cart of abandonedCarts) {
      const emailNumber = cart.email_sent_count + 1
      
      if (emailNumber <= 3) {
        await sendAbandonedCartEmail(cart, emailNumber)
        
        // Add delay between emails to avoid rate limiting
        await new Promise(resolve => setTimeout(resolve, 1000))
      }
    }

    console.log('Abandoned cart email campaign completed')
  } catch (error) {
    console.error('Error processing abandoned carts:', error)
  }
}

// Run the script if called directly
if (require.main === module) {
  processAbandonedCarts()
}

module.exports = { processAbandonedCarts, sendAbandonedCartEmail } 