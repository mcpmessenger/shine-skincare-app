'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ArrowLeft, Star, ShoppingCart } from 'lucide-react'
import { products } from '@/lib/products'
import { ProductImage } from '@/components/product-image'

// Simulated analysis data for testing
const testAnalysisData = {
  result: {
    health_score: 65,
    conditions: ['acne', 'hyperpigmentation', 'sensitive'],
    primary_concerns: ['acne', 'hyperpigmentation', 'sensitive']
  },
  enhanced_ml: true,
  model_version: 'Hare_Run_V6_Facial_v1.0',
  accuracy: '97.13%'
}

export default function TestRecommendationsPage() {
  const [recommendations, setRecommendations] = useState<any[]>([])
  const [isGenerating, setIsGenerating] = useState(false)

  // Generate intelligent recommendations based on test data
  const generateIntelligentRecommendations = (data: any) => {
    console.log('🧠 Starting enhanced recommendation generation for test data:', data)
    
    const conditions = data.result?.conditions || []
    const healthScore = data.result?.health_score || 50
    
    console.log('📊 Test conditions:', conditions)
    console.log('📊 Test health score:', healthScore)
    
    if (!conditions || conditions.length === 0) {
      console.log('⚠️ No conditions found, cannot generate recommendations')
      return []
    }
    
    // Enhanced scoring system with better condition matching
    const scoredProducts = products.map(product => {
      let score = 0
      let reasons: string[] = []

      // Score based on health score (more nuanced)
      if (healthScore < 30) {
        if (product.category === 'treatment' || product.category === 'serum') {
          score += 10
          reasons.push('Intensive treatment for significant skin concerns')
        }
        if (product.category === 'cleanser') {
          score += 6
          reasons.push('Gentle cleansing for sensitive skin')
        }
      } else if (healthScore < 50) {
        if (product.category === 'treatment' || product.category === 'serum') {
          score += 8
          reasons.push('Treatment for skin concerns')
        }
        if (product.category === 'moisturizer') {
          score += 6
          reasons.push('Moisturizing for compromised skin barrier')
        }
      } else if (healthScore < 70) {
        if (product.category === 'moisturizer' || product.category === 'sunscreen') {
          score += 7
          reasons.push('Maintenance and protection for moderate skin health')
        }
        if (product.category === 'serum') {
          score += 5
          reasons.push('Targeted improvement for moderate concerns')
        }
      } else {
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
        
        // Acne-related conditions
        if (conditionLower.includes('acne') || conditionLower.includes('breakout')) {
          if (product.category === 'cleanser') {
            score += 9
            reasons.push('Gentle cleansing for acne-prone skin')
          }
          if (product.category === 'treatment' && product.description.toLowerCase().includes('salicylic')) {
            score += 10
            reasons.push('Salicylic acid treatment for acne')
          }
          if (product.description.toLowerCase().includes('gentle') || product.description.toLowerCase().includes('non-comedogenic')) {
            score += 4
            reasons.push('Non-irritating for acne-prone skin')
          }
        }
        
        // Hyperpigmentation and dark spots
        if (conditionLower.includes('hyperpigmentation') || conditionLower.includes('dark spot') || conditionLower.includes('melasma')) {
          if (product.category === 'treatment' && (product.description.toLowerCase().includes('vitamin c') || product.description.toLowerCase().includes('niacinamide'))) {
            score += 10
            reasons.push('Targets hyperpigmentation with proven ingredients')
          }
          if (product.category === 'serum' && product.description.toLowerCase().includes('brightening')) {
            score += 8
            reasons.push('Brightening serum for uneven skin tone')
          }
        }
        
        // Sensitivity and redness
        if (conditionLower.includes('sensitive') || conditionLower.includes('redness') || conditionLower.includes('irritated')) {
          if (product.description.toLowerCase().includes('gentle') || product.description.toLowerCase().includes('calming')) {
            score += 8
            reasons.push('Gentle and calming for sensitive skin')
          }
          if (product.description.toLowerCase().includes('fragrance-free') || product.description.toLowerCase().includes('hypoallergenic')) {
            score += 6
            reasons.push('Fragrance-free for sensitive skin')
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
    
    // Ensure we have a good mix of categories
    const topRecommendations = []
    const categoryCounts = { cleanser: 0, treatment: 0, serum: 0, moisturizer: 0, sunscreen: 0 }
    
    for (const product of sortedByScore) {
      if (topRecommendations.length >= 6) break
      
      const category = product.category as keyof typeof categoryCounts
      if (categoryCounts[category] < 2) { // Max 2 products per category
        topRecommendations.push(product)
        categoryCounts[category]++
      }
    }
    
    // Fill remaining slots with highest scoring products
    for (const product of sortedByScore) {
      if (topRecommendations.length >= 6) break
      if (!topRecommendations.find(p => p.id === product.id)) {
        topRecommendations.push(product)
      }
    }
    
    console.log('🎯 Final enhanced recommendations:', topRecommendations.map(p => ({ 
      name: p.name, 
      score: p.score, 
      category: p.category 
    })))
    
    return topRecommendations
  }

  const handleGenerateRecommendations = () => {
    setIsGenerating(true)
    console.log('🧪 Testing recommendation system with data:', testAnalysisData)
    
    // Simulate API delay
    setTimeout(() => {
      const testRecommendations = generateIntelligentRecommendations(testAnalysisData)
      setRecommendations(testRecommendations)
      setIsGenerating(false)
      console.log('✅ Test recommendations generated:', testRecommendations.length)
    }, 1000)
  }

  return (
    <div className="min-h-screen bg-primary text-primary p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link 
            href="/"
            className="inline-flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Analysis
          </Link>
          <h1 className="text-3xl font-bold">🧪 Test Recommendations System</h1>
        </div>

        {/* Test Data Display */}
        <div className="mb-8 p-6 bg-blue-50 border border-blue-200 rounded-xl">
          <h2 className="text-xl font-semibold text-blue-700 mb-4">Test Analysis Data</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="font-medium">Health Score:</span> {testAnalysisData.result.health_score}%
            </div>
            <div>
              <span className="font-medium">Conditions:</span> {testAnalysisData.result.conditions.join(', ')}
            </div>
            <div>
              <span className="font-medium">Model:</span> {testAnalysisData.model_version}
            </div>
          </div>
          
          <button
            onClick={handleGenerateRecommendations}
            disabled={isGenerating}
            className="mt-4 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isGenerating ? 'Generating...' : 'Generate Test Recommendations'}
          </button>
        </div>

        {/* Test Results */}
        {recommendations.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">Test Recommendations Generated</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recommendations.map(product => (
                <div key={product.id} className="bg-secondary rounded-xl p-6 border-2 border-green-500 relative">
                  <div className="absolute top-2 right-2 bg-green-500 text-white px-2 py-1 rounded text-xs font-bold">
                    TEST
                  </div>
                  
                  {/* Product Image */}
                  <div className="mb-4 text-center">
                    <ProductImage
                      src={product.image}
                      alt={product.name}
                      className="w-full h-48 object-cover rounded-lg border border-primary"
                    />
                  </div>
                  
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
                    <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-2">
                          <Star className="w-4 h-4 text-green-500" />
                          <span className="text-sm font-medium text-green-700">Why Recommended</span>
                        </div>
                        {product.score !== undefined && (
                          <span className="text-xs bg-green-200 text-green-800 px-2 py-1 rounded-full font-medium">
                            Score: {product.score}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-green-600">{product.matchReason}</p>
                    </div>
                  )}
                  
                  <div className="flex justify-between items-center">
                    <span className="px-3 py-1 bg-blue-100 border border-blue-300 rounded-xl text-xs capitalize text-blue-700">
                      {product.category}
                    </span>
                    
                    <span className="text-sm text-gray-500">
                      Test Product
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="p-6 bg-gray-50 border border-gray-200 rounded-xl">
          <h3 className="text-lg font-semibold mb-2">How to Test:</h3>
          <ol className="list-decimal list-inside space-y-2 text-sm text-gray-700">
            <li>Click "Generate Test Recommendations" above</li>
            <li>Check the console for detailed logging</li>
            <li>Verify that products are scored and ranked correctly</li>
            <li>Check that recommendations match the test conditions (acne, hyperpigmentation, sensitive)</li>
            <li>Verify category diversity in recommendations</li>
          </ol>
          
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h4 className="font-medium text-blue-700 mb-2">Expected Results:</h4>
            <ul className="text-sm text-blue-600 space-y-1">
              <li>• Cleansers should score high for acne conditions</li>
              <li>• Treatments with Vitamin C/Niacinamide should score high for hyperpigmentation</li>
              <li>• Gentle, fragrance-free products should score high for sensitive skin</li>
              <li>• Products should be diverse across categories</li>
              <li>• Scores should reflect the enhanced algorithm</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
