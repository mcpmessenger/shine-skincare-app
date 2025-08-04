'use client'

import { useState, useRef, useEffect } from 'react'
import { Camera, Upload, Sparkles, Zap, Sun, Brain, CheckCircle, Zap as Target, User, Eye, TrendingUp, ShoppingCart, X } from 'lucide-react'
import Link from 'next/link'
import { useCart } from '@/hooks/useCart'
import { useAuth } from '@/hooks/useAuth'
import { CartDrawer } from '@/components/cart-drawer'
import { SignInModal } from '@/components/sign-in-modal'
import { products } from '@/lib/products'
import { useTheme } from '@/hooks/useTheme'
import { ThemeToggle } from '@/components/theme-toggle'
import { directBackendClient, isDirectBackendAvailable } from '@/lib/direct-backend'

interface EnhancedAnalysisResult {
  status: string
  timestamp: string
  analysis_type: string
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
    method: string
    quality_metrics: {
      overall_quality: string
      quality_score: number
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
  similarity_search: {
    dataset_used: string
    similar_cases: Array<{
      condition: string
      similarity_score: number
      dataset_source: string
      demographic_match: string
      treatment_suggestions: string[]
    }>
  }
  recommendations: {
    immediate_care: string[]
    long_term_care: string[]
    professional_consultation: boolean
  }
  quality_assessment: {
    image_quality: string
    confidence_reliability: string
  }
}

interface DemographicAnalysisResult {
  status: string
  timestamp: string
  analysis_type: string
  dataset_used: string
  model_used: string
  demographic_info: {
    age_category: string
    gender: string
    ethnicity: string
  }
  health_score: number
  demographic_baseline: {
    age_group: string
    gender: string
    ethnicity: string
    baseline_health_score: number
    sample_count: number
  }
  comparison_metrics: {
    similarity_to_baseline: number
    percentile_rank: number
    confidence_level: string
  }
  recommendations: {
    demographic_specific: string[]
    general_health: string[]
    professional_consultation: boolean
  }
}

interface ConditionAnalysisResult {
  status: string
  timestamp: string
  analysis_type: string
  dataset_used: string
  model_used: string
  best_match: string
  best_similarity: number
  assessment: string
  condition_results: {
    [condition: string]: {
      similarity: number
      confidence: number
      sample_count: number
    }
  }
  recommendations: string[]
}

interface RealTimeDetectionResult {
  status: string
  face_detected: boolean
  face_bounds: {
    x: number
    y: number
    width: number
    height: number
  }
  confidence: number
  quality_metrics: {
    lighting: string
    sharpness: string
    positioning: string
  }
  guidance: {
    message: string
    suggestions: string[]
  }
}

export default function EnhancedSkinAnalysis() {
  const { dispatch, isAuthenticated } = useCart()
  const { state: authState } = useAuth()
  const { theme } = useTheme()
  const [showSignInModal, setShowSignInModal] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<EnhancedAnalysisResult | null>(null)
  const [demographicResult, setDemographicResult] = useState<DemographicAnalysisResult | null>(null)
  const [conditionResult, setConditionResult] = useState<ConditionAnalysisResult | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [analysisType, setAnalysisType] = useState<'enhanced' | 'demographic' | 'condition' | 'basic'>('enhanced')
  const [demographicInfo, setDemographicInfo] = useState({
    age: '',
    gender: '',
    ethnicity: ''
  })
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisError, setAnalysisError] = useState<string | null>(null)
  const [cameraActive, setCameraActive] = useState(false)
  const [faceDetected, setFaceDetected] = useState(false)
  const [detectionResult, setDetectionResult] = useState<RealTimeDetectionResult | null>(null)
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null)
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const [showCamera, setShowCamera] = useState(false)
  const [cameraPermission, setCameraPermission] = useState<'granted' | 'denied' | 'prompt'>('prompt')
  const [uploadMethod, setUploadMethod] = useState<'camera' | 'file' | null>(null)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [recommendations, setRecommendations] = useState<string[]>([])
  const [productRecommendations, setProductRecommendations] = useState<any[]>([])
  const [showResults, setShowResults] = useState(false)
  const [currentStep, setCurrentStep] = useState<'upload' | 'analysis' | 'results'>('upload')
  const [analysisHistory, setAnalysisHistory] = useState<Array<{
    timestamp: string
    type: string
    result: any
  }>>([])
  const [systemStatus, setSystemStatus] = useState({
    utkface: false,
    facial_skin_diseases: false,
    enhanced_embeddings: false
  })

  // Phase 2: Demographic inputs
  const [ageCategory, setAgeCategory] = useState<string>('')
  const [raceCategory, setRaceCategory] = useState<string>('')
  const [showDemographics, setShowDemographics] = useState(false)
  const [userImage, setUserImage] = useState<string | null>(null)
  const [analysisLoading, setAnalysisLoading] = useState(false)
  const [cameraError, setCameraError] = useState<string | null>(null)

  // Upload face detection states
  const [uploadFaceDetected, setUploadFaceDetected] = useState(false)
  const [uploadFaceBounds, setUploadFaceBounds] = useState<{ x: number; y: number; width: number; height: number }>({ x: 0, y: 0, width: 0, height: 0 })
  const [uploadFaceDetectionResult, setUploadFaceDetectionResult] = useState<RealTimeDetectionResult | null>(null)
  const [isDetectingFace, setIsDetectingFace] = useState(false)

  // Theme-aware color utility
  const getThemeColor = (lightColor: string, darkColor: string) => {
    return theme === 'dark' ? darkColor : lightColor
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

  const resetUploadStates = () => {
    setSelectedFile(null)
    setUserImage(null)
    setUploadFaceDetected(false)
    setUploadFaceBounds({ x: 0, y: 0, width: 0, height: 0 })
    setUploadFaceDetectionResult(null)
    setIsDetectingFace(false)
    setAnalysisResult(null)
  }

  // Product recommendations based on analysis
  const getProductRecommendations = (analysis: EnhancedAnalysisResult) => {
    // Filter products based on analysis results
    let recommendedProducts = [...products]
    
    // Filter by detected conditions
    const conditions = analysis?.skin_analysis?.conditions_detected?.map(c => c.condition.toLowerCase()) || []
    
    if (conditions.some(c => c.includes('acne') || c.includes('breakout'))) {
      recommendedProducts = recommendedProducts.filter(p => 
        p.category === 'cleanser' || p.category === 'treatment'
      )
    }
    
    if (conditions.some(c => c.includes('aging') || c.includes('wrinkle'))) {
      recommendedProducts = recommendedProducts.filter(p => 
        p.category === 'serum' || p.category === 'treatment'
      )
    }
    
    if (conditions.some(c => c.includes('pigment') || c.includes('dark'))) {
      recommendedProducts = recommendedProducts.filter(p => 
        p.category === 'treatment' || p.category === 'serum'
      )
    }
    
    // Return top 4 recommendations
    return recommendedProducts.slice(0, 4)
  }
  
  // Age and race categories
  const ageCategories = [
    '18-25', '26-35', '36-45', '46-55', '56-65', '65+'
  ]
  
  const raceCategories = [
    'Caucasian', 'African American', 'Asian', 'Hispanic/Latino', 
    'Middle Eastern', 'Native American', 'Mixed/Other'
  ]
  
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const faceDetectionInterval = useRef<NodeJS.Timeout | null>(null)

  // Camera setup
  useEffect(() => {
    if (uploadMethod === 'camera' && !cameraActive) {
      startCamera()
    } else if (uploadMethod === 'file' && cameraActive) {
      stopCamera()
    }
    
    // Reset face detection state when not in camera mode
    if (uploadMethod === 'file') {
      setFaceDetected(false)
      setDetectionResult(null)
      if (faceDetectionInterval.current) {
        clearInterval(faceDetectionInterval.current)
        faceDetectionInterval.current = null
      }
    }
  }, [uploadMethod])

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 720 },
          height: { ideal: 1280 }, // Portrait orientation
          facingMode: 'user',
          aspectRatio: { ideal: 0.5625 } // 9:16 aspect ratio for portrait
        }
      })
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        streamRef.current = stream
        setCameraActive(true)
        startFaceDetection()
      }
    } catch (error) {
      console.error('Camera access failed:', error)
      setCameraError('Camera access denied. Please allow camera permissions.')
    }
  }

  const startFaceDetection = () => {
    if (faceDetectionInterval.current) {
      clearInterval(faceDetectionInterval.current)
    }
    
    faceDetectionInterval.current = setInterval(async () => {
      await detectFaceInVideo()
    }, 1000) // Check every second
  }

  const detectFaceInVideo = async () => {
    if (!videoRef.current || !canvasRef.current) return
    
    try {
      const canvas = canvasRef.current
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      
      // Set canvas size to match video
      canvas.width = videoRef.current.videoWidth
      canvas.height = videoRef.current.videoHeight
      
      // Draw video frame to canvas
      ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height)
      
      // Get image data for face detection
      const imageData = canvas.toDataURL('image/jpeg', 0.8)
      
      // Extract base64 data from data URL
      const base64Data = imageData.split(',')[1]
      
      // Call real-time detection API
      const response = await fetch('/api/v3/face/detect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image_data: base64Data
        })
      })
      
      if (response.ok) {
        const detectionResult: RealTimeDetectionResult = await response.json()
        setDetectionResult(detectionResult)
        
        if (detectionResult.face_detected) {
          setFaceDetected(true)
        } else {
          setFaceDetected(false)
        }
      }
    } catch (error) {
      console.error('Face detection failed:', error)
    }
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
    
    setCameraActive(false)
    setFaceDetected(false)
    setDetectionResult(null)
  }

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current
      const video = videoRef.current
      
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      
      const ctx = canvas.getContext('2d')
      if (ctx) {
        ctx.drawImage(video, 0, 0)
        
        // Store the captured image
        const imageData = canvas.toDataURL('image/jpeg', 0.8)
        setUserImage(imageData)
        
        // Stop camera after capture
        stopCamera()
        
        // Convert to base64 for analysis
        const base64Data = imageData.split(',')[1]
        
        // Perform analysis with the captured image
        handleAnalysis(base64Data)
      }
    }
  }

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = async (e) => {
        const result = e.target?.result as string
        setUserImage(result)
        setSelectedFile(file)
        
        // Reset face detection states
        setUploadFaceDetected(false)
        setUploadFaceBounds({ x: 0, y: 0, width: 0, height: 0 })
        setUploadFaceDetectionResult(null)
        
        // Perform face detection on uploaded image
        await detectFaceInUploadedImage(result)
      }
      reader.readAsDataURL(file)
    }
  }

  const detectFaceInUploadedImage = async (imageData: string) => {
    try {
      setIsDetectingFace(true)
      
      // Extract base64 data from data URL
      const base64Data = imageData.includes(',') ? imageData.split(',')[1] : imageData
      
      // Call face detection API
      const response = await fetch('/api/v3/face/detect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image_data: base64Data
        })
      })
      
      if (response.ok) {
        const detectionResult: RealTimeDetectionResult = await response.json()
        setUploadFaceDetectionResult(detectionResult)
        
        if (detectionResult.face_detected && detectionResult.face_bounds) {
          setUploadFaceDetected(true)
          setUploadFaceBounds(detectionResult.face_bounds)
        } else {
          setUploadFaceDetected(false)
          setUploadFaceBounds({ x: 0, y: 0, width: 0, height: 0 })
        }
      } else {
        console.error('Face detection failed for uploaded image')
        setUploadFaceDetected(false)
      }
    } catch (error) {
      console.error('Face detection error for uploaded image:', error)
      setUploadFaceDetected(false)
    } finally {
      setIsDetectingFace(false)
    }
  }

  const handleAnalysis = async (imageData: string) => {
    if (!imageData) {
      setAnalysisError('No image data provided')
      return
    }

    // Extract base64 data from data URL
    const base64Data = imageData.includes(',') ? imageData.split(',')[1] : imageData

    setIsAnalyzing(true)
    setAnalysisError(null)
    setAnalysisProgress(0)

    try {
      let response: Response
      let result: any

      // Choose analysis type based on user selection
      switch (analysisType) {
        case 'basic':
          // Basic analysis using the integrated system with embedded conditions and normalized data
          // Pass face detection result if available
          const basicPayload: any = {
            image_data: base64Data,
            analysis_type: 'integrated',
            user_parameters: {
              age_category: ageCategory,
              race_category: raceCategory
            }
          }
          
          // Add face detection result if available
          if (uploadFaceDetectionResult && uploadFaceDetectionResult.face_detected) {
            basicPayload.face_detection_result = {
              face_detected: uploadFaceDetectionResult.face_detected,
              confidence: uploadFaceDetectionResult.confidence,
              face_bounds: uploadFaceDetectionResult.face_bounds
            }
          }
          
          // Try proxy first, then fallback to direct backend
          try {
            response = await fetch('/api/v3/skin/analyze-basic', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(basicPayload)
            })
            
            if (response.ok) {
              result = await response.json()
              setAnalysisResult(result)
              setDemographicResult(null)
              setConditionResult(null)
            } else {
              console.log('❌ Proxy failed, trying direct backend...')
              // Fallback to direct backend
              const directResult = await directBackendClient.basicAnalysis(basicPayload)
              if (directResult.success && directResult.data) {
                setAnalysisResult(directResult.data)
                setDemographicResult(null)
                setConditionResult(null)
              } else {
                throw new Error(`Basic analysis failed: ${directResult.error}`)
              }
            }
          } catch (error) {
            console.log('❌ Proxy failed, trying direct backend...')
            // Fallback to direct backend
            const directResult = await directBackendClient.basicAnalysis(basicPayload)
            if (directResult.success && directResult.data) {
              setAnalysisResult(directResult.data)
              setDemographicResult(null)
              setConditionResult(null)
            } else {
              throw new Error(`Basic analysis failed: ${directResult.error}`)
            }
          }
          break

        case 'demographic':
          // Demographic analysis with UTKFace
          response = await fetch('/api/v3/skin/analyze-demographic', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              image_data: base64Data,
              age: demographicInfo.age,
              gender: demographicInfo.gender,
              ethnicity: demographicInfo.ethnicity
            })
          })
          
          if (response.ok) {
            result = await response.json()
            setDemographicResult(result)
            setAnalysisResult(null)
            setConditionResult(null)
          } else {
            throw new Error(`Demographic analysis failed: ${response.statusText}`)
          }
          break

        case 'condition':
          // Condition analysis with Facial Skin Diseases
          response = await fetch('/api/v3/skin/analyze-conditions', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              image_data: base64Data
            })
          })
          
          if (response.ok) {
            result = await response.json()
            setConditionResult(result)
            setAnalysisResult(null)
            setDemographicResult(null)
          } else {
            throw new Error(`Condition analysis failed: ${response.statusText}`)
          }
          break

        case 'enhanced':
        default:
          // Enhanced analysis (existing functionality)
          // Pass face detection result if available
          const enhancedPayload: any = {
            image_data: base64Data,
            analysis_type: 'comprehensive',
            user_parameters: {
              age_category: ageCategory,
              race_category: raceCategory
            }
          }
          
          // Add face detection result if available
          if (uploadFaceDetectionResult && uploadFaceDetectionResult.face_detected) {
            enhancedPayload.face_detection_result = {
              face_detected: uploadFaceDetectionResult.face_detected,
              confidence: uploadFaceDetectionResult.confidence,
              face_bounds: uploadFaceDetectionResult.face_bounds
            }
          }
          
          // Try proxy first, then fallback to direct backend
          try {
            response = await fetch('/api/v3/skin/analyze-enhanced-embeddings', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(enhancedPayload)
            })
            
            if (response.ok) {
              result = await response.json()
              setAnalysisResult(result)
              setDemographicResult(null)
              setConditionResult(null)
            } else {
              console.log('❌ Proxy failed, trying direct backend...')
              // Fallback to direct backend
              const directResult = await directBackendClient.enhancedAnalysis(enhancedPayload)
              if (directResult.success && directResult.data) {
                setAnalysisResult(directResult.data)
                setDemographicResult(null)
                setConditionResult(null)
              } else {
                throw new Error(`Enhanced analysis failed: ${directResult.error}`)
              }
            }
          } catch (error) {
            console.log('❌ Proxy failed, trying direct backend...')
            // Fallback to direct backend
            const directResult = await directBackendClient.enhancedAnalysis(enhancedPayload)
            if (directResult.success && directResult.data) {
              setAnalysisResult(directResult.data)
              setDemographicResult(null)
              setConditionResult(null)
            } else {
              throw new Error(`Enhanced analysis failed: ${directResult.error}`)
            }
          }
          break
      }

      // Update analysis history
      setAnalysisHistory(prev => [...prev, {
        timestamp: new Date().toISOString(),
        type: analysisType,
        result: result
      }])

              // Generate recommendations based on analysis type
        if (result) {
          if (analysisType === 'demographic' && result.recommendations) {
            setRecommendations([
              ...result.recommendations.demographic_specific || [],
              ...result.recommendations.general_health || []
            ])
          } else if (analysisType === 'condition' && result.recommendations) {
            setRecommendations(result.recommendations)
          } else if ((analysisType === 'enhanced' || analysisType === 'basic') && result.recommendations) {
            setRecommendations([
              ...result.recommendations.immediate_care || [],
              ...result.recommendations.long_term_care || []
            ])
          }

        // Generate product recommendations for enhanced and basic analysis
        if ((analysisType === 'enhanced' || analysisType === 'basic') && result) {
          const products = getProductRecommendations(result)
          setProductRecommendations(products)
        }
      }

      setCurrentStep('results')
      setShowResults(true)

    } catch (error) {
      console.error('Analysis error:', error)
      setAnalysisError(error instanceof Error ? error.message : 'Analysis failed')
    } finally {
      setIsAnalyzing(false)
      setAnalysisProgress(0)
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

      // Perform analysis with the uploaded image
      await handleAnalysis(base64)
    } catch (error) {
      console.error('Upload failed:', error)
    } finally {
      setIsUploading(false)
      setUploadProgress(0)
    }
  }

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
              onMouseEnter={(e) => {
                e.currentTarget.style.opacity = '0.8';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.opacity = '1';
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
            transition: 'all 0.3s ease'
          }}>
            View All Products
          </Link>
            <ThemeToggle />
            <CartDrawer />
          </div>


        </div>
      </header>

      {/* Main Content */}
      <div className="mobile-container" style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '1rem'
      }}>


        {/* Phase 2: Enhanced Interface */}
        <div className="mobile-grid" style={{
          display: 'grid',
          gridTemplateColumns: '1fr',
          gap: '2rem',
          marginBottom: '2rem'
        }}>
          {/* Left Column - Upload & Camera */}
          <div>
            {/* Mode Selection */}
            <div style={{
              display: 'flex',
              gap: '1rem',
              marginBottom: '2rem'
            }}>
              <button
                className="mobile-button"
                onClick={() => {
                  setUploadMethod('camera')
                  resetUploadStates()
                  startCamera()
                }}
                style={{
                  flex: 1,
                  padding: '1rem',
                  backgroundColor: uploadMethod === 'camera' ? getBgColor(0.15) : getBgColor(0.05),
                  border: `1px solid ${uploadMethod === 'camera' ? getBorderColor(0.4) : getBorderColor(0.2)}`,
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
                <Camera width={20} height={20} />
                Camera
              </button>
              
              <button
                className="mobile-button"
                onClick={() => {
                  setUploadMethod('file')
                  resetUploadStates()
                }}
                style={{
                  flex: 1,
                  padding: '1rem',
                  backgroundColor: uploadMethod === 'file' ? getBgColor(0.15) : getBgColor(0.05),
                  border: `1px solid ${uploadMethod === 'file' ? getBorderColor(0.4) : getBorderColor(0.2)}`,
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
                <Upload width={20} height={20} />
                Upload
              </button>
            </div>

            {/* Fallback Upload Area - Always Visible */}
            {!uploadMethod && (
              <div style={{
                backgroundColor: getBgColor(0.05),
                borderRadius: '16px',
                padding: '2rem',
                border: `1px solid ${getBorderColor(0.1)}`,
                marginBottom: '2rem'
              }}>
                <h3 style={{
                  fontSize: '1.2rem',
                  fontWeight: 500,
                  color: getTextColor(1),
                  marginBottom: '1rem',
                  textAlign: 'center'
                }}>
                  Ready for Analysis
                </h3>
                <p style={{
                  fontSize: '0.9rem',
                  color: getTextColor(0.7),
                  textAlign: 'center',
                  marginBottom: '1.5rem'
                }}>
                  Upload an image or use the camera to begin your enhanced skin analysis
                </p>
                
                {/* Quick Upload Button */}
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  style={{ display: 'none' }}
                  id="quick-file-upload"
                />
                <label
                  htmlFor="quick-file-upload"
                  style={{
                    display: 'block',
                    padding: '1rem',
                    border: `2px dashed ${getBorderColor(0.3)}`,
                    borderRadius: '12px',
                    textAlign: 'center',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    backgroundColor: getBgColor(0.05),
                    marginBottom: '1rem'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = getBorderColor(0.5)
                    e.currentTarget.style.backgroundColor = getBgColor(0.1)
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = getBorderColor(0.3)
                    e.currentTarget.style.backgroundColor = getBgColor(0.05)
                  }}
                >
                  <Upload width={24} height={24} style={{ marginBottom: '0.5rem', opacity: 0.7 }} />
                  <p style={{
                    margin: 0,
                    fontSize: '0.9rem',
                    color: getTextColor(0.8)
                  }}>
                    Click to select an image or drag and drop
                  </p>
                </label>
              </div>
            )}

            {/* Upload Mode */}
            {uploadMethod === 'file' && (
              <div style={{
                backgroundColor: getBgColor(0.05),
                borderRadius: '16px',
                padding: '2rem',
                border: `1px solid ${getBorderColor(0.1)}`
              }}>
                {/* Phase 2: Demographic Input */}
                <div style={{
                  marginBottom: '2rem'
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    marginBottom: '1rem'
                  }}>
                    <User width={20} height={20} style={{ opacity: 0.7 }} />
                    <h3 style={{
                      fontSize: '1.1rem',
                      fontWeight: 400,
                      color: getTextColor(1)
                    }}>
                      Demographic Information (Optional)
                    </h3>
                  </div>
                  
                  <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '1rem',
                    marginBottom: '1rem'
                  }}>
                    <div style={{ flex: 1 }}>
                      <label style={{
                        display: 'block',
                        fontSize: '0.9rem',
                        color: getTextColor(0.7),
                        marginBottom: '0.5rem'
                      }}>
                        Age
                      </label>
                      <select
                        className="mobile-select"
                        value={ageCategory}
                        onChange={(e) => setAgeCategory(e.target.value)}
                        style={{
                          width: '100%',
                          padding: '0.75rem',
                          backgroundColor: getBgColor(0.1),
                          border: `1px solid ${getBorderColor(0.2)}`,
                          borderRadius: '8px',
                          color: getTextColor(1),
                          fontSize: '0.9rem'
                        }}
                      >
                        <option value="">Select age category</option>
                        {ageCategories.map(category => (
                          <option key={category} value={category}>{category}</option>
                        ))}
                      </select>
                    </div>
                    
                    <div style={{ flex: 1 }}>
                      <label style={{
                        display: 'block',
                        fontSize: '0.9rem',
                        color: getTextColor(0.7),
                        marginBottom: '0.5rem'
                      }}>
                        Ethnicity
                      </label>
                      <select
                        className="mobile-select"
                        value={raceCategory}
                        onChange={(e) => setRaceCategory(e.target.value)}
                        style={{
                          width: '100%',
                          padding: '0.75rem',
                          backgroundColor: getBgColor(0.1),
                          border: `1px solid ${getBorderColor(0.2)}`,
                          borderRadius: '8px',
                          color: getTextColor(1),
                          fontSize: '0.9rem'
                        }}
                      >
                        <option value="">Select race/ethnicity</option>
                        {raceCategories.map(category => (
                          <option key={category} value={category}>{category}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                  
                  <p style={{
                    fontSize: '0.8rem',
                    color: getTextColor(0.5),
                    fontStyle: 'italic'
                  }}>
                    Providing demographic information helps improve analysis accuracy and provides more personalized recommendations.
                  </p>
                </div>

                {/* Analysis Type Selection */}
                <div style={{
                  marginBottom: '2rem'
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    marginBottom: '1rem'
                  }}>
                    <Sparkles width={20} height={20} style={{ opacity: 0.7 }} />
                    <h3 style={{
                      fontSize: '1.1rem',
                      fontWeight: 400,
                      color: getTextColor(1)
                    }}>
                      Analysis Type
                    </h3>
                  </div>
                  
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                    gap: '1rem'
                  }}>
                    <button
                      onClick={() => setAnalysisType('enhanced')}
                      style={{
                        padding: '1rem',
                        backgroundColor: analysisType === 'enhanced' ? getBgColor(0.15) : getBgColor(0.05),
                        border: `1px solid ${analysisType === 'enhanced' ? getBorderColor(0.4) : getBorderColor(0.2)}`,
                        borderRadius: '8px',
                        color: getTextColor(1),
                        cursor: 'pointer',
                        transition: 'all 0.3s ease',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: '0.5rem'
                      }}
                    >
                      <Sparkles width={20} height={20} />
                      <span style={{ fontSize: '0.9rem', fontWeight: 500 }}>Enhanced</span>
                      <span style={{ fontSize: '0.7rem', color: getTextColor(0.6), textAlign: 'center' }}>
                        Comprehensive skin analysis with multiple datasets
                      </span>
                    </button>
                    
                    <button
                      onClick={() => setAnalysisType('demographic')}
                      style={{
                        padding: '1rem',
                        backgroundColor: analysisType === 'demographic' ? getBgColor(0.15) : getBgColor(0.05),
                        border: `1px solid ${analysisType === 'demographic' ? getBorderColor(0.4) : getBorderColor(0.2)}`,
                        borderRadius: '8px',
                        color: getTextColor(1),
                        cursor: 'pointer',
                        transition: 'all 0.3s ease',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: '0.5rem'
                      }}
                    >
                      <User width={20} height={20} />
                      <span style={{ fontSize: '0.9rem', fontWeight: 500 }}>Demographic</span>
                      <span style={{ fontSize: '0.7rem', color: getTextColor(0.6), textAlign: 'center' }}>
                        Age, gender, and ethnicity-specific analysis
                      </span>
                    </button>
                    
                    <button
                      onClick={() => setAnalysisType('condition')}
                      style={{
                        padding: '1rem',
                        backgroundColor: analysisType === 'condition' ? getBgColor(0.15) : getBgColor(0.05),
                        border: `1px solid ${analysisType === 'condition' ? getBorderColor(0.4) : getBorderColor(0.2)}`,
                        borderRadius: '8px',
                        color: getTextColor(1),
                        cursor: 'pointer',
                        transition: 'all 0.3s ease',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: '0.5rem'
                      }}
                    >
                      <Eye width={20} height={20} />
                      <span style={{ fontSize: '0.9rem', fontWeight: 500 }}>Condition</span>
                      <span style={{ fontSize: '0.7rem', color: getTextColor(0.6), textAlign: 'center' }}>
                        Specific skin condition identification
                      </span>
                    </button>
                    
                    <button
                      onClick={() => setAnalysisType('basic')}
                      style={{
                        padding: '1rem',
                        backgroundColor: analysisType === 'basic' ? getBgColor(0.15) : getBgColor(0.05),
                        border: `1px solid ${analysisType === 'basic' ? getBorderColor(0.4) : getBorderColor(0.2)}`,
                        borderRadius: '8px',
                        color: getTextColor(1),
                        cursor: 'pointer',
                        transition: 'all 0.3s ease',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: '0.5rem'
                      }}
                    >
                      <CheckCircle width={20} height={20} />
                      <span style={{ fontSize: '0.9rem', fontWeight: 500 }}>Basic</span>
                      <span style={{ fontSize: '0.7rem', color: getTextColor(0.6), textAlign: 'center' }}>
                        Integrated analysis with embedded conditions and normalized data
                      </span>
                    </button>
                  </div>
                  
                  {/* Demographic Info for Demographic Analysis */}
                  {analysisType === 'demographic' && (
                    <div style={{
                      marginTop: '1rem',
                      padding: '1rem',
                      backgroundColor: getBgColor(0.1),
                      borderRadius: '8px',
                      border: `1px solid ${getBorderColor(0.2)}`
                    }}>
                      <h4 style={{
                        fontSize: '1rem',
                        fontWeight: 500,
                        color: getTextColor(1),
                        marginBottom: '1rem'
                      }}>
                        Required Demographic Information
                      </h4>
                      
                      <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                        gap: '1rem'
                      }}>
                        <div>
                          <label style={{
                            display: 'block',
                            fontSize: '0.9rem',
                            color: getTextColor(0.7),
                            marginBottom: '0.5rem'
                          }}>
                            Age
                          </label>
                          <input
                            type="text"
                            value={demographicInfo.age}
                            onChange={(e) => setDemographicInfo(prev => ({ ...prev, age: e.target.value }))}
                            placeholder="e.g., 25"
                            style={{
                              width: '100%',
                              padding: '0.75rem',
                              backgroundColor: getBgColor(0.1),
                              border: `1px solid ${getBorderColor(0.2)}`,
                              borderRadius: '8px',
                              color: getTextColor(1),
                              fontSize: '0.9rem'
                            }}
                          />
                        </div>
                        
                        <div>
                          <label style={{
                            display: 'block',
                            fontSize: '0.9rem',
                            color: getTextColor(0.7),
                            marginBottom: '0.5rem'
                          }}>
                            Gender
                          </label>
                          <select
                            value={demographicInfo.gender}
                            onChange={(e) => setDemographicInfo(prev => ({ ...prev, gender: e.target.value }))}
                            style={{
                              width: '100%',
                              padding: '0.75rem',
                              backgroundColor: getBgColor(0.1),
                              border: `1px solid ${getBorderColor(0.2)}`,
                              borderRadius: '8px',
                              color: getTextColor(1),
                              fontSize: '0.9rem'
                            }}
                          >
                            <option value="">Select gender</option>
                            <option value="male">Male</option>
                            <option value="female">Female</option>
                          </select>
                        </div>
                        
                        <div>
                          <label style={{
                            display: 'block',
                            fontSize: '0.9rem',
                            color: getTextColor(0.7),
                            marginBottom: '0.5rem'
                          }}>
                            Ethnicity
                          </label>
                          <select
                            value={demographicInfo.ethnicity}
                            onChange={(e) => setDemographicInfo(prev => ({ ...prev, ethnicity: e.target.value }))}
                            style={{
                              width: '100%',
                              padding: '0.75rem',
                              backgroundColor: getBgColor(0.1),
                              border: `1px solid ${getBorderColor(0.2)}`,
                              borderRadius: '8px',
                              color: getTextColor(1),
                              fontSize: '0.9rem'
                            }}
                          >
                            <option value="">Select ethnicity</option>
                            <option value="white">White</option>
                            <option value="black">Black</option>
                            <option value="asian">Asian</option>
                            <option value="hispanic">Hispanic</option>
                            <option value="other">Other</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* File Upload Section */}
                <div style={{
                  marginBottom: '2rem'
                }}>
                  <h3 style={{
                    fontSize: '1.2rem',
                    fontWeight: 500,
                    color: getTextColor(1),
                    marginBottom: '1rem'
                  }}>
                    Upload Image
                  </h3>
                  
                  {/* File Input */}
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileSelect}
                    style={{
                      display: 'none'
                    }}
                    id="file-upload"
                  />
                  
                  <label
                    htmlFor="file-upload"
                    style={{
                      display: 'block',
                      padding: '1rem',
                      border: `2px dashed ${getBorderColor(0.3)}`,
                      borderRadius: '12px',
                      textAlign: 'center',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      backgroundColor: getBgColor(0.05)
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = getBorderColor(0.5)
                      e.currentTarget.style.backgroundColor = getBgColor(0.1)
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = getBorderColor(0.3)
                      e.currentTarget.style.backgroundColor = getBgColor(0.05)
                    }}
                  >
                    <Upload width={24} height={24} style={{ marginBottom: '0.5rem', opacity: 0.7 }} />
                    <p style={{
                      margin: 0,
                      fontSize: '0.9rem',
                      color: getTextColor(0.8)
                    }}>
                      Click to select an image or drag and drop
                    </p>
                  </label>

                  {/* Upload Preview */}
                  {userImage && (
                    <div style={{
                      marginTop: '1rem',
                      textAlign: 'center'
                    }}>
                      <h4 style={{
                        fontSize: '1rem',
                        fontWeight: 500,
                        color: getTextColor(1),
                        marginBottom: '0.5rem'
                      }}>
                        Preview
                      </h4>
                      <div style={{
                        position: 'relative',
                        display: 'inline-block',
                        borderRadius: '8px',
                        overflow: 'hidden',
                        border: `2px solid ${getBorderColor(0.2)}`,
                        maxWidth: '200px',
                        maxHeight: '200px'
                      }}>
                        <img 
                          src={userImage}
                          alt="Upload preview"
                          style={{
                            width: '100%',
                            height: 'auto',
                            objectFit: 'cover',
                            display: 'block'
                          }}
                        />
                        
                        {/* Face Detection Overlay */}
                        {uploadFaceDetected && uploadFaceBounds && (
                          <div style={{
                            position: 'absolute',
                            top: '0',
                            left: '0',
                            width: '100%',
                            height: '100%',
                            pointerEvents: 'none'
                          }}>
                            {/* Face Detection Zone */}
                            <svg
                              width="100%"
                              height="100%"
                              style={{
                                position: 'absolute',
                                top: 0,
                                left: 0
                              }}
                            >
                              <rect
                                x={`${uploadFaceBounds?.x || 0}%`}
                                y={`${uploadFaceBounds?.y || 0}%`}
                                width={`${uploadFaceBounds?.width || 0}%`}
                                height={`${uploadFaceBounds?.height || 0}%`}
                                fill="none"
                                stroke="#10b981"
                                strokeWidth="2"
                                strokeDasharray="5,5"
                                opacity="0.8"
                              />
                              
                              {/* Corner Indicators */}
                              <circle
                                cx={`${uploadFaceBounds?.x || 0}%`}
                                cy={`${uploadFaceBounds?.y || 0}%`}
                                r="3"
                                fill="#10b981"
                                opacity="0.9"
                              />
                              <circle
                                cx={`${(uploadFaceBounds?.x || 0) + (uploadFaceBounds?.width || 0)}%`}
                                cy={`${uploadFaceBounds?.y || 0}%`}
                                r="3"
                                fill="#10b981"
                                opacity="0.9"
                              />
                              <circle
                                cx={`${uploadFaceBounds?.x || 0}%`}
                                cy={`${(uploadFaceBounds?.y || 0) + (uploadFaceBounds?.height || 0)}%`}
                                r="3"
                                fill="#10b981"
                                opacity="0.9"
                              />
                              <circle
                                cx={`${(uploadFaceBounds?.x || 0) + (uploadFaceBounds?.width || 0)}%`}
                                cy={`${(uploadFaceBounds?.y || 0) + (uploadFaceBounds?.height || 0)}%`}
                                r="3"
                                fill="#10b981"
                                opacity="0.9"
                              />
                            </svg>
                            
                            {/* Face Detection Label */}
                            <div style={{
                              position: 'absolute',
                              top: `${Math.max(0, (uploadFaceBounds?.y || 0) - 5)}%`,
                              left: `${uploadFaceBounds?.x || 0}%`,
                              backgroundColor: 'rgba(16, 185, 129, 0.9)',
                              color: '#000000',
                              padding: '0.25rem 0.5rem',
                              borderRadius: '4px',
                              fontSize: '0.7rem',
                              fontWeight: 'bold',
                              transform: 'translateY(-100%)'
                            }}>
                              FACE DETECTED
                            </div>
                          </div>
                        )}
                      </div>
                      
                      {/* Face Detection Status */}
                      {isDetectingFace && (
                        <div style={{
                          marginTop: '0.5rem',
                          padding: '0.5rem',
                          backgroundColor: 'rgba(59, 130, 246, 0.1)',
                          border: '1px solid rgba(59, 130, 246, 0.3)',
                          borderRadius: '6px',
                          fontSize: '0.8rem',
                          color: '#3b82f6'
                        }}>
                          <div style={{
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
                            Detecting face...
                          </div>
                        </div>
                      )}
                      
                      {!isDetectingFace && uploadFaceDetectionResult && (
                        <div style={{
                          marginTop: '0.5rem',
                          padding: '0.5rem',
                          backgroundColor: uploadFaceDetected ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                          border: uploadFaceDetected ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(239, 68, 68, 0.3)',
                          borderRadius: '6px',
                          fontSize: '0.8rem',
                          color: uploadFaceDetected ? '#10b981' : '#ef4444'
                        }}>
                          <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '0.5rem'
                          }}>
                            {uploadFaceDetected ? (
                              <>
                                <CheckCircle width={14} height={14} />
                                Face detected - Ready for analysis
                              </>
                            ) : (
                              <>
                                <X width={14} height={14} />
                                No face detected - Please upload a clear face image
                              </>
                            )}
                          </div>
                          {uploadFaceDetectionResult.quality_metrics && (
                            <div style={{
                              marginTop: '0.25rem',
                              fontSize: '0.7rem',
                              opacity: 0.8
                            }}>
                              Quality: {uploadFaceDetectionResult.quality_metrics.lighting}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                  
                  {/* Upload Progress */}
                  {isUploading && (
                    <div style={{
                      marginTop: '1rem',
                      padding: '1rem',
                      backgroundColor: 'rgba(59, 130, 246, 0.1)',
                      border: '1px solid rgba(59, 130, 246, 0.3)',
                      borderRadius: '8px'
                    }}>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        marginBottom: '0.5rem'
                      }}>
                        <div style={{
                          width: '16px',
                          height: '16px',
                          border: '2px solid #3b82f6',
                          borderTop: '2px solid transparent',
                          borderRadius: '50%',
                          animation: 'spin 1s linear infinite'
                        }} />
                        <span style={{
                          fontSize: '0.9rem',
                          color: '#3b82f6'
                        }}>
                          Analyzing image... {uploadProgress}%
                        </span>
                      </div>
                      <div style={{
                        width: '100%',
                        height: '4px',
                        backgroundColor: 'rgba(59, 130, 246, 0.2)',
                        borderRadius: '2px',
                        overflow: 'hidden'
                      }}>
                        <div style={{
                          width: `${uploadProgress}%`,
                          height: '100%',
                          backgroundColor: '#3b82f6',
                          transition: 'width 0.3s ease'
                        }} />
                      </div>
                    </div>
                  )}
                  
                  {/* Upload Button */}
                  <button
                    onClick={handleUpload}
                    disabled={!selectedFile || isUploading || !uploadFaceDetected}
                    style={{
                      width: '100%',
                      padding: '1rem',
                      backgroundColor: selectedFile && !isUploading && uploadFaceDetected ? '#10b981' : getBgColor(0.1),
                      border: 'none',
                      borderRadius: '12px',
                      color: getTextColor(1),
                      fontSize: '1rem',
                      fontWeight: 500,
                      cursor: selectedFile && !isUploading && uploadFaceDetected ? 'pointer' : 'not-allowed',
                      transition: 'all 0.3s ease',
                      marginTop: '1rem',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '0.5rem'
                    }}
                  >
                    <Sparkles width={20} height={20} />
                    {isUploading ? 'Analyzing...' : uploadFaceDetected ? 'Analyze Image' : 'Face Detection Required'}
                  </button>
                </div>
              </div>
            )}

            {/* Camera Mode */}
            {uploadMethod === 'camera' && (
              <div style={{
                backgroundColor: getBgColor(0.05),
                borderRadius: '16px',
                padding: '2rem',
                border: `1px solid ${getBorderColor(0.1)}`
              }}>
                {/* Phase 2: Demographic Input for Camera */}
                <div style={{
                  marginBottom: '2rem'
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    marginBottom: '1rem'
                  }}>
                    <User width={20} height={20} style={{ opacity: 0.7 }} />
                    <h3 style={{
                      fontSize: '1.1rem',
                      fontWeight: 400,
                      color: getTextColor(1)
                    }}>
                      Demographic Information (Optional)
                    </h3>
                  </div>
                  
                  <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '1rem',
                    marginBottom: '1rem'
                  }}>
                    <div style={{ flex: 1 }}>
                      <label style={{
                        display: 'block',
                        fontSize: '0.9rem',
                        color: getTextColor(0.7),
                        marginBottom: '0.5rem'
                      }}>
                        Age
                      </label>
                      <select
                        className="mobile-select"
                        value={ageCategory}
                        onChange={(e) => setAgeCategory(e.target.value)}
                        style={{
                          width: '100%',
                          padding: '0.75rem',
                          backgroundColor: getBgColor(0.1),
                          border: `1px solid ${getBorderColor(0.2)}`,
                          borderRadius: '8px',
                          color: getTextColor(1),
                          fontSize: '0.9rem'
                        }}
                      >
                        <option value="">Select age category</option>
                        {ageCategories.map(category => (
                          <option key={category} value={category}>{category}</option>
                        ))}
                      </select>
                    </div>
                    
                    <div style={{ flex: 1 }}>
                      <label style={{
                        display: 'block',
                        fontSize: '0.9rem',
                        color: getTextColor(0.7),
                        marginBottom: '0.5rem'
                      }}>
                        Ethnicity
                      </label>
                      <select
                        className="mobile-select"
                        value={raceCategory}
                        onChange={(e) => setRaceCategory(e.target.value)}
                        style={{
                          width: '100%',
                          padding: '0.75rem',
                          backgroundColor: getBgColor(0.1),
                          border: `1px solid ${getBorderColor(0.2)}`,
                          borderRadius: '8px',
                          color: getTextColor(1),
                          fontSize: '0.9rem'
                        }}
                      >
                        <option value="">Select race/ethnicity</option>
                        {raceCategories.map(category => (
                          <option key={category} value={category}>{category}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                  
                  <p style={{
                    fontSize: '0.8rem',
                    color: getTextColor(0.5),
                    fontStyle: 'italic'
                  }}>
                    Providing demographic information helps improve analysis accuracy and provides more personalized recommendations.
                  </p>
                </div>

                {/* Camera View */}
                <div style={{
                  position: 'relative',
                  marginBottom: '2rem'
                }}>
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    style={{
                      width: '100%',
                      borderRadius: '12px',
                      backgroundColor: '#000000'
                    }}
                  />
                  
                  {/* Facial Matrix Overlay */}
                  {faceDetected && (
                    <div style={{
                      position: 'absolute',
                      top: '0',
                      left: '0',
                      width: '100%',
                      height: '100%',
                      pointerEvents: 'none'
                    }}>
                      {/* Matrix Scan Line */}
                      <div className="matrix-scan" style={{
                        animationDelay: '0s'
                      }} />
                      <div className="matrix-scan" style={{
                        animationDelay: '1s'
                      }} />
                      <div className="matrix-scan" style={{
                        animationDelay: '2s'
                      }} />
                      {/* Matrix Grid Lines */}
                      <svg
                        width="100%"
                        height="100%"
                        style={{
                          position: 'absolute',
                          top: 0,
                          left: 0
                        }}
                      >
                        {/* Vertical Matrix Lines */}
                        {Array.from({ length: 10 }, (_, i) => (
                          <line
                            key={`v-${i}`}
                            x1={`${(i + 1) * 10}%`}
                            y1="0"
                            x2={`${(i + 1) * 10}%`}
                            y2="100%"
                            stroke="#00ff41"
                            strokeWidth="1"
                            opacity="0.3"
                            className="matrix-line"
                          />
                        ))}
                        
                        {/* Horizontal Matrix Lines */}
                        {Array.from({ length: 8 }, (_, i) => (
                          <line
                            key={`h-${i}`}
                            x1="0"
                            y1={`${(i + 1) * 12.5}%`}
                            x2="100%"
                            y2={`${(i + 1) * 12.5}%`}
                            stroke="#00ff41"
                            strokeWidth="1"
                            opacity="0.3"
                            className="matrix-line"
                          />
                        ))}
                        
                        {/* Face Detection Zone */}
                        <rect
                          x={`${detectionResult?.face_bounds?.x || 0}%`}
                          y={`${detectionResult?.face_bounds?.y || 0}%`}
                          width={`${detectionResult?.face_bounds?.width || 0}%`}
                          height={`${detectionResult?.face_bounds?.height || 0}%`}
                          fill="none"
                          stroke="#00ff41"
                          strokeWidth="3"
                          strokeDasharray="5,5"
                          opacity="0.8"
                        />
                        
                        {/* Corner Indicators */}
                        <circle
                          cx={`${detectionResult?.face_bounds?.x || 0}%`}
                          cy={`${detectionResult?.face_bounds?.y || 0}%`}
                          r="4"
                          fill="#00ff41"
                          opacity="0.9"
                        />
                        <circle
                          cx={`${(detectionResult?.face_bounds?.x || 0) + (detectionResult?.face_bounds?.width || 0)}%`}
                          cy={`${detectionResult?.face_bounds?.y || 0}%`}
                          r="4"
                          fill="#00ff41"
                          opacity="0.9"
                        />
                        <circle
                          cx={`${uploadFaceBounds.x}%`}
                          cy={`${uploadFaceBounds.y + uploadFaceBounds.height}%`}
                          r="4"
                          fill="#00ff41"
                          opacity="0.9"
                        />
                        <circle
                          cx={`${uploadFaceBounds.x + uploadFaceBounds.width}%`}
                          cy={`${uploadFaceBounds.y + uploadFaceBounds.height}%`}
                          r="4"
                          fill="#00ff41"
                          opacity="0.9"
                        />
                      </svg>
                      
                      {/* Face Detection Label */}
                      <div style={{
                        position: 'absolute',
                        top: `${Math.max(0, uploadFaceBounds.y - 5)}%`,
                        left: `${uploadFaceBounds.x}%`,
                        backgroundColor: 'rgba(0, 255, 65, 0.9)',
                        color: '#000000',
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.8rem',
                        fontWeight: 'bold',
                        transform: 'translateY(-100%)'
                      }}>
                        FACE DETECTED
                      </div>
                    </div>
                  )}
                  
                  {/* Real-time Detection Feedback */}
                  {uploadFaceDetectionResult && (
                    <div style={{
                      position: 'absolute',
                      top: '1rem',
                      right: '1rem',
                      backgroundColor: 'rgba(0, 0, 0, 0.8)',
                      padding: '0.75rem',
                      borderRadius: '8px',
                      fontSize: '0.8rem'
                    }}>
                      <div style={{
                        color: uploadFaceDetectionResult.face_detected ? '#10b981' : '#ef4444',
                        marginBottom: '0.25rem'
                      }}>
                        {uploadFaceDetectionResult.face_detected ? '✓ Face Detected' : '✗ No Face'}
                      </div>
                      <div style={{
                        color: getTextColor(0.7),
                        fontSize: '0.7rem'
                      }}>
                        Quality: {uploadFaceDetectionResult.quality_metrics.lighting}
                      </div>
                    </div>
                  )}
                  
                  {/* Additional guidance for no face detected in upload */}
                  {uploadFaceDetectionResult && !uploadFaceDetectionResult.face_detected && (
                    <div style={{
                      position: 'absolute',
                      bottom: '1rem',
                      left: '1rem',
                      right: '1rem',
                      backgroundColor: 'rgba(59, 130, 246, 0.9)',
                      padding: '0.75rem',
                      borderRadius: '8px',
                      fontSize: '0.8rem'
                    }}>
                      <div style={{
                        color: '#ffffff',
                        fontWeight: 500,
                        marginBottom: '0.25rem'
                      }}>
                        📸 No Face Detected
                      </div>
                      <div style={{
                        color: '#ffffff',
                        fontSize: '0.7rem',
                        opacity: 0.9
                      }}>
                        Try a different image with better lighting and a clear, centered face
                      </div>
                    </div>
                  )}
                </div>

                {/* Camera Controls */}
                <div style={{
                  display: 'flex',
                  gap: '1rem'
                }}>
                  <button
                    onClick={capturePhoto}
                    disabled={!faceDetected}
                    style={{
                      flex: 1,
                      padding: '1rem',
                      backgroundColor: faceDetected ? '#10b981' : getBgColor(0.1),
                      border: 'none',
                      borderRadius: '12px',
                      color: getTextColor(1),
                      fontSize: '1rem',
                      fontWeight: 500,
                      cursor: faceDetected ? 'pointer' : 'not-allowed',
                      transition: 'all 0.3s ease',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '0.5rem'
                    }}
                  >
                    <Camera width={20} height={20} />
                    Capture Photo
                  </button>
                  
                  <button
                    onClick={testCameraPermissions}
                    style={{
                      padding: '1rem',
                      backgroundColor: 'transparent',
                      border: `1px solid ${getBorderColor(0.2)}`,
                      borderRadius: '12px',
                      color: getTextColor(1),
                      fontSize: '0.9rem',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease'
                    }}
                  >
                    Test Camera
                  </button>
                </div>

                {/* Camera Guidance */}
                {!faceDetected && cameraActive && (
                  <div style={{
                    marginTop: '1rem',
                    padding: '1rem',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    border: '1px solid rgba(59, 130, 246, 0.3)',
                    borderRadius: '8px'
                  }}>
                    <p style={{
                      fontSize: '0.9rem',
                      color: '#3b82f6',
                      margin: 0
                    }}>
                      Position your face in the center of the camera for best results
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Hidden canvas for face detection */}
            <canvas
              ref={canvasRef}
              style={{ display: 'none' }}
            />
          </div>

          {/* Right Column - Results */}
          <div>
            {/* Analysis Error Display */}
            {analysisError && (
              <div style={{
                marginBottom: '1rem',
                padding: '1rem',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                borderRadius: '8px'
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  marginBottom: '0.5rem'
                }}>
                  <div style={{ color: '#ef4444', fontSize: '1.2rem' }}>⚠️</div>
                  <h4 style={{
                    fontSize: '1rem',
                    fontWeight: 500,
                    color: '#ef4444',
                    margin: 0
                  }}>
                    Analysis Error
                  </h4>
                </div>
                <p style={{
                  fontSize: '0.9rem',
                  color: '#ef4444',
                  margin: 0
                }}>
                  {analysisError}
                </p>
              </div>
            )}
            
            {analysisResult ? (
              <div style={{
                backgroundColor: getBgColor(0.05),
                borderRadius: '16px',
                padding: '2rem',
                border: `1px solid ${getBorderColor(0.1)}`
              }}>
                {/* Analysis Header */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '1rem',
                  marginBottom: '2rem'
                }}>
                  <CheckCircle width={24} height={24} style={{ color: '#10b981' }} />
                  <div>
                    <h2 style={{
                      fontSize: '1.5rem',
                      fontWeight: 400,
                      color: getTextColor(1),
                      margin: 0
                    }}>
                      Analysis Complete
                    </h2>
                    <p style={{
                      fontSize: '0.9rem',
                      color: getTextColor(0.7),
                      margin: 0
                    }}>
                      Enhanced analysis with demographic awareness
                    </p>
                  </div>
                </div>

                {/* User Image Display */}
                {userImage && (
                  <div style={{
                    marginBottom: '2rem',
                    textAlign: 'center'
                  }}>
                    <h3 style={{
                      fontSize: '1.1rem',
                      fontWeight: 500,
                      color: getTextColor(1),
                      marginBottom: '1rem'
                    }}>
                      Your Image
                    </h3>
                    <div style={{
                      position: 'relative',
                      display: 'inline-block',
                      borderRadius: '12px',
                      overflow: 'hidden',
                                              border: `2px solid ${getBorderColor(0.2)}`,
                      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)'
                    }}>
                      <img 
                        src={userImage}
                        alt="Analyzed image"
                        style={{
                          maxWidth: '300px',
                          maxHeight: '300px',
                          width: 'auto',
                          height: 'auto',
                          objectFit: 'contain',
                          display: 'block'
                        }}
                      />
                      {/* Face detection overlay if available */}
                      {analysisResult?.face_detection?.detected && (
                        <div style={{
                          position: 'absolute',
                          top: analysisResult?.face_detection?.face_bounds?.y || 0,
                          left: analysisResult?.face_detection?.face_bounds?.x || 0,
                          width: analysisResult?.face_detection?.face_bounds?.width || 0,
                          height: analysisResult?.face_detection?.face_bounds?.height || 0,
                          border: '2px solid #10b981',
                          borderRadius: '4px',
                          pointerEvents: 'none'
                        }} />
                      )}
                    </div>
                    <p style={{
                      fontSize: '0.8rem',
                      color: getTextColor(0.6),
                      marginTop: '0.5rem',
                      margin: 0
                    }}>
                      Confidence: {analysisResult?.face_detection?.confidence ? Math.round(analysisResult.face_detection?.confidence * 100) : 0}%
                    </p>
                    
                    {/* Face Detection Guidance */}
                    {!analysisResult?.face_detection?.detected && (
                      <div style={{
                        marginTop: '1rem',
                        padding: '1rem',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        border: '1px solid rgba(59, 130, 246, 0.3)',
                        borderRadius: '8px'
                      }}>
                        <h4 style={{
                          fontSize: '1rem',
                          fontWeight: 500,
                          color: '#3b82f6',
                          margin: '0 0 0.5rem 0'
                        }}>
                          📸 No Face Detected
                        </h4>
                        <p style={{
                          fontSize: '0.9rem',
                          color: '#3b82f6',
                          margin: '0 0 0.5rem 0'
                        }}>
                          We couldn't detect a face in your image. This could be due to:
                        </p>
                        <ul style={{
                          fontSize: '0.85rem',
                          color: '#3b82f6',
                          margin: 0,
                          paddingLeft: '1.5rem'
                        }}>
                          <li>Poor lighting - try taking the photo in better light</li>
                          <li>Face too small or not centered in the frame</li>
                          <li>Blurry or low-quality image</li>
                          <li>Face partially obscured or at wrong angle</li>
                        </ul>
                        <p style={{
                          fontSize: '0.85rem',
                          color: '#3b82f6',
                          margin: '0.5rem 0 0 0',
                          fontStyle: 'italic'
                        }}>
                          💡 Tip: Hold your phone steady, ensure good lighting, and position your face in the center of the camera.
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {/* Health Score */}
                <div style={{
                  marginBottom: '2rem',
                  padding: '1.5rem',
                  backgroundColor: 'rgba(16, 185, 129, 0.1)',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                  borderRadius: '12px'
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem',
                    marginBottom: '1rem'
                  }}>
                    <TrendingUp width={24} height={24} style={{ color: '#10b981' }} />
                    <h3 style={{
                      fontSize: '1.2rem',
                      fontWeight: 400,
                      color: getTextColor(1),
                      margin: 0
                    }}>
                      Overall Health Score
                    </h3>
                  </div>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem'
                  }}>
                    <div style={{
                      fontSize: '2.5rem',
                      fontWeight: 200,
                      color: '#10b981'
                    }}>
                      {analysisResult?.skin_analysis?.overall_health_score ? Math.round(analysisResult.skin_analysis?.overall_health_score * 100) : 0}%
                    </div>
                    <div style={{
                      flex: 1,
                      height: '8px',
                      backgroundColor: getBgColor(0.1),
                      borderRadius: '4px',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        width: `${analysisResult?.skin_analysis?.overall_health_score ? analysisResult.skin_analysis?.overall_health_score * 100 : 0}%`,
                        height: '100%',
                        backgroundColor: '#10b981',
                        transition: 'width 0.3s ease'
                      }} />
                    </div>
                  </div>
                </div>

                {/* Detected Conditions */}
                {analysisResult?.skin_analysis?.conditions_detected?.length > 0 && (
                  <div style={{
                    marginBottom: '2rem'
                  }}>
                    <h3 style={{
                      fontSize: '1.2rem',
                      fontWeight: 400,
                      color: getTextColor(1),
                      marginBottom: '1rem'
                    }}>
                      Detected Conditions
                    </h3>
                    {analysisResult?.skin_analysis?.conditions_detected?.map((condition, index) => (
                      <div key={index} style={{
                        padding: '1rem',
                        backgroundColor: getBgColor(0.05),
                        borderRadius: '8px',
                        marginBottom: '1rem'
                      }}>
                        <div style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          marginBottom: '0.5rem'
                        }}>
                          <span style={{
                            fontSize: '1rem',
                            fontWeight: 500,
                            color: getTextColor(1)
                          }}>
                            {condition.condition.replace('_', ' ').toUpperCase()}
                          </span>
                          <span style={{
                            fontSize: '0.9rem',
                            color: getTextColor(0.7)
                          }}>
                            {Math.round(condition.confidence * 100)}% confidence
                          </span>
                        </div>
                        <p style={{
                          fontSize: '0.9rem',
                          color: getTextColor(0.7),
                          margin: '0.5rem 0'
                        }}>
                          {condition.description}
                        </p>
                        <div style={{
                          display: 'flex',
                          gap: '0.5rem',
                          flexWrap: 'wrap'
                        }}>
                          <span style={{
                            padding: '0.25rem 0.5rem',
                            backgroundColor: 'rgba(59, 130, 246, 0.2)',
                            color: '#3b82f6',
                            borderRadius: '4px',
                            fontSize: '0.8rem'
                          }}>
                            {condition.severity}
                          </span>
                          <span style={{
                            padding: '0.25rem 0.5rem',
                            backgroundColor: getBgColor(0.1),
                            color: getTextColor(0.7),
                            borderRadius: '4px',
                            fontSize: '0.8rem'
                          }}>
                            {condition.location}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Recommendations */}
                <div style={{
                  marginBottom: '2rem'
                }}>
                  <h3 style={{
                    fontSize: '1.2rem',
                    fontWeight: 400,
                    color: getTextColor(1),
                    marginBottom: '1rem'
                  }}>
                    Recommendations
                  </h3>
                  
                  {/* Immediate Care */}
                  <div style={{
                    marginBottom: '1.5rem'
                  }}>
                    <h4 style={{
                      fontSize: '1rem',
                      fontWeight: 500,
                      color: getTextColor(1),
                      marginBottom: '0.5rem'
                    }}>
                      Immediate Care
                    </h4>
                    <ul style={{
                      listStyle: 'none',
                      padding: 0,
                      margin: 0
                    }}>
                      {analysisResult.recommendations?.immediate_care?.map((rec, index) => (
                        <li key={index} style={{
                          padding: '0.5rem 0',
                          borderBottom: `1px solid ${getBorderColor(0.1)}`,
                          fontSize: '0.9rem',
                          color: getTextColor(0.8)
                        }}>
                          • {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  {/* Long-term Care */}
                  <div>
                    <h4 style={{
                      fontSize: '1rem',
                      fontWeight: 500,
                      color: getTextColor(1),
                      marginBottom: '0.5rem'
                    }}>
                      Long-term Care
                    </h4>
                    <ul style={{
                      listStyle: 'none',
                      padding: 0,
                      margin: 0
                    }}>
                      {analysisResult.recommendations?.long_term_care?.map((rec, index) => (
                        <li key={index} style={{
                          padding: '0.5rem 0',
                          borderBottom: `1px solid ${getBorderColor(0.1)}`,
                          fontSize: '0.9rem',
                          color: getTextColor(0.8)
                        }}>
                          • {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Professional Consultation Warning */}
                {analysisResult.recommendations?.professional_consultation && (
                  <div style={{
                    padding: '1rem',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid rgba(239, 68, 68, 0.3)',
                    borderRadius: '8px',
                    marginBottom: '2rem'
                  }}>
                    <p style={{
                      fontSize: '0.9rem',
                      color: '#ef4444',
                      margin: 0,
                      fontWeight: 500
                    }}>
                      ⚠️ Professional consultation recommended
                    </p>
                  </div>
                )}

                {/* Product Recommendations */}
                <div style={{
                  marginBottom: '2rem'
                }}>
                  <h3 style={{
                    fontSize: '1.2rem',
                    fontWeight: 400,
                    color: getTextColor(1),
                    marginBottom: '1rem'
                  }}>
                    Recommended Products
                  </h3>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                    gap: '1rem'
                  }}>
                    {analysisResult && getProductRecommendations(analysisResult).map((product, index) => (
                      <div key={index} style={{
                        backgroundColor: getBgColor(0.05),
                        borderRadius: '12px',
                        padding: '1rem',
                        border: `1px solid ${getBorderColor(0.1)}`,
                        transition: 'all 0.3s ease',
                        cursor: 'pointer'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = getBgColor(0.1)
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = getBgColor(0.05)
                      }}
                      >
                        <div style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '1rem',
                          marginBottom: '0.5rem'
                        }}>
                          <img 
                            src={product.image}
                            alt={product.name}
                            style={{
                              width: '60px',
                              height: '60px',
                              objectFit: 'cover',
                              borderRadius: '8px'
                            }}
                            onError={(e) => {
                              e.currentTarget.style.display = 'none'
                            }}
                          />
                          <div style={{ flex: 1 }}>
                            <h4 style={{
                              fontSize: '1rem',
                              fontWeight: 500,
                              color: getTextColor(1),
                              margin: '0 0 0.25rem 0'
                            }}>
                              {product.name}
                            </h4>
                            <span style={{
                              fontSize: '0.8rem',
                              color: getTextColor(0.6),
                              textTransform: 'capitalize'
                            }}>
                              {product.category}
                            </span>
                          </div>
                        </div>
                        <p style={{
                          fontSize: '0.85rem',
                          color: getTextColor(0.8),
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
                            fontSize: '1.1rem',
                            fontWeight: 'bold',
                            color: '#3b82f6'
                          }}>
                            ${product.price.toFixed(2)}
                          </span>
                          <button
                            onClick={() => {
                              if (isAuthenticated) {
                                dispatch({ type: 'ADD_ITEM', payload: product })
                              } else {
                                setShowSignInModal(true)
                              }
                            }}
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '0.5rem',
                              padding: '0.5rem 1rem',
                              backgroundColor: isAuthenticated ? '#3b82f6' : 'rgba(59, 130, 246, 0.5)',
                              border: '1px solid #3b82f6',
                              borderRadius: '6px',
                              color: getTextColor(1),
                              cursor: isAuthenticated ? 'pointer' : 'not-allowed',
                              fontSize: '0.8rem',
                              fontWeight: 'bold',
                              transition: 'all 0.3s ease'
                            }}
                          >
                            <ShoppingCart width={14} height={14} />
                            {isAuthenticated ? 'Add to Cart' : 'Sign In to Add'}
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Analysis Details */}
                <div style={{
                  fontSize: '0.8rem',
                  color: getTextColor(0.5),
                  borderTop: `1px solid ${getBorderColor(0.1)}`,
                  paddingTop: '1rem'
                }}>
                  <p style={{ margin: '0.25rem 0' }}>
                    Analysis Method: {analysisResult?.face_detection?.method || 'Unknown'}
                  </p>
                  <p style={{ margin: '0.25rem 0' }}>
                    Confidence: {analysisResult?.skin_analysis?.analysis_confidence ? Math.round(analysisResult.skin_analysis?.analysis_confidence * 100) : 0}%
                  </p>
                  <p style={{ margin: '0.25rem 0' }}>
                    Dataset: {analysisResult?.similarity_search?.dataset_used || 'Unknown'}
                  </p>
                  {analysisResult?.demographics?.age_category && (
                    <p style={{ margin: '0.25rem 0' }}>
                      Age Category: {analysisResult.demographics.age_category}
                    </p>
                  )}
                  {analysisResult?.demographics?.race_category && (
                    <p style={{ margin: '0.25rem 0' }}>
                      Race Category: {analysisResult.demographics.race_category}
                    </p>
                  )}
                                  </div>
                </div>
            ) : (
              <div style={{
                backgroundColor: getBgColor(0.05),
                borderRadius: '16px',
                padding: '2rem',
                border: `1px solid ${getBorderColor(0.1)}`,
                textAlign: 'center'
              }}>
                <Sparkles width={48} height={48} style={{ opacity: 0.3, marginBottom: '1rem' }} />
                <h3 style={{
                  fontSize: '1.2rem',
                  fontWeight: 400,
                  color: getTextColor(1),
                  marginBottom: '0.5rem'
                }}>
                  Ready for Analysis
                </h3>
                <p style={{
                  fontSize: '0.9rem',
                  color: getTextColor(0.7)
                }}>
                  Upload an image or use the camera to begin your enhanced skin analysis
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>

      {/* Sign In Modal */}
      <SignInModal 
        isOpen={showSignInModal}
        onClose={() => setShowSignInModal(false)}
        onSuccess={() => setShowSignInModal(false)}
      />
    </div>
  )
} 