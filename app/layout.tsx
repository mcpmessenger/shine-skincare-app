import type { Metadata } from 'next'
import { GeistSans } from 'geist/font/sans'
import { GeistMono } from 'geist/font/mono'
import './globals.css'
import { AuthProvider } from '@/hooks/useAuth'
import { CartProvider } from '@/hooks/useCart'
import { ThemeProvider } from '@/components/theme-provider'
import Header from '@/components/header'
import ServiceDegradationBanner from '@/components/service-degradation-banner'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Shine - AI-Powered Skincare',
  description: 'Get AI-powered skin analysis and tailored product recommendations for your unique skin profile',
  generator: 'v0.dev',
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
  icons: {
    icon: [
      { url: '/favicon.ico', sizes: 'any' },
      { url: 'https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png', type: 'image/png' }
    ],
    shortcut: 'https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png',
    apple: 'https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png',
  },
  openGraph: {
    title: 'Shine - AI-Powered Skincare',
    description: 'Get AI-powered skin analysis and tailored product recommendations for your unique skin profile',
    url: 'https://shine-skincare.com',
    siteName: 'Shine',
    images: [
      {
        url: 'https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png',
        width: 1200,
        height: 630,
        alt: 'Shine - AI-Powered Skincare',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Shine - AI-Powered Skincare',
    description: 'Get AI-powered skin analysis and tailored product recommendations for your unique skin profile',
    images: ['https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png'],
  },
  manifest: '/manifest.json',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="Shine" />
        <meta name="application-name" content="Shine" />
        <meta name="theme-color" content="#000000" />
        <meta name="msapplication-TileColor" content="#000000" />
        <meta name="msapplication-tap-highlight" content="no" />
        <link rel="manifest" href="/manifest.json" />
        <style>{`
html {
  font-family: ${GeistSans.style.fontFamily};
  --font-sans: ${GeistSans.variable};
  --font-mono: ${GeistMono.variable};
}

/* Critical CSS for basic styling */
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  background-color: #000;
  color: #fff;
  font-family: ${GeistSans.style.fontFamily};
}

/* Basic button styles */
button {
  background-color: #3b82f6;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background-color 0.2s;
  margin: 0.25rem;
}

button:hover {
  background-color: #2563eb;
}

/* Basic input styles */
input, select {
  background-color: white;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  color: #111827;
  margin: 0.25rem;
}

input:focus, select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Basic card styles */
.card {
  background-color: white;
  border-radius: 0.5rem;
  padding: 1rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  margin: 0.5rem;
}

/* Basic link styles */
a {
  color: #3b82f6;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
        `}</style>
      </head>
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <AuthProvider>
            <CartProvider>
              <Header />
              <nav className="hidden md:flex space-x-6">
                <Link href="/" className="text-sm font-medium transition-colors hover:text-primary">
                  Home
                </Link>
                <Link href="/skin-analysis" className="text-sm font-medium transition-colors hover:text-primary">
                  Skin Analysis
                </Link>
                <Link href="/selfie-analysis" className="text-sm font-medium transition-colors hover:text-primary">
                  Selfie Analysis
                </Link>
                <Link href="/recommendations" className="text-sm font-medium transition-colors hover:text-primary">
                  Recommendations
                </Link>
                <Link href="/profile" className="text-sm font-medium transition-colors hover:text-primary">
                  Profile
                </Link>
              </nav>
              <ServiceDegradationBanner />
              <main className="flex-1">
                {children}
              </main>
            </CartProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
