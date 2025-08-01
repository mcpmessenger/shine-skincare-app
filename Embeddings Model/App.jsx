import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Camera, Upload, Sparkles, Shield, Zap, Users, Star, CheckCircle, Settings, User, CreditCard } from 'lucide-react'
import { motion } from 'framer-motion'
import './App.css'

// Components
import Header from './components/Header'
import SkinAnalysis from './components/SkinAnalysis'
import Dashboard from './components/Dashboard'
import Settings from './components/Settings'
import Pricing from './components/Pricing'

function App() {
  const [user, setUser] = useState(null)
  const [currentPage, setCurrentPage] = useState('home')

  useEffect(() => {
    // Check for existing authentication
    const token = localStorage.getItem('shine_token')
    if (token) {
      // Validate token and get user info
      fetchUserInfo(token)
    }
  }, [])

  const fetchUserInfo = async (token) => {
    try {
      const response = await fetch('/api/auth/user', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const userData = await response.json()
        setUser(userData.user)
      }
    } catch (error) {
      console.error('Error fetching user info:', error)
    }
  }

  const handleGoogleLogin = async () => {
    // Implement Google OAuth login
    try {
      // This would integrate with Google OAuth
      console.log('Google login initiated')
    } catch (error) {
      console.error('Login error:', error)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('shine_token')
    setUser(null)
    setCurrentPage('home')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50">
      <Header 
        user={user} 
        onLogin={handleGoogleLogin}
        onLogout={handleLogout}
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
      />
      
      <main className="container mx-auto px-4 py-8">
        {currentPage === 'home' && <HomePage setCurrentPage={setCurrentPage} />}
        {currentPage === 'analysis' && <SkinAnalysis user={user} />}
        {currentPage === 'dashboard' && <Dashboard user={user} />}
        {currentPage === 'settings' && <Settings user={user} />}
        {currentPage === 'pricing' && <Pricing user={user} />}
      </main>
    </div>
  )
}

function HomePage({ setCurrentPage }) {
  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <motion.section 
        className="text-center py-20"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <div className="max-w-4xl mx-auto">
          <motion.div
            className="inline-flex items-center gap-2 bg-purple-100 text-purple-700 px-4 py-2 rounded-full text-sm font-medium mb-6"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
          >
            <Sparkles className="w-4 h-4" />
            AI-Powered Skin Analysis
          </motion.div>
          
          <motion.h1 
            className="text-5xl md:text-7xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            Your Personalized
            <br />
            Skincare Journey
          </motion.h1>
          
          <motion.p 
            className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            Get AI-powered skin analysis using advanced computer vision and the SCIN medical dataset. 
            Receive personalized product recommendations tailored to your unique skin profile.
          </motion.p>
          
          <motion.div 
            className="flex flex-col sm:flex-row gap-4 justify-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <Button 
              size="lg" 
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-8 py-6 text-lg"
              onClick={() => setCurrentPage('analysis')}
            >
              <Camera className="w-5 h-5 mr-2" />
              Start Skin Analysis
            </Button>
            <Button 
              size="lg" 
              variant="outline" 
              className="border-2 border-purple-200 hover:border-purple-300 px-8 py-6 text-lg"
              onClick={() => setCurrentPage('pricing')}
            >
              View Pricing
            </Button>
          </motion.div>
        </div>
      </motion.section>

      {/* Features Section */}
      <motion.section 
        className="py-16"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
        viewport={{ once: true }}
      >
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Advanced AI Technology
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Powered by OpenAI embeddings, Google Vision API, and the comprehensive SCIN medical dataset
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              icon: <Zap className="w-8 h-8 text-yellow-500" />,
              title: "Real-time Analysis",
              description: "Get instant skin condition analysis using advanced computer vision and machine learning algorithms"
            },
            {
              icon: <Shield className="w-8 h-8 text-green-500" />,
              title: "Medical-Grade Accuracy",
              description: "Powered by the SCIN dataset with 10,000+ dermatology cases for precise condition matching"
            },
            {
              icon: <Users className="w-8 h-8 text-blue-500" />,
              title: "Personalized Recommendations",
              description: "Receive tailored product suggestions based on your unique skin profile and concerns"
            }
          ].map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <Card className="h-full hover:shadow-lg transition-shadow duration-300">
                <CardHeader className="text-center">
                  <div className="mx-auto mb-4 p-3 bg-gray-50 rounded-full w-fit">
                    {feature.icon}
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-center">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* How It Works Section */}
      <motion.section 
        className="py-16 bg-white rounded-3xl shadow-sm"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
        viewport={{ once: true }}
      >
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            How It Works
          </h2>
          <p className="text-lg text-gray-600">
            Simple, fast, and accurate skin analysis in just a few steps
          </p>
        </div>
        
        <div className="grid md:grid-cols-4 gap-8">
          {[
            {
              step: "1",
              title: "Take Photo",
              description: "Capture a clear selfie with good lighting"
            },
            {
              step: "2", 
              title: "AI Analysis",
              description: "Our AI analyzes your skin using Google Vision API"
            },
            {
              step: "3",
              title: "SCIN Matching",
              description: "Find similar conditions in medical dataset"
            },
            {
              step: "4",
              title: "Get Results",
              description: "Receive personalized recommendations"
            }
          ].map((step, index) => (
            <motion.div
              key={index}
              className="text-center"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <div className="w-12 h-12 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full flex items-center justify-center text-lg font-bold mx-auto mb-4">
                {step.step}
              </div>
              <h3 className="text-lg font-semibold mb-2">{step.title}</h3>
              <p className="text-gray-600 text-sm">{step.description}</p>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* CTA Section */}
      <motion.section 
        className="text-center py-16"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
        viewport={{ once: true }}
      >
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-3xl p-12 text-white">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Transform Your Skincare?
          </h2>
          <p className="text-lg mb-8 opacity-90">
            Join thousands of users who have discovered their perfect skincare routine
          </p>
          <Button 
            size="lg" 
            className="bg-white text-purple-600 hover:bg-gray-100 px-8 py-6 text-lg"
            onClick={() => setCurrentPage('analysis')}
          >
            Start Your Analysis Now
          </Button>
        </div>
      </motion.section>
    </div>
  )
}

export default App
