import type { Metadata } from 'next'
import { GeistSans } from 'geist/font/sans'
import { GeistMono } from 'geist/font/mono'
import './globals.css'
import { AuthProvider } from '@/hooks/useAuth'
import { CartProvider } from '@/hooks/useCart'
import { ThemeProvider } from '@/components/theme-provider'
import Header from '@/components/header'

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
              {children}
            </CartProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
