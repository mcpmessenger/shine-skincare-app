'use client'

import { useState } from 'react'
import { X, LogIn, User, Lock } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { useTheme } from '@/hooks/useTheme'

interface SignInModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
}

export const SignInModal = ({ isOpen, onClose, onSuccess }: SignInModalProps) => {
  const { login, state } = useAuth()
  const { theme } = useTheme()
  const [isLoggingIn, setIsLoggingIn] = useState(false)

  const handleLogin = async () => {
    setIsLoggingIn(true)
    try {
      await login()
      // The login function will redirect to Google OAuth
      // onSuccess will be called when user returns from OAuth
    } catch (error) {
      console.error('Login failed:', error)
      setIsLoggingIn(false)
    }
  }

  if (!isOpen) return null

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      backdropFilter: 'blur(8px)'
    }}>
      <div style={{
        backgroundColor: theme === 'dark' ? '#1a1a1a' : '#ffffff',
        borderRadius: '16px',
        padding: '2rem',
        maxWidth: '400px',
        width: '90%',
        border: theme === 'dark' ? '1px solid rgba(255, 255, 255, 0.1)' : '1px solid rgba(0, 0, 0, 0.1)',
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
        position: 'relative'
      }}>
        {/* Close Button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '1rem',
            right: '1rem',
            background: 'none',
            border: 'none',
            color: theme === 'dark' ? '#ffffff' : '#000000',
            cursor: 'pointer',
            padding: '0.5rem',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.3s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'transparent'
          }}
        >
          <X size={20} />
        </button>

        {/* Header */}
        <div style={{
          textAlign: 'center',
          marginBottom: '2rem'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem',
            marginBottom: '1rem'
          }}>
            <Lock size={24} style={{ color: '#3b82f6' }} />
            <h2 style={{
              fontSize: '1.5rem',
              fontWeight: 600,
              color: theme === 'dark' ? '#ffffff' : '#000000',
              margin: 0
            }}>
              Sign In Required
            </h2>
          </div>
          <p style={{
            fontSize: '0.9rem',
            color: theme === 'dark' ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)',
            margin: 0,
            lineHeight: '1.5'
          }}>
            Please sign in to add products to your cart and access your personalized recommendations.
          </p>
        </div>

        {/* Benefits */}
        <div style={{
          marginBottom: '2rem',
          padding: '1rem',
          backgroundColor: theme === 'dark' ? 'rgba(59, 130, 246, 0.1)' : 'rgba(59, 130, 246, 0.05)',
          borderRadius: '12px',
          border: theme === 'dark' ? '1px solid rgba(59, 130, 246, 0.3)' : '1px solid rgba(59, 130, 246, 0.2)'
        }}>
          <h3 style={{
            fontSize: '1rem',
            fontWeight: 500,
            color: theme === 'dark' ? '#ffffff' : '#000000',
            margin: '0 0 0.5rem 0'
          }}>
            Benefits of signing in:
          </h3>
          <ul style={{
            listStyle: 'none',
            padding: 0,
            margin: 0,
            fontSize: '0.85rem',
            color: theme === 'dark' ? 'rgba(255, 255, 255, 0.8)' : 'rgba(0, 0, 0, 0.8)'
          }}>
            <li style={{ marginBottom: '0.25rem' }}>• Save your cart and preferences</li>
            <li style={{ marginBottom: '0.25rem' }}>• Get personalized product recommendations</li>
            <li style={{ marginBottom: '0.25rem' }}>• Track your skin analysis history</li>
            <li style={{ marginBottom: '0.25rem' }}>• Secure checkout process</li>
          </ul>
        </div>

        {/* Sign In Button */}
        <button
          onClick={handleLogin}
          disabled={isLoggingIn}
          style={{
            width: '100%',
            padding: '1rem',
            backgroundColor: isLoggingIn ? 'rgba(59, 130, 246, 0.5)' : '#3b82f6',
            border: 'none',
            borderRadius: '12px',
            color: '#ffffff',
            fontSize: '1rem',
            fontWeight: 600,
            cursor: isLoggingIn ? 'not-allowed' : 'pointer',
            transition: 'all 0.3s ease',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem'
          }}
          onMouseEnter={(e) => {
            if (!isLoggingIn) {
              e.currentTarget.style.backgroundColor = '#2563eb'
            }
          }}
          onMouseLeave={(e) => {
            if (!isLoggingIn) {
              e.currentTarget.style.backgroundColor = '#3b82f6'
            }
          }}
        >
          {isLoggingIn ? (
            <>
              <div style={{
                width: '16px',
                height: '16px',
                border: '2px solid #ffffff',
                borderTop: '2px solid transparent',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }} />
              Signing in...
            </>
          ) : (
            <>
              <LogIn size={20} />
              Sign in with Google
            </>
          )}
        </button>

        {/* Privacy Notice */}
        <p style={{
          fontSize: '0.75rem',
          color: theme === 'dark' ? 'rgba(255, 255, 255, 0.5)' : 'rgba(0, 0, 0, 0.5)',
          textAlign: 'center',
          margin: '1rem 0 0 0',
          lineHeight: '1.4'
        }}>
          By signing in, you agree to our{' '}
          <a 
            href="#" 
            style={{ color: '#3b82f6', textDecoration: 'none' }}
            onMouseEnter={(e) => {
              e.currentTarget.style.textDecoration = 'underline'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.textDecoration = 'none'
            }}
          >
            Privacy Policy
          </a>
          {' '}and{' '}
          <a 
            href="#" 
            style={{ color: '#3b82f6', textDecoration: 'none' }}
            onMouseEnter={(e) => {
              e.currentTarget.style.textDecoration = 'underline'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.textDecoration = 'none'
            }}
          >
            Terms of Service
          </a>
        </p>
      </div>

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
} 