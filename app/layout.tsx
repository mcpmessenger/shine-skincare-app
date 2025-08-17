import type { Metadata } from 'next'
import './globals.css'
import { CartProvider } from '@/hooks/useCart'
import { ThemeProvider } from '@/hooks/useTheme'
import { AuthProvider } from '@/hooks/useAuth'
import { AnalysisProvider } from './contexts/AnalysisContext'

export const metadata: Metadata = {
  title: 'Shine Skin Collective - AI-Powered Skincare Analysis',
  description: 'Get AI-powered skin analysis and tailored product recommendations for your unique skin profile with Shine Skin Collective',
  keywords: 'skincare, AI analysis, skin health, personalized recommendations, dermatology',
  authors: [{ name: 'Shine Skin Collective' }],
  manifest: '/manifest.json',
  icons: {
    icon: '/favicon.ico',
    apple: '/apple-touch-icon.png',
  },
}

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#000000',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider>
          <AuthProvider>
            <CartProvider>
              <AnalysisProvider>
                {children}
              </AnalysisProvider>
            </CartProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
