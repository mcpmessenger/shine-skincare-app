'use client'

import { useTheme } from '@/hooks/useTheme'
import { Sun } from 'lucide-react'

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()

  return (
    <button
      onClick={toggleTheme}
      className="theme-toggle"
      aria-label="Toggle theme"
    >
      <div className="theme-toggle-track">
        <div className="theme-toggle-thumb">
          <Sun className="w-4 h-4" />
        </div>
      </div>
    </button>
  )
} 