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
              {children}
            </CartProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
