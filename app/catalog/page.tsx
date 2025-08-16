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
import { ProductImage } from '@/components/product-image'

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
  health_score?: number
  conditions?: string[]
  skinType?: string
  concerns?: string[]
  metrics?: any
  intelligentRecommendations?: RecommendedProduct[]
  // Additional properties from actual API response
  result?: {
    conditions: string[]
    health_score: number
    primary_concerns: string[]
  }
  primary_concerns?: string[]
  accuracy?: string
  analysis_type?: string
  model_type?: string
  model_version?: string
}

export default function CatalogPage() {
  const { theme } = useTheme()
  const { state: authState } = useAuth()
  const { dispatch, isAuthenticated } = useCart()
  const [showSignInModal, setShowSignInModal] = useState(false)
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null)
  const [showRecommendations, setShowRecommendations] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  // Parse analysis data from sessionStorage (like suggestions page)
  useEffect(() => {
    if (typeof window !== 'undefined') {
      console.log('🔍 Catalog page loading...')
      
      // Try to get analysis data from sessionStorage first (new approach)
      const storedAnalysis = sessionStorage.getItem('analysisResult')
      console.log('📦 Stored analysis data:', storedAnalysis ? 'Found' : 'Not found')
      
      if (storedAnalysis) {
        try {
          const result = JSON.parse(storedAnalysis)
          console.log('✅ Successfully parsed analysis result from sessionStorage:', result)
          setAnalysisData(result)
          setShowRecommendations(true)
        } catch (error) {
          console.error('❌ Failed to parse analysis data from sessionStorage:', error)
        }
      } else {
        // Fallback to URL parameter for backward compatibility
        const urlParams = new URLSearchParams(window.location.search)
        const analysisParam = urlParams.get('analysis')
        console.log('🔗 URL analysis parameter:', analysisParam ? 'Found' : 'Not found')
        
        if (analysisParam) {
          try {
            const parsed = JSON.parse(decodeURIComponent(analysisParam))
            console.log('✅ Parsed analysis data from URL:', parsed)
            setAnalysisData(parsed)
            setShowRecommendations(true)
          } catch (error) {
            console.error('❌ Failed to parse analysis data from URL:', error)
          }
        } else {
          console.log('⚠️ No analysis data found in sessionStorage or URL')
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
      console.log('🔄 Analysis data found but no recommendations, generating now...')
      fetchIntelligentRecommendations()
    } else if (analysisData && analysisData.intelligentRecommendations) {
      console.log('✅ Recommendations already available:', analysisData.intelligentRecommendations.length)
    }
  }, [analysisData])

  const getRecommendedProducts = (): RecommendedProduct[] => {
    if (!analysisData) {
      console.log('⚠️ No analysis data for recommendations')
      return []
    }
    
    console.log('🔍 Getting recommended products...')
    console.log('📊 Analysis data:', analysisData)
    console.log('🧠 Intelligent recommendations:', analysisData.intelligentRecommendations)
    
    // If we have intelligent recommendations from the enhanced algorithm, use those
    if (analysisData.intelligentRecommendations && analysisData.intelligentRecommendations.length > 0) {
      console.log('✅ Using intelligent recommendations:', analysisData.intelligentRecommendations)
      return analysisData.intelligentRecommendations
    }
    
    console.log('🔄 No intelligent recommendations found, generating them now...')
    // Generate intelligent recommendations if they don't exist
    const intelligentRecs = generateIntelligentRecommendations(analysisData)
    if (intelligentRecs && intelligentRecs.length > 0) {
      console.log('✨ Generated intelligent recommendations:', intelligentRecs)
      // Update the analysis data with the new recommendations
      setAnalysisData(prev => prev ? {
        ...prev,
        intelligentRecommendations: intelligentRecs,
      } : null)
      return intelligentRecs
    }
    
    console.log('⚠️ Failed to generate intelligent recommendations, using fallback')
    // Fallback to basic logic only if intelligent generation fails
    const recommended = products.filter(product => {
      // Match based on conditions
      const conditionMatch = analysisData.conditions?.some(condition =>
        product.description.toLowerCase().includes(condition.toLowerCase()) ||
        product.name.toLowerCase().includes(condition.toLowerCase())
      ) || false
      
      // Match based on health score
      const healthMatch = (analysisData.health_score || 50) < 50 
        ? product.category === 'treatment' || product.category === 'serum'
        : product.category === 'moisturizer' || product.category === 'sunscreen'
      
      return conditionMatch || healthMatch
    })
    
    console.log('📋 Fallback recommendations found:', recommended.length)
    
    // Remove duplicates and limit to top 6, convert to RecommendedProduct type
    const unique = recommended.filter((product, index, self) =>
      index === self.findIndex(p => p.id === product.id)
    )
    
    const result = unique.slice(0, 6).map(product => ({
      ...product,
      matchReason: `Matched based on your skin profile`,
      score: 0
    }))
    
    console.log('🎯 Final fallback recommendations:', result)
    return result
  }

  const fetchIntelligentRecommendations = async () => {
    if (!analysisData) {
      console.log('⚠️ No analysis data available for recommendations')
      return
    }
    
    try {
      console.log('🧠 Generating intelligent recommendations for:', analysisData)
      // Generate intelligent recommendations locally from existing analysis data
      const recommendations = generateIntelligentRecommendations(analysisData)
      console.log('✨ Generated recommendations:', recommendations)
      
      if (recommendations && recommendations.length > 0) {
        setAnalysisData(prev => prev ? {
          ...prev,
          intelligentRecommendations: recommendations,
        } : null)
        console.log('✅ Updated analysis data with recommendations')
      } else {
        console.log('⚠️ No recommendations generated')
      }
    } catch (error) {
      console.error('❌ Failed to generate intelligent recommendations:', error)
    }
  }

  // Generate intelligent recommendations based on analysis data
  const generateIntelligentRecommendations = (data: AnalysisData): RecommendedProduct[] => {
    console.log('🧠 Starting enhanced recommendation generation for data:', data)
    console.log('🔍 Full data object keys:', Object.keys(data))
    
    // Extract data from the nested structure
    const conditions = data.result?.conditions || data.conditions || data.primary_concerns || []
    const healthScore = data.result?.health_score || data.health_score || 50
    
    console.log('📊 Extracted conditions:', conditions)
    console.log('📊 Extracted health score:', healthScore)
    console.log('📊 Data.result exists:', !!data.result)
    console.log('📊 Data.conditions exists:', !!data.conditions)
    console.log('📊 Data.primary_concerns exists:', !!data.primary_concerns)
    
    if (!conditions || conditions.length === 0) {
      console.log('⚠️ No conditions found, cannot generate recommendations')
      console.log('🔍 Available data for debugging:', {
        result_conditions: data.result?.conditions,
        direct_conditions: data.conditions,
        primary_concerns: data.primary_concerns,
        full_data: data
      })
      return []
    }
    
    console.log('✅ Conditions found, proceeding with intelligent scoring...')
    console.log('📦 Total products to score:', products.length)
    
    // Enhanced scoring system with better condition matching
    const scoredProducts = products.map(product => {
      let score = 0
      let reasons: string[] = []

      // Score based on health score (more nuanced)
      if (healthScore < 30) {
        // Very low health score needs intensive treatment
        if (product.category === 'treatment' || product.category === 'serum') {
          score += 10
          reasons.push('Intensive treatment for significant skin concerns')
        }
        if (product.category === 'cleanser') {
          score += 6
          reasons.push('Gentle cleansing for sensitive skin')
        }
      } else if (healthScore < 50) {
        // Low health score needs treatment + maintenance
        if (product.category === 'treatment' || product.category === 'serum') {
          score += 8
          reasons.push('Treatment for skin concerns')
        }
        if (product.category === 'moisturizer') {
          score += 6
          reasons.push('Moisturizing for compromised skin barrier')
        }
      } else if (healthScore < 70) {
        // Moderate health score - balanced approach
        if (product.category === 'moisturizer' || product.category === 'sunscreen') {
          score += 7
          reasons.push('Maintenance and protection for moderate skin health')
        }
        if (product.category === 'serum') {
          score += 5
          reasons.push('Targeted improvement for moderate concerns')
        }
      } else {
        // High health score - maintenance and enhancement
        if (product.category === 'sunscreen') {
          score += 8
          reasons.push('Protection for healthy skin')
        }
        if (product.category === 'moisturizer') {
          score += 6
          reasons.push('Maintenance for healthy skin')
        }
      }

      // Enhanced condition-based scoring
      conditions.forEach(condition => {
        const conditionLower = condition.toLowerCase()
        console.log(`🔍 Scoring product "${product.name}" for condition: ${conditionLower}`)
        
        // Acne-related conditions
        if (conditionLower.includes('acne') || conditionLower.includes('breakout')) {
          if (product.category === 'cleanser') {
            score += 9
            reasons.push('Gentle cleansing for acne-prone skin')
            console.log(`✅ ${product.name} scored +9 for acne condition (cleanser)`)
          }
          if (product.category === 'treatment' && product.description.toLowerCase().includes('salicylic')) {
            score += 10
            reasons.push('Salicylic acid treatment for acne')
            console.log(`✅ ${product.name} scored +10 for acne condition (salicylic acid)`)
          }
          if (product.description.toLowerCase().includes('gentle') || product.description.toLowerCase().includes('non-comedogenic')) {
            score += 4
            reasons.push('Non-irritating for acne-prone skin')
            console.log(`✅ ${product.name} scored +4 for acne condition (gentle/non-comedogenic)`)
          }
        }
        
        // Hyperpigmentation and dark spots
        if (conditionLower.includes('hyperpigmentation') || conditionLower.includes('dark spot') || conditionLower.includes('melasma')) {
          if (product.category === 'treatment' && (product.description.toLowerCase().includes('vitamin c') || product.description.toLowerCase().includes('niacinamide'))) {
            score += 10
            reasons.push('Targets hyperpigmentation with proven ingredients')
            console.log(`✅ ${product.name} scored +10 for hyperpigmentation (vitamin c/niacinamide)`)
          }
          if (product.category === 'serum' && product.description.toLowerCase().includes('brightening')) {
            score += 8
            reasons.push('Brightening serum for uneven skin tone')
            console.log(`✅ ${product.name} scored +8 for hyperpigmentation (brightening serum)`)
          }
        }
        
        // Dryness and dehydration
        if (conditionLower.includes('dry') || conditionLower.includes('dehydrated') || conditionLower.includes('flaky')) {
          if (product.category === 'moisturizer' && product.description.toLowerCase().includes('hydrating')) {
            score += 9
            reasons.push('Hydrating moisturizer for dry skin')
            console.log(`✅ ${product.name} scored +9 for dryness (hydrating moisturizer)`)
          }
          if (product.category === 'serum' && product.description.toLowerCase().includes('hyaluronic')) {
            score += 8
            reasons.push('Hyaluronic acid for hydration')
            console.log(`✅ ${product.name} scored +8 for dryness (hyaluronic acid)`)
          }
        }
        
        // Sensitivity and redness
        if (conditionLower.includes('sensitive') || conditionLower.includes('redness') || conditionLower.includes('irritated')) {
          if (product.description.toLowerCase().includes('gentle') || product.description.toLowerCase().includes('calming')) {
            score += 8
            reasons.push('Gentle and calming for sensitive skin')
            console.log(`✅ ${product.name} scored +8 for sensitivity (gentle/calming)`)
          }
          if (product.description.toLowerCase().includes('fragrance-free') || product.description.toLowerCase().includes('hypoallergenic')) {
            score += 6
            reasons.push('Fragrance-free for sensitive skin')
            console.log(`✅ ${product.name} scored +6 for sensitivity (fragrance-free/hypoallergenic)`)
          }
        }
        
        // Aging and fine lines
        if (conditionLower.includes('aging') || conditionLower.includes('fine line') || conditionLower.includes('wrinkle')) {
          if (product.category === 'serum' && product.description.toLowerCase().includes('retinol')) {
            score += 9
            reasons.push('Retinol for anti-aging benefits')
            console.log(`✅ ${product.name} scored +9 for aging (retinol)`)
          }
          if (product.category === 'moisturizer' && product.description.toLowerCase().includes('anti-aging')) {
            score += 7
            reasons.push('Anti-aging moisturizer')
            console.log(`✅ ${product.name} scored +7 for aging (anti-aging moisturizer)`)
          }
        }
        
        // Sun damage
        if (conditionLower.includes('sun damage') || conditionLower.includes('uv damage')) {
          if (product.category === 'sunscreen') {
            score += 10
            reasons.push('Essential protection for sun-damaged skin')
            console.log(`✅ ${product.name} scored +10 for sun damage (sunscreen)`)
          }
          if (product.description.toLowerCase().includes('repair') || product.description.toLowerCase().includes('recovery')) {
            score += 6
            reasons.push('Repair and recovery for sun damage')
            console.log(`✅ ${product.name} scored +6 for sun damage (repair/recovery)`)
          }
        }
      })

      // Category balance and essential products
      if (product.category === 'cleanser') score += 3
      if (product.category === 'sunscreen') score += 4
      if (product.category === 'moisturizer') score += 2
      
      // Brand reputation and quality indicators
      if (product.description.toLowerCase().includes('clinical') || product.description.toLowerCase().includes('medical-grade')) {
        score += 2
        reasons.push('Medical-grade formulation')
      }
      
      // Price consideration (affordability bonus)
      if (product.price < 50) score += 1

      console.log(`📊 ${product.name} final score: ${score}, reasons: ${reasons.join(', ')}`)

      return {
        ...product,
        score,
        matchReason: reasons.length > 0 ? reasons.join('; ') : 'Recommended for your skin profile'
      }
    })

    console.log('🎯 Enhanced scored products:', scoredProducts.map(p => ({ 
      name: p.name, 
      score: p.score, 
      reason: p.matchReason,
      category: p.category 
    })))

    // Sort by score and return top recommendations with category diversity
    const sortedByScore = scoredProducts.sort((a, b) => b.score - a.score)
    console.log('📊 Top 10 scored products:', sortedByScore.slice(0, 10).map(p => ({ name: p.name, score: p.score, category: p.category })))
    
    // Ensure we have a good mix of categories
    const topRecommendations = []
    const categoryCounts = { cleanser: 0, treatment: 0, serum: 0, moisturizer: 0, sunscreen: 0 }
    
    for (const product of sortedByScore) {
      if (topRecommendations.length >= 6) break
      
      const category = product.category as keyof typeof categoryCounts
      if (categoryCounts[category] < 2) { // Max 2 products per category
        topRecommendations.push(product)
        categoryCounts[category]++
        console.log(`✅ Added ${product.name} (${category}) to recommendations`)
      }
    }
    
    // Fill remaining slots with highest scoring products
    for (const product of sortedByScore) {
      if (topRecommendations.length >= 6) break
      if (!topRecommendations.find(p => p.id === product.id)) {
        topRecommendations.push(product)
        console.log(`✅ Added ${product.name} (${product.category}) to fill remaining slot`)
      }
    }
    
    console.log('🎯 Final enhanced recommendations:', topRecommendations.map(p => ({ 
      name: p.name, 
      score: p.score, 
      category: p.category 
    })))
    
    return topRecommendations
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
             <span>Health Score: {Math.round(analysisData.result?.health_score || analysisData.health_score || 50)}%</span>
             <span>•</span>
             <span>Conditions: {(analysisData.result?.conditions || analysisData.conditions || []).slice(0, 3).join(', ')}</span>
             {(analysisData.result?.conditions || analysisData.conditions || []).length > 3 && <span>+{(analysisData.result?.conditions || analysisData.conditions || []).length - 3} more</span>}
           </div>
           
           {/* Debug Button */}
           <div className="mt-4">
             <button
               onClick={() => {
                 console.log('🔧 Manual trigger of recommendations')
                 console.log('🔍 Current analysis data:', analysisData)
                 fetchIntelligentRecommendations()
               }}
               className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-sm"
             >
               Generate Recommendations
             </button>
             <span className="ml-2 text-xs text-gray-500">
               (Debug: Click to manually generate recommendations)
             </span>
           </div>
           
           {/* Test Intelligent Recommendations Button */}
           <div className="mt-2">
             <button
               onClick={() => {
                 console.log('🧪 Testing intelligent recommendations directly...')
                 console.log('🔍 Analysis data for testing:', analysisData)
                 const testRecs = generateIntelligentRecommendations(analysisData)
                 console.log('🧪 Direct test results:', testRecs)
                 if (testRecs && testRecs.length > 0) {
                   setAnalysisData(prev => prev ? {
                     ...prev,
                     intelligentRecommendations: testRecs,
                   } : null)
                   console.log('✅ Updated analysis data with test recommendations')
                 }
               }}
               className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 text-sm"
             >
               Test Intelligent Algorithm
             </button>
             <span className="ml-2 text-xs text-gray-500">
               (Test: Direct algorithm testing)
             </span>
           </div>
           
           {/* Enhanced Debug Information */}
           <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
             <h4 className="font-medium text-sm mb-2">🔍 Debug Information:</h4>
             <div className="text-xs space-y-1">
               <div>Health Score: {Math.round(analysisData.result?.health_score || analysisData.health_score || 50)}%</div>
               <div>Conditions: {(analysisData.result?.conditions || analysisData.conditions || []).join(', ') || 'None detected'}</div>
               <div>Recommendations Generated: {analysisData.intelligentRecommendations?.length || 0}</div>
               <div>Data Source: {analysisData.result ? 'Nested result structure' : 'Direct properties'}</div>
             </div>
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
                    <ProductImage
                      src={product.image}
                      alt={product.name}
                      className="w-full h-48 object-cover rounded-lg border border-primary"
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
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <Star className="w-4 h-4 text-blue-500" />
                        <span className="text-sm font-medium text-blue-700">Why Recommended</span>
                      </div>
                      {product.score !== undefined && (
                        <span className="text-xs bg-blue-200 text-blue-800 px-2 py-1 rounded-full font-medium">
                          Score: {product.score}
                        </span>
                      )}
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
        
        {/* No Analysis Data Message */}
        {!showRecommendations && (
          <div className="mb-6 p-6 bg-blue-50 border border-blue-200 rounded-xl text-center">
            <Star className="w-12 h-12 text-blue-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-blue-700 mb-2">
              Get Personalized Recommendations
            </h3>
            <p className="text-blue-600 mb-4">
              Complete a skin analysis to receive intelligent product recommendations tailored to your skin profile.
            </p>
            <Link 
              href="/"
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
            >
              Start Skin Analysis
            </Link>
          </div>
        )}
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map(product => (
            <div key={product.id} className="bg-secondary rounded-xl p-6 border border-primary">
              
              {/* Product Image */}
              {product.image && (
                <div className="mb-4 text-center">
                  <ProductImage
                    src={product.image}
                    alt={product.name}
                    className="w-full h-48 object-cover rounded-lg border border-primary"
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