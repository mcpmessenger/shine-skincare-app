'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Star, ShoppingCart } from 'lucide-react'
import { useTheme } from 'next-themes'
import { useAuth } from '@/hooks/useAuth'
import { useCart } from '@/hooks/useCart'
import { CartDrawer } from '@/components/cart-drawer'
import { ThemeToggle } from '@/components/theme-toggle'
import { SignInModal } from '@/components/sign-in-modal'

interface AnalysisData {
  health_score: number
  conditions: string[]
  recommendations: string[]
  face_detected: boolean
}

export default function CatalogPage() {
  const { theme } = useTheme()
  const { state: authState } = useAuth()
  const { dispatch, isAuthenticated } = useCart()
  const [showSignInModal, setShowSignInModal] = useState(false)
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null)
  const [showRecommendations, setShowRecommendations] = useState(false)

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
  }, [])

  const getRecommendedProducts = () => {
    if (!analysisData) return []
    
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
    
    // Remove duplicates and limit to top 6
    const unique = recommended.filter((product, index, self) =>
      index === self.findIndex(p => p.id === product.id)
    )
    
    return unique.slice(0, 6)
  }

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
            Product Catalog
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

      {/* Analysis Results Summary */}
      {showRecommendations && analysisData && (
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '1rem',
          backgroundColor: getBgColor(0.1),
          borderRadius: '12px',
          border: `1px solid ${getBorderColor(0.2)}`,
          marginBottom: '1rem'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            marginBottom: '0.5rem'
          }}>
            <Star style={{ color: '#3b82f6' }} />
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: getTextColor(1) }}>
              Personalized Recommendations
            </h3>
          </div>
          <div style={{
            display: 'flex',
            gap: '1rem',
            flexWrap: 'wrap',
            fontSize: '0.9rem',
            color: getTextColor(0.8)
          }}>
            <span>Health Score: {Math.round(analysisData.health_score)}%</span>
            <span>•</span>
            <span>Conditions: {analysisData.conditions.slice(0, 3).join(', ')}</span>
            {analysisData.conditions.length > 3 && <span>+{analysisData.conditions.length - 3} more</span>}
          </div>
        </div>
      )}

      {/* Recommended Products */}
      {showRecommendations && analysisData && getRecommendedProducts().length > 0 && (
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '1rem'
        }}>
          <h2 style={{
            fontSize: '1.3rem',
            marginBottom: '1rem',
            color: getTextColor(1)
          }}>
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
                  margin: '0 0 1rem 0',
                  lineHeight: '1.4'
                }}>
                  {product.description}
                </p>
                
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

      {/* All Products */}
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '1rem'
      }}>
        <h2 style={{
          fontSize: '1.3rem',
          marginBottom: '1rem',
          color: getTextColor(1)
        }}>
          All Products
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: '1.5rem'
        }}>
          {products.map(product => (
            <div key={product.id} style={{
              backgroundColor: getBgColor(0.05),
              borderRadius: '12px',
              padding: '1.5rem',
              border: `1px solid ${getBorderColor(0.1)}`
            }}>
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
                margin: '0 0 1rem 0',
                lineHeight: '1.4'
              }}>
                {product.description}
              </p>
              
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

// Sample products data
const products = [
  {
    id: 1,
    name: "Vitamin C Serum",
    description: "Brightening serum with 20% Vitamin C for even skin tone and radiance",
    price: 45.00,
    category: "serum"
  },
  {
    id: 2,
    name: "Hyaluronic Acid Moisturizer",
    description: "Deeply hydrating moisturizer with hyaluronic acid for plump, smooth skin",
    price: 32.00,
    category: "moisturizer"
  },
  {
    id: 3,
    name: "Retinol Night Cream",
    description: "Anti-aging night cream with retinol to reduce fine lines and wrinkles",
    price: 58.00,
    category: "treatment"
  },
  {
    id: 4,
    name: "SPF 50 Sunscreen",
    description: "Broad-spectrum sunscreen with zinc oxide for daily protection",
    price: 28.00,
    category: "sunscreen"
  },
  {
    id: 5,
    name: "Niacinamide Serum",
    description: "Pore-refining serum with 10% niacinamide for clearer, smoother skin",
    price: 38.00,
    category: "serum"
  },
  {
    id: 6,
    name: "Gentle Cleanser",
    description: "pH-balanced cleanser that removes impurities without stripping skin",
    price: 24.00,
    category: "cleanser"
  }
] 