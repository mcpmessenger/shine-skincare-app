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
  // New V4 format fields
  status?: string
  analysis_type?: string
  demographics?: any
  face_detection?: {
    detected: boolean
    confidence: number
    face_bounds?: {
      x: number
      y: number
      width: number
      height: number
    }
    method?: string
    quality_metrics?: {
      overall_quality: string
      quality_score: number
    }
  }
  skin_analysis?: {
    overall_health_score: number
    texture: string
    tone: string
    conditions_detected: Array<{
      condition: string
      severity: string
      confidence: number
      location: string
      description: string
    }>
    analysis_confidence: number
  }
  similarity_search?: {
    dataset_used: string
    similar_cases: Array<{
      condition: string
      similarity_score: number
      dataset_source: string
      demographic_match: string
      treatment_suggestions: string[]
    }>
  }
  recommendations?: {
    immediate_care: string[]
    long_term_care: string[]
    professional_consultation: boolean
  }
  quality_assessment?: {
    image_quality: string
    confidence_reliability: string
  }
  
  // Legacy V3 format fields (for backward compatibility)
  success?: boolean
  confidence_score?: number
  analysis_summary?: string
  primary_concerns?: string[]
  detected_conditions?: Array<{
    confidence: number
    description: string
    name: string
    severity: string
    source: string
  }>
  severity_level?: string
  top_recommendations?: string[]
  immediate_actions?: string[]
  lifestyle_changes?: string[]
  medical_advice?: string[]
  prevention_tips?: string[]
  best_match?: string
  condition_matches?: any[]
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
    // Handle new V4 format
    if (analysisResult?.recommendations?.immediate_care) {
      const recommendations = [
        ...analysisResult.recommendations.immediate_care,
        ...analysisResult.recommendations.long_term_care
      ]
      return mapRecommendationsToProducts(recommendations)
    }
    
    // Handle legacy V3 format
    if (analysisResult?.top_recommendations) {
      return mapRecommendationsToProducts(analysisResult.top_recommendations)
    }
    
    return []
  }

  const mapRecommendationsToProducts = (recommendations: string[]) => {
    const recommendedProducts: any[] = []
    
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
      
      // Sunscreen recommendations
      if (recLower.includes('sunscreen') || recLower.includes('spf') || recLower.includes('sun protection')) {
        const sunscreenProducts = products.filter(p => p.category === 'sunscreen')
        if (sunscreenProducts.length > 0) {
          recommendedProducts.push({ ...sunscreenProducts[0], match: rec })
        }
      }
    })
    
    // If no specific matches, add basic products
    if (recommendedProducts.length === 0) {
      const basicProducts = products.filter(p => 
        p.category === 'cleanser' || p.category === 'moisturizer'
      ).slice(0, 2)
      basicProducts.forEach(product => {
        recommendedProducts.push({ ...product, match: 'Basic skincare' })
      })
    }
    
    // Remove duplicates and limit to top 6
    const unique = recommendedProducts.filter((product, index, self) =>
      index === self.findIndex(p => p.id === product.id)
    )
    
    return unique.slice(0, 6)
  }

  // Helper function to get condition name (handles both V3 and V4 formats)
  const getConditionName = (condition: any) => {
    // V4 format has 'condition' property
    if ('condition' in condition) {
      return condition.condition
    }
    // V3 format has 'name' property
    if ('name' in condition) {
      return condition.name
    }
    return 'Unknown condition'
  }

  // Helper function to get confidence score
  const getConfidenceScore = () => {
    // New V4 format
    if (analysisResult?.skin_analysis?.analysis_confidence) {
      // Convert from 0-10 scale to 0-100 percentage
      return Math.round((analysisResult.skin_analysis.analysis_confidence / 10) * 100)
    }
    // Legacy V3 format
    if (analysisResult?.confidence_score) {
      return analysisResult.confidence_score
    }
    return 0
  }

  // Helper function to get analysis summary
  const getAnalysisSummary = () => {
    // New V4 format
    if (analysisResult?.skin_analysis?.texture) {
      return `Skin type: ${analysisResult.skin_analysis.texture}. Overall health score: ${analysisResult.skin_analysis.overall_health_score}/10.`
    }
    // Legacy V3 format
    if (analysisResult?.analysis_summary) {
      return analysisResult.analysis_summary
    }
    return "Analysis completed successfully."
  }

  // Helper function to get detected conditions
  const getDetectedConditions = () => {
    // New V4 format
    if (analysisResult?.skin_analysis?.conditions_detected) {
      return analysisResult.skin_analysis.conditions_detected
    }
    // Legacy V3 format
    if (analysisResult?.detected_conditions) {
      return analysisResult.detected_conditions
    }
    return []
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
                {getConfidenceScore()}%
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

          {getAnalysisSummary() && (
            <div className="card mb-4">
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="text-blue-500" />
                <span className="font-semibold">Analysis Summary</span>
              </div>
              <p className="leading-relaxed">
                {getAnalysisSummary()}
              </p>
            </div>
          )}

          {getDetectedConditions().length > 0 && (
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <AlertCircle className="text-red-500" />
                <span className="font-semibold">Detected Conditions</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {getDetectedConditions().map((condition, index) => (
                  <div key={index} className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3 text-sm">
                    <div className="font-semibold mb-1 text-red-800 dark:text-red-200">
                      {getConditionName(condition)}
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
        {getRecommendedProducts().length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <ShoppingCart className="text-blue-500" />
              Recommended Products
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {getRecommendedProducts().map((product, index) => (
                <div key={index} className="card hover:shadow-lg transition-shadow">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-1 rounded">
                      {product.category}
                    </span>
                    <button
                      onClick={() => addToCart(product)}
                      className="text-blue-500 hover:text-blue-600 transition-colors"
                    >
                      <ShoppingCart className="w-4 h-4" />
                    </button>
                  </div>
                  
                  <h3 className="font-semibold mb-2 text-lg">
                    {product.name}
                  </h3>
                  
                  <p className="text-secondary text-sm leading-relaxed mb-3">
                    {product.description}
                  </p>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-bold text-green-600">
                      ${product.price}
                    </span>
                    
                    <p className="text-secondary text-sm leading-relaxed">
                      {product.match}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Additional Recommended Products (if any that weren't matched) */}
        {(() => {
          const matchedRecommendations = getRecommendedProducts()
          const allRecommendedProducts = getRecommendedProducts()
          const unmatchedProducts = allRecommendedProducts.filter(product => 
            !matchedRecommendations.some(rec => 
              rec.match === product.match || 
              rec.name.toLowerCase().includes(product.name.toLowerCase()) ||
              product.name.toLowerCase().includes(rec.match.toLowerCase())
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