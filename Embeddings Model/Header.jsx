import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Sparkles, User, Settings, CreditCard, LogOut, Menu } from 'lucide-react'
import { motion } from 'framer-motion'

export default function Header({ user, onLogin, onLogout, currentPage, setCurrentPage }) {
  return (
    <motion.header 
      className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <motion.div 
            className="flex items-center gap-2 cursor-pointer"
            onClick={() => setCurrentPage('home')}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              Shine
            </span>
          </motion.div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center gap-6">
            {user && (
              <>
                <Button
                  variant={currentPage === 'analysis' ? 'default' : 'ghost'}
                  onClick={() => setCurrentPage('analysis')}
                  className={currentPage === 'analysis' ? 'bg-purple-600 hover:bg-purple-700' : ''}
                >
                  Skin Analysis
                </Button>
                <Button
                  variant={currentPage === 'dashboard' ? 'default' : 'ghost'}
                  onClick={() => setCurrentPage('dashboard')}
                  className={currentPage === 'dashboard' ? 'bg-purple-600 hover:bg-purple-700' : ''}
                >
                  Dashboard
                </Button>
                <Button
                  variant={currentPage === 'settings' ? 'default' : 'ghost'}
                  onClick={() => setCurrentPage('settings')}
                  className={currentPage === 'settings' ? 'bg-purple-600 hover:bg-purple-700' : ''}
                >
                  <Settings className="w-4 h-4 mr-2" />
                  Settings
                </Button>
              </>
            )}
            <Button
              variant={currentPage === 'pricing' ? 'default' : 'ghost'}
              onClick={() => setCurrentPage('pricing')}
              className={currentPage === 'pricing' ? 'bg-purple-600 hover:bg-purple-700' : ''}
            >
              <CreditCard className="w-4 h-4 mr-2" />
              Pricing
            </Button>
          </nav>

          {/* User Actions */}
          <div className="flex items-center gap-4">
            {user ? (
              <div className="flex items-center gap-3">
                {/* Usage Badge */}
                <Badge variant="secondary" className="hidden sm:flex">
                  {user.profile?.api_calls_used || 0} / {user.profile?.api_calls_limit || 10} calls
                </Badge>
                
                {/* User Menu */}
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center">
                    <User className="w-4 h-4 text-white" />
                  </div>
                  <span className="hidden sm:block text-sm font-medium">
                    {user.user_metadata?.full_name || user.email}
                  </span>
                </div>
                
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onLogout}
                  className="text-gray-600 hover:text-gray-900"
                >
                  <LogOut className="w-4 h-4" />
                </Button>
              </div>
            ) : (
              <Button
                onClick={onLogin}
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white"
              >
                Sign In with Google
              </Button>
            )}
          </div>
        </div>
      </div>
    </motion.header>
  )
}

