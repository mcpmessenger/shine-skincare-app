'use client'

import { ShoppingCart } from 'lucide-react'
import { useCart } from '@/hooks/useCart'
import { useTheme } from '@/hooks/useTheme'

export const CartIcon = () => {
  const { state } = useCart()
  const { theme } = useTheme()
  const itemCount = state.items.reduce((total, item) => total + item.quantity, 0)

  return (
    <div style={{
      position: 'relative',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      width: '40px',
      height: '40px',
      borderRadius: '50%',
      backgroundColor: theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
      border: theme === 'dark' ? '1px solid rgba(255, 255, 255, 0.2)' : '1px solid rgba(0, 0, 0, 0.2)',
      transition: 'all 0.3s ease'
    }}>
      <ShoppingCart className="w-5 h-5" />
      {itemCount > 0 && (
        <div style={{
          position: 'absolute',
          top: '-8px',
          right: '-8px',
          backgroundColor: '#ef4444',
          color: '#ffffff',
          borderRadius: '50%',
          width: '20px',
          height: '20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '0.75rem',
          fontWeight: 'bold'
        }}>
          {itemCount}
        </div>
      )}
    </div>
  )
} 