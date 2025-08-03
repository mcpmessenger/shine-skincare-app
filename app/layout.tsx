import type { Metadata } from 'next'
import { GeistSans } from 'geist/font/sans'
import { GeistMono } from 'geist/font/mono'
import './globals.css'

export const metadata: Metadata = {
  title: 'Shine - AI-Powered Skincare',
  description: 'Get AI-powered skin analysis and tailored product recommendations for your unique skin profile',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="description" content="AI-powered skincare analysis and recommendations" />
        <meta name="theme-color" content="#000000" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="manifest" href="/manifest.json" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;500;600&display=swap" rel="stylesheet" />
      </head>
      <body style={{
        margin: 0,
        padding: 0,
        fontFamily: `Inter, ${GeistSans.variable}, ${GeistMono.variable}, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`,
        backgroundColor: '#000000',
        color: '#ffffff',
        minHeight: '100vh',
        fontWeight: 300
      }}>
        {children}
      </body>
    </html>
  )
}
