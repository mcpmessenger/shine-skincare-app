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
import { handleFileUpload, handleCameraCapture, validateImage, ProcessedImage } from '@/lib/image-processing'
import { Header } from '@/components/header'

export default function SimplifiedSkinAnalysis() {
  const { dispatch, isAuthenticated } = useCart()
  const { state: authState } = useAuth()
  const { theme } = useTheme()
  const [showSignInModal, setShowSignInModal] = useState(false)
  
  // Core states
  const [userImage, setUserImage] = useState<string | null>(null)
  const [processedImage, setProcessedImage] = useState<ProcessedImage | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisError, setAnalysisError] = useState<string | null>(null)
  const [imageValidation, setImageValidation] = useState<{
    isValid: boolean
    errors: string[]
    warnings: string[]
  } | null>(null)
  
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

  const resetStates = () => {
    setUserImage(null)
    setProcessedImage(null)
    setAnalysisError(null)
    setSelectedFile(null)
    setFaceDetection(null)
    setLiveFaceDetection(null)
    setImageValidation(null)
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
      
      const processedImage = await handleCameraCapture(videoRef.current)
      
      setUserImage(processedImage.dataUrl)
      setProcessedImage(processedImage)
      setUploadMethod('camera')
      
      // Validate the captured image
      const validation = validateImage(processedImage)
      setImageValidation(validation)
      
      console.log('📸 Captured image dimensions:', processedImage.width, 'x', processedImage.height)
      console.log('📸 Image size:', processedImage.size, 'bytes')
      console.log('✅ Static JPEG photo captured from camera')
      
      if (!validation.isValid) {
        console.warn('⚠️ Image validation warnings:', validation.errors, validation.warnings)
      }
      
      // Stop camera and hide preview
      stopCamera()
      setShowCameraPreview(false)
      
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
      try {
        setSelectedFile(file)
        setUploadMethod('upload')
        
        // Process the uploaded file using the new utility
        const processedImage = await handleFileUpload(file)
        
        setUserImage(processedImage.dataUrl)
        setProcessedImage(processedImage)
        
        // Validate the uploaded image
        const validation = validateImage(processedImage)
        setImageValidation(validation)
        
        console.log('📁 File uploaded successfully')
        console.log('📁 Image dimensions:', processedImage.width, 'x', processedImage.height)
        console.log('📁 Image size:', processedImage.size, 'bytes')
        
        if (!validation.isValid) {
          console.warn('⚠️ Image validation warnings:', validation.errors, validation.warnings)
        }
        
      } catch (error) {
        console.error('❌ File upload failed:', error)
        setAnalysisError(error instanceof Error ? error.message : 'Failed to process uploaded file')
        setSelectedFile(null)
        setUploadMethod(null)
      }
    }
  }

  const handleAnalysis = async () => {
    if (!userImage || !processedImage) {
      setAnalysisError('No image available for analysis')
      return
    }

    // Check image validation
    if (imageValidation && !imageValidation.isValid) {
      setAnalysisError(`Image validation failed: ${imageValidation.errors.join(', ')}`)
      return
    }

    setIsAnalyzing(true)
    setAnalysisError(null)

    try {
      // Use the processed image base64 data
      const imageData = processedImage.base64

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
        console.log('🔍 Analysis successful, checking face detection...')
        
        // Extract face detection results from analysis response (for both camera and upload)
        let finalFaceDetection = null
        if (response.data.face_detection) {
          // Handle both 'detected' and 'face_detected' field names
          const isDetected = response.data.face_detection.detected || response.data.face_detection.face_detected || false
          const faceBounds = response.data.face_detection.face_bounds || { x: 0, y: 0, width: 0, height: 0 }
          const confidence = response.data.face_detection.confidence || 0
          
          console.log(`🔍 Frontend Face Detection Debug (${uploadMethod === 'camera' ? 'Camera' : 'Upload'} Mode):`)
          console.log('  Received face_bounds:', faceBounds)
          console.log('  Is detected:', isDetected)
          console.log('  Confidence:', confidence)
          
          finalFaceDetection = {
            detected: isDetected,
            confidence: confidence,
            face_bounds: {
              x: faceBounds.x,
              y: faceBounds.y,
              width: faceBounds.width,
              height: faceBounds.height
            }
          }
          
          setFaceDetection(finalFaceDetection)
        }
        
        // Check if no face was detected and show notification
        if (finalFaceDetection && !finalFaceDetection.detected) {
          setAnalysisError('⚠️ No face detected in the image. Please ensure your face is clearly visible and try again. For best results, use a well-lit photo with your face centered.')
          setIsAnalyzing(false)
          return
        }
        
        // If face detected but confidence is low, adjust the analysis data
        if (finalFaceDetection && finalFaceDetection.detected && finalFaceDetection.confidence < 0.5) {
          console.log('⚠️ Face detected but confidence is low:', finalFaceDetection.confidence)
          
          // Modify the analysis data to indicate lower confidence
          response.data.confidence_score = Math.min(response.data.confidence_score || 0.8, 0.6)
          response.data.analysis_summary = 'Analysis performed with reduced confidence due to unclear face detection. Please consider retaking the photo for more accurate results.'
          
          // Add a warning to the recommendations
          if (response.data.top_recommendations) {
            response.data.top_recommendations.unshift('⚠️ Consider retaking photo for clearer face detection')
          }
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
      <div className="face-detection-overlay">
        {/* Face Detection Circle/Oval */}
        <div 
          className="face-detection-circle"
          style={{
            left: `${face_bounds.x}%`,
            top: `${face_bounds.y}%`,
            width: `${face_bounds.width}%`,
            height: `${face_bounds.height}%`
          }}
        />
        
        {/* Confidence Badge */}
        <div className="face-confidence-badge">
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
      <div className="face-detection-overlay">
        {/* Face Detection Circle/Oval */}
        {detected && (
          <div 
            className="face-detection-circle-live"
            style={{
              left: `${face_bounds.x}%`,
              top: `${face_bounds.y}%`,
              width: `${face_bounds.width}%`,
              height: `${face_bounds.height}%`
            }}
          />
        )}
        
        {/* Live Detection Status */}
        <div className={`live-detection-status ${detected ? 'detected' : 'not-detected'}`}>
          {detected ? `Face: ${confidencePercent}%` : 'No Face Detected'}
        </div>
        
        {/* Capture Hint */}
        {detected && confidence > 0.7 && (
          <div className="capture-hint">
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
    <div className="h-screen bg-primary text-primary font-inter font-light flex flex-col overflow-hidden">
      {/* Header */}
      <Header />

      {/* Main Content */}
      <div className="flex-1 max-w-6xl mx-auto p-1 flex flex-col gap-1 w-full h-full overflow-hidden">
        
        {/* Photo Display Area */}
        <div className="bg-secondary rounded-2xl p-1 border border-primary flex flex-col items-center justify-center relative aspect-[3/4] max-h-[65vh] min-h-[300px] flex-1 shadow-lg">
          {/* Camera Preview */}
          {showCameraPreview && (
            <div className="w-full h-full relative">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                onLoadedMetadata={() => console.log('🎥 Video metadata loaded in JSX')}
                onCanPlay={() => console.log('🎥 Video can play')}
                onPlaying={() => console.log('🎥 Video is playing')}
                onError={(e) => console.error('🎥 Video error in JSX:', e)}
                className="w-full h-full rounded-md object-cover aspect-[3/4] bg-black block"
              />
              {/* Live Face Detection Overlay */}
              {liveFaceDetection && <LiveFaceDetectionOverlay faceDetection={liveFaceDetection} />}
              {/* Camera Controls */}
              <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 flex gap-2 z-10">
                <button
                  onClick={capturePhoto}
                  disabled={!liveFaceDetection?.detected || (liveFaceDetection?.confidence || 0) < 0.5}
                  className={`px-4 py-2 rounded-md text-sm font-medium flex items-center gap-1 transition-all duration-200 ${
                    liveFaceDetection?.detected && (liveFaceDetection?.confidence || 0) >= 0.5 
                      ? 'bg-blue-500 text-white cursor-pointer opacity-100' 
                      : 'bg-gray-500 text-white cursor-not-allowed opacity-60'
                  }`}
                >
                  <Camera />
                  {liveFaceDetection?.detected && (liveFaceDetection?.confidence || 0) >= 0.5 ? 'Capture' : 'No Face'}
                </button>
                <button
                  onClick={() => {
                    stopCamera()
                    setShowCameraPreview(false)
                  }}
                  className="px-4 py-2 bg-black/50 text-white border-none rounded-md cursor-pointer text-sm font-medium"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {/* Ready State */}
          {!userImage && !showCameraPreview && (
            <div className="text-center p-4">
              <Sparkles className="opacity-50 mb-2 text-2xl" />
              <h3 className="text-xl font-medium text-primary mb-1">
                Ready for Skin Analysis
              </h3>
              <p className="text-sm text-secondary mb-2">
                Take a selfie or upload a photo
              </p>
              <div className="text-xs text-secondary bg-secondary p-2 rounded-md border border-primary">
                💡 <strong>Tip:</strong> Ensure your face is clearly visible
              </div>
            </div>
          )}

          {/* Captured/Uploaded Image */}
          {userImage && !showCameraPreview && (
            <div className="w-full h-full relative">
              <img
                src={userImage}
                alt="User photo"
                className="w-full h-full rounded-md object-cover aspect-[3/4] bg-gray-100"
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
                className="absolute top-1 right-1 p-1 bg-black/50 text-white border-none rounded-full cursor-pointer w-6 h-6 flex items-center justify-center z-10"
              >
                <X />
              </button>
            </div>
          )}

          {cameraError && (
            <div className="text-red-500 text-sm text-center mt-2">
              {cameraError}
            </div>
          )}
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          className="hidden"
        />

                 {/* Demographic Inputs */}
         {userImage && (
           <div className="bg-secondary rounded-xl p-3 border border-primary mb-1 max-w-md mx-auto mb-1 shadow-sm">
            <h4 className="text-sm font-medium text-primary mb-1 text-center">
              Optional: Help improve analysis accuracy
            </h4>
            
                         <div className="flex gap-3 mb-3">
               <div className="flex-1">
                 <label className="text-xs text-secondary mb-2 block">
                   Age
                 </label>
                 <select
                   value={ageCategory}
                   onChange={(e) => setAgeCategory(e.target.value)}
                   className="w-full p-2 rounded-lg border border-primary bg-primary text-primary text-xs"
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
               
                                <div className="flex-1">
                   <label className="text-xs text-secondary mb-2 block">
                     Ethnicity
                   </label>
                   <select
                     value={ethnicity}
                     onChange={(e) => setEthnicity(e.target.value)}
                     className="w-full p-2 rounded-lg border border-primary bg-primary text-primary text-xs"
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
        
                            

                            {/* Error Display */}
           {analysisError && (
             <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-red-600 text-sm mb-2 max-w-lg mx-auto mb-2 shadow-sm">
               {analysisError}
             </div>
           )}
           
           {/* Analysis Status */}
           {isAnalyzing && (
             <div className="bg-secondary rounded-xl p-3 mb-1 max-w-md mx-auto mb-1 text-center shadow-sm">
             <div className="text-sm text-secondary flex items-center justify-center gap-2">
               <div className="w-3 h-3 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
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

        {/* Bottom Action Buttons */}
        <div className="flex-shrink-0 p-1">
          {/* Input Methods - Moved to bottom */}
          {!userImage && !showCameraPreview && (
            <div className="flex gap-2 justify-center max-w-md mx-auto mb-1">
              <button
                onClick={startCamera}
                disabled={cameraLoading}
                className="flex-1 max-w-[140px] p-3 bg-secondary border border-primary rounded-xl text-primary cursor-pointer transition-all duration-300 flex items-center justify-center gap-2 font-medium text-sm hover:bg-hover hover:shadow-lg disabled:opacity-50"
              >
                <Camera />
                {cameraLoading ? 'Starting...' : 'Use Camera'}
              </button>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="flex-1 max-w-[140px] p-3 bg-secondary border border-primary rounded-xl text-primary cursor-pointer transition-all duration-300 flex items-center justify-center gap-2 font-medium text-sm hover:bg-hover hover:shadow-lg"
              >
                <Upload />
                Upload
              </button>
            </div>
          )}

          {/* Submit for Analysis Button */}
          {userImage && !showCameraPreview && (
            <div className="flex justify-center mb-1">
              <button
                onClick={handleAnalysis}
                disabled={isAnalyzing}
                className={`w-full max-w-[280px] p-3 rounded-xl text-sm font-medium flex items-center justify-center gap-2 transition-all duration-300 ${
                  isAnalyzing 
                    ? 'bg-secondary text-secondary cursor-not-allowed' 
                    : 'bg-blue-500 text-white cursor-pointer hover:bg-blue-600 hover:shadow-lg'
                }`}
              >
                {isAnalyzing ? (
                  <>
                    <div className="w-3 h-3 border-2 border-transparent border-t-current rounded-full animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Sparkles />
                    Submit for Analysis
                  </>
                )}
              </button>
            </div>
          )}
        </div>

        {/* Footer */}
        <footer className="p-1 px-4 text-center text-xs text-primary flex-shrink-0">
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