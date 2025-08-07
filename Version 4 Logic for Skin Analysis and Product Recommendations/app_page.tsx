
'use client'

import { useState, useRef, useEffect } from 'react'
import { Camera, Upload, Sparkles, Sun, User, ShoppingCart, X, ArrowRight } from 'lucide-react'
import Link from 'next/link'
import { useCart } from '@/hooks/useCart'
import { useAuth } from '@/hooks/useAuth'
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
    }[]
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
    }[]
  } | null>(null)

  // Camera states
  const [cameraLoading, setCameraLoading] = useState(false)
  const [cameraError, setCameraError] = useState<string | null>(null)
  const [cameraActive, setCameraActive] = useState(false)
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null)

  // Analysis results
  const [analysisResults, setAnalysisResults] = useState<any | null>(null)

  // Demographic data
  const [age, setAge] = useState<string>('')
  const [ethnicity, setEthnicity] = useState<string>('')
  const [gender, setGender] = useState<string>('')

  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    if (cameraActive && videoRef.current) {
      navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
          if (videoRef.current) {
            videoRef.current.srcObject = stream
            setCameraStream(stream)
          }
        })
        .catch((err) => {
          console.error("Error accessing camera: ", err)
          setCameraError("Failed to access camera. Please ensure it's enabled and try again.")
          setCameraLoading(false)
        })
    }

    return () => {
      if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop())
      }
    }
  }, [cameraActive])

  const captureImage = async () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current
      const canvas = canvasRef.current
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      const context = canvas.getContext('2d')
      if (context) {
        context.drawImage(video, 0, 0, canvas.width, canvas.height)
        const imageDataUrl = canvas.toDataURL('image/jpeg')
        setUserImage(imageDataUrl)
        setCameraActive(false) // Stop camera after capture
        if (cameraStream) {
          cameraStream.getTracks().forEach(track => track.stop())
          setCameraStream(null)
        }

        // Validate and process the captured image
        const validation = validateImage(imageDataUrl)
        setImageValidation(validation)
        if (validation.isValid) {
          const processed = await handleCameraCapture(imageDataUrl)
          setProcessedImage(processed)
        }
      }
    }
  }

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = async () => {
        const imageDataUrl = reader.result as string
        setUserImage(imageDataUrl)

        // Validate and process the uploaded image
        const validation = validateImage(imageDataUrl)
        setImageValidation(validation)
        if (validation.isValid) {
          const processed = await handleFileUpload(file)
          setProcessedImage(processed)
        }
      }
      reader.readAsDataURL(file)
    }
  }

  const analyzeSkin = async () => {
    if (!processedImage?.base64) {
      setAnalysisError("No image to analyze. Please upload or capture an image.")
      return
    }

    setIsAnalyzing(true)
    setAnalysisError(null)
    setAnalysisResults(null)

    try {
      const response = await directBackendClient.post('/api/v3/skin/analyze-real', {
        image: processedImage.base64,
        age: age || null,
        ethnicity: ethnicity || null,
        gender: gender || null,
      })

      if (response.status === 200 && response.data.status === 'success') {
        setAnalysisResults(response.data.data)
        // Redirect to suggestions page or display results directly
        // For now, we'll just log and display on this page
        console.log("Analysis Results:", response.data.data)
      } else {
        setAnalysisError(response.data.message || "An unknown error occurred during analysis.")
      }
    } catch (error: any) {
      console.error("Error during skin analysis API call:", error)
      setAnalysisError(error.response?.data?.message || error.message || "Failed to connect to backend for analysis.")
    } finally {
      setIsAnalyzing(false)
    }
  }

  const detectFace = async () => {
    if (!processedImage?.base64) {
      setFaceDetection(null)
      return
    }

    try {
      const response = await directBackendClient.post('/api/v3/face/detect', {
        image: processedImage.base64,
      })

      if (response.status === 200 && response.data.status === 'success') {
        setFaceDetection(response.data)
        console.log("Face Detection Results:", response.data)
      } else {
        setFaceDetection(null)
        console.error("Face detection failed:", response.data.message)
      }
    } catch (error) {
      console.error("Error during face detection API call:", error)
      setFaceDetection(null)
    }
  }

  const handleClear = () => {
    setUserImage(null)
    setProcessedImage(null)
    setIsAnalyzing(false)
    setAnalysisError(null)
    setImageValidation(null)
    setFaceDetection(null)
    setLiveFaceDetection(null)
    setAnalysisResults(null)
    setAge('')
    setEthnicity('')
    setGender('')
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop())
      setCameraStream(null)
    }
    setCameraActive(false)
  }

  const handleSignInClick = () => {
    setShowSignInModal(true)
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-gray-900 dark:to-black text-gray-900 dark:text-gray-100 transition-colors duration-300">
      <Header isAuthenticated={isAuthenticated} onSignInClick={handleSignInClick} />
      <SignInModal isOpen={showSignInModal} onClose={() => setShowSignInModal(false)} />

      <main className="flex flex-col items-center justify-center flex-1 w-full max-w-4xl">
        <h1 className="text-5xl font-extrabold mb-6 text-center leading-tight tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400">
          SHINE Skin Collective
        </h1>
        <p className="text-xl mb-8 text-center max-w-2xl opacity-90">
          AI-Powered Skincare Analysis & Personalized Recommendations
        </p>

        <div className="w-full bg-white dark:bg-gray-800 rounded-xl shadow-2xl p-8 mb-8 border border-gray-200 dark:border-gray-700 transform transition-all duration-300 hover:scale-[1.01]">
          <h2 className="text-3xl font-bold text-center mb-6 text-blue-700 dark:text-blue-300">Analyze Your Skin</h2>

          <div className="flex flex-col md:flex-row gap-6 mb-6">
            <div className="flex-1 flex flex-col items-center justify-center border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center hover:border-blue-500 dark:hover:border-blue-400 transition-colors duration-200">
              <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
                <Upload className="w-12 h-12 text-gray-500 dark:text-gray-400 mb-3" />
                <span className="text-lg font-semibold mb-2">Upload Image</span>
                <span className="text-sm text-gray-600 dark:text-gray-400">Drag & drop or click to select a file</span>
                <input id="file-upload" type="file" accept="image/*" className="hidden" onChange={handleImageUpload} />
              </label>
            </div>

            <div className="flex-1 flex flex-col items-center justify-center border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center hover:border-blue-500 dark:hover:border-blue-400 transition-colors duration-200">
              <button onClick={() => setCameraActive(!cameraActive)} className="flex flex-col items-center w-full h-full justify-center">
                <Camera className="w-12 h-12 text-gray-500 dark:text-gray-400 mb-3" />
                <span className="text-lg font-semibold mb-2">{cameraActive ? 'Stop Camera' : 'Use Camera'}</span>
                <span className="text-sm text-gray-600 dark:text-gray-400">Capture a live image for analysis</span>
              </button>
            </div>
          </div>

          {cameraActive && (
            <div className="mb-6 flex flex-col items-center">
              <video ref={videoRef} autoPlay playsInline className="w-full max-w-md rounded-lg shadow-md mb-4"></video>
              <canvas ref={canvasRef} className="hidden"></canvas>
              <button onClick={captureImage} className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-full transition-colors duration-200 shadow-lg">
                Capture Photo
              </button>
              {cameraError && <p className="text-red-500 mt-2">{cameraError}</p>}
            </div>
          )}

          {userImage && (
            <div className="mb-6 text-center">
              <h3 className="text-xl font-semibold mb-3">Image Preview:</h3>
              <img src={userImage} alt="User Upload" className="max-w-full h-auto rounded-lg shadow-md mx-auto" />
              {imageValidation && !imageValidation.isValid && (
                <div className="text-red-500 mt-4">
                  <p className="font-semibold">Image Validation Errors:</p>
                  <ul className="list-disc list-inside">
                    {imageValidation.errors.map((err, index) => (
                      <li key={index}>{err}</li>
                    ))}
                  </ul>
                </div>
              )}
              {imageValidation && imageValidation.warnings.length > 0 && (
                <div className="text-yellow-500 mt-2">
                  <p className="font-semibold">Image Validation Warnings:</p>
                  <ul className="list-disc list-inside">
                    {imageValidation.warnings.map((warn, index) => (
                      <li key={index}>{warn}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          <div className="mb-6">
            <h3 className="text-xl font-semibold mb-3 text-center">Optional: Provide Demographics for Better Accuracy</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label htmlFor="age" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Age</label>
                <input
                  type="number"
                  id="age"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  placeholder="e.g., 30"
                />
              </div>
              <div>
                <label htmlFor="ethnicity" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Ethnicity</label>
                <select
                  id="ethnicity"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                  value={ethnicity}
                  onChange={(e) => setEthnicity(e.target.value)}
                >
                  <option value="">Select...</option>
                  <option value="asian">Asian</option>
                  <option value="black">Black</option>
                  <option value="hispanic">Hispanic</option>
                  <option value="white">White</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div>
                <label htmlFor="gender" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Gender</label>
                <select
                  id="gender"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                  value={gender}
                  onChange={(e) => setGender(e.target.value)}
                >
                  <option value="">Select...</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
          </div>

          <div className="flex justify-center gap-4">
            <button
              onClick={analyzeSkin}
              disabled={!userImage || isAnalyzing || (imageValidation && !imageValidation.isValid)}
              className="bg-gradient-to-r from-green-500 to-teal-600 hover:from-green-600 hover:to-teal-700 text-white font-bold py-3 px-8 rounded-full transition-all duration-300 shadow-lg transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isAnalyzing ? (
                <span className="flex items-center">
                  <Sparkles className="animate-spin mr-2" /> Analyzing...
                </span>
              ) : (
                "Analyze My Skin"
              )}
            </button>
            <button
              onClick={handleClear}
              className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-3 px-8 rounded-full transition-colors duration-200 shadow-lg transform hover:scale-105"
            >
              Clear
            </button>
          </div>

          {analysisError && (
            <div className="mt-6 p-4 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded-lg shadow-md">
              <p className="font-semibold">Analysis Error:</p>
              <p>{analysisError}</p>
            </div>
          )}

          {analysisResults && (
            <div className="mt-8 p-6 bg-green-50 dark:bg-green-900 rounded-xl shadow-inner border border-green-200 dark:border-green-700">
              <h2 className="text-3xl font-bold text-center mb-6 text-green-700 dark:text-green-300">Analysis Results</h2>
              <div className="space-y-4">
                <p className="text-lg"><span className="font-semibold">Confidence Score:</span> {analysisResults.confidence_score}%</p>
                <p className="text-lg"><span className="font-semibold">Summary:</span> {analysisResults.analysis_summary}</p>
                
                {analysisResults.detected_conditions && analysisResults.detected_conditions.length > 0 && (
                  <div>
                    <h3 className="text-xl font-semibold mb-3 text-green-600 dark:text-green-400">Detected Conditions:</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {analysisResults.detected_conditions.map((condition: any, index: number) => (
                        <div key={index} className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
                          <p className="font-bold text-lg text-blue-600 dark:text-blue-400">{condition.name}</p>
                          <p>Confidence: {condition.confidence}%</p>
                          <p>Severity: {condition.severity}</p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">{condition.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {analysisResults.recommendations && analysisResults.recommendations.length > 0 && (
                  <div>
                    <h3 className="text-xl font-semibold mb-3 text-green-600 dark:text-green-400">Product Recommendations:</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {analysisResults.recommendations.map((rec: any, index: number) => (
                        <div key={index} className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 flex flex-col">
                          <h4 className="font-bold text-lg mb-2 text-purple-600 dark:text-purple-400">{rec.product_name}</h4>
                          <p className="text-sm text-gray-600 dark:text-gray-400 flex-grow">{rec.description}</p>
                          <p className="text-sm font-semibold mt-2">Target Condition: {rec.target_condition}</p>
                          <p className="text-sm font-semibold">Ingredients: {rec.ingredients}</p>
                          <p className="text-sm font-semibold">Usage: {rec.usage}</p>
                          <button
                            onClick={() => dispatch({ type: 'ADD_ITEM', payload: { id: rec.product_id, name: rec.product_name, price: rec.price || 0, quantity: 1 } })}
                            className="mt-4 bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-full transition-colors duration-200"
                          >
                            Add to Cart
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {analysisResults.health_score !== undefined && (
                  <p className="text-lg"><span className="font-semibold">Health Score:</span> {analysisResults.health_score}/100</p>
                )}

                {analysisResults.demographic_baselines_used && (
                  <p className="text-lg"><span className="font-semibold">Demographic Baselines Used:</span> {analysisResults.demographic_baselines_used}</p>
                )}

                {analysisResults.additional_notes && (
                  <p className="text-lg"><span className="font-semibold">Additional Notes:</span> {analysisResults.additional_notes}</p>
                )}

                <Link href="/suggestions" className="inline-flex items-center justify-center bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-full transition-colors duration-200 shadow-lg transform hover:scale-105 mt-6">
                  View All Product Suggestions <ArrowRight className="ml-2" />
                </Link>
              </div>
            </div>
          )}

          {faceDetection && (
            <div className="mt-8 p-6 bg-blue-50 dark:bg-blue-900 rounded-xl shadow-inner border border-blue-200 dark:border-blue-700">
              <h2 className="text-3xl font-bold text-center mb-6 text-blue-700 dark:text-blue-300">Face Detection Results</h2>
              <p className="text-lg"><span className="font-semibold">Faces Detected:</span> {faceDetection.faces_detected}</p>
              {faceDetection.faces_detected > 0 && (
                <div>
                  <h3 className="text-xl font-semibold mb-3 text-blue-600 dark:text-blue-400">Face Bounds:</h3>
                  <ul className="list-disc list-inside">
                    {faceDetection.faces.map((face: any, index: number) => (
                      <li key={index}>Box: ({face.box[0]}, {face.box[1]}, {face.box[2]}, {face.box[3]}), Confidence: {face.confidence}%</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

        </div>
      </main>

      <footer className="w-full text-center mt-8 text-gray-600 dark:text-gray-400 text-sm">
        <p>&copy; {new Date().getFullYear()} SHINE Skin Collective. All rights reserved.</p>
      </footer>
    </div>
  )
}


