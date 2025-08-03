'use client'

import { useState } from 'react'
import { ShoppingCart, Star, Filter } from 'lucide-react'
import { useCart } from '@/hooks/useCart'
import { useAuth } from '@/hooks/useAuth'
import { products } from '@/lib/products'
import { CartDrawer } from '@/components/cart-drawer'
import { SignInModal } from '@/components/sign-in-modal'
import { useTheme } from '@/hooks/useTheme'
import { ThemeToggle } from '@/components/theme-toggle'

export default function CatalogPage() {
  const { dispatch, isAuthenticated } = useCart()
  const { state: authState } = useAuth()
  const { theme } = useTheme()
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [sortBy, setSortBy] = useState('name')
  const [showSignInModal, setShowSignInModal] = useState(false)

  const categories = ['all', 'cleanser', 'serum', 'moisturizer', 'treatment', 'sunscreen']

  const filteredProducts = products.filter(product => 
    selectedCategory === 'all' || product.category === selectedCategory
  )

  const sortedProducts = [...filteredProducts].sort((a, b) => {
    switch (sortBy) {
      case 'price-low':
        return a.price - b.price
      case 'price-high':
        return b.price - a.price
      case 'name':
        return a.name.localeCompare(b.name)
      default:
        return 0
    }
  })

  const addToCart = (product: any) => {
    if (isAuthenticated) {
      dispatch({ type: 'ADD_ITEM', payload: product })
    } else {
      setShowSignInModal(true)
    }
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
          <img
            src="https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png"
            alt="Shine Logo"
            style={{
              height: '40px',
              width: 'auto'
            }}
          />
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

      {/* Filters */}
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '1rem',
        display: 'flex',
        gap: '1rem',
        flexWrap: 'wrap',
        alignItems: 'center'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <Filter size={16} />
          <span style={{ fontSize: '0.9rem' }}>Filter:</span>
        </div>
        {categories.map(category => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: selectedCategory === category 
                ? (theme === 'dark' ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.2)')
                : (theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'),
              border: theme === 'dark' ? '1px solid rgba(255, 255, 255, 0.2)' : '1px solid rgba(0, 0, 0, 0.2)',
              borderRadius: '20px',
              color: theme === 'dark' ? '#ffffff' : '#000000',
              cursor: 'pointer',
              fontSize: '0.8rem',
              textTransform: 'capitalize'
            }}
          >
            {category}
          </button>
        ))}
        
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          style={{
            padding: '0.5rem',
            backgroundColor: theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
            border: theme === 'dark' ? '1px solid rgba(255, 255, 255, 0.2)' : '1px solid rgba(0, 0, 0, 0.2)',
            borderRadius: '8px',
            color: theme === 'dark' ? '#ffffff' : '#000000',
            fontSize: '0.8rem',
            marginLeft: 'auto'
          }}
        >
          <option value="name">Sort by Name</option>
          <option value="price-low">Price: Low to High</option>
          <option value="price-high">Price: High to Low</option>
        </select>
      </div>

      {/* Products Grid */}
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '1rem',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
        gap: '2rem'
      }}>
        {sortedProducts.map((product) => (
          <div key={product.id} style={{
            backgroundColor: theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
            borderRadius: '16px',
            padding: '1.5rem',
            border: theme === 'dark' ? '1px solid rgba(255, 255, 255, 0.2)' : '1px solid rgba(0, 0, 0, 0.2)',
            backdropFilter: 'blur(10px)',
            transition: 'all 0.3s ease',
            cursor: 'pointer'
          }}>
            <img
              src={product.image}
              alt={product.name}
              style={{
                width: '100%',
                height: '200px',
                objectFit: 'cover',
                borderRadius: '12px',
                marginBottom: '1rem'
              }}
            />
            
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
                <ShoppingCart size={16} />
                {isAuthenticated ? 'Add to Cart' : 'Sign In to Add'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {sortedProducts.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: '4rem 1rem',
          color: 'rgba(255, 255, 255, 0.7)'
        }}>
          <h3>No products found</h3>
          <p>Try adjusting your filters</p>
        </div>
      )}

      {/* Sign In Modal */}
      <SignInModal 
        isOpen={showSignInModal}
        onClose={() => setShowSignInModal(false)}
        onSuccess={() => setShowSignInModal(false)}
      />
    </div>
  )
} 