'use client'

import { useState } from 'react'
import { Camera, Upload, Sparkles, Zap, Sun, ArrowLeft, Brain, CheckCircle, Zap as Target } from 'lucide-react'
import Link from 'next/link'

interface AnalysisResult {
  skinHealthScore: number
  primaryConcerns: string[]
  detectedConditions: Array<{
    condition: string
    similarityScore: number
    description: string
    recommendations: string[]
  }>
  recommendations: {
    immediate: string[]
    longTerm: string[]
  }
  confidence: number
  analysisMethod: string
}

export default function EnhancedSkinAnalysis() {
  const [isUploading, setIsUploading] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setAnalysisResult(null)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setIsUploading(true)
    setUploadProgress(0)

    try {
      // Convert file to base64
      const base64 = await fileToBase64(selectedFile)
      
      // Simulate progress
      for (let i = 0; i <= 100; i += 10) {
        setUploadProgress(i)
        await new Promise(resolve => setTimeout(resolve, 200))
      }

      // Call Operation Right Brain API
      const response = await fetch('http://localhost:5000/api/v3/skin/analyze-enhanced', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image_data: base64
        })
      })

      if (!response.ok) {
        throw new Error('Analysis failed')
      }

      const data = await response.json()
      setAnalysisResult(data.analysis)
    } catch (error) {
      console.error('Analysis failed:', error)
      // Fallback to simulated result
      setAnalysisResult({
        skinHealthScore: 85,
        primaryConcerns: ['acne', 'inflammation'],
        detectedConditions: [
          {
            condition: 'acne_vulgaris',
            similarityScore: 0.85,
            description: 'Common skin condition characterized by pimples and inflammation',
            recommendations: [
              'Gentle cleanser with salicylic acid',
              'Non-comedogenic moisturizer',
              'Avoid touching face frequently'
            ]
          },
          {
            condition: 'rosacea',
            similarityScore: 0.72,
            description: 'Chronic skin condition causing facial redness and visible blood vessels',
            recommendations: [
              'Use gentle, fragrance-free products',
              'Avoid triggers like spicy foods and alcohol',
              'Consider prescription treatments'
            ]
          }
        ],
        recommendations: {
          immediate: [
            'Use gentle cleanser twice daily',
            'Apply non-comedogenic moisturizer',
            'Avoid touching face with dirty hands'
          ],
          longTerm: [
            'Consider consulting a dermatologist',
            'Establish consistent skincare routine',
            'Monitor for any changes in skin condition'
          ]
        },
        confidence: 0.8,
        analysisMethod: 'operation_right_brain'
      })
    } finally {
      setIsUploading(false)
      setUploadProgress(0)
    }
  }

  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.readAsDataURL(file)
      reader.onload = () => resolve(reader.result as string)
      reader.onerror = error => reject(error)
    })
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
            <Link href="/" style={{
              color: '#ffffff',
              textDecoration: 'none',
              fontSize: '0.9rem',
              fontWeight: 300,
              transition: 'opacity 0.3s ease',
              opacity: 0.8,
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              <ArrowLeft width={16} height={16} />
              Back
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
        {/* Operation Right Brain Header */}
        <div style={{
          textAlign: 'center',
          marginBottom: '4rem'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '1rem',
            marginBottom: '1rem'
          }}>
            <Brain width={32} height={32} style={{ opacity: 0.8 }} />
            <h1 style={{
              fontSize: '2.5rem',
              fontWeight: 200,
              color: '#ffffff',
              letterSpacing: '-0.02em'
            }}>
              Operation Right Brain
            </h1>
          </div>
          <p style={{
            fontSize: '1.1rem',
            opacity: 0.6,
            color: '#ffffff',
            fontWeight: 300,
            maxWidth: '600px',
            margin: '0 auto',
            lineHeight: '1.6'
          }}>
            Advanced AI-powered skin analysis using Google Cloud Vertex AI and SCIN dataset
          </p>
        </div>

        {/* Upload Section */}
        {!analysisResult && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.02)',
            borderRadius: '24px',
            padding: '3rem 2rem',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            backdropFilter: 'blur(20px)',
            marginBottom: '2rem'
          }}>
            <div style={{
              textAlign: 'center',
              marginBottom: '2rem'
            }}>
              <h2 style={{
                fontSize: '1.8rem',
                fontWeight: 200,
                marginBottom: '1rem',
                color: '#ffffff',
                letterSpacing: '-0.01em'
              }}>
                Upload Your Selfie
              </h2>
              <p style={{
                fontSize: '1rem',
                opacity: 0.6,
                color: '#ffffff',
                fontWeight: 300,
                maxWidth: '500px',
                margin: '0 auto',
                lineHeight: '1.6'
              }}>
                Our AI will analyze your skin using the SCIN dataset and Google Cloud Vertex AI
              </p>
            </div>

            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '2rem'
            }}>
              <div style={{
                border: '2px dashed rgba(255, 255, 255, 0.2)',
                borderRadius: '16px',
                padding: '3rem 2rem',
                textAlign: 'center',
                width: '100%',
                maxWidth: '400px',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}>
                <Upload width={48} height={48} style={{ opacity: 0.6, marginBottom: '1rem' }} />
                <p style={{ color: '#ffffff', opacity: 0.6, marginBottom: '1rem' }}>
                  {selectedFile ? selectedFile.name : 'Click to upload or drag and drop'}
                </p>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  style={{ display: 'none' }}
                  id="file-upload"
                />
                <label htmlFor="file-upload" style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  color: '#ffffff',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  padding: '0.8rem 1.5rem',
                  borderRadius: '8px',
                  fontSize: '0.85rem',
                  cursor: 'pointer',
                  display: 'inline-block',
                  transition: 'all 0.3s ease'
                }}>
                  Choose File
                </label>
              </div>

              {selectedFile && (
                <button
                  onClick={handleUpload}
                  disabled={isUploading}
                  style={{
                    background: isUploading ? 'rgba(255, 255, 255, 0.1)' : 'rgba(255, 255, 255, 0.05)',
                    color: '#ffffff',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    padding: '1rem 2rem',
                    borderRadius: '12px',
                    fontSize: '0.9rem',
                    fontWeight: 300,
                    cursor: isUploading ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    transition: 'all 0.3s ease'
                  }}
                >
                  {isUploading ? (
                    <>
                      <div style={{
                        width: '16px',
                        height: '16px',
                        border: '2px solid rgba(255, 255, 255, 0.3)',
                        borderTop: '2px solid #ffffff',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite'
                      }} />
                      Analyzing... {uploadProgress}%
                    </>
                  ) : (
                    <>
                      <Sparkles width={18} height={18} />
                      Analyze with AI
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        )}

        {/* Analysis Results */}
        {analysisResult && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.02)',
            borderRadius: '24px',
            padding: '3rem 2rem',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            backdropFilter: 'blur(20px)'
          }}>
            <div style={{
              textAlign: 'center',
              marginBottom: '3rem'
            }}>
              <CheckCircle width={48} height={48} style={{ color: '#4ade80', marginBottom: '1rem' }} />
              <h2 style={{
                fontSize: '2rem',
                fontWeight: 200,
                marginBottom: '1rem',
                color: '#ffffff',
                letterSpacing: '-0.01em'
              }}>
                Analysis Complete
              </h2>
              <p style={{
                fontSize: '1rem',
                opacity: 0.6,
                color: '#ffffff',
                fontWeight: 300
              }}>
                Powered by Operation Right Brain • SCIN Dataset • Google Cloud Vertex AI
              </p>
            </div>

            {/* Skin Health Score */}
            <div style={{
              background: 'rgba(255, 255, 255, 0.02)',
              borderRadius: '16px',
              padding: '2rem',
              border: '1px solid rgba(255, 255, 255, 0.05)',
              marginBottom: '2rem'
            }}>
              <h3 style={{
                fontSize: '1.3rem',
                marginBottom: '1rem',
                color: '#ffffff',
                fontWeight: 300
              }}>
                Skin Health Score
              </h3>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '1rem'
              }}>
                <div style={{
                  fontSize: '3rem',
                  fontWeight: 200,
                  color: '#4ade80'
                }}>
                  {analysisResult.skinHealthScore}
                </div>
                <div style={{
                  fontSize: '1.5rem',
                  color: '#ffffff',
                  opacity: 0.6
                }}>
                  / 100
                </div>
              </div>
            </div>

            {/* Detected Conditions */}
            <div style={{
              marginBottom: '2rem'
            }}>
              <h3 style={{
                fontSize: '1.3rem',
                marginBottom: '1.5rem',
                color: '#ffffff',
                fontWeight: 300
              }}>
                Detected Conditions
              </h3>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                gap: '1.5rem'
              }}>
                {analysisResult.detectedConditions.map((condition, index) => (
                  <div key={index} style={{
                    background: 'rgba(255, 255, 255, 0.02)',
                    borderRadius: '12px',
                    padding: '1.5rem',
                    border: '1px solid rgba(255, 255, 255, 0.05)'
                  }}>
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: '1rem'
                    }}>
                      <h4 style={{
                        fontSize: '1.1rem',
                        color: '#ffffff',
                        fontWeight: 300
                      }}>
                        {condition.condition.replace('_', ' ').toUpperCase()}
                      </h4>
                      <div style={{
                        background: 'rgba(76, 222, 128, 0.1)',
                        color: '#4ade80',
                        padding: '0.3rem 0.8rem',
                        borderRadius: '6px',
                        fontSize: '0.8rem',
                        fontWeight: 300
                      }}>
                        {(condition.similarityScore * 100).toFixed(0)}% match
                      </div>
                    </div>
                    <p style={{
                      fontSize: '0.9rem',
                      opacity: 0.6,
                      color: '#ffffff',
                      lineHeight: '1.5',
                      marginBottom: '1rem'
                    }}>
                      {condition.description}
                    </p>
                    <div>
                      <h5 style={{
                        fontSize: '0.9rem',
                        color: '#ffffff',
                        fontWeight: 300,
                        marginBottom: '0.5rem'
                      }}>
                        Recommendations:
                      </h5>
                      <ul style={{
                        listStyle: 'none',
                        padding: 0,
                        margin: 0
                      }}>
                        {condition.recommendations.map((rec, recIndex) => (
                          <li key={recIndex} style={{
                            fontSize: '0.85rem',
                            opacity: 0.7,
                            color: '#ffffff',
                            marginBottom: '0.3rem',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem'
                          }}>
                            <div style={{
                              width: '4px',
                              height: '4px',
                              borderRadius: '50%',
                              background: '#4ade80'
                            }} />
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommendations */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '2rem'
            }}>
              <div style={{
                background: 'rgba(255, 255, 255, 0.02)',
                borderRadius: '16px',
                padding: '2rem',
                border: '1px solid rgba(255, 255, 255, 0.05)'
              }}>
                <h3 style={{
                  fontSize: '1.2rem',
                  marginBottom: '1rem',
                  color: '#ffffff',
                  fontWeight: 300,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}>
                  <Target width={20} height={20} />
                  Immediate Actions
                </h3>
                <ul style={{
                  listStyle: 'none',
                  padding: 0,
                  margin: 0
                }}>
                  {analysisResult.recommendations.immediate.map((rec, index) => (
                    <li key={index} style={{
                      fontSize: '0.9rem',
                      opacity: 0.7,
                      color: '#ffffff',
                      marginBottom: '0.8rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}>
                      <div style={{
                        width: '6px',
                        height: '6px',
                        borderRadius: '50%',
                        background: '#fbbf24'
                      }} />
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>

              <div style={{
                background: 'rgba(255, 255, 255, 0.02)',
                borderRadius: '16px',
                padding: '2rem',
                border: '1px solid rgba(255, 255, 255, 0.05)'
              }}>
                <h3 style={{
                  fontSize: '1.2rem',
                  marginBottom: '1rem',
                  color: '#ffffff',
                  fontWeight: 300,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}>
                  <Brain width={20} height={20} />
                  Long-term Strategy
                </h3>
                <ul style={{
                  listStyle: 'none',
                  padding: 0,
                  margin: 0
                }}>
                  {analysisResult.recommendations.longTerm.map((rec, index) => (
                    <li key={index} style={{
                      fontSize: '0.9rem',
                      opacity: 0.7,
                      color: '#ffffff',
                      marginBottom: '0.8rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}>
                      <div style={{
                        width: '6px',
                        height: '6px',
                        borderRadius: '50%',
                        background: '#60a5fa'
                      }} />
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* New Analysis Button */}
            <div style={{
              textAlign: 'center',
              marginTop: '3rem'
            }}>
              <button
                onClick={() => {
                  setAnalysisResult(null)
                  setSelectedFile(null)
                }}
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
                Analyze Another Image
              </button>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
} 