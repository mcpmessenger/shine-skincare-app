'use client'

import { useEffect, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { useTheme } from '@/hooks/useTheme'
import { CheckCircle, XCircle, Loader } from 'lucide-react'

export default function AuthCallback() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const { handleOAuthCallback } = useAuth()
  const { theme } = useTheme()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [error, setError] = useState<string>('')

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const code = searchParams.get('code')
        const state = searchParams.get('state')
        const error = searchParams.get('error')

        if (error) {
          setError('Authentication was cancelled or failed')
          setStatus('error')
          return
        }

        if (!code || !state) {
          setError('Missing authorization code or state')
          setStatus('error')
          return
        }

        // Verify state matches stored state
        const storedState = localStorage.getItem('oauth_state')
        if (state !== storedState) {
          setError('Invalid state parameter')
          setStatus('error')
          return
        }

        // Exchange code for tokens
        const response = await fetch('/api/auth/callback', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ code, state }),
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || 'Failed to complete authentication')
        }

        const data = await response.json()
        
        // Handle OAuth callback with Supabase integration
        await handleOAuthCallback(data.user_info)
        
        setStatus('success')
        
        // Redirect to home page after successful authentication
        setTimeout(() => {
          router.push('/')
        }, 2000)
        
      } catch (error) {
        console.error('Authentication error:', error)
        setError(error instanceof Error ? error.message : 'Authentication failed')
        setStatus('error')
      }
    }

    handleCallback()
  }, [searchParams, handleOAuthCallback, router])

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: theme === 'dark' ? '#000000' : '#ffffff',
      color: theme === 'dark' ? '#ffffff' : '#000000',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      <div style={{
        maxWidth: '400px',
        width: '90%',
        textAlign: 'center',
        padding: '2rem'
      }}>
        {status === 'loading' && (
          <>
            <Loader size={48} style={{ 
              color: '#3b82f6', 
              marginBottom: '1rem',
              animation: 'spin 1s linear infinite'
            }} />
            <h1 style={{
              fontSize: '1.5rem',
              fontWeight: 600,
              marginBottom: '0.5rem'
            }}>
              Completing Sign In
            </h1>
            <p style={{
              fontSize: '0.9rem',
              color: theme === 'dark' ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)'
            }}>
              Please wait while we complete your authentication...
            </p>
          </>
        )}

        {status === 'success' && (
          <>
            <CheckCircle size={48} style={{ 
              color: '#10b981', 
              marginBottom: '1rem'
            }} />
            <h1 style={{
              fontSize: '1.5rem',
              fontWeight: 600,
              marginBottom: '0.5rem'
            }}>
              Sign In Successful!
            </h1>
            <p style={{
              fontSize: '0.9rem',
              color: theme === 'dark' ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)'
            }}>
              You have been successfully signed in. Redirecting you to the home page...
            </p>
          </>
        )}

        {status === 'error' && (
          <>
            <XCircle size={48} style={{ 
              color: '#ef4444', 
              marginBottom: '1rem'
            }} />
            <h1 style={{
              fontSize: '1.5rem',
              fontWeight: 600,
              marginBottom: '0.5rem'
            }}>
              Sign In Failed
            </h1>
            <p style={{
              fontSize: '0.9rem',
              color: theme === 'dark' ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)',
              marginBottom: '1rem'
            }}>
              {error}
            </p>
            <button
              onClick={() => router.push('/')}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: '#3b82f6',
                border: 'none',
                borderRadius: '8px',
                color: '#ffffff',
                fontSize: '0.9rem',
                fontWeight: 500,
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#2563eb'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#3b82f6'
              }}
            >
              Return to Home
            </button>
          </>
        )}

        <style jsx>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    </div>
  )
} 