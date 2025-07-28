'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { apiClient, User } from '../lib/api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: () => Promise<void>;
  loginAsGuest: () => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already authenticated on mount
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      // Only access localStorage on client side
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('shine_token');
        if (token) {
          const response = await apiClient.getProfile();
          if (response.success && response.data) {
            setUser(response.data);
          }
        }
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      // Clear invalid tokens (only on client side)
      if (typeof window !== 'undefined') {
        localStorage.removeItem('shine_token');
        localStorage.removeItem('shine_refresh_token');
      }
    } finally {
      setLoading(false);
    }
  };

  const login = async () => {
    try {
      console.log('Starting login process...');
      const response = await apiClient.login();
      console.log('Login response:', response);
      
      const { authorization_url } = response.data;
      console.log('Authorization URL:', authorization_url);
      console.log('Authorization URL type:', typeof authorization_url);
      
      if (!authorization_url) {
        console.error('Authorization URL is undefined or null');
        throw new Error('Authorization URL is missing');
      }
      
      // Redirect to Google OAuth
      console.log('Redirecting to:', authorization_url);
      window.location.href = authorization_url;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const loginAsGuest = async () => {
    // Create a temporary guest user profile
    const guestUser: User = {
      id: 'guest',
      email: 'guest@example.com',
      name: 'Guest User',
      profile_picture_url: '/guest-avatar.svg',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    } as User;

    // Persist a dummy token so auth-required fetches still include Authorization header
    if (typeof window !== 'undefined') {
      localStorage.setItem('shine_token', 'guest');
    }

    setUser(guestUser);
  };

  const logout = async () => {
    try {
      await apiClient.logout();
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
      // Clear tokens even if logout fails
      setUser(null);
    }
  };

  const updateProfile = async (data: Partial<User>) => {
    try {
      const response = await apiClient.updateProfile(data);
      if (response.success && response.data) {
        setUser(response.data);
      }
    } catch (error) {
      console.error('Profile update failed:', error);
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    loading,
    login,
    logout,
    loginAsGuest,
    updateProfile,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
} 