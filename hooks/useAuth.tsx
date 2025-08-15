'use client'

import { createContext, useContext, useEffect, useState } from 'react'
import { User, Session } from '@supabase/supabase-js'
import { createSupabaseClient } from '@/lib/supabase'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'

interface AuthContextType {
  user: User | null
  session: Session | null
  loading: boolean
  isAuthenticated: boolean
  signInWithGoogle: () => Promise<void>
  signOut: () => Promise<void>
  updateProfile: (data: any) => Promise<void>
  state: {
    isAuthenticated: boolean
    user: User | null
    loading: boolean
  }
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const supabase = createSupabaseClient()

  useEffect(() => {
    // Get initial session
    const getInitialSession = async () => {
      const { data: { session }, error } = await supabase.auth.getSession()
      if (error) {
        console.error('Error getting session:', error)
      } else {
        setSession(session)
        setUser(session?.user ?? null)
      }
      setLoading(false)
    }

    getInitialSession()

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event: string, session: Session | null) => {
        setSession(session)
        setUser(session?.user ?? null)
        setLoading(false)

        if (event === 'SIGNED_IN' && session?.user) {
          // Update user's last login time
          await supabase
            .from('users')
            .update({ last_login_at: new Date().toISOString() })
            .eq('id', session.user.id)
          
          toast.success('Successfully signed in!')
        } else if (event === 'SIGNED_OUT') {
          toast.success('Successfully signed out!')
          router.push('/')
        }
      }
    )

    return () => subscription.unsubscribe()
  }, [supabase, router])

  const signInWithGoogle = async () => {
    try {
      setLoading(true)
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
          queryParams: {
            access_type: 'offline',
            prompt: 'consent',
          },
        },
      })
      if (error) throw error
    } catch (error) {
      console.error('Error signing in with Google:', error)
      toast.error('Failed to sign in with Google')
    } finally {
      setLoading(false)
    }
  }

  const signOut = async () => {
    try {
      setLoading(true)
      const { error } = await supabase.auth.signOut()
      if (error) throw error
    } catch (error) {
      console.error('Error signing out:', error)
      toast.error('Failed to sign out')
    } finally {
      setLoading(false)
    }
  }

  const updateProfile = async (data: any) => {
    try {
      if (!user) throw new Error('No user logged in')
      
      const { error } = await supabase
        .from('users')
        .update(data)
        .eq('id', user.id)
      
      if (error) throw error
      toast.success('Profile updated successfully!')
    } catch (error) {
      console.error('Error updating profile:', error)
      toast.error('Failed to update profile')
    }
  }

  const value = {
    user,
    session,
    loading,
    isAuthenticated: !!user,
    signInWithGoogle,
    signOut,
    updateProfile,
    state: {
      isAuthenticated: !!user,
      user,
      loading,
    },
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
} 