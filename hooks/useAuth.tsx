'use client'

import { createContext, useContext, useReducer, ReactNode, useEffect } from 'react'
import { supabase } from '@/lib/supabase'

export interface User {
  id: string
  email: string
  name: string
  profile_picture_url: string
}

export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: User }
  | { type: 'LOGIN_FAILURE'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'CLEAR_ERROR' }

const AuthContext = createContext<{
  state: AuthState
  login: () => Promise<void>
  logout: () => void
  clearError: () => void
  handleOAuthCallback: (userInfo: any) => Promise<void>
} | null>(null)

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'LOGIN_START':
      return {
        ...state,
        isLoading: true,
        error: null
      }
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload,
        isAuthenticated: true,
        isLoading: false,
        error: null
      }
    case 'LOGIN_FAILURE':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload
      }
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null
      }
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null
      }
    default:
      return state
  }
}

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [state, dispatch] = useReducer(authReducer, {
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null
  })

  // Check for existing auth token on mount
  useEffect(() => {
    const token = localStorage.getItem('auth_token')
    const userData = localStorage.getItem('user_data')
    
    if (token && userData) {
      try {
        const user = JSON.parse(userData)
        dispatch({ type: 'LOGIN_SUCCESS', payload: user })
      } catch (error) {
        console.error('Failed to parse stored user data:', error)
        localStorage.removeItem('auth_token')
        localStorage.removeItem('user_data')
      }
    }
  }, [])

  const login = async () => {
    try {
      dispatch({ type: 'LOGIN_START' })

      // Get OAuth URL from backend
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ client_type: 'web' }),
      })

      if (!response.ok) {
        throw new Error('Failed to get OAuth URL')
      }

      const data = await response.json()
      
      // Store state for verification
      localStorage.setItem('oauth_state', data.state)
      
      // Redirect to Google OAuth
      window.location.href = data.authorization_url
    } catch (error) {
      dispatch({ 
        type: 'LOGIN_FAILURE', 
        payload: error instanceof Error ? error.message : 'Login failed' 
      })
    }
  }

  // Handle OAuth callback and user creation in Supabase
  const handleOAuthCallback = async (userInfo: any) => {
    try {
      if (!supabase) {
        throw new Error('Supabase not configured')
      }

      // Check if user exists in Supabase
      const { data: existingUser, error: userError } = await supabase
        .from('users')
        .select('*')
        .eq('google_id', userInfo.id)
        .single()

      let userId: string

      if (existingUser) {
        // Update existing user
        userId = existingUser.id
        await supabase
          .from('users')
          .update({
            name: userInfo.name,
            email: userInfo.email,
            profile_picture_url: userInfo.picture,
            last_login_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          })
          .eq('id', userId)
      } else {
        // Create new user
        const { data: newUser, error: createError } = await supabase
          .from('users')
          .insert({
            google_id: userInfo.id,
            email: userInfo.email,
            name: userInfo.name,
            profile_picture_url: userInfo.picture,
            is_active: true,
            subscription_tier: 'free',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          })
          .select()
          .single()

        if (createError) {
          throw createError
        }

        userId = newUser.id
      }

      // Store user data and token
      const userData = {
        id: userId,
        email: userInfo.email,
        name: userInfo.name,
        profile_picture_url: userInfo.picture
      }

      localStorage.setItem('auth_token', userInfo.access_token)
      localStorage.setItem('user_data', JSON.stringify(userData))
      localStorage.removeItem('oauth_state')

      dispatch({ type: 'LOGIN_SUCCESS', payload: userData })
    } catch (error) {
      console.error('Error handling OAuth callback:', error)
      dispatch({ 
        type: 'LOGIN_FAILURE', 
        payload: error instanceof Error ? error.message : 'Login failed' 
      })
    }
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_data')
    localStorage.removeItem('oauth_state')
    dispatch({ type: 'LOGOUT' })
  }

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' })
  }

  return (
    <AuthContext.Provider value={{ state, login, logout, clearError, handleOAuthCallback }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
} 