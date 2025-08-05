'use client'

import { useState, useRef, useEffect } from 'react'
import { Camera, Upload, Sparkles, Sun, User, ShoppingCart, X, ArrowRight } from 'lucide-react'
import Link from 'next/link'
import { useCart } from '@/hooks/useCart'
import { useAuth } from '@/hooks/useAuth'
import { CartDrawer } from '@/components/cart-drawer'
import { SignInModal } from '@/components/sign-in-modal'
import { products } from '@/lib/products'
import { useTheme } from '@/hooks/useTheme'
import { ThemeToggle } from '@/components/theme-toggle'
import { directBackendClient, isDirectBackendAvailable } from '@/lib/direct-backend'

interface AnalysisResult {
  status: string
  timestamp: string
  demographics: {
    age_category: string | null
    race_category: string | null
  }
  face_detection: {
    detected: boolean
    confidence: number
    face_bounds: {
      x: number
      y: number
      width: number
      height: number
    }
  }
  skin_analysis: {
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
  recommendations: {
    immediate_care: string[]
    long_term_care: string[]
    professional_consultation: boolean
  }
}

export default function SimplifiedSkinAnalysis() {
  const { dispatch, isAuthenticated } = useCart()
  const { state: authState } = useAuth()
  const { theme } = useTheme()
  const [showSignInModal, setShowSignInModal] = useState(false)
  
  // Core states
  const [userImage, setUserImage] = useState<string | null>(null)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisError, setAnalysisError] = useState<string | null>(null)
  
  // Face detection states
  const [faceDetection, setFaceDetection] = useState<{
    detected: boolean
    confidence: number
    face_bounds: {
      x: number
      y: number
      width: number
      height: number
    }
  } | null>(null)
  
  // Camera states
  const [cameraLoading, setCameraLoading] = useState(false)
  const [cameraError, setCameraError] = useState<string | null>(null)
  const [cameraActive, setCameraActive] = useState(false)
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null)
  const [showCameraPreview, setShowCameraPreview] = useState(false)
  
  // Upload states
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadMethod, setUploadMethod] = useState<'camera' | 'upload' | null>(null)
  
  // Demographic inputs
  const [ageCategory, setAgeCategory] = useState<string>('')
  const [ethnicity, setEthnicity] = useState<string>('')
  
  // UI states
  const [showResults, setShowResults] = useState(false)
  const [showDemographics, setShowDemographics] = useState(false)
  
  const fileInputRef = useRef<HTMLInputElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)

  // Theme-aware color utility
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

  const resetStates = () => {
    setUserImage(null)
    setAnalysisResult(null)
    setAnalysisError(null)
    setShowResults(false)
    setSelectedFile(null)
    setFaceDetection(null)
    stopCamera()
    setShowCameraPreview(false)
  }

  // Start camera with live preview
  const startCamera = async () => {
    try {
      setCameraError(null)
      setCameraLoading(true)
      setShowCameraPreview(false)
      
      console.log('📸 Starting camera with live preview...')
      
      // Check if MediaDevices API is available
      if (!navigator.mediaDevices) {
        console.error('❌ MediaDevices API not available')
        setCameraError('Camera API not supported in this browser')
        setCameraLoading(false)
        return
      }
      
      // Check available devices
      const devices = await navigator.mediaDevices.enumerateDevices()
      const videoDevices = devices.filter(device => device.kind === 'videoinput')
      console.log('📹 Available video devices:', videoDevices)
      
      if (videoDevices.length === 0) {
        setCameraError('No camera devices found')
        setCameraLoading(false)
        return
      }
      
      // Get camera stream
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'user' } 
      })
      
      console.log('✅ Camera stream obtained successfully')
      
      // Show camera preview first to ensure video element exists
      setShowCameraPreview(true)
      
      // Wait a bit for the video element to be rendered
      await new Promise(resolve => setTimeout(resolve, 100))
      
      // Set up the video element for live preview
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        videoRef.current.muted = true
        videoRef.current.autoplay = true
        videoRef.current.playsInline = true
        
        // Wait for video to be ready
        await new Promise((resolve, reject) => {
          if (videoRef.current) {
            videoRef.current.onloadedmetadata = () => {
              console.log('✅ Video metadata loaded')
              resolve(true)
            }
            videoRef.current.onerror = (error) => {
              console.error('❌ Video error:', error)
              reject(error)
            }
            videoRef.current.play().then(() => {
              console.log('✅ Video started playing')
            }).catch(reject)
          }
        })
        
        console.log('✅ Video element ready for preview')
        setCameraStream(stream)
        setCameraActive(true)
        setCameraLoading(false)
        
      } else {
        throw new Error('Video element not found')
      }
      
    } catch (error) {
      console.error('❌ Camera failed:', error)
      setCameraError(`Camera failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
      setCameraLoading(false)
      setShowCameraPreview(false)
    }
  }

  // Capture photo from live preview
  const capturePhoto = async () => {
    if (!videoRef.current || !cameraStream) return
    
    try {
      console.log('📸 Capturing photo from live preview...')
      
      // Create canvas to capture the photo
      const canvas = document.createElement('canvas')
      const context = canvas.getContext('2d')
      
      if (context && videoRef.current) {
        // Set canvas size to match video
        canvas.width = videoRef.current.videoWidth
        canvas.height = videoRef.current.videoHeight
        
        console.log('🎨 Canvas created with dimensions:', canvas.width, 'x', canvas.height)
        
        // Draw video frame to canvas
        context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height)
        
        // Convert to JPEG data URL
        const imageData = canvas.toDataURL('image/jpeg', 0.9)
        
        console.log('📸 Captured image data type:', typeof imageData)
        console.log('📸 Image data starts with:', imageData.substring(0, 50))
        console.log('📸 Image data length:', imageData.length)
        
        // Ensure it's a proper JPEG data URL
        if (!imageData.startsWith('data:image/jpeg;base64,')) {
          throw new Error('Failed to capture proper JPEG image')
        }
        
        setUserImage(imageData)
        setUploadMethod('camera')
        
        console.log('✅ Static JPEG photo captured from camera')
        
        // Stop camera and hide preview
        stopCamera()
        setShowCameraPreview(false)
        
      } else {
        throw new Error('Could not get canvas context or video element')
      }
      
    } catch (error) {
      console.error('❌ Photo capture failed:', error)
      setCameraError(`Photo capture failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  const stopCamera = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop())
      setCameraActive(false)
      setCameraStream(null)
    }
  }

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setUploadMethod('upload')
      
      const reader = new FileReader()
      reader.onload = (e) => {
        const result = e.target?.result as string
        setUserImage(result)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleAnalysis = async () => {
    if (!userImage) return

    setIsAnalyzing(true)
    setAnalysisError(null)

    try {
      // Convert data URL to pure base64
      let imageData = userImage
      if (userImage.startsWith('data:')) {
        imageData = userImage.split(',')[1]
      }

      console.log('🔍 Starting analysis with image data length:', imageData.length)
      console.log('🔍 Image data starts with:', imageData.substring(0, 50))
      console.log('🔍 Image data type:', typeof imageData)
      console.log('🔍 Original userImage type:', typeof userImage)
      console.log('🔍 Original userImage starts with:', userImage.substring(0, 50))

      const response = await directBackendClient.enhancedAnalysis({
        image_data: imageData,
        analysis_type: 'comprehensive',
        user_parameters: {
          age_category: ageCategory,
          race_category: ethnicity
        }
      })

      console.log('🔍 Analysis response:', response)

      if (response.success && response.data) {
        setAnalysisResult(response.data)
        // Extract face detection results
        if (response.data.face_detection) {
          setFaceDetection(response.data.face_detection)
        }
        setShowResults(true)
      } else {
        console.error('❌ Analysis failed:', response.error)
        setAnalysisError(response.error || 'Analysis failed. Please try again.')
      }
    } catch (error) {
      console.error('❌ Analysis error:', error)
      setAnalysisError('Analysis failed. Please try again.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  // Face Detection Overlay Component
  const FaceDetectionOverlay = ({ faceDetection }: { faceDetection: any }) => {
    if (!faceDetection || !faceDetection.detected) return null

    const { face_bounds, confidence } = faceDetection
    const confidencePercent = Math.round(confidence * 100)

    return (
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 5
      }}>
        {/* Face Detection Box */}
        <div style={{
          position: 'absolute',
          left: `${face_bounds.x}%`,
          top: `${face_bounds.y}%`,
          width: `${face_bounds.width}%`,
          height: `${face_bounds.height}%`,
          border: '3px solid #3b82f6',
          borderRadius: '8px',
          boxShadow: '0 0 0 2px rgba(59, 130, 246, 0.3)',
          animation: 'pulse 2s infinite'
        }} />
        
        {/* Confidence Badge */}
        <div style={{
          position: 'absolute',
          top: '1rem',
          right: '1rem',
          backgroundColor: '#3b82f6',
          color: 'white',
          padding: '0.5rem 0.75rem',
          borderRadius: '20px',
          fontSize: '0.8rem',
          fontWeight: '500',
          boxShadow: '0 2px 8px rgba(59, 130, 246, 0.3)'
        }}>
          Face Detected: {confidencePercent}%
        </div>
      </div>
    )
  }

  useEffect(() => {
    return () => {
      // Clean up camera resources
      if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop())
      }
    }
  }, [cameraStream])

  // Debug video element state
  useEffect(() => {
    if (showCameraPreview && videoRef.current) {
      console.log('🎥 Video element state:', {
        srcObject: videoRef.current.srcObject,
        readyState: videoRef.current.readyState,
        videoWidth: videoRef.current.videoWidth,
        videoHeight: videoRef.current.videoHeight,
        paused: videoRef.current.paused,
        ended: videoRef.current.ended,
        currentTime: videoRef.current.currentTime
      })
      
      // Ensure video is playing when preview is shown
      if (videoRef.current.paused) {
        console.log('🔄 Ensuring video is playing...')
        videoRef.current.play().catch(e => console.error('Failed to play video:', e))
      }
    }
  }, [showCameraPreview])

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
        borderBottom: theme === 'dark' ? '1px solid rgba(255, 255, 255, 0.1)' : '1px solid rgba(0, 0, 0, 0.1)',
        position: 'sticky',
        top: 0,
        zIndex: 1000
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '1rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          {/* Logo */}
          <Link href="/" style={{
            display: 'flex',
            alignItems: 'center',
            gap: '1rem',
            textDecoration: 'none'
          }}>
            <img 
              src="https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png"
              alt="Shine Skin Collective"
              style={{
                height: '48px',
                width: 'auto',
                objectFit: 'contain',
                cursor: 'pointer',
                transition: 'opacity 0.3s ease'
              }}
              onError={(e) => {
                console.error('Logo failed to load');
                e.currentTarget.style.display = 'none';
              }}
            />
          </Link>

          {/* Navigation */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '1rem'
          }}>
            <Link href="/catalog" style={{
              padding: '0.5rem 1rem',
              backgroundColor: getBgColor(0.1),
              border: `1px solid ${getBorderColor(0.2)}`,
              borderRadius: '8px',
              color: getTextColor(1),
              textDecoration: 'none',
              fontSize: '0.9rem',
              transition: 'all 0.3s ease',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              <ShoppingCart />
              Products
            </Link>
            <ThemeToggle />
            <CartDrawer />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div style={{
        maxWidth: '600px',
        margin: '0 auto',
        padding: '1rem',
        minHeight: 'calc(100vh - 80px)',
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem'
      }}>
        
        {/* Photo Display Area */}
        <div style={{
          backgroundColor: getBgColor(0.05),
          borderRadius: '16px',
          padding: '1rem',
          border: `1px solid ${getBorderColor(0.1)}`,
          minHeight: '400px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative'
        }}>
          {/* Camera Preview */}
          {showCameraPreview && (
            <div style={{ width: '100%', position: 'relative' }}>
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                onLoadedMetadata={() => console.log('🎥 Video metadata loaded in JSX')}
                onCanPlay={() => console.log('🎥 Video can play')}
                onPlaying={() => console.log('🎥 Video is playing')}
                onError={(e) => console.error('🎥 Video error in JSX:', e)}
                style={{
                  width: '100%',
                  borderRadius: '12px',
                  maxHeight: '400px',
                  objectFit: 'cover',
                  aspectRatio: '9/16',
                  backgroundColor: '#000000',
                  display: 'block'
                }}
              />
              {/* Camera Controls */}
              <div style={{
                position: 'absolute',
                bottom: '1rem',
                left: '50%',
                transform: 'translateX(-50%)',
                display: 'flex',
                gap: '1rem',
                zIndex: 10
              }}>
                <button
                  onClick={capturePhoto}
                  style={{
                    padding: '0.75rem 1.5rem',
                    backgroundColor: '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '0.9rem',
                    fontWeight: '500',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}
                >
                  <Camera />
                  Capture Photo
                </button>
                <button
                  onClick={() => {
                    stopCamera()
                    setShowCameraPreview(false)
                  }}
                  style={{
                    padding: '0.75rem 1.5rem',
                    backgroundColor: 'rgba(0, 0, 0, 0.5)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '0.9rem',
                    fontWeight: '500'
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {/* Ready State */}
          {!userImage && !showCameraPreview && (
            <div style={{ textAlign: 'center' }}>
              <Sparkles style={{ opacity: 0.5, marginBottom: '1rem' }} />
              <h3 style={{
                fontSize: '1.2rem',
                fontWeight: 500,
                color: getTextColor(1),
                marginBottom: '0.5rem'
              }}>
                Ready for Skin Analysis
              </h3>
              <p style={{
                fontSize: '0.9rem',
                color: getTextColor(0.7),
                marginBottom: '1rem'
              }}>
                Take a selfie or upload a photo to begin your skin analysis
              </p>
              <div style={{
                fontSize: '0.8rem',
                color: getTextColor(0.6),
                backgroundColor: getBgColor(0.1),
                padding: '0.75rem',
                borderRadius: '8px',
                border: `1px solid ${getBorderColor(0.2)}`
              }}>
                💡 <strong>Tip:</strong> Ensure your face is clearly visible and well-lit for the best analysis results
              </div>
            </div>
          )}

          {/* Captured/Uploaded Image */}
          {userImage && !showCameraPreview && (
            <div style={{ width: '100%', position: 'relative' }}>
              <img
                src={userImage}
                alt="User photo"
                style={{
                  width: '100%',
                  borderRadius: '12px',
                  maxHeight: '400px',
                  objectFit: 'cover',
                  aspectRatio: '9/16',
                  backgroundColor: '#f0f0f0'
                }}
                onLoad={() => {
                  console.log('Image loaded successfully')
                }}
                onError={(e) => {
                  console.error('Image failed to load:', e)
                  setAnalysisError('Failed to load captured image')
                }}
              />
              {/* Face Detection Overlay */}
              {faceDetection && <FaceDetectionOverlay faceDetection={faceDetection} />}
              <button
                onClick={resetStates}
                style={{
                  position: 'absolute',
                  top: '0.5rem',
                  right: '0.5rem',
                  padding: '0.5rem',
                  backgroundColor: 'rgba(0, 0, 0, 0.5)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '50%',
                  cursor: 'pointer',
                  width: '32px',
                  height: '32px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 10
                }}
              >
                <X />
              </button>
            </div>
          )}

          {cameraError && (
            <div style={{
              color: '#ef4444',
              fontSize: '0.9rem',
              textAlign: 'center',
              marginTop: '1rem'
            }}>
              {cameraError}
            </div>
          )}
        </div>

        {/* Input Methods */}
        {!userImage && !showCameraPreview && (
          <div style={{
            display: 'flex',
            gap: '1rem',
            marginBottom: '1rem'
          }}>
            <button
              onClick={startCamera}
              disabled={cameraLoading}
              style={{
                flex: 1,
                padding: '1rem',
                backgroundColor: getBgColor(0.1),
                border: `1px solid ${getBorderColor(0.2)}`,
                borderRadius: '12px',
                color: getTextColor(1),
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                fontWeight: '500'
              }}
            >
              <Camera />
              {cameraLoading ? 'Starting Camera...' : 'Use Camera'}
            </button>
            <button
              onClick={() => fileInputRef.current?.click()}
              style={{
                flex: 1,
                padding: '1rem',
                backgroundColor: getBgColor(0.1),
                border: `1px solid ${getBorderColor(0.2)}`,
                borderRadius: '12px',
                color: getTextColor(1),
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                fontWeight: '500'
              }}
            >
              <Upload />
              Upload
            </button>
          </div>
        )}

        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />

        {/* Demographic Inputs */}
        {userImage && !showResults && (
          <div style={{
            backgroundColor: getBgColor(0.05),
            borderRadius: '12px',
            padding: '1rem',
            border: `1px solid ${getBorderColor(0.1)}`
          }}>
            <h4 style={{
              fontSize: '1rem',
              fontWeight: 500,
              color: getTextColor(1),
              marginBottom: '1rem'
            }}>
              Optional: Help improve analysis accuracy
            </h4>
            
            <div style={{
              display: 'flex',
              gap: '1rem',
              marginBottom: '1rem'
            }}>
              <div style={{ flex: 1 }}>
                <label style={{
                  fontSize: '0.8rem',
                  color: getTextColor(0.7),
                  marginBottom: '0.5rem',
                  display: 'block'
                }}>
                  Age Category
                </label>
                <select
                  value={ageCategory}
                  onChange={(e) => setAgeCategory(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    borderRadius: '8px',
                    border: `1px solid ${getBorderColor(0.2)}`,
                    backgroundColor: theme === 'dark' ? '#1f2937' : '#ffffff',
                    color: getTextColor(1),
                    fontSize: '0.9rem'
                  }}
                >
                  <option value="">Select age</option>
                  <option value="18-25">18-25</option>
                  <option value="26-35">26-35</option>
                  <option value="36-45">36-45</option>
                  <option value="46-55">46-55</option>
                  <option value="56-65">56-65</option>
                  <option value="65+">65+</option>
                </select>
              </div>
              
              <div style={{ flex: 1 }}>
                <label style={{
                  fontSize: '0.8rem',
                  color: getTextColor(0.7),
                  marginBottom: '0.5rem',
                  display: 'block'
                }}>
                  Ethnicity
                </label>
                <select
                  value={ethnicity}
                  onChange={(e) => setEthnicity(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    borderRadius: '8px',
                    border: `1px solid ${getBorderColor(0.2)}`,
                    backgroundColor: theme === 'dark' ? '#1f2937' : '#ffffff',
                    color: getTextColor(1),
                    fontSize: '0.9rem'
                  }}
                >
                  <option value="">Select ethnicity</option>
                  <option value="caucasian">Caucasian</option>
                  <option value="african_american">African American</option>
                  <option value="asian">Asian</option>
                  <option value="hispanic">Hispanic</option>
                  <option value="middle_eastern">Middle Eastern</option>
                  <option value="mixed">Mixed</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
          </div>
        )}
        
        {/* Analysis Button */}
        {userImage && !showResults && (
          <button
            onClick={handleAnalysis}
            disabled={isAnalyzing}
            style={{
              width: '100%',
              padding: '1rem',
              backgroundColor: isAnalyzing ? getBgColor(0.1) : '#3b82f6',
              color: isAnalyzing ? getTextColor(0.5) : 'white',
              border: 'none',
              borderRadius: '12px',
              cursor: isAnalyzing ? 'not-allowed' : 'pointer',
              fontSize: '1rem',
              fontWeight: '500',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem',
              transition: 'all 0.3s ease'
            }}
          >
            {isAnalyzing ? (
              <>
                <div style={{
                  width: '16px',
                  height: '16px',
                  border: '2px solid transparent',
                  borderTop: '2px solid currentColor',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }} />
                Analyzing... (Detecting Face & Analyzing Skin)
              </>
            ) : (
              <>
                <Sparkles />
                Analyze My Skin
              </>
            )}
          </button>
        )}

        {/* Error Display */}
        {analysisError && (
          <div style={{
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '8px',
            padding: '1rem',
            color: '#dc2626',
            fontSize: '0.9rem'
          }}>
            {analysisError}
          </div>
        )}
        
        {/* Results */}
        {showResults && analysisResult && (
          <div style={{
            backgroundColor: getBgColor(0.05),
            borderRadius: '12px',
            padding: '1rem',
            border: `1px solid ${getBorderColor(0.1)}`
          }}>
            <h3 style={{
              fontSize: '1.1rem',
              fontWeight: 500,
              color: getTextColor(1),
              marginBottom: '0.75rem',
              textAlign: 'center'
            }}>
              Analysis Complete
            </h3>
            
            {/* Health Score */}
            <div style={{
              backgroundColor: getBgColor(0.1),
              borderRadius: '8px',
              padding: '0.75rem',
              marginBottom: '0.75rem',
              textAlign: 'center'
            }}>
              <div style={{
                fontSize: '1.5rem',
                fontWeight: '600',
                color: '#3b82f6',
                marginBottom: '0.25rem'
              }}>
                {Math.round(analysisResult.skin_analysis.overall_health_score)}%
              </div>
              <div style={{
                fontSize: '0.8rem',
                color: getTextColor(0.7)
              }}>
                Health Score
              </div>
            </div>

            {/* Face Detection Status */}
            {analysisResult.face_detection && (
              <div style={{
                backgroundColor: getBgColor(0.1),
                borderRadius: '8px',
                padding: '0.75rem',
                marginBottom: '0.75rem',
                border: `1px solid ${getBorderColor(0.2)}`
              }}>
                <div style={{
                  fontSize: '0.9rem',
                  color: getTextColor(0.8),
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}>
                  <div style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: analysisResult.face_detection.detected ? '#10b981' : '#ef4444'
                  }} />
                  {analysisResult.face_detection.detected ? 
                    `Face detected (${Math.round(analysisResult.face_detection.confidence * 100)}%)` : 
                    'No face detected'}
                </div>
              </div>
            )}

            {/* Conditions Summary */}
            {analysisResult.skin_analysis.conditions_detected.length > 0 && (
              <div style={{ marginBottom: '0.75rem' }}>
                <div style={{
                  fontSize: '0.9rem',
                  fontWeight: 500,
                  color: getTextColor(1),
                  marginBottom: '0.5rem'
                }}>
                  Conditions Found:
                </div>
                <div style={{ 
                  display: 'flex', 
                  flexWrap: 'wrap', 
                  gap: '0.25rem',
                  fontSize: '0.8rem'
                }}>
                  {analysisResult.skin_analysis.conditions_detected.slice(0, 3).map((condition, index) => (
                    <span key={index} style={{
                      backgroundColor: getBgColor(0.1),
                      padding: '0.25rem 0.5rem',
                      borderRadius: '12px',
                      color: getTextColor(0.8),
                      border: `1px solid ${getBorderColor(0.2)}`
                    }}>
                      {condition.condition.replace('_', ' ')}
                    </span>
                  ))}
                  {analysisResult.skin_analysis.conditions_detected.length > 3 && (
                    <span style={{
                      backgroundColor: getBgColor(0.1),
                      padding: '0.25rem 0.5rem',
                      borderRadius: '12px',
                      color: getTextColor(0.6),
                      border: `1px solid ${getBorderColor(0.2)}`
                    }}>
                      +{analysisResult.skin_analysis.conditions_detected.length - 3} more
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Top Recommendation */}
            {analysisResult.recommendations.immediate_care.length > 0 && (
              <div style={{ marginBottom: '0.75rem' }}>
                <div style={{
                  fontSize: '0.9rem',
                  fontWeight: 500,
                  color: getTextColor(1),
                  marginBottom: '0.25rem'
                }}>
                  Top Recommendation:
                </div>
                <div style={{
                  fontSize: '0.8rem',
                  color: getTextColor(0.8),
                  backgroundColor: getBgColor(0.05),
                  padding: '0.5rem',
                  borderRadius: '6px',
                  border: `1px solid ${getBorderColor(0.1)}`
                }}>
                  {analysisResult.recommendations.immediate_care[0]}
                </div>
              </div>
            )}

            {/* Products Button */}
            <Link href="/catalog" style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem',
              padding: '0.75rem',
              backgroundColor: '#10b981',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '8px',
              fontSize: '0.9rem',
              fontWeight: '500',
              marginTop: '0.5rem'
            }}>
              <ShoppingCart />
              View Products
              <ArrowRight />
            </Link>
          </div>
        )}

        {/* Sign In Modal */}
        <SignInModal 
          isOpen={showSignInModal} 
          onClose={() => setShowSignInModal(false)} 
        />
      </div>

      <style jsx>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        
        @keyframes pulse {
          0% { box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3); }
          50% { box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.6); }
          100% { box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3); }
        }
      `}</style>
    </div>
  )
} 