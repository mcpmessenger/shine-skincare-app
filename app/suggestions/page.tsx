'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Star, ShoppingCart, CheckCircle, AlertCircle, Info } from 'lucide-react'
import { useTheme } from 'next-themes'
import { useAuth } from '@/hooks/useAuth'
import { useCart } from '@/hooks/useCart'
import { CartDrawer } from '@/components/cart-drawer'
import { ThemeToggle } from '@/components/theme-toggle'
import { SignInModal } from '@/components/sign-in-modal'
import { products } from '@/lib/products'

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

  const getTextColor = (opacity: number = 1) => {
    return theme === 'dark' 
      ? `rgba(255, 255, 255, ${opacity})` 
      : `rgba(0, 0, 0, ${opacity})`
  }

  const getBgColor = (opacity: number = 0.05) => {
    return theme === 'dark' 
      ? `rgba(255, 255, 255, ${opacity})` 
      : `rgba(0, 0, 0, ${opacity})`
  }

  const getBorderColor = (opacity: number = 0.1) => {
    return theme === 'dark' 
      ? `rgba(255, 255, 255, ${opacity})` 
      : `rgba(0, 0, 0, ${opacity})`
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
      <div style={{
        minHeight: '100vh',
        backgroundColor: theme === 'dark' ? '#000000' : '#ffffff',
        color: theme === 'dark' ? '#ffffff' : '#000000',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{ textAlign: 'center' }}>
          <h2>No Analysis Results Found</h2>
          <p>Please complete a skin analysis first.</p>
          <Link href="/" style={{
            display: 'inline-block',
            padding: '0.75rem 1.5rem',
            backgroundColor: '#3b82f6',
            color: '#ffffff',
            textDecoration: 'none',
            borderRadius: '8px',
            marginTop: '1rem'
          }}>
            Go to Analysis
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: theme === 'dark' ? '#000000' : '#ffffff',
      color: theme === 'dark' ? '#ffffff' : '#000000'
    }}>
      {/* Header */}
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '1rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '1rem'
        }}>
          <Link href="/">
            <img
              src="https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png"
              alt="Shine Logo"
              style={{
                height: '40px',
                width: 'auto'
              }}
            />
          </Link>
          <h1 style={{ margin: 0, fontSize: '1.5rem' }}>
            Personalized Recommendations
          </h1>
        </div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '1rem'
        }}>
          <ThemeToggle />
          <CartDrawer />
        </div>
      </div>

      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '1rem'
      }}>
        {/* Analysis Summary */}
        <div style={{
          backgroundColor: getBgColor(0.1),
          borderRadius: '12px',
          padding: '1.5rem',
          border: `1px solid ${getBorderColor(0.2)}`,
          marginBottom: '2rem'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            marginBottom: '1rem'
          }}>
            <Star style={{ color: '#3b82f6' }} />
            <h2 style={{ margin: 0, fontSize: '1.3rem' }}>
              Analysis Results
            </h2>
          </div>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '1rem',
            marginBottom: '1rem'
          }}>
            <div style={{
              backgroundColor: getBgColor(0.05),
              padding: '1rem',
              borderRadius: '8px',
              border: `1px solid ${getBorderColor(0.1)}`
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <CheckCircle style={{ color: getConfidenceColor(analysisResult.confidence_score) }} />
                <span style={{ fontWeight: 'bold' }}>Confidence Score</span>
              </div>
              <span style={{ 
                fontSize: '1.5rem', 
                fontWeight: 'bold',
                color: getConfidenceColor(analysisResult.confidence_score)
              }}>
                {analysisResult.confidence_score}%
              </span>
            </div>
            
            {analysisResult.severity_level && (
              <div style={{
                backgroundColor: getBgColor(0.05),
                padding: '1rem',
                borderRadius: '8px',
                border: `1px solid ${getBorderColor(0.1)}`
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <AlertCircle style={{ color: getSeverityColor(analysisResult.severity_level) }} />
                  <span style={{ fontWeight: 'bold' }}>Severity Level</span>
                </div>
                <span style={{ 
                  fontSize: '1.5rem', 
                  fontWeight: 'bold',
                  color: getSeverityColor(analysisResult.severity_level)
                }}>
                  {analysisResult.severity_level}
                </span>
              </div>
            )}
          </div>

          {analysisResult.analysis_summary && (
            <div style={{
              backgroundColor: getBgColor(0.05),
              padding: '1rem',
              borderRadius: '8px',
              border: `1px solid ${getBorderColor(0.1)}`,
              marginBottom: '1rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <Info style={{ color: '#3b82f6' }} />
                <span style={{ fontWeight: 'bold' }}>Analysis Summary</span>
              </div>
              <p style={{ margin: 0, lineHeight: '1.5' }}>
                {analysisResult.analysis_summary}
              </p>
            </div>
          )}

          {analysisResult.detected_conditions && analysisResult.detected_conditions.length > 0 && (
            <div style={{
              backgroundColor: getBgColor(0.05),
              padding: '1rem',
              borderRadius: '8px',
              border: `1px solid ${getBorderColor(0.1)}`
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <AlertCircle style={{ color: '#ef4444' }} />
                <span style={{ fontWeight: 'bold' }}>Detected Conditions</span>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {analysisResult.detected_conditions.map((condition, index) => (
                  <div key={index} style={{
                    padding: '0.5rem',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid rgba(239, 68, 68, 0.3)',
                    borderRadius: '8px',
                    fontSize: '0.8rem',
                    minWidth: '200px'
                  }}>
                    <div style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>
                      {condition.name}
                    </div>
                    <div style={{ fontSize: '0.7rem', color: getTextColor(0.7), marginBottom: '0.25rem' }}>
                      {condition.description}
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem' }}>
                      <span>Confidence: {condition.confidence}%</span>
                      <span>Severity: {condition.severity}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Recommendations */}
        {analysisResult.top_recommendations && analysisResult.top_recommendations.length > 0 && (
          <div style={{ marginBottom: '2rem' }}>
            <h2 style={{
              fontSize: '1.3rem',
              marginBottom: '1rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              <Star style={{ color: '#3b82f6' }} />
              Top Recommendations
            </h2>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
              gap: '1rem'
            }}>
              {analysisResult.top_recommendations.map((recommendation, index) => (
                <div key={index} style={{
                  backgroundColor: getBgColor(0.05),
                  padding: '1rem',
                  borderRadius: '8px',
                  border: `1px solid ${getBorderColor(0.1)}`
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    <CheckCircle style={{ color: '#10b981' }} />
                    <span style={{ fontWeight: 'bold' }}>Recommendation {index + 1}</span>
                  </div>
                  <p style={{ margin: 0, lineHeight: '1.5' }}>
                    {recommendation}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recommended Products */}
        {getRecommendedProducts().length > 0 && (
          <div style={{ marginBottom: '2rem' }}>
            <h2 style={{
              fontSize: '1.3rem',
              marginBottom: '1rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              <ShoppingCart style={{ color: '#3b82f6' }} />
              Recommended Products
            </h2>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
              gap: '1.5rem'
            }}>
              {getRecommendedProducts().map(product => (
                <div key={product.id} style={{
                  backgroundColor: getBgColor(0.05),
                  borderRadius: '12px',
                  padding: '1.5rem',
                  border: `2px solid #3b82f6`,
                  position: 'relative'
                }}>
                  <div style={{
                    position: 'absolute',
                    top: '0.5rem',
                    right: '0.5rem',
                    backgroundColor: '#3b82f6',
                    color: 'white',
                    padding: '0.25rem 0.5rem',
                    borderRadius: '4px',
                    fontSize: '0.7rem',
                    fontWeight: 'bold'
                  }}>
                    RECOMMENDED
                  </div>
                                     <div style={{
                     display: 'flex',
                     gap: '1rem',
                     marginBottom: '1rem'
                   }}>
                     {product.image && (
                       <img
                         src={product.image}
                         alt={product.name}
                         style={{
                           width: '80px',
                           height: '80px',
                           objectFit: 'cover',
                           borderRadius: '8px',
                           border: `1px solid ${getBorderColor(0.2)}`
                         }}
                         onError={(e) => {
                           // Hide image if it fails to load
                           e.currentTarget.style.display = 'none'
                         }}
                       />
                     )}
                     <div style={{ flex: 1 }}>
                       <div style={{
                         display: 'flex',
                         justifyContent: 'space-between',
                         alignItems: 'flex-start',
                         marginBottom: '0.5rem'
                       }}>
                         <h3 style={{
                           margin: 0,
                           fontSize: '1.1rem',
                           fontWeight: 'bold'
                         }}>
                           {product.name}
                         </h3>
                         <span style={{
                           fontSize: '1.2rem',
                           fontWeight: 'bold',
                           color: '#3b82f6'
                         }}>
                           ${product.price.toFixed(2)}
                         </span>
                       </div>
                       
                       <p style={{
                         color: theme === 'dark' ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)',
                         fontSize: '0.9rem',
                         margin: 0,
                         lineHeight: '1.4'
                       }}>
                         {product.description}
                       </p>
                     </div>
                   </div>
                  
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <span style={{
                      padding: '0.25rem 0.75rem',
                      backgroundColor: 'rgba(59, 130, 246, 0.2)',
                      border: '1px solid rgba(59, 130, 246, 0.3)',
                      borderRadius: '12px',
                      fontSize: '0.8rem',
                      textTransform: 'capitalize'
                    }}>
                      {product.category}
                    </span>
                    
                    <button
                      onClick={() => addToCart(product)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.75rem 1.5rem',
                        backgroundColor: isAuthenticated ? '#3b82f6' : 'rgba(59, 130, 246, 0.5)',
                        border: '1px solid #3b82f6',
                        borderRadius: '8px',
                        color: '#ffffff',
                        cursor: isAuthenticated ? 'pointer' : 'not-allowed',
                        fontSize: '0.9rem',
                        fontWeight: 'bold',
                        transition: 'all 0.3s ease'
                      }}
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

        {/* Immediate Actions */}
        {analysisResult.immediate_actions && analysisResult.immediate_actions.length > 0 && (
          <div style={{ marginBottom: '2rem' }}>
            <h2 style={{
              fontSize: '1.3rem',
              marginBottom: '1rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              <AlertCircle style={{ color: '#f59e0b' }} />
              Immediate Actions
            </h2>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
              gap: '1rem'
            }}>
              {analysisResult.immediate_actions.map((action, index) => (
                <div key={index} style={{
                  backgroundColor: getBgColor(0.05),
                  padding: '1rem',
                  borderRadius: '8px',
                  border: `1px solid ${getBorderColor(0.1)}`
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    <AlertCircle style={{ color: '#f59e0b' }} />
                    <span style={{ fontWeight: 'bold' }}>Action {index + 1}</span>
                  </div>
                  <p style={{ margin: 0, lineHeight: '1.5' }}>
                    {action}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Lifestyle Changes */}
        {analysisResult.lifestyle_changes && analysisResult.lifestyle_changes.length > 0 && (
          <div style={{ marginBottom: '2rem' }}>
            <h2 style={{
              fontSize: '1.3rem',
              marginBottom: '1rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              <Info style={{ color: '#10b981' }} />
              Lifestyle Changes
            </h2>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
              gap: '1rem'
            }}>
              {analysisResult.lifestyle_changes.map((change, index) => (
                <div key={index} style={{
                  backgroundColor: getBgColor(0.05),
                  padding: '1rem',
                  borderRadius: '8px',
                  border: `1px solid ${getBorderColor(0.1)}`
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    <Info style={{ color: '#10b981' }} />
                    <span style={{ fontWeight: 'bold' }}>Change {index + 1}</span>
                  </div>
                  <p style={{ margin: 0, lineHeight: '1.5' }}>
                    {change}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

                 {/* Action Buttons */}
         <div style={{ 
           textAlign: 'center', 
           marginTop: '2rem',
           display: 'flex',
           gap: '1rem',
           justifyContent: 'center',
           flexWrap: 'wrap'
         }}>
           <Link href="/catalog" style={{
             display: 'inline-flex',
             alignItems: 'center',
             gap: '0.5rem',
             padding: '0.75rem 1.5rem',
             backgroundColor: '#10b981',
             color: '#ffffff',
             textDecoration: 'none',
             borderRadius: '8px',
             fontWeight: 'bold',
             transition: 'all 0.3s ease'
           }}>
             <ShoppingCart />
             View All Products
           </Link>
           <Link href="/" style={{
             display: 'inline-flex',
             alignItems: 'center',
             gap: '0.5rem',
             padding: '0.75rem 1.5rem',
             backgroundColor: '#3b82f6',
             color: '#ffffff',
             textDecoration: 'none',
             borderRadius: '8px',
             fontWeight: 'bold',
             transition: 'all 0.3s ease'
           }}>
             <ArrowLeft />
             New Analysis
           </Link>
         </div>
      </div>

      {/* Footer */}
      <footer style={{
        padding: '0.25rem 1rem',
        textAlign: 'center',
        fontSize: '0.6rem',
        color: theme === 'dark' ? '#ffffff' : '#000000',
        flexShrink: 0,
        marginTop: '2rem'
      }}>
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