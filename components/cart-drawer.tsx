'use client'

import { useState } from 'react'
import { X, Trash2 } from 'lucide-react'
import { useCart } from '@/hooks/useCart'
import { CartIcon } from './cart-icon'
import Link from 'next/link'
import { useTheme } from '@/hooks/useTheme'

export const CartDrawer = () => {
  const { state, dispatch } = useCart()
  const { theme } = useTheme()
  const [isOpen, setIsOpen] = useState(false)

  const updateQuantity = (id: string, quantity: number) => {
    if (quantity <= 0) {
      dispatch({ type: 'REMOVE_ITEM', payload: id })
    } else {
      dispatch({ type: 'UPDATE_QUANTITY', payload: { id, quantity } })
    }
  }

  const removeItem = (id: string) => {
    dispatch({ type: 'REMOVE_ITEM', payload: id })
  }

  const clearCart = () => {
    dispatch({ type: 'CLEAR_CART' })
  }

  return (
    <>
      <div onClick={() => setIsOpen(true)}>
        <CartIcon />
      </div>

      {isOpen && (
        <div style={{
          position: 'fixed',
          top: 0,
          right: 0,
          width: '100%',
          maxWidth: '400px',
          height: '100vh',
          backgroundColor: theme === 'dark' ? 'rgba(0, 0, 0, 0.95)' : 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          borderLeft: theme === 'dark' ? '1px solid rgba(255, 255, 255, 0.1)' : '1px solid rgba(0, 0, 0, 0.1)',
          zIndex: 1000,
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }}>
          {/* Header */}
          <div style={{
            padding: '1.5rem',
            borderBottom: theme === 'dark' ? '1px solid rgba(255, 255, 255, 0.1)' : '1px solid rgba(0, 0, 0, 0.1)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <h2 style={{ color: theme === 'dark' ? '#ffffff' : '#000000', margin: 0, fontSize: '1.25rem' }}>
              Shopping Cart ({state.items.length} items)
            </h2>
            <button
              onClick={() => setIsOpen(false)}
              style={{
                background: 'none',
                border: 'none',
                color: theme === 'dark' ? '#ffffff' : '#000000',
                cursor: 'pointer',
                padding: '0.5rem'
              }}
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Cart Items */}
          <div style={{
            flex: 1,
            overflowY: 'auto',
            padding: '1rem'
          }}>
            {state.items.length === 0 ? (
              <div style={{
                textAlign: 'center',
                color: theme === 'dark' ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)',
                padding: '2rem'
              }}>
                Your cart is empty
              </div>
            ) : (
              state.items.map((item) => (
                <div key={item.id} style={{
                  display: 'flex',
                  gap: '1rem',
                  padding: '1rem',
                  borderBottom: theme === 'dark' ? '1px solid rgba(255, 255, 255, 0.1)' : '1px solid rgba(0, 0, 0, 0.1)',
                  marginBottom: '1rem'
                }}>
                  <img
                    src={item.image}
                    alt={item.name}
                    style={{
                      width: '60px',
                      height: '60px',
                      objectFit: 'cover',
                      borderRadius: '8px'
                    }}
                  />
                  <div style={{ flex: 1 }}>
                    <h3 style={{
                      color: theme === 'dark' ? '#ffffff' : '#000000',
                      margin: '0 0 0.5rem 0',
                      fontSize: '0.9rem'
                    }}>
                      {item.name}
                    </h3>
                    <p style={{
                      color: theme === 'dark' ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)',
                      margin: '0 0 0.5rem 0',
                      fontSize: '0.8rem'
                    }}>
                      ${item.price.toFixed(2)}
                    </p>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}>
                                             <button
                         onClick={() => updateQuantity(item.id, item.quantity - 1)}
                         style={{
                           background: theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
                           border: theme === 'dark' ? '1px solid rgba(255, 255, 255, 0.2)' : '1px solid rgba(0, 0, 0, 0.2)',
                           color: theme === 'dark' ? '#ffffff' : '#000000',
                           borderRadius: '4px',
                           width: '24px',
                           height: '24px',
                           display: 'flex',
                           alignItems: 'center',
                           justifyContent: 'center',
                           cursor: 'pointer'
                         }}
                       >
                         <span className="text-xs">−</span>
                       </button>
                       <span style={{
                         color: theme === 'dark' ? '#ffffff' : '#000000',
                         minWidth: '20px',
                         textAlign: 'center'
                       }}>
                         {item.quantity}
                       </span>
                       <button
                         onClick={() => updateQuantity(item.id, item.quantity + 1)}
                         style={{
                           background: theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
                           border: theme === 'dark' ? '1px solid rgba(255, 255, 255, 0.2)' : '1px solid rgba(0, 0, 0, 0.2)',
                           color: theme === 'dark' ? '#ffffff' : '#000000',
                           borderRadius: '4px',
                           width: '24px',
                           height: '24px',
                           display: 'flex',
                           alignItems: 'center',
                           justifyContent: 'center',
                           cursor: 'pointer'
                         }}
                       >
                         <span className="text-xs">+</span>
                       </button>
                      <button
                        onClick={() => removeItem(item.id)}
                        style={{
                          background: 'rgba(239, 68, 68, 0.2)',
                          border: '1px solid rgba(239, 68, 68, 0.3)',
                          color: '#ef4444',
                          borderRadius: '4px',
                          padding: '0.25rem 0.5rem',
                          cursor: 'pointer',
                          marginLeft: 'auto'
                        }}
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          {state.items.length > 0 && (
            <div style={{
              padding: '1.5rem',
              borderTop: theme === 'dark' ? '1px solid rgba(255, 255, 255, 0.1)' : '1px solid rgba(0, 0, 0, 0.1)',
              backgroundColor: theme === 'dark' ? 'rgba(0, 0, 0, 0.3)' : 'rgba(255, 255, 255, 0.3)'
            }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '1rem'
              }}>
                <span style={{ color: theme === 'dark' ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)' }}>
                  Total:
                </span>
                <span style={{
                  color: theme === 'dark' ? '#ffffff' : '#000000',
                  fontSize: '1.25rem',
                  fontWeight: 'bold'
                }}>
                  ${state.total.toFixed(2)}
                </span>
              </div>
              <div style={{
                display: 'flex',
                gap: '0.5rem'
              }}>
                <button
                  onClick={clearCart}
                  style={{
                    flex: 1,
                    padding: '0.75rem',
                    backgroundColor: 'rgba(239, 68, 68, 0.2)',
                    border: '1px solid rgba(239, 68, 68, 0.3)',
                    color: '#ef4444',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '0.9rem'
                  }}
                >
                  Clear Cart
                </button>
                <Link href="/checkout" style={{
                  flex: 2,
                  padding: '0.75rem',
                  backgroundColor: '#3b82f6',
                  border: '1px solid #3b82f6',
                  color: '#ffffff',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                  fontWeight: 'bold',
                  textDecoration: 'none',
                  textAlign: 'center'
                }}>
                  Checkout
                </Link>
              </div>
            </div>
          )}
        </div>
      )}
    </>
  )
} 