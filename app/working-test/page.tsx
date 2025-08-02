'use client'

import { useTheme } from 'next-themes'
import { Sun } from 'lucide-react'

export default function WorkingTest() {
  const { theme, setTheme } = useTheme()

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: theme === 'dark' ? '#000000' : '#ffffff',
      color: theme === 'dark' ? '#ffffff' : '#000000',
      fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      fontWeight: 300
    }}>
      {/* Header */}
      <header style={{
        backgroundColor: theme === 'dark' ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.8)',
        backdropFilter: 'blur(20px)',
        borderBottom: `1px solid ${theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'}`,
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
                filter: theme === 'dark' ? 'brightness(0) invert(1)' : 'none'
              }}
            />
          </div>

          {/* Navigation */}
          <nav style={{
            display: 'flex',
            alignItems: 'center',
            gap: '2rem'
          }}>
            <button
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              style={{
                background: theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)',
                border: `1px solid ${theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'}`,
                borderRadius: '6px',
                padding: '0.5rem',
                color: theme === 'dark' ? '#ffffff' : '#000000',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.3s ease'
              }}
            >
              <Sun width={16} height={16} />
            </button>
          </nav>
        </div>
      </header>

      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '3rem 2rem'
      }}>
        <div style={{
          textAlign: 'center',
          marginBottom: '4rem'
        }}>
          <h1 style={{
            fontSize: '3rem',
            marginBottom: '1rem',
            fontWeight: 200,
            color: theme === 'dark' ? '#ffffff' : '#000000',
            letterSpacing: '-0.02em'
          }}>
            Working Test Page
          </h1>
          <p style={{
            fontSize: '1.2rem',
            opacity: 0.6,
            color: theme === 'dark' ? '#ffffff' : '#000000',
            fontWeight: 300
          }}>
            This page uses inline styles to bypass any Tailwind CSS issues
          </p>
        </div>

        <div style={{
          background: theme === 'dark' ? 'rgba(255, 255, 255, 0.02)' : 'rgba(0, 0, 0, 0.02)',
          borderRadius: '24px',
          padding: '3rem 2rem',
          border: `1px solid ${theme === 'dark' ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)'}`,
          backdropFilter: 'blur(20px)',
          marginBottom: '2rem'
        }}>
          <h2 style={{
            fontSize: '2rem',
            marginBottom: '1rem',
            color: theme === 'dark' ? '#ffffff' : '#000000',
            fontWeight: 200
          }}>
            Test Status
          </h2>
          <div style={{
            background: theme === 'dark' ? 'rgba(0, 255, 0, 0.1)' : 'rgba(0, 255, 0, 0.05)',
            border: `2px solid ${theme === 'dark' ? '#00ff00' : '#00cc00'}`,
            borderRadius: '12px',
            padding: '1rem',
            margin: '1rem 0',
            textAlign: 'center'
          }}>
            ✅ Next.js Page Working - Inline Styles Applied Successfully
          </div>
          <p style={{
            color: theme === 'dark' ? '#ffffff' : '#000000',
            opacity: 0.6,
            fontWeight: 300
          }}>
            This page uses inline styles to bypass any Tailwind CSS issues.
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '2rem',
          marginBottom: '4rem'
        }}>
          <div style={{
            background: theme === 'dark' ? 'rgba(255, 255, 255, 0.02)' : 'rgba(0, 0, 0, 0.02)',
            borderRadius: '16px',
            padding: '2rem',
            textAlign: 'center',
            border: `1px solid ${theme === 'dark' ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)'}`,
            backdropFilter: 'blur(20px)'
          }}>
            <div style={{
              fontSize: '2rem',
              marginBottom: '1rem',
              opacity: 0.8
            }}>
              🧠
            </div>
            <h3 style={{
              fontSize: '1.2rem',
              marginBottom: '0.8rem',
              color: theme === 'dark' ? '#ffffff' : '#000000',
              fontWeight: 300
            }}>
              AI-Powered Analysis
            </h3>
            <p style={{
              color: theme === 'dark' ? '#ffffff' : '#000000',
              fontSize: '0.9rem',
              opacity: 0.6,
              fontWeight: 300,
              lineHeight: '1.6'
            }}>
              Advanced skin analysis using Google Cloud Vertex AI
            </p>
          </div>

          <div style={{
            background: theme === 'dark' ? 'rgba(255, 255, 255, 0.02)' : 'rgba(0, 0, 0, 0.02)',
            borderRadius: '16px',
            padding: '2rem',
            textAlign: 'center',
            border: `1px solid ${theme === 'dark' ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)'}`,
            backdropFilter: 'blur(20px)'
          }}>
            <div style={{
              fontSize: '2rem',
              marginBottom: '1rem',
              opacity: 0.8
            }}>
              ⚡
            </div>
            <h3 style={{
              fontSize: '1.2rem',
              marginBottom: '0.8rem',
              color: theme === 'dark' ? '#ffffff' : '#000000',
              fontWeight: 300
            }}>
              Instant Results
            </h3>
            <p style={{
              color: theme === 'dark' ? '#ffffff' : '#000000',
              fontSize: '0.9rem',
              opacity: 0.6,
              fontWeight: 300,
              lineHeight: '1.6'
            }}>
              Get personalized recommendations in seconds
            </p>
          </div>

          <div style={{
            background: theme === 'dark' ? 'rgba(255, 255, 255, 0.02)' : 'rgba(0, 0, 0, 0.02)',
            borderRadius: '16px',
            padding: '2rem',
            textAlign: 'center',
            border: `1px solid ${theme === 'dark' ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)'}`,
            backdropFilter: 'blur(20px)'
          }}>
            <div style={{
              fontSize: '2rem',
              marginBottom: '1rem',
              opacity: 0.8
            }}>
              📱
            </div>
            <h3 style={{
              fontSize: '1.2rem',
              marginBottom: '0.8rem',
              color: theme === 'dark' ? '#ffffff' : '#000000',
              fontWeight: 300
            }}>
              Mobile Optimized
            </h3>
            <p style={{
              color: theme === 'dark' ? '#ffffff' : '#000000',
              fontSize: '0.9rem',
              opacity: 0.6,
              fontWeight: 300,
              lineHeight: '1.6'
            }}>
              Perfect for selfie analysis on your phone
            </p>
          </div>
        </div>

        <div style={{
          background: theme === 'dark' ? 'rgba(255, 255, 255, 0.02)' : 'rgba(0, 0, 0, 0.02)',
          borderRadius: '24px',
          padding: '2.5rem',
          border: `1px solid ${theme === 'dark' ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)'}`,
          backdropFilter: 'blur(20px)'
        }}>
          <h2 style={{
            fontSize: '1.8rem',
            marginBottom: '2rem',
            textAlign: 'center',
            color: theme === 'dark' ? '#ffffff' : '#000000',
            fontWeight: 200,
            letterSpacing: '-0.01em'
          }}>
            Technical Information
          </h2>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '1.5rem'
          }}>
            <div style={{
              background: theme === 'dark' ? 'rgba(255, 255, 255, 0.02)' : 'rgba(0, 0, 0, 0.02)',
              borderRadius: '12px',
              padding: '1.5rem',
              border: `1px solid ${theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'}`,
              transition: 'all 0.3s ease'
            }}>
              <h3 style={{
                fontSize: '1.1rem',
                marginBottom: '0.8rem',
                color: theme === 'dark' ? '#ffffff' : '#000000',
                fontWeight: 300
              }}>
                Current Issue
              </h3>
              <p style={{
                fontSize: '0.85rem',
                opacity: 0.6,
                marginBottom: '1.2rem',
                color: theme === 'dark' ? '#ffffff' : '#000000',
                lineHeight: '1.5',
                fontWeight: 300
              }}>
                Tailwind CSS styles not loading properly
              </p>
            </div>

            <div style={{
              background: theme === 'dark' ? 'rgba(255, 255, 255, 0.02)' : 'rgba(0, 0, 0, 0.02)',
              borderRadius: '12px',
              padding: '1.5rem',
              border: `1px solid ${theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'}`,
              transition: 'all 0.3s ease'
            }}>
              <h3 style={{
                fontSize: '1.1rem',
                marginBottom: '0.8rem',
                color: theme === 'dark' ? '#ffffff' : '#000000',
                fontWeight: 300
              }}>
                Solution
              </h3>
              <p style={{
                fontSize: '0.85rem',
                opacity: 0.6,
                marginBottom: '1.2rem',
                color: theme === 'dark' ? '#ffffff' : '#000000',
                lineHeight: '1.5',
                fontWeight: 300
              }}>
                This page uses inline styles to bypass Tailwind
              </p>
            </div>

            <div style={{
              background: theme === 'dark' ? 'rgba(255, 255, 255, 0.02)' : 'rgba(0, 0, 0, 0.02)',
              borderRadius: '12px',
              padding: '1.5rem',
              border: `1px solid ${theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'}`,
              transition: 'all 0.3s ease'
            }}>
              <h3 style={{
                fontSize: '1.1rem',
                marginBottom: '0.8rem',
                color: theme === 'dark' ? '#ffffff' : '#000000',
                fontWeight: 300
              }}>
                Next Steps
              </h3>
              <p style={{
                fontSize: '0.85rem',
                opacity: 0.6,
                marginBottom: '1.2rem',
                color: theme === 'dark' ? '#ffffff' : '#000000',
                lineHeight: '1.5',
                fontWeight: 300
              }}>
                Fix Tailwind CSS integration or use inline styles
              </p>
            </div>
          </div>
        </div>

        {/* Back Button */}
        <div style={{
          textAlign: 'center',
          marginTop: '3rem'
        }}>
          <button
            onClick={() => window.history.back()}
            style={{
              background: theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)',
              color: theme === 'dark' ? '#ffffff' : '#000000',
              border: `1px solid ${theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'}`,
              padding: '1rem 2rem',
              borderRadius: '12px',
              fontSize: '0.9rem',
              fontWeight: 300,
              cursor: 'pointer',
              transition: 'all 0.3s ease'
            }}
          >
            ← Back to Main App
          </button>
        </div>
      </div>
    </div>
  )
} 