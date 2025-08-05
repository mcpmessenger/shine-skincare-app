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



export default function SimplifiedSkinAnalysis() {
  const { dispatch, isAuthenticated } = useCart()
  const { state: authState } = useAuth()
  const { theme } = useTheme()
  const [showSignInModal, setShowSignInModal] = useState(false)
  
  // Core states
  const [userImage, setUserImage] = useState<string | null>(null)
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
  
  // Live camera face detection
  const [liveFaceDetection, setLiveFaceDetection] = useState<{
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
    setAnalysisError(null)
    setSelectedFile(null)
    setFaceDetection(null)
    setLiveFaceDetection(null)
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

  // Live face detection for camera preview
  const performLiveFaceDetection = async () => {
    if (!videoRef.current || !cameraActive) return
    
    try {
      // Create a canvas to capture the current video frame
      const canvas = document.createElement('canvas')
      const context = canvas.getContext('2d')
      
      if (context && videoRef.current) {
        // Set canvas size to match video
        canvas.width = videoRef.current.videoWidth
        canvas.height = videoRef.current.videoHeight
        
        // Draw current video frame to canvas
        context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height)
        
        // Convert canvas to base64 for analysis
        const imageData = canvas.toDataURL('image/jpeg', 0.8).split(',')[1]
        
        // Use dedicated face detection endpoint for faster response
        const response = await fetch('http://localhost:5000/api/v3/face/detect', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            image_data: imageData
          })
        })
        
        if (response.ok) {
          const result = await response.json()
          if (result.status === 'success') {
            // Convert pixel coordinates to percentages
            setLiveFaceDetection({
              detected: result.face_detected,
              confidence: result.confidence,
              face_bounds: {
                x: result.face_bounds.x,
                y: result.face_bounds.y,
                width: result.face_bounds.width,
                height: result.face_bounds.height
              }
            })
          } else {
            setLiveFaceDetection({
              detected: false,
              confidence: 0,
              face_bounds: { x: 0, y: 0, width: 0, height: 0 }
            })
          }
        } else {
          setLiveFaceDetection({
            detected: false,
            confidence: 0,
            face_bounds: { x: 0, y: 0, width: 0, height: 0 }
          })
        }
      }
    } catch (error) {
      console.log('Live face detection error:', error)
      // Don't show error to user for live detection
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
    if (!userImage) {
      return
    }

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

      // Perform face detection first for upload mode
      if (uploadMethod === 'upload') {
        console.log('🔍 Performing face detection for upload mode...')
        const faceDetectionResponse = await directBackendClient.faceDetection({
          image_data: imageData
        })
        
        if (faceDetectionResponse.success && faceDetectionResponse.data) {
          console.log('🔍 Face detection result:', faceDetectionResponse.data)
          
          // Handle the face detection response structure
          const isDetected = faceDetectionResponse.data.face_detected || false
          const faceBounds = faceDetectionResponse.data.face_bounds || { x: 0, y: 0, width: 0, height: 0 }
          
          console.log('🔍 Frontend Face Detection Debug (Upload Mode):')
          console.log('  Received face_bounds:', faceBounds)
          console.log('  Is detected:', isDetected)
          
          setFaceDetection({
            detected: isDetected,
            confidence: faceDetectionResponse.data.confidence || 0,
            face_bounds: {
              x: faceBounds.x,
              y: faceBounds.y,
              width: faceBounds.width,
              height: faceBounds.height
            }
          })
        } else {
          console.log('⚠️ Face detection failed for upload mode:', faceDetectionResponse.error)
          setFaceDetection({
            detected: false,
            confidence: 0,
            face_bounds: { x: 0, y: 0, width: 0, height: 0 }
          })
        }
      }

      const response = await directBackendClient.realSkinAnalysis({
        image_data: imageData,
        user_demographics: {
          age_category: ageCategory,
          race_category: ethnicity
        }
      })

      console.log('🔍 Analysis response:', response)
      console.log('🔍 Response success:', response.success)
      console.log('🔍 Response data:', response.data)
      console.log('🔍 Response data type:', typeof response.data)
      console.log('🔍 Top recommendations in response:', response.data?.top_recommendations)
      console.log('🔍 Top recommendations length:', response.data?.top_recommendations?.length)

      if (response.success && response.data) {
        console.log('🔍 Analysis successful, redirecting to suggestions page')
        
        // Extract face detection results from analysis response (for camera mode)
        if (response.data.face_detection && uploadMethod === 'camera') {
          // Handle both 'detected' and 'face_detected' field names
          const isDetected = response.data.face_detection.detected || response.data.face_detection.face_detected || false
          const faceBounds = response.data.face_detection.face_bounds || { x: 0, y: 0, width: 0, height: 0 }
          
          console.log('🔍 Frontend Face Detection Debug (Camera Mode):')
          console.log('  Received face_bounds:', faceBounds)
          console.log('  Is detected:', isDetected)
          
          setFaceDetection({
            detected: isDetected,
            confidence: response.data.face_detection.confidence || 0,
            face_bounds: {
              x: faceBounds.x,
              y: faceBounds.y,
              width: faceBounds.width,
              height: faceBounds.height
            }
          })
        }
        
        // Redirect to suggestions page with analysis data
        const analysisData = encodeURIComponent(JSON.stringify(response.data))
        window.location.href = `/suggestions?analysis=${analysisData}`
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
        {/* Face Detection Circle/Oval */}
        <div style={{
          position: 'absolute',
          left: `${face_bounds.x}%`,
          top: `${face_bounds.y}%`,
          width: `${face_bounds.width}%`,
          height: `${face_bounds.height}%`,
          border: '3px solid #3b82f6',
          borderRadius: '50%', // Changed from '8px' to '50%' for circle/oval
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

  // Live Face Detection Overlay Component for Camera
  const LiveFaceDetectionOverlay = ({ faceDetection }: { faceDetection: any }) => {
    if (!faceDetection) return null

    const { face_bounds, confidence, detected } = faceDetection
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
        {/* Face Detection Circle/Oval */}
        {detected && (
          <div style={{
            position: 'absolute',
            left: `${face_bounds.x}%`,
            top: `${face_bounds.y}%`,
            width: `${face_bounds.width}%`,
            height: `${face_bounds.height}%`,
            border: '3px solid #10b981',
            borderRadius: '50%', // Changed from '8px' to '50%' for circle/oval
            boxShadow: '0 0 0 2px rgba(16, 185, 129, 0.3)',
            animation: 'pulse 2s infinite'
          }} />
        )}
        
        {/* Live Detection Status */}
        <div style={{
          position: 'absolute',
          top: '0.5rem',
          right: '0.5rem',
          backgroundColor: detected ? '#10b981' : '#f59e0b',
          color: 'white',
          padding: '0.25rem 0.5rem',
          borderRadius: '12px',
          fontSize: '0.7rem',
          fontWeight: '500',
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)'
        }}>
          {detected ? `Face: ${confidencePercent}%` : 'No Face Detected'}
        </div>
        
        {/* Capture Hint */}
        {detected && confidence > 0.7 && (
          <div style={{
            position: 'absolute',
            bottom: '4rem',
            left: '50%',
            transform: 'translateX(-50%)',
            backgroundColor: 'rgba(16, 185, 129, 0.9)',
            color: 'white',
            padding: '0.25rem 0.5rem',
            borderRadius: '8px',
            fontSize: '0.7rem',
            fontWeight: '500',
            textAlign: 'center'
          }}>
            ✅ Ready to capture
          </div>
        )}
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

  // Live face detection interval
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null
    
    if (cameraActive && showCameraPreview) {
      // Perform initial face detection after a short delay
      const initialDetection = setTimeout(() => {
        performLiveFaceDetection()
      }, 1000)
      
      // Set up periodic face detection
      interval = setInterval(() => {
        performLiveFaceDetection()
      }, 2000) // Check every 2 seconds
      
      return () => {
        clearTimeout(initialDetection)
        if (interval) clearInterval(interval)
      }
    } else {
      // Clear live face detection when camera stops
      setLiveFaceDetection(null)
    }
    
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [cameraActive, showCameraPreview])

  return (
    <div style={{
      height: '100vh',
      backgroundColor: theme === 'dark' ? '#000000' : '#ffffff',
      color: theme === 'dark' ? '#ffffff' : '#000000',
      fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      fontWeight: 300,
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
             {/* Header */}
       <header style={{
         backgroundColor: theme === 'dark' ? getBgColor(0.1) : '#ffffff',
         borderBottom: `1px solid ${getBorderColor(0.2)}`,
         padding: '0.75rem 1rem',
         display: 'flex',
         alignItems: 'center',
         justifyContent: 'space-between',
         gap: '1rem',
         flexShrink: 0
       }}>
                 {/* Logo */}
         <div style={{
           display: 'flex',
           alignItems: 'center'
         }}>
           <Link href="/" style={{
             display: 'flex',
             alignItems: 'center',
             textDecoration: 'none',
             cursor: 'pointer'
           }}>
             <img 
               src="https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png"
               alt="SHINE SKIN COLLECTIVE"
               style={{
                 height: '48px',
                 width: 'auto',
                 objectFit: 'contain'
               }}
             />
           </Link>
         </div>

        {/* Navigation */}
        <nav style={{
          display: 'flex',
          alignItems: 'center',
          gap: '1rem'
        }}>
          <Link href="/catalog" style={{
            color: getTextColor(0.8),
            textDecoration: 'none',
            fontSize: '0.9rem',
            fontWeight: '500',
            padding: '0.5rem',
            borderRadius: '6px',
            transition: 'all 0.2s ease',
            backgroundColor: getBgColor(0.05)
          }}>
            Products
          </Link>
        </nav>

        {/* Right Side Controls */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem'
        }}>
          {/* Theme Toggle */}
          <ThemeToggle />

          {/* Cart */}
          <button
            onClick={() => setShowSignInModal(true)}
            style={{
              backgroundColor: getBgColor(0.05),
              border: 'none',
              color: getTextColor(1),
              cursor: 'pointer',
              padding: '0.5rem',
              borderRadius: '6px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '32px',
              height: '32px'
            }}
          >
            <ShoppingCart style={{ width: '16px', height: '16px' }} />
          </button>

          {/* Auth Avatar / Sign In */}
          {isAuthenticated ? (
            <button
              onClick={() => setShowSignInModal(true)}
              style={{
                backgroundColor: getBgColor(0.1),
                border: 'none',
                cursor: 'pointer',
                padding: '0.25rem',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '32px',
                height: '32px'
              }}
            >
              <User style={{ width: '16px', height: '16px', color: getTextColor(1) }} />
            </button>
          ) : (
            <button
              onClick={() => setShowSignInModal(true)}
              style={{
                backgroundColor: getBgColor(0.1),
                border: `1px solid ${getBorderColor(0.2)}`,
                color: getTextColor(1),
                cursor: 'pointer',
                padding: '0.5rem 0.75rem',
                borderRadius: '6px',
                fontSize: '0.8rem',
                fontWeight: '500',
                transition: 'all 0.2s ease'
              }}
            >
              Sign In
            </button>
          )}
        </div>
      </header>

      {/* Main Content */}
      <div style={{
        flex: 1,
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '0.25rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.25rem',
        width: '100%',
        height: '100%',
        overflow: 'hidden'
      }}>
        
        {/* Photo Display Area */}
        <div style={{
          backgroundColor: getBgColor(0.05),
          borderRadius: '8px',
          padding: '0.25rem',
          border: `1px solid ${getBorderColor(0.1)}`,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative',
          aspectRatio: '3/4',
          maxHeight: '65vh',
          minHeight: '300px',
          flex: 1
        }}>
                     {/* Camera Preview */}
           {showCameraPreview && (
             <div style={{ width: '100%', height: '100%', position: 'relative' }}>
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
                   height: '100%',
                   borderRadius: '6px',
                   objectFit: 'cover',
                   aspectRatio: '3/4',
                   backgroundColor: '#000000',
                   display: 'block'
                 }}
               />
               {/* Live Face Detection Overlay */}
               {liveFaceDetection && <LiveFaceDetectionOverlay faceDetection={liveFaceDetection} />}
               {/* Camera Controls */}
               <div style={{
                 position: 'absolute',
                 bottom: '0.5rem',
                 left: '50%',
                 transform: 'translateX(-50%)',
                 display: 'flex',
                 gap: '0.5rem',
                 zIndex: 10
               }}>
                                 <button
                   onClick={capturePhoto}
                   disabled={!liveFaceDetection?.detected || (liveFaceDetection?.confidence || 0) < 0.5}
                   style={{
                     padding: '0.5rem 1rem',
                     backgroundColor: liveFaceDetection?.detected && (liveFaceDetection?.confidence || 0) >= 0.5 ? '#3b82f6' : '#6b7280',
                     color: 'white',
                     border: 'none',
                     borderRadius: '6px',
                     cursor: liveFaceDetection?.detected && (liveFaceDetection?.confidence || 0) >= 0.5 ? 'pointer' : 'not-allowed',
                     fontSize: '0.8rem',
                     fontWeight: '500',
                     display: 'flex',
                     alignItems: 'center',
                     gap: '0.25rem',
                     opacity: liveFaceDetection?.detected && (liveFaceDetection?.confidence || 0) >= 0.5 ? 1 : 0.6
                   }}
                 >
                   <Camera />
                   {liveFaceDetection?.detected && (liveFaceDetection?.confidence || 0) >= 0.5 ? 'Capture' : 'No Face'}
                 </button>
                <button
                  onClick={() => {
                    stopCamera()
                    setShowCameraPreview(false)
                  }}
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: 'rgba(0, 0, 0, 0.5)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '0.8rem',
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
            <div style={{ textAlign: 'center', padding: '1rem' }}>
              <Sparkles style={{ opacity: 0.5, marginBottom: '0.5rem', fontSize: '1.5rem' }} />
              <h3 style={{
                fontSize: '1.2rem',
                fontWeight: 500,
                color: getTextColor(1),
                marginBottom: '0.25rem'
              }}>
                Ready for Skin Analysis
              </h3>
              <p style={{
                fontSize: '0.9rem',
                color: getTextColor(0.7),
                marginBottom: '0.5rem'
              }}>
                Take a selfie or upload a photo
              </p>
              <div style={{
                fontSize: '0.8rem',
                color: getTextColor(0.6),
                backgroundColor: getBgColor(0.1),
                padding: '0.5rem',
                borderRadius: '6px',
                border: `1px solid ${getBorderColor(0.2)}`
              }}>
                💡 <strong>Tip:</strong> Ensure your face is clearly visible
              </div>
            </div>
          )}

          {/* Captured/Uploaded Image */}
          {userImage && !showCameraPreview && (
            <div style={{ width: '100%', height: '100%', position: 'relative' }}>
              <img
                src={userImage}
                alt="User photo"
                style={{
                  width: '100%',
                  height: '100%',
                  borderRadius: '6px',
                  objectFit: 'cover',
                  aspectRatio: '3/4',
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
                  top: '0.25rem',
                  right: '0.25rem',
                  padding: '0.25rem',
                  backgroundColor: 'rgba(0, 0, 0, 0.5)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '50%',
                  cursor: 'pointer',
                  width: '24px',
                  height: '24px',
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
              fontSize: '0.8rem',
              textAlign: 'center',
              marginTop: '0.5rem'
            }}>
              {cameraError}
            </div>
          )}
        </div>

        {/* Input Methods */}
        {!userImage && !showCameraPreview && (
          <div style={{
            display: 'flex',
            gap: '0.25rem',
            marginBottom: '0.25rem',
            justifyContent: 'center',
            maxWidth: '400px',
            margin: '0 auto 0.25rem auto'
          }}>
            <button
              onClick={startCamera}
              disabled={cameraLoading}
              style={{
                flex: 1,
                maxWidth: '120px',
                padding: '0.5rem',
                backgroundColor: getBgColor(0.1),
                border: `1px solid ${getBorderColor(0.2)}`,
                borderRadius: '6px',
                color: getTextColor(1),
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.25rem',
                fontWeight: '500',
                fontSize: '0.8rem'
              }}
            >
              <Camera />
              {cameraLoading ? 'Starting...' : 'Use Camera'}
            </button>
            <button
              onClick={() => fileInputRef.current?.click()}
              style={{
                flex: 1,
                maxWidth: '120px',
                padding: '0.5rem',
                backgroundColor: getBgColor(0.1),
                border: `1px solid ${getBorderColor(0.2)}`,
                borderRadius: '6px',
                color: getTextColor(1),
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.25rem',
                fontWeight: '500',
                fontSize: '0.8rem'
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
        {userImage && (
          <div style={{
            backgroundColor: getBgColor(0.05),
            borderRadius: '6px',
            padding: '0.25rem',
            border: `1px solid ${getBorderColor(0.1)}`,
            marginBottom: '0.25rem',
            maxWidth: '400px',
            margin: '0 auto 0.25rem auto'
          }}>
            <h4 style={{
              fontSize: '0.8rem',
              fontWeight: 500,
              color: getTextColor(1),
              marginBottom: '0.25rem',
              textAlign: 'center'
            }}>
              Optional: Help improve analysis accuracy
            </h4>
            
            <div style={{
              display: 'flex',
              gap: '0.25rem',
              marginBottom: '0.25rem'
            }}>
              <div style={{ flex: 1 }}>
                <label style={{
                  fontSize: '0.8rem',
                  color: getTextColor(0.7),
                  marginBottom: '0.25rem',
                  display: 'block'
                }}>
                  Age
                </label>
                <select
                  value={ageCategory}
                  onChange={(e) => setAgeCategory(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.25rem',
                    borderRadius: '4px',
                    border: `1px solid ${getBorderColor(0.2)}`,
                    backgroundColor: theme === 'dark' ? '#1f2937' : '#ffffff',
                    color: getTextColor(1),
                    fontSize: '0.8rem'
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
                  marginBottom: '0.25rem',
                  display: 'block'
                }}>
                  Ethnicity
                </label>
                <select
                  value={ethnicity}
                  onChange={(e) => setEthnicity(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.25rem',
                    borderRadius: '4px',
                    border: `1px solid ${getBorderColor(0.2)}`,
                    backgroundColor: theme === 'dark' ? '#1f2937' : '#ffffff',
                    color: getTextColor(1),
                    fontSize: '0.8rem'
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
        {userImage && (
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            marginBottom: '0.25rem'
          }}>
            <button
              onClick={handleAnalysis}
              disabled={isAnalyzing}
              style={{
                width: '100%',
                maxWidth: '250px',
                padding: '0.5rem',
                backgroundColor: isAnalyzing ? getBgColor(0.1) : '#3b82f6',
                color: isAnalyzing ? getTextColor(0.5) : 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: isAnalyzing ? 'not-allowed' : 'pointer',
                fontSize: '0.8rem',
                fontWeight: '500',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.25rem',
                transition: 'all 0.3s ease'
              }}
            >
              {isAnalyzing ? (
                <>
                  <div style={{
                    width: '12px',
                    height: '12px',
                    border: '2px solid transparent',
                    borderTop: '2px solid currentColor',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite'
                  }} />
                  Analyzing...
                </>
              ) : (
                <>
                  <Sparkles />
                  Analyze My Skin
                </>
              )}
            </button>
          </div>
        )}

        {/* Error Display */}
        {analysisError && (
          <div style={{
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '6px',
            padding: '0.5rem',
            color: '#dc2626',
            fontSize: '0.8rem',
            marginBottom: '0.5rem',
            maxWidth: '600px',
            margin: '0 auto 0.5rem auto'
          }}>
            {analysisError}
          </div>
        )}
        
        {/* Analysis Status */}
        {isAnalyzing && (
          <div style={{
            backgroundColor: getBgColor(0.05),
            borderRadius: '6px',
            padding: '0.5rem',
            marginBottom: '0.25rem',
            maxWidth: '400px',
            margin: '0 auto 0.25rem auto',
            textAlign: 'center'
          }}>
            <div style={{
              fontSize: '0.9rem',
              color: getTextColor(0.8),
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem'
            }}>
              <div style={{
                width: '12px',
                height: '12px',
                border: '2px solid #3b82f6',
                borderTop: '2px solid transparent',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }} />
              Analyzing your skin...
            </div>
          </div>
        )}

                 {/* Sign In Modal */}
         <SignInModal 
           isOpen={showSignInModal} 
           onClose={() => setShowSignInModal(false)} 
         />
      </div>

             {/* Footer */}
       <footer style={{
         padding: '0.25rem 1rem',
         textAlign: 'center',
         fontSize: '0.6rem',
         color: theme === 'dark' ? '#ffffff' : '#000000',
         flexShrink: 0
       }}>
         © 2025 SHINE SKIN COLLECTIVE. All Rights Reserved.
       </footer>

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