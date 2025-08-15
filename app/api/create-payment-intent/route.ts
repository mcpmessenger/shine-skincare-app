import { NextRequest, NextResponse } from 'next/server'

// Only import Stripe if the secret key is available
let stripe: any = null
try {
  if (process.env.STRIPE_SECRET_KEY) {
    const Stripe = require('stripe')
    stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
      apiVersion: '2023-10-16'
    })
  }
} catch (error) {
  console.warn('Stripe not configured, payment features will be disabled')
}

export async function POST(request: NextRequest) {
  try {
    const { amount, currency = 'usd' } = await request.json()

    if (!amount) {
      return NextResponse.json(
        { error: 'Amount is required' },
        { status: 400 }
      )
    }

    // If Stripe is not configured, return a mock response for development
    if (!stripe) {
      return NextResponse.json({
        clientSecret: 'pi_mock_secret_key_for_development_only',
      })
    }

    const paymentIntent = await stripe.paymentIntents.create({
      amount: Math.round(amount * 100), // Convert to cents
      currency,
      automatic_payment_methods: {
        enabled: true,
      },
    })

    return NextResponse.json({
      clientSecret: paymentIntent.client_secret,
    })
  } catch (error) {
    console.error('Payment intent creation failed:', error)
    return NextResponse.json(
      { error: 'Payment intent creation failed' },
      { status: 500 }
    )
  }
} 