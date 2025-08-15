'use client'

import { useState } from 'react'
import { useStripe, useElements, PaymentElement } from '@stripe/react-stripe-js'
import { useCart } from '@/hooks/useCart'
import { useRouter } from 'next/navigation'

export const CheckoutForm = () => {
  const stripe = useStripe()
  const elements = useElements()
  const { dispatch } = useCart()
  const router = useRouter()
  const [isProcessing, setIsProcessing] = useState(false)
  const [message, setMessage] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!stripe || !elements) {
      return
    }

    setIsProcessing(true)

    const result = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/success`,
      },
    })

    if (result.error) {
      setMessage(result.error.message || 'An error occurred')
    } else {
      // Payment was successful
      setMessage('Payment successful!')
      dispatch({ type: 'CLEAR_CART' })
      router.push('/success')
    }

    setIsProcessing(false)
  }

  return (
    <form onSubmit={handleSubmit}>
      <PaymentElement />
      
      {message && (
        <div style={{
          marginTop: '1rem',
          padding: '1rem',
          backgroundColor: message.includes('error') ? 'rgba(239, 68, 68, 0.2)' : 'rgba(34, 197, 94, 0.2)',
          border: message.includes('error') ? '1px solid rgba(239, 68, 68, 0.3)' : '1px solid rgba(34, 197, 94, 0.3)',
          borderRadius: '8px',
          color: message.includes('error') ? '#ef4444' : '#22c55e'
        }}>
          {message}
        </div>
      )}
      
      <button
        type="submit"
        disabled={!stripe || isProcessing}
        style={{
          width: '100%',
          marginTop: '1.5rem',
          padding: '1rem',
          backgroundColor: isProcessing ? 'rgba(255, 255, 255, 0.3)' : '#3b82f6',
          border: '1px solid #3b82f6',
          borderRadius: '8px',
          color: '#ffffff',
          fontSize: '1rem',
          fontWeight: 'bold',
          cursor: isProcessing ? 'not-allowed' : 'pointer',
          transition: 'all 0.3s ease'
        }}
      >
        {isProcessing ? 'Processing...' : 'Pay Now'}
      </button>
    </form>
  )
} 