'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Star, ShoppingCart, CheckCircle, AlertCircle } from 'lucide-react'
import { useTheme } from '@/hooks/useTheme'
import { useAuth } from '@/hooks/useAuth'
import { useCart } from '@/hooks/useCart'
import { CartDrawer } from '@/components/cart-drawer'
import { ThemeToggle } from '@/components/theme-toggle'
import { SignInModal } from '@/components/sign-in-modal'
import { products } from '@/lib/products'
import { Header } from '@/components/header'

interface AnalysisResult {
  success: boolean
  confidence_score: number
  analysis_summary: string
  primary_concerns: string[]
  detected_conditions: Array<{
    confidence: number
    description: string
    name: string
    severity: string
    source: string
  }>
  severity_level: string
  top_recommendations: string[]
  immediate_actions: string[]
  lifestyle_changes: string[]
  medical_advice: string[]
  prevention_tips: string[]
  best_match: string
  condition_matches: any[]
  face_detection?: {
    confidence: number
    detected: boolean
    face_bounds?: {
      x: number
      y: number
      width: number
      height: number
    }
    image_dimensions?: number[]
  }
}

export default function SuggestionsPage() {
  const { theme } = useTheme()
  const { state: authState } = useAuth()
  const { dispatch, isAuthenticated } = useCart()
  const [showSignInModal, setShowSignInModal] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)

  // Parse analysis data from URL parameters
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search)
      const analysisParam = urlParams.get('analysis')
      if (analysisParam) {
        try {
          const parsed = JSON.parse(decodeURIComponent(analysisParam))
          setAnalysisResult(parsed)
        } catch (error) {
          console.error('Failed to parse analysis data:', error)
        }
      }
    }
  }, [])

  const addToCart = (product: any) => {
    if (!isAuthenticated) {
      setShowSignInModal(true)
      return
    }
    dispatch({ type: 'ADD_ITEM', payload: product })
  }



  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'low': return '#10b981'
      case 'moderate': return '#f59e0b'
      case 'high': return '#ef4444'
      default: return '#6b7280'
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return '#10b981'
    if (confidence >= 60) return '#f59e0b'
    return '#ef4444'
  }

  // Map recommendations to real products
  const getRecommendedProducts = () => {
    if (!analysisResult?.top_recommendations) return []
    
    const recommendations = analysisResult.top_recommendations
    const recommendedProducts = []
    
    // Map recommendations to actual products
    recommendations.forEach(rec => {
      const recLower = rec.toLowerCase()
      
      // Vitamin C recommendations
      if (recLower.includes('vitamin c') || recLower.includes('brightening')) {
        const vitaminCProduct = products.find(p => 
          p.name.toLowerCase().includes('vitamin c') || 
          p.name.toLowerCase().includes('ce ferulic')
        )
        if (vitaminCProduct) {
          recommendedProducts.push({ ...vitaminCProduct, match: rec })
        }
      }
      
      // Cleanser recommendations
      if (recLower.includes('cleanser') || recLower.includes('gentle')) {
        const cleanserProducts = products.filter(p => p.category === 'cleanser')
        if (cleanserProducts.length > 0) {
          recommendedProducts.push({ ...cleanserProducts[0], match: rec })
        }
      }
      
      // Moisturizer recommendations
      if (recLower.includes('moisturizer') || recLower.includes('hydration') || recLower.includes('hyaluronic')) {
        const moisturizerProducts = products.filter(p => p.category === 'moisturizer')
        if (moisturizerProducts.length > 0) {
          recommendedProducts.push({ ...moisturizerProducts[0], match: rec })
        }
      }
      
      // Treatment recommendations (retinol, anti-aging)
      if (recLower.includes('retinol') || recLower.includes('anti-aging') || recLower.includes('treatment')) {
        const treatmentProducts = products.filter(p => p.category === 'treatment')
        if (treatmentProducts.length > 0) {
          recommendedProducts.push({ ...treatmentProducts[0], match: rec })
        }
      }
      
      // Serum recommendations
      if (recLower.includes('serum') || recLower.includes('niacinamide')) {
        const serumProducts = products.filter(p => p.category === 'serum')
        if (serumProducts.length > 0) {
          recommendedProducts.push({ ...serumProducts[0], match: rec })
        }
      }
      
      // Sunscreen recommendations
      if (recLower.includes('sunscreen') || recLower.includes('spf')) {
        const sunscreenProducts = products.filter(p => p.category === 'sunscreen')
        if (sunscreenProducts.length > 0) {
          recommendedProducts.push({ ...sunscreenProducts[0], match: rec })
        }
      }
    })
    
    // If no specific matches, add some general recommendations based on conditions
    if (recommendedProducts.length === 0) {
      const detectedConditions = analysisResult.detected_conditions || []
      const hasAcne = detectedConditions.some(c => c.name.toLowerCase().includes('acne'))
      const hasAging = detectedConditions.some(c => c.name.toLowerCase().includes('aging') || c.name.toLowerCase().includes('wrinkle'))
      const hasPigmentation = detectedConditions.some(c => c.name.toLowerCase().includes('pigment') || c.name.toLowerCase().includes('spot'))
      
      if (hasAcne) {
        const acneProducts = products.filter(p => 
          p.description.toLowerCase().includes('acne') || 
          p.name.toLowerCase().includes('cleansing')
        )
        if (acneProducts.length > 0) {
          recommendedProducts.push({ ...acneProducts[0], match: 'Acne treatment' })
        }
      }
      
      if (hasAging) {
        const antiAgingProducts = products.filter(p => 
          p.description.toLowerCase().includes('anti-aging') || 
          p.name.toLowerCase().includes('advanced')
        )
        if (antiAgingProducts.length > 0) {
          recommendedProducts.push({ ...antiAgingProducts[0], match: 'Anti-aging treatment' })
        }
      }
      
      if (hasPigmentation) {
        const pigmentProducts = products.filter(p => 
          p.description.toLowerCase().includes('pigment') || 
          p.name.toLowerCase().includes('pigment')
        )
        if (pigmentProducts.length > 0) {
          recommendedProducts.push({ ...pigmentProducts[0], match: 'Pigmentation treatment' })
        }
      }
      
      // Default to basic skincare if no specific conditions
      if (recommendedProducts.length === 0) {
        const basicProducts = products.slice(0, 3) // First 3 products as basic recommendations
        basicProducts.forEach(product => {
          recommendedProducts.push({ ...product, match: 'Basic skincare' })
        })
      }
    }
    
    // Remove duplicates and limit to top 6
    const unique = recommendedProducts.filter((product, index, self) =>
      index === self.findIndex(p => p.id === product.id)
    )
    
    return unique.slice(0, 6)
  }

  if (!analysisResult) {
    return (
      <div className="min-h-screen bg-primary text-primary flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-semibold mb-4">No Analysis Results Found</h2>
          <p className="text-secondary mb-6">Please complete a skin analysis first.</p>
          <Link href="/" className="btn btn-primary">
            Go to Analysis
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-primary text-primary">
      {/* Header */}
      <Header title="Personalized Recommendations" />

      <div className="max-w-6xl mx-auto p-4">
        {/* Analysis Summary */}
        <div className="card mb-8">
          <div className="flex items-center gap-2 mb-4">
            <Star className="text-blue-500" />
            <h2 className="text-xl font-semibold">
              Analysis Results
            </h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
            <div className="card">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="text-green-500" />
                <span className="font-semibold">Analysis Confidence</span>
              </div>
              <span className="text-2xl font-bold text-green-500">
                {analysisResult.confidence_score}%
              </span>
            </div>
            
            {analysisResult.severity_level && (
              <div className="card">
                <div className="flex items-center gap-2 mb-2">
                  <AlertCircle className="text-orange-500" />
                  <span className="font-semibold">Severity Level</span>
                </div>
                <span className="text-2xl font-bold text-orange-500">
                  {analysisResult.severity_level}
                </span>
              </div>
            )}

            {analysisResult.face_detection && (
              <div className="card">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle className={analysisResult.face_detection.detected ? "text-green-500" : "text-red-500"} />
                  <span className="font-semibold">Face Detection</span>
                </div>
                <div className="flex flex-col gap-1">
                  <span className={`text-lg font-bold ${analysisResult.face_detection.detected ? "text-green-500" : "text-red-500"}`}>
                    {analysisResult.face_detection.detected ? "Detected" : "Not Detected"}
                  </span>
                  <span className="text-sm text-secondary">
                    Confidence: {Math.round(analysisResult.face_detection.confidence * 100)}%
                  </span>
                </div>
              </div>
            )}
          </div>

          {analysisResult.analysis_summary && (
            <div className="card mb-4">
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="text-blue-500" />
                <span className="font-semibold">Analysis Summary</span>
              </div>
              <p className="leading-relaxed">
                {analysisResult.analysis_summary}
              </p>
            </div>
          )}

          {analysisResult.detected_conditions && analysisResult.detected_conditions.length > 0 && (
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <AlertCircle className="text-red-500" />
                <span className="font-semibold">Detected Conditions</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {analysisResult.detected_conditions.map((condition, index) => (
                  <div key={index} className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3 text-sm">
                    <div className="font-semibold mb-1 text-red-800 dark:text-red-200">
                      {condition.name}
                    </div>
                    <div className="text-red-600 dark:text-red-300 text-xs mb-2">
                      {condition.description}
                    </div>
                    <div className="flex justify-between text-xs text-red-700 dark:text-red-300">
                      <span>Confidence: {condition.confidence}%</span>
                      <span>Severity: {condition.severity}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Combined Recommendations and Products */}
        {analysisResult.top_recommendations && analysisResult.top_recommendations.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Star className="text-blue-500" />
              Personalized Recommendations & Products
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {analysisResult.top_recommendations.map((recommendation, index) => {
                // Find matching product for this recommendation
                const matchingProduct = getRecommendedProducts().find(product => 
                  product.match === recommendation || 
                  recommendation.toLowerCase().includes(product.name.toLowerCase()) ||
                  product.name.toLowerCase().includes(recommendation.toLowerCase())
                )
                
                return (
                  <div key={index} className="card-product border-2 border-blue-500 relative">
                    {matchingProduct && (
                      <div className="absolute top-2 left-2 bg-blue-500 text-white px-2 py-1 rounded text-xs font-bold z-10">
                        RECOMMENDED
                      </div>
                    )}
                    
                    <div className="flex gap-4 mb-4">
                      {matchingProduct?.image && (
                        <img
                          src={matchingProduct.image}
                          alt={matchingProduct.name}
                          className="w-20 h-20 object-cover rounded-lg border border-primary"
                          onError={(e) => {
                            e.currentTarget.style.display = 'none'
                          }}
                        />
                      )}
                      <div className="flex-1">
                        <div className="flex justify-between items-start mb-2">
                          <h3 className="text-lg font-semibold">
                            {matchingProduct ? matchingProduct.name : `Recommendation ${index + 1}`}
                          </h3>
                          {matchingProduct && (
                            <span className="text-xl font-bold text-blue-500">
                              ${matchingProduct.price.toFixed(2)}
                            </span>
                          )}
                        </div>
                        
                        <p className="text-secondary text-sm leading-relaxed">
                          {recommendation}
                        </p>
                        
                        {matchingProduct && (
                          <p className="text-secondary text-xs mt-2">
                            {matchingProduct.description}
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex justify-between items-center">
                      {matchingProduct && (
                        <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 border border-blue-300 dark:border-blue-700 rounded-xl text-xs capitalize text-blue-800 dark:text-blue-200 font-medium">
                          {matchingProduct.category}
                        </span>
                      )}
                      
                      {matchingProduct ? (
                        <button
                          onClick={() => addToCart(matchingProduct)}
                          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-300 ${
                            isAuthenticated 
                              ? 'bg-blue-500 text-white hover:bg-blue-600' 
                              : 'bg-blue-300 text-white cursor-not-allowed'
                          }`}
                        >
                          <ShoppingCart />
                          {isAuthenticated ? 'Add to Cart' : 'Sign In to Add'}
                        </button>
                      ) : (
                        <div className="text-xs text-secondary">
                          General recommendation
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Additional Recommended Products (if any that weren't matched) */}
        {(() => {
          const matchedRecommendations = analysisResult.top_recommendations || []
          const allRecommendedProducts = getRecommendedProducts()
          const unmatchedProducts = allRecommendedProducts.filter(product => 
            !matchedRecommendations.some(rec => 
              rec === product.match || 
              rec.toLowerCase().includes(product.name.toLowerCase()) ||
              product.name.toLowerCase().includes(rec.toLowerCase())
            )
          )
          
          if (unmatchedProducts.length > 0) {
            return (
              <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <ShoppingCart className="text-green-500" />
                  Additional Recommended Products
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {unmatchedProducts.map(product => (
                    <div key={product.id} className="card-product border-2 border-green-500 relative">
                      <div className="absolute top-2 left-2 bg-green-500 text-white px-2 py-1 rounded text-xs font-bold z-10">
                        RECOMMENDED
                      </div>
                      <div className="flex gap-4 mb-4">
                        {product.image && (
                          <img
                            src={product.image}
                            alt={product.name}
                            className="w-20 h-20 object-cover rounded-lg border border-primary"
                            onError={(e) => {
                              e.currentTarget.style.display = 'none'
                            }}
                          />
                        )}
                        <div className="flex-1">
                          <div className="flex justify-between items-start mb-2">
                            <h3 className="text-lg font-semibold">
                              {product.name}
                            </h3>
                            <span className="text-xl font-bold text-green-500">
                              ${product.price.toFixed(2)}
                            </span>
                          </div>
                          
                          <p className="text-secondary text-sm leading-relaxed">
                            {product.description}
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex justify-between items-center">
                        <span className="px-3 py-1 bg-green-100 dark:bg-green-900/30 border border-green-300 dark:border-green-700 rounded-xl text-xs capitalize text-green-800 dark:text-green-200 font-medium">
                          {product.category}
                        </span>
                        
                        <button
                          onClick={() => addToCart(product)}
                          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-300 ${
                            isAuthenticated 
                              ? 'bg-green-500 text-white hover:bg-green-600' 
                              : 'bg-green-300 text-white cursor-not-allowed'
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
            )
          }
          return null
        })()}

        {/* Immediate Actions */}
        {analysisResult.immediate_actions && analysisResult.immediate_actions.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <AlertCircle className="text-orange-500" />
              Immediate Actions
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {analysisResult.immediate_actions.map((action, index) => (
                <div key={index} className="card">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertCircle className="text-orange-500" />
                    <span className="font-semibold">Action {index + 1}</span>
                  </div>
                  <p className="leading-relaxed">
                    {action}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Lifestyle Changes */}
        {analysisResult.lifestyle_changes && analysisResult.lifestyle_changes.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <AlertCircle className="text-green-500" />
              Lifestyle Changes
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {analysisResult.lifestyle_changes.map((change, index) => (
                <div key={index} className="card">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertCircle className="text-green-500" />
                    <span className="font-semibold">Change {index + 1}</span>
                  </div>
                  <p className="leading-relaxed">
                    {change}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="text-center mt-8 flex gap-4 justify-center flex-wrap">
          <Link href="/catalog" className="btn btn-primary flex items-center gap-2">
            <ShoppingCart />
            View All Products
          </Link>
          <Link href="/" className="btn btn-secondary flex items-center gap-2">
            <ArrowLeft />
            New Analysis
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="p-1 text-center text-xs text-tertiary mt-8">
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