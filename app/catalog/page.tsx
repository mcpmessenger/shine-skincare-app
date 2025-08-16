'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Star, ShoppingCart } from 'lucide-react'
import { useTheme } from '@/hooks/useTheme'
import { useAuth } from '@/hooks/useAuth'
import { useCart } from '@/hooks/useCart'
import { CartDrawer } from '@/components/cart-drawer'
import { SignInModal } from '@/components/sign-in-modal'
import { products } from '@/lib/products'
import { Header } from '@/components/header'

// Interface for recommended products with additional properties
interface RecommendedProduct {
  id: string
  name: string
  price: number
  image: string
  description: string
  category: string
  matchReason?: string
  score?: number
}

interface AnalysisData {
  health_score: number
  conditions: string[]
  skinType?: string
  concerns?: string[]
  metrics?: any
  intelligentRecommendations?: RecommendedProduct[]
}

export default function CatalogPage() {
  const { theme } = useTheme()
  const { state: authState } = useAuth()
  const { dispatch, isAuthenticated } = useCart()
  const [showSignInModal, setShowSignInModal] = useState(false)
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null)
  const [showRecommendations, setShowRecommendations] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  // Parse analysis data from URL parameters
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search)
      const analysisParam = urlParams.get('analysis')
      if (analysisParam) {
        try {
          const parsed = JSON.parse(decodeURIComponent(analysisParam))
          setAnalysisData(parsed)
          setShowRecommendations(true)
        } catch (error) {
          console.error('Failed to parse analysis data:', error)
        }
      }
    }
    
    // Set loading to false after initialization
    setTimeout(() => {
      setIsLoading(false);
    }, 1000); // Show logo for 1 second
  }, [])

  useEffect(() => {
    // Fetch intelligent recommendations if we have analysis data
    if (analysisData && !analysisData.intelligentRecommendations) {
      fetchIntelligentRecommendations()
    }
  }, [analysisData])

  const getRecommendedProducts = (): RecommendedProduct[] => {
    if (!analysisData) return []
    
    // If we have intelligent recommendations from the API, use those
    if (analysisData.intelligentRecommendations && analysisData.intelligentRecommendations.length > 0) {
      return analysisData.intelligentRecommendations
    }
    
    // Fallback to local logic if no API recommendations
    const recommended = products.filter(product => {
      // Match based on conditions
      const conditionMatch = analysisData.conditions.some(condition =>
        product.description.toLowerCase().includes(condition.toLowerCase()) ||
        product.name.toLowerCase().includes(condition.toLowerCase())
      )
      
      // Match based on health score
      const healthMatch = analysisData.health_score < 50 
        ? product.category === 'treatment' || product.category === 'serum'
        : product.category === 'moisturizer' || product.category === 'sunscreen'
      
      return conditionMatch || healthMatch
    })
    
    // Remove duplicates and limit to top 6, convert to RecommendedProduct type
    const unique = recommended.filter((product, index, self) =>
      index === self.findIndex(p => p.id === product.id)
    )
    
    return unique.slice(0, 6).map(product => ({
      ...product,
      matchReason: `Matched based on your skin profile`,
      score: 0
    }))
  }

  const fetchIntelligentRecommendations = async () => {
    if (!analysisData) return
    
    try {
      // Create a mock image for the API call (since we already have analysis data)
      const mockImage = new File(['mock'], 'mock.jpg', { type: 'image/jpeg' })
      const formData = new FormData()
      formData.append('image', mockImage)
      
      const response = await fetch('/api/analysis/skin', {
        method: 'POST',
        body: formData
      })
      
      if (response.ok) {
        const result = await response.json()
        if (result.products && result.products.length > 0) {
          setAnalysisData(prev => prev ? {
            ...prev,
            intelligentRecommendations: result.products,
            skinType: result.skinType,
            concerns: result.concerns,
            metrics: result.metrics
          } : null)
        }
      }
    } catch (error) {
      console.error('Failed to fetch intelligent recommendations:', error)
    }
  }

  const addToCart = (product: any) => {
    if (!isAuthenticated) {
      setShowSignInModal(true)
      return
    }
    dispatch({ type: 'ADD_ITEM', payload: product })
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-primary text-primary flex items-center justify-center">
        <div className="text-center">
          <img 
            src="https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png" 
            alt="Shine Skin Collective" 
            className="w-32 h-32 mx-auto mb-6 animate-pulse"
          />
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-300 font-light">Loading Shine...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-primary text-primary">
      {/* Header */}
      <Header title="Product Catalog" />

      {/* Analysis Results Summary */}
      {showRecommendations && analysisData && (
        <div className="max-w-6xl mx-auto p-4 bg-secondary rounded-xl border border-primary mb-4">
          <div className="flex items-center gap-2 mb-2">
            <Star className="text-blue-500" />
            <h3 className="text-xl font-semibold text-primary">
              Personalized Recommendations
            </h3>
          </div>
          <div className="flex gap-4 flex-wrap text-sm text-secondary">
            <span>Health Score: {Math.round(analysisData.health_score)}%</span>
            <span>•</span>
            <span>Conditions: {analysisData.conditions.slice(0, 3).join(', ')}</span>
            {analysisData.conditions.length > 3 && <span>+{analysisData.conditions.length - 3} more</span>}
          </div>
        </div>
      )}

      {/* Recommended Products */}
      {showRecommendations && analysisData && getRecommendedProducts().length > 0 && (
        <div className="max-w-6xl mx-auto p-4">
          <h2 className="text-2xl font-semibold mb-4 text-primary">
            Recommended Products
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {getRecommendedProducts().map(product => (
              <div key={product.id} className="bg-secondary rounded-xl p-6 border-2 border-blue-500 relative">
                <div className="absolute top-2 right-2 bg-blue-500 text-white px-2 py-1 rounded text-xs font-bold">
                  RECOMMENDED
                </div>
                
                {/* Product Image */}
                {product.image && (
                  <div className="mb-4 text-center">
                    <img
                      src={product.image}
                      alt={product.name}
                      className="w-full h-48 object-cover rounded-lg border border-primary"
                      onError={(e) => {
                        console.log('🖼️ Product image failed to load:', product.image);
                        const target = e.target as HTMLImageElement;
                        target.src = 'https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png';
                      }}
                    />
                  </div>
                )}
                
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-lg font-bold text-primary">
                    {product.name}
                  </h3>
                  <span className="text-xl font-bold text-blue-500">
                    ${product.price.toFixed(2)}
                  </span>
                </div>
                
                <p className="text-secondary text-sm mb-4 leading-relaxed">
                  {product.description}
                </p>
                
                {/* Recommendation Reason */}
                {product.matchReason && (
                  <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-center gap-2 mb-1">
                      <Star className="w-4 h-4 text-blue-500" />
                      <span className="text-sm font-medium text-blue-700">Why Recommended</span>
                    </div>
                    <p className="text-sm text-blue-600">{product.matchReason}</p>
                  </div>
                )}
                
                <div className="flex justify-between items-center">
                  <span className="px-3 py-1 bg-blue-100 border border-blue-300 rounded-xl text-xs capitalize text-blue-700">
                    {product.category}
                  </span>
                  
                  <button
                    onClick={() => addToCart(product)}
                    className={`flex items-center gap-2 px-6 py-3 bg-blue-500 border border-blue-500 rounded-lg text-white text-sm font-bold transition-all duration-300 ${
                      isAuthenticated ? 'cursor-pointer hover:bg-blue-600' : 'cursor-not-allowed opacity-50'
                    }`}
                  >
                    <ShoppingCart />
                    {isAuthenticated ? 'Add to Cart' : 'Sign In to Add'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* All Products */}
      <div className="max-w-6xl mx-auto p-4">
        <h2 className="text-2xl font-semibold mb-4 text-primary">
          All Products
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map(product => (
            <div key={product.id} className="bg-secondary rounded-xl p-6 border border-primary">
              
              {/* Product Image */}
              {product.image && (
                <div className="mb-4 text-center">
                  <img
                    src={product.image}
                    alt={product.name}
                    className="w-full h-48 object-cover rounded-lg border border-primary"
                    onError={(e) => {
                      console.log('🖼️ Product image failed to load:', product.image);
                      const target = e.target as HTMLImageElement;
                      target.src = 'https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png';
                    }}
                  />
                </div>
              )}
              
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-lg font-bold text-primary">
                  {product.name}
                </h3>
                <span className="text-xl font-bold text-blue-500">
                  ${product.price.toFixed(2)}
                </span>
              </div>
              
              <p className="text-secondary text-sm mb-4 leading-relaxed">
                {product.description}
              </p>
              
              <div className="flex justify-between items-center">
                <span className="px-3 py-1 bg-blue-100 border border-blue-300 rounded-xl text-xs capitalize text-blue-700">
                  {product.category}
                </span>
                
                <button
                  onClick={() => addToCart(product)}
                  className={`flex items-center gap-2 px-6 py-3 bg-blue-500 border border-blue-500 rounded-lg text-white text-sm font-bold transition-all duration-300 ${
                    isAuthenticated ? 'cursor-pointer hover:bg-blue-600' : 'cursor-not-allowed opacity-50'
                  }`}
                >
                  <ShoppingCart />
                  {isAuthenticated ? 'Add to Cart' : 'Sign In to Add'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <footer className="p-1 px-4 text-center text-xs text-primary flex-shrink-0 mt-8">
        © 2025 SHINE SKIN COLLECTIVE. All Rights Reserved.
      </footer>

      {/* Sign In Modal */}
      <SignInModal 
        isOpen={showSignInModal}
        onClose={() => setShowSignInModal(false)}
        onSuccess={() => setShowSignInModal(false)}
      />
    </div>
  )
}

// Using imported products from lib/products.ts 