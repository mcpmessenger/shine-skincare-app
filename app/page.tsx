'use client'

import { useState } from 'react'
import Link from 'next/link'

export default function HomePage() {
  const [isCameraActive, setIsCameraActive] = useState(false)

  const startCamera = async () => {
    try {
      await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'user' },
        audio: false 
      })
      setIsCameraActive(true)
    } catch (error) {
      console.error('Camera access denied:', error)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#000000',
      color: '#ffffff',
      fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      fontWeight: 300
    }}>
      {/* Header */}
      <header style={{
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        position: 'sticky',
        top: 0,
        zIndex: 1000
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '1rem 2rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          {/* Logo */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '1rem'
          }}>
            <img 
              src="https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png"
              alt="Shine Logo"
              style={{
                height: '48px',
                width: 'auto',
                filter: 'brightness(0) invert(1)'
              }}
            />
          </div>

          {/* Navigation */}
          <nav style={{
            display: 'flex',
            alignItems: 'center',
            gap: '2rem'
          }}>
            <Link href="/enhanced-skin-analysis" style={{
              color: '#ffffff',
              textDecoration: 'none',
              fontSize: '0.9rem',
              fontWeight: 300,
              transition: 'opacity 0.3s ease',
              opacity: 0.8
            }}>
              Analysis
            </Link>
            <Link href="/working-test" style={{
              color: '#ffffff',
              textDecoration: 'none',
              fontSize: '0.9rem',
              fontWeight: 300,
              transition: 'opacity 0.3s ease',
              opacity: 0.8
            }}>
              Test
            </Link>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '3rem 2rem'
      }}>
        {/* Camera Interface */}
        <div style={{
          textAlign: 'center',
          marginBottom: '4rem'
        }}>
          <div style={{
            background: 'rgba(255, 255, 255, 0.02)',
            borderRadius: '24px',
            padding: '3rem 2rem',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            backdropFilter: 'blur(20px)',
            marginBottom: '2rem'
          }}>
            {!isCameraActive ? (
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '2rem'
              }}>
                <div>
                  <h1 style={{
                    fontSize: '2.5rem',
                    fontWeight: 200,
                    marginBottom: '1rem',
                    color: '#ffffff',
                    letterSpacing: '-0.02em'
                  }}>
                    Take a Selfie
                  </h1>
                  <p style={{
                    fontSize: '1rem',
                    opacity: 0.6,
                    color: '#ffffff',
                    fontWeight: 300,
                    maxWidth: '400px',
                    margin: '0 auto',
                    lineHeight: '1.6'
                  }}>
                    Capture your selfie for instant AI-powered skin analysis
                  </p>
                </div>

                <button
                  onClick={startCamera}
                  style={{
                    background: 'rgba(255, 255, 255, 0.05)',
                    color: '#ffffff',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    padding: '1rem 2rem',
                    borderRadius: '12px',
                    fontSize: '0.9rem',
                    fontWeight: 300,
                    cursor: 'pointer',
                    transition: 'all 0.3s ease'
                  }}
                >
                  Start Camera
                </button>
              </div>
            ) : (
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '2rem'
              }}>
                <div style={{
                  width: '280px',
                  height: '280px',
                  borderRadius: '16px',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: 'rgba(255, 255, 255, 0.05)'
                }}>
                  <p style={{ color: '#ffffff', opacity: 0.6 }}>Camera Active</p>
                </div>
                
                <button
                  onClick={() => setIsCameraActive(false)}
                  style={{
                    background: 'rgba(255, 255, 255, 0.05)',
                    color: '#ffffff',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    padding: '0.8rem 1.5rem',
                    borderRadius: '8px',
                    fontSize: '0.85rem',
                    fontWeight: 300,
                    cursor: 'pointer',
                    transition: 'all 0.3s ease'
                  }}
                >
                  Stop Camera
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Feature Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '1.5rem',
          marginBottom: '4rem'
        }}>
          <div style={{
            background: 'rgba(255, 255, 255, 0.02)',
            borderRadius: '16px',
            padding: '2rem',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            backdropFilter: 'blur(20px)'
          }}>
            <h3 style={{
              fontSize: '1.2rem',
              marginBottom: '0.8rem',
              color: '#ffffff',
              fontWeight: 300
            }}>
              AI-Powered Analysis
            </h3>
            <p style={{
              color: '#ffffff',
              fontSize: '0.9rem',
              opacity: 0.6,
              fontWeight: 300,
              lineHeight: '1.6'
            }}>
              Advanced skin analysis using Google Cloud Vertex AI
            </p>
          </div>

          <div style={{
            background: 'rgba(255, 255, 255, 0.02)',
            borderRadius: '16px',
            padding: '2rem',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            backdropFilter: 'blur(20px)'
          }}>
            <h3 style={{
              fontSize: '1.2rem',
              marginBottom: '0.8rem',
              color: '#ffffff',
              fontWeight: 300
            }}>
              Instant Results
            </h3>
            <p style={{
              color: '#ffffff',
              fontSize: '0.9rem',
              opacity: 0.6,
              fontWeight: 300,
              lineHeight: '1.6'
            }}>
              Get personalized recommendations in seconds
            </p>
          </div>

          <div style={{
            background: 'rgba(255, 255, 255, 0.02)',
            borderRadius: '16px',
            padding: '2rem',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            backdropFilter: 'blur(20px)'
          }}>
            <h3 style={{
              fontSize: '1.2rem',
              marginBottom: '0.8rem',
              color: '#ffffff',
              fontWeight: 300
            }}>
              Mobile Optimized
            </h3>
            <p style={{
              color: '#ffffff',
              fontSize: '0.9rem',
              opacity: 0.6,
              fontWeight: 300,
              lineHeight: '1.6'
            }}>
              Perfect for selfie analysis on your phone
            </p>
          </div>
        </div>

        {/* Call to Action */}
        <div style={{
          textAlign: 'center',
          marginTop: '4rem',
          padding: '3rem 2rem',
          background: 'rgba(255, 255, 255, 0.02)',
          borderRadius: '20px',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          backdropFilter: 'blur(20px)'
        }}>
          <h2 style={{
            fontSize: '2rem',
            marginBottom: '1rem',
            color: '#ffffff',
            fontWeight: 200,
            letterSpacing: '-0.01em'
          }}>
            Ready to Transform Your Skin?
          </h2>
          <p style={{
            fontSize: '1rem',
            marginBottom: '2rem',
            opacity: 0.6,
            color: '#ffffff',
            fontWeight: 300,
            maxWidth: '500px',
            margin: '0 auto 2rem',
            lineHeight: '1.6'
          }}>
            Join thousands of users who have discovered their perfect skincare routine
          </p>
          <Link href="/enhanced-skin-analysis" style={{
            background: 'rgba(255, 255, 255, 0.05)',
            color: '#ffffff',
            textDecoration: 'none',
            padding: '1rem 2rem',
            borderRadius: '12px',
            fontSize: '0.9rem',
            fontWeight: 300,
            display: 'inline-block',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            transition: 'all 0.3s ease'
          }}>
            Start Your Analysis
          </Link>
        </div>
      </div>
    </div>
  )
} 