'use client';

import Link from "next/link"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Sheet, SheetTrigger, SheetContent } from "@/components/ui/sheet"
import { Menu, Sun, ShoppingCart, User, LogOut } from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import { CartIcon } from "./cart-icon"
import { ThemeToggle } from "./theme-toggle"

export default function Header() {
  const { user, isAuthenticated, logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <header className="flex h-16 items-center justify-between px-4 md:px-6 border-b">
      <Link href="/" className="flex items-center gap-2" prefetch={false}>
        <Image 
          src="https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png" 
          alt="Shine Logo" 
          width={60} 
          height={24} 
          className="h-10 w-auto md:h-12 lg:h-14"
          unoptimized
        />
        <span className="sr-only">Shine</span>
      </Link>
      <nav className="hidden md:flex items-center gap-6 text-sm font-medium">
        <Link href="/skin-analysis" className="hover:underline underline-offset-4" prefetch={false}>
          Skin Analysis
        </Link>
        <Link href="/recommendations" className="hover:underline underline-offset-4" prefetch={false}>
          Recommendations
        </Link>
        <Link href="/cart" className="hover:underline underline-offset-4" prefetch={false}>
          Cart
        </Link>
        <Link href="/profile" className="hover:underline underline-offset-4" prefetch={false}>
          Profile
        </Link>
      </nav>
      <div className="flex items-center gap-4">
        <ThemeToggle />
        <CartIcon />
        {isAuthenticated ? (
          <div className="flex items-center gap-2">
            {user?.profile_picture_url && (
              <Image
                src={user.profile_picture_url}
                alt={user.name}
                width={32}
                height={32}
                className="rounded-full"
              />
            )}
            <span className="text-sm font-medium hidden sm:block">{user?.name}</span>
            <Button variant="ghost" size="icon" onClick={handleLogout} className="rounded-full">
              <LogOut className="h-5 w-5" />
              <span className="sr-only">Logout</span>
            </Button>
          </div>
        ) : (
          <Link href="/auth/login">
            <Button variant="outline">Login</Button>
          </Link>
        )}
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="outline" size="icon" className="md:hidden bg-transparent">
              <Menu className="h-6 w-6" />
              <span className="sr-only">Toggle navigation menu</span>
            </Button>
          </SheetTrigger>
          <SheetContent side="right">
            <div className="grid gap-6 p-6">
              <Link href="/" className="flex items-center gap-2" prefetch={false}>
                <Image 
                  src="https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png" 
                  alt="Shine Logo" 
                  width={60} 
                  height={24} 
                  className="h-10 w-auto"
                  unoptimized
                />
                <span className="sr-only">Shine</span>
              </Link>
              <nav className="grid gap-4 text-lg font-medium">
                <Link href="/skin-analysis" className="hover:underline underline-offset-4" prefetch={false}>
                  Skin Analysis
                </Link>
                <Link href="/recommendations" className="hover:underline underline-offset-4" prefetch={false}>
                  Recommendations
                </Link>
                <Link href="/cart" className="hover:underline underline-offset-4" prefetch={false}>
                  Cart
                </Link>
                <Link href="/profile" className="hover:underline underline-offset-4" prefetch={false}>
                  Profile
                </Link>
                {isAuthenticated ? (
                  <>
                    <div className="flex items-center gap-2 py-2">
                      {user?.profile_picture_url && (
                        <Image
                          src={user.profile_picture_url}
                          alt={user.name}
                          width={32}
                          height={32}
                          className="rounded-full"
                        />
                      )}
                      <span className="font-medium">{user?.name}</span>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="flex items-center gap-2 hover:underline underline-offset-4 text-left"
                    >
                      <LogOut className="h-5 w-5" />
                      Logout
                    </button>
                  </>
                ) : (
                  <>
                    <Link href="/auth/login" className="hover:underline underline-offset-4" prefetch={false}>
                      Login
                    </Link>
                    <Link href="/auth/signup" className="hover:underline underline-offset-4" prefetch={false}>
                      Sign Up
                    </Link>
                  </>
                )}
              </nav>
            </div>
          </SheetContent>
        </Sheet>
      </div>
    </header>
  )
}
