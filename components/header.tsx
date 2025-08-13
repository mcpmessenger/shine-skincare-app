'use client'

import Link from 'next/link'
import { ShoppingCart, User } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { useCart } from '@/hooks/useCart'
import ThemeToggle from '@/components/theme-toggle'
import { SignInModal } from '@/components/sign-in-modal'
import { useState } from 'react'

interface HeaderProps {
  showProductsTab?: boolean
  title?: string
}

export function Header({ showProductsTab = true, title }: HeaderProps) {
  const { state: authState } = useAuth()
  const { isAuthenticated } = useCart()
  const [showSignInModal, setShowSignInModal] = useState(false)

  return (
    <>
      {/* Header */}
      <header className="bg-primary border-b border-primary p-3 flex items-center justify-between gap-4 flex-shrink-0">
        {/* Logo */}
        <div className="flex items-center">
          <Link href="/" className="flex items-center no-underline cursor-pointer">
            <img 
              src="https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png"
              alt="SHINE SKIN COLLECTIVE"
              className="h-12 w-auto object-contain"
            />
          </Link>
          {title && (
            <h1 className="text-xl font-semibold ml-4 text-primary">
              {title}
            </h1>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex items-center gap-4">
          {showProductsTab && (
            <Link href="/catalog" className="text-secondary no-underline text-sm font-medium p-3 rounded-xl transition-all duration-200 bg-secondary hover:bg-hover shadow-sm">
              Products
            </Link>
          )}
          <Link href="/training-dashboard" className="text-secondary no-underline text-sm font-medium p-3 rounded-xl transition-all duration-200 bg-secondary hover:bg-hover shadow-sm">
            Training
          </Link>
        </nav>

        {/* Right Side Controls */}
        <div className="flex items-center gap-4">
          {/* Theme Toggle */}
          <div className="flex-shrink-0">
            <ThemeToggle />
          </div>

          {/* Cart */}
          <button
            onClick={() => setShowSignInModal(true)}
            className="bg-secondary border-none text-primary cursor-pointer p-2 rounded-xl flex items-center justify-center w-8 h-8 hover:bg-hover transition-colors shadow-sm flex-shrink-0"
          >
            <ShoppingCart className="w-4 h-4" />
          </button>

          {/* Auth Avatar / Sign In */}
          {isAuthenticated ? (
            <button
              onClick={() => setShowSignInModal(true)}
              className="bg-hover border-none cursor-pointer p-1 rounded-full flex items-center justify-center w-8 h-8 hover:bg-secondary transition-colors flex-shrink-0"
            >
              <User className="w-4 h-4 text-primary" />
            </button>
          ) : (
            <button
              onClick={() => setShowSignInModal(true)}
              className="bg-hover border border-primary text-primary cursor-pointer px-3 py-2 rounded-xl text-xs font-medium transition-all duration-200 hover:bg-secondary shadow-sm flex-shrink-0"
            >
              Sign In
            </button>
          )}
        </div>
      </header>

      {/* Sign In Modal */}
      <SignInModal 
        isOpen={showSignInModal} 
        onClose={() => setShowSignInModal(false)} 
      />
    </>
  )
} 