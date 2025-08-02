'use client'

import { useTheme } from 'next-themes'
import { Moon, Sun } from 'lucide-react'

export default function MinimalTest() {
  const { theme, setTheme } = useTheme()

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800">
      {/* Simple Header */}
      <header className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm border-b border-slate-200 dark:border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
              Minimal Tailwind Test
            </h1>
            
            <button
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
            >
              {theme === 'dark' ? (
                <Sun className="h-5 w-5 text-yellow-500" />
              ) : (
                <Moon className="h-5 w-5 text-slate-600" />
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-slate-900 dark:text-white mb-4">
            Tailwind CSS Test
          </h2>
          <p className="text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto">
            If you can see styled content below, Tailwind is working properly!
          </p>
        </div>

        {/* Test Cards */}
        <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-700 p-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <div className="text-2xl">✅</div>
              </div>
              <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                Tailwind Working
              </h3>
              <p className="text-slate-600 dark:text-slate-300">
                If you can see this styled card, Tailwind is working!
              </p>
            </div>
          </div>

          <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-700 p-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <div className="text-2xl">🎨</div>
              </div>
              <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                Dark Mode
              </h3>
              <p className="text-slate-600 dark:text-slate-300">
                Click the theme toggle to test dark mode!
              </p>
            </div>
          </div>

          <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-700 p-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <div className="text-2xl">⚡</div>
              </div>
              <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                Responsive
              </h3>
              <p className="text-slate-600 dark:text-slate-300">
                This layout should work on all screen sizes!
              </p>
            </div>
          </div>
        </div>

        {/* Color Test */}
        <div className="mt-12 max-w-4xl mx-auto">
          <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-6 text-center">
            Color Palette Test
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-red-500 text-white p-4 rounded-lg text-center">Red</div>
            <div className="bg-blue-500 text-white p-4 rounded-lg text-center">Blue</div>
            <div className="bg-green-500 text-white p-4 rounded-lg text-center">Green</div>
            <div className="bg-yellow-500 text-white p-4 rounded-lg text-center">Yellow</div>
          </div>
        </div>
      </main>
    </div>
  )
} 