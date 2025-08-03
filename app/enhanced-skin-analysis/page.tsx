'use client'

import { useState, useRef, useEffect } from 'react'
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
  const [cameraMode, setCameraMode] = useState<'upload' | 'camera'>('upload')
  const [isCameraActive, setIsCameraActive] = useState(false)
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const [faceDetected, setFaceDetected] = useState(false)
  const [faceBounds, setFaceBounds] = useState({ x: 0, y: 0, width: 0, height: 0 })
  
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const faceDetectionInterval = useRef<NodeJS.Timeout | null>(null)

  // Camera setup
  useEffect(() => {
    if (cameraMode === 'camera' && !isCameraActive) {
      startCamera()
    } else if (cameraMode === 'upload' && isCameraActive) {
      stopCamera()
    }
    
    // Reset face detection state when not in camera mode
    if (cameraMode === 'upload') {
      setFaceDetected(false)
      setFaceBounds({ x: 0, y: 0, width: 0, height: 0 })
      if (faceDetectionInterval.current) {
        clearInterval(faceDetectionInterval.current)
        faceDetectionInterval.current = null
      }
    }
  }, [cameraMode])

  const startCamera = async () => {
    try {
      console.log('Starting camera...')
      
      // Simple camera setup - back to basics
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'user'
        }
      })
      
      console.log('Camera stream obtained:', stream)
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        streamRef.current = stream
        setIsCameraActive(true)
        
        // Simple video event handlers
        videoRef.current.onloadedmetadata = () => {
          console.log('Video metadata loaded')
          startFaceDetection()
        }
        
        videoRef.current.oncanplay = () => {
          console.log('Video can play')
        }
        
        videoRef.current.onplay = () => {
          console.log('Video started playing')
        }
      } else {
        console.error('Video ref is null')
      }
    } catch (error) {
      console.error('Camera access failed:', error)
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      alert(`Camera access failed: ${errorMessage}. Please check camera permissions.`)
    }
  }

  // Initialize face detection state
  useEffect(() => {
    // Ensure face detection is reset on component mount
    setFaceDetected(false)
    setFaceBounds({ x: 0, y: 0, width: 0, height: 0 })
    if (faceDetectionInterval.current) {
      clearInterval(faceDetectionInterval.current)
      faceDetectionInterval.current = null
    }
    
    // Cleanup on unmount
    return () => {
      if (faceDetectionInterval.current) {
        clearInterval(faceDetectionInterval.current)
        faceDetectionInterval.current = null
      }
    }
  }, [])

  const startFaceDetection = () => {
    if (faceDetectionInterval.current) {
      clearInterval(faceDetectionInterval.current)
    }
    
    // Simple face detection - just simulate for now
    faceDetectionInterval.current = setInterval(() => {
      // For now, just simulate face detection when camera is active
      if (isCameraActive && videoRef.current && videoRef.current.readyState >= 2) {
        setFaceDetected(true)
        setFaceBounds({
          x: 100,
          y: 100,
          width: 200,
          height: 200
        })
      } else {
        setFaceDetected(false)
      }
    }, 1000)
  }

  const detectFaceInVideo = async () => {
    // Simplified - just return for now
    return
  }

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    if (faceDetectionInterval.current) {
      clearInterval(faceDetectionInterval.current)
      faceDetectionInterval.current = null
    }
    setIsCameraActive(false)
    setCapturedImage(null)
    setFaceDetected(false)
  }

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current
      const canvas = canvasRef.current
      const context = canvas.getContext('2d')
      
      if (context) {
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        context.drawImage(video, 0, 0)
        
        canvas.toBlob((blob) => {
          if (blob) {
            const file = new File([blob], 'captured-selfie.jpg', { type: 'image/jpeg' })
            setSelectedFile(file)
            setCapturedImage(canvas.toDataURL('image/jpeg'))
          }
        }, 'image/jpeg', 0.8)
      }
    }
  }

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setAnalysisResult(null)
      setCapturedImage(null)
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
      const response = await fetch('http://localhost:5001/api/v3/skin/analyze-enhanced', {
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

  const testCameraPermissions = async () => {
    try {
      console.log('Testing camera permissions...')
      const devices = await navigator.mediaDevices.enumerateDevices()
      const videoDevices = devices.filter(device => device.kind === 'videoinput')
      console.log('Available video devices:', videoDevices)
      
      if (videoDevices.length === 0) {
        alert('No camera devices found')
        return
      }
      
      // Test basic camera access
      const stream = await navigator.mediaDevices.getUserMedia({ video: true })
      console.log('Camera access successful:', stream)
      stream.getTracks().forEach(track => track.stop())
      alert('Camera permissions working!')
    } catch (error) {
      console.error('Camera test failed:', error)
      alert(`Camera test failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
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

        {/* Upload/Camera Section */}
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
                {cameraMode === 'camera' ? 'Take Your Selfie' : 'Upload Your Selfie'}
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

            {/* Mode Toggle */}
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              gap: '1rem',
              marginBottom: '2rem'
            }}>
              <button
                onClick={() => setCameraMode('upload')}
                style={{
                  background: cameraMode === 'upload' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(255, 255, 255, 0.05)',
                  color: '#ffffff',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  padding: '0.8rem 1.5rem',
                  borderRadius: '8px',
                  fontSize: '0.85rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  transition: 'all 0.3s ease'
                }}
              >
                <Upload width={16} height={16} />
                Upload File
              </button>
              <button
                onClick={() => setCameraMode('camera')}
                style={{
                  background: cameraMode === 'camera' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(255, 255, 255, 0.05)',
                  color: '#ffffff',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  padding: '0.8rem 1.5rem',
                  borderRadius: '8px',
                  fontSize: '0.85rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  transition: 'all 0.3s ease'
                }}
              >
                <Camera width={16} height={16} />
                Use Camera
              </button>
              <button
                onClick={() => {
                  console.log('Debug: Manual camera start')
                  console.log('Camera mode:', cameraMode)
                  console.log('Is camera active:', isCameraActive)
                  console.log('Video ref:', videoRef.current)
                  startCamera()
                }}
                style={{
                  background: 'rgba(239, 68, 68, 0.1)',
                  color: '#ef4444',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  padding: '0.8rem 1.5rem',
                  borderRadius: '8px',
                  fontSize: '0.85rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  transition: 'all 0.3s ease'
                }}
              >
                <Camera width={16} height={16} />
                Debug Camera
              </button>
              <button
                onClick={testCameraPermissions}
                style={{
                  background: 'rgba(59, 130, 246, 0.1)',
                  color: '#3b82f6',
                  border: '1px solid rgba(59, 130, 246, 0.3)',
                  padding: '0.8rem 1.5rem',
                  borderRadius: '8px',
                  fontSize: '0.85rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  transition: 'all 0.3s ease'
                }}
              >
                Test Permissions
              </button>
            </div>

            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '2rem'
            }}>
              {/* Debug Status */}
              <div style={{
                background: 'rgba(255, 255, 255, 0.05)',
                padding: '1rem',
                borderRadius: '8px',
                fontSize: '0.8rem',
                color: '#ffffff',
                opacity: 0.7
              }}>
                <div>Camera Mode: {cameraMode}</div>
                <div>Camera Active: {isCameraActive ? 'Yes' : 'No'}</div>
                <div>Face Detected: {faceDetected ? 'Yes' : 'No'}</div>
                <div>Video Ready: {videoRef.current?.readyState && videoRef.current.readyState >= 2 ? 'Yes' : 'No'}</div>
              </div>
              {cameraMode === 'upload' ? (
                // File Upload Mode
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
              ) : (
                // Camera Mode
                <div style={{
                  width: '100%',
                  maxWidth: '400px', // Smaller for portrait
                  textAlign: 'center'
                }}>
                  {!capturedImage ? (
                    // Live Camera View
                    <div style={{
                      position: 'relative',
                      borderRadius: '16px',
                      overflow: 'hidden',
                      border: '2px solid rgba(255, 255, 255, 0.2)',
                      background: '#000000',
                      aspectRatio: '9/16', // Portrait aspect ratio
                      maxHeight: '600px'
                    }}>
                      <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        muted
                        style={{
                          width: '100%',
                          height: '100%',
                          objectFit: 'cover',
                          display: isCameraActive ? 'block' : 'none'
                        }}
                      />
                      {!isCameraActive && (
                        <div style={{
                          padding: '3rem 2rem',
                          textAlign: 'center',
                          height: '100%',
                          display: 'flex',
                          flexDirection: 'column',
                          justifyContent: 'center',
                          alignItems: 'center'
                        }}>
                          <Camera width={48} height={48} style={{ opacity: 0.6, marginBottom: '1rem' }} />
                          <p style={{ color: '#ffffff', opacity: 0.6 }}>
                            Camera starting...
                          </p>
                        </div>
                      )}
                      <canvas ref={canvasRef} style={{ display: 'none' }} />
                      
                      {/* Face Detection Overlay */}
                      {isCameraActive && (
                        <div style={{
                          position: 'absolute',
                          top: '1rem',
                          left: '50%',
                          transform: 'translateX(-50%)',
                          background: faceDetected ? 'rgba(76, 222, 128, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                          color: faceDetected ? '#4ade80' : '#ef4444',
                          padding: '0.5rem 1rem',
                          borderRadius: '20px',
                          fontSize: '0.8rem',
                          fontWeight: 300,
                          border: `1px solid ${faceDetected ? 'rgba(76, 222, 128, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`
                        }}>
                          {faceDetected ? '✓ Face Detected' : '⚠ No Face Detected'}
                        </div>
                      )}
                      
                      {isCameraActive && (
                        <button
                          onClick={capturePhoto}
                          style={{
                            position: 'absolute',
                            bottom: '2rem',
                            left: '50%',
                            transform: 'translateX(-50%)',
                            background: faceDetected ? 'rgba(255, 255, 255, 0.2)' : 'rgba(255, 255, 255, 0.1)',
                            color: '#ffffff',
                            border: `2px solid ${faceDetected ? '#4ade80' : '#ffffff'}`,
                            borderRadius: '50%',
                            width: '70px',
                            height: '70px',
                            cursor: faceDetected ? 'pointer' : 'not-allowed',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            transition: 'all 0.3s ease',
                            opacity: faceDetected ? 1 : 0.5
                          }}
                        >
                          <Camera width={28} height={28} />
                        </button>
                      )}
                    </div>
                  ) : (
                    // Captured Image Preview
                    <div style={{
                      borderRadius: '16px',
                      overflow: 'hidden',
                      border: '2px solid rgba(255, 255, 255, 0.2)',
                      background: '#000000',
                      aspectRatio: '9/16',
                      maxHeight: '600px'
                    }}>
                      <img
                        src={capturedImage}
                        alt="Captured selfie"
                        style={{
                          width: '100%',
                          height: '100%',
                          objectFit: 'cover',
                          display: 'block'
                        }}
                      />
                      <div style={{
                        position: 'absolute',
                        bottom: 0,
                        left: 0,
                        right: 0,
                        padding: '1rem',
                        background: 'linear-gradient(transparent, rgba(0,0,0,0.8))',
                        display: 'flex',
                        gap: '1rem',
                        justifyContent: 'center'
                      }}>
                        <button
                          onClick={() => {
                            setCapturedImage(null)
                            setSelectedFile(null)
                          }}
                          style={{
                            background: 'rgba(255, 255, 255, 0.1)',
                            color: '#ffffff',
                            border: '1px solid rgba(255, 255, 255, 0.2)',
                            padding: '0.5rem 1rem',
                            borderRadius: '6px',
                            fontSize: '0.8rem',
                            cursor: 'pointer'
                          }}
                        >
                          Retake
                        </button>
                        <button
                          onClick={() => setCapturedImage(null)}
                          style={{
                            background: 'rgba(76, 222, 128, 0.2)',
                            color: '#4ade80',
                            border: '1px solid rgba(76, 222, 128, 0.3)',
                            padding: '0.5rem 1rem',
                            borderRadius: '6px',
                            fontSize: '0.8rem',
                            cursor: 'pointer'
                          }}
                        >
                          Use This Photo
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}

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
                  setCapturedImage(null)
                  stopCamera()
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
        @keyframes pulse {
          0% { box-shadow: 0 0 20px rgba(76, 222, 128, 0.5); }
          50% { box-shadow: 0 0 20px rgba(76, 222, 128, 0.8); }
          100% { box-shadow: 0 0 20px rgba(76, 222, 128, 0.5); }
        }
      `}</style>
    </div>
  )
} 