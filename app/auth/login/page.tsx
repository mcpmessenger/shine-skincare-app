'use client';

import { useState, useEffect } from 'react';
import Link from "next/link"
import Image from "next/image"

import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { useAuth } from "@/hooks/useAuth"
import { useRouter } from "next/navigation"
import { useSearchParams } from "next/navigation"
import { Loader2 } from "lucide-react"

// Force dynamic rendering to prevent prerendering issues
export const dynamic = 'force-dynamic';

export default function LoginPage() {
  const [mounted, setMounted] = useState(false);
  const { login, loginAsGuest } = useAuth();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const searchParams = useSearchParams();
  const redirect = searchParams.get('redirect') || '/';

  useEffect(() => {
    setMounted(true);
  }, []);

  // Don't render anything until mounted to prevent SSR issues
  if (!mounted) {
    return null;
  }

  const handleGoogleLogin = async () => {
    try {
      setIsLoading(true);
      setError('');
      await login();
    } catch (error) {
      console.error('Login failed:', error);
      setError('Failed to initiate login. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGuestLogin = async () => {
    try {
      setIsLoading(true);
      setError('');
      await loginAsGuest();
      // Redirect to desired page after guest login
      router.push(redirect);
    } catch (error) {
      console.error('Guest login failed:', error);
      setError('Failed to continue as guest. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };
  return (
    <div className="flex min-h-[100dvh] items-center justify-center bg-background px-4 py-12 sm:px-6 lg:px-8">
      <Card className="mx-auto max-w-sm">
        <CardHeader className="space-y-1 text-center">
          <Image 
            src="https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png" 
            alt="Shine Logo" 
            width={80} 
            height={32} 
            className="mx-auto mb-4"
            priority
            style={{ width: 'auto', height: 'auto' }}
            unoptimized
          />
          <CardTitle className="text-2xl font-bold">Welcome to Shine</CardTitle>
          <CardDescription>Sign in with your Google account to get personalized skincare recommendations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            {error && (
              <p className="text-sm text-red-600 text-center">{error}</p>
            )}
            <Button 
              variant="outline" 
              className="w-full bg-transparent hover:bg-gray-50" 
              onClick={handleGoogleLogin}
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Connecting to Google...
                </>
              ) : (
                <>
                  <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  Continue with Google
                </>
              )}
            </Button>
            <Button 
              variant="secondary" 
              className="w-full mt-2" 
              onClick={handleGuestLogin}
              disabled={isLoading}
            >
              Continue as Guest
            </Button>
          </div>
        </CardContent>
        <CardFooter className="text-center text-sm text-muted-foreground">
          By continuing, you agree to our Terms of Service and Privacy Policy
        </CardFooter>
      </Card>
    </div>
  )
}
