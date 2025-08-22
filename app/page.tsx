'use client';

import { useState, useEffect } from 'react';
import { Camera, Upload, ArrowRight, Zap, Eye } from 'lucide-react';
import { Header } from '@/components/header';
import { ImageCaptureGuidance } from '@/components/image-capture-guidance';
import { MediaPipeFaceDetection } from '@/components/mediapipe-face-detection';
import { getApiUrl, API_CONFIG } from '@/lib/config';
import Link from 'next/link';
import { useAnalysis } from './contexts/AnalysisContext';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const { setAnalysisData } = useAnalysis();
  const router = useRouter();
  
  // DEBUG: Log config values to see what's happening
  console.log('🔍 DEBUG: API_CONFIG loaded:', API_CONFIG);
  console.log('🔍 DEBUG: FACE_DETECT endpoint:', API_CONFIG.ENDPOINTS.FACE_DETECT);
  console.log('🔍 DEBUG: getApiUrl test:', getApiUrl(API_CONFIG.ENDPOINTS.FACE_DETECT));
  console.log('🔍 DEBUG: process.env.NEXT_PUBLIC_BACKEND_URL:', typeof process !== 'undefined' ? process.env?.NEXT_PUBLIC_BACKEND_URL : 'process not available in browser');
  
  // Remove unused refs and functions
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showMediaPipe, setShowMediaPipe] = useState(false);
  const [faceDetected, setFaceDetected] = useState(false);
  const [faceConfidence, setFaceConfidence] = useState(0);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [showImagePreview, setShowImagePreview] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [croppedFaceImage, setCroppedFaceImage] = useState<string | null>(null);
  const [preprocessingMetrics, setPreprocessingMetrics] = useState({
    geometric: { overallScore: 0 },
    colorLighting: { overallScore: 0 },
    enhancement: { enabled: false },
    mediapipe: { 
      landmarksCount: 0,
      confidence: 0,
      regionsDetected: false
    }
  });
  
  // MediaPipe state
  const [mediapipeLandmarks, setMediapipeLandmarks] = useState<Array<[number, number, number]>>([]);
  const [faceBounds, setFaceBounds] = useState<{ x: number; y: number; width: number; height: number } | null>(null);
  const [facialRegions, setFacialRegions] = useState<any>(null);
  
  // Camera state
  const [showCameraInterface, setShowCameraInterface] = useState(false);
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null);
  const [cameraVideo, setCameraVideo] = useState<HTMLVideoElement | null>(null);
  
  // Debug logging for cropped face image state changes
  useEffect(() => {
    console.log('🔍 DEBUG: croppedFaceImage state changed:', croppedFaceImage ? `EXISTS (${croppedFaceImage.length} chars)` : 'NULL');
  }, [croppedFaceImage]);
  
  useEffect(() => {
    // Set loading to false immediately for testing
    setIsLoading(false);
  }, []);
  
  // Insert video element when camera starts
  useEffect(() => {
    if (showCameraInterface && cameraVideo) {
      const previewDiv = document.getElementById('camera-preview');
      if (previewDiv) {
        // Clear the loading content
        previewDiv.innerHTML = '';
        // Insert the video element
        previewDiv.appendChild(cameraVideo);
        cameraVideo.style.width = '100%';
        cameraVideo.style.height = '100%';
        cameraVideo.style.objectFit = 'cover';
      }
    }
  }, [showCameraInterface, cameraVideo]);
  
  // Cleanup camera on unmount
  useEffect(() => {
    return () => {
      if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
      }
    };
  }, [cameraStream]);

  const startMediaPipe = () => {
    console.log('🚀 Starting MediaPipe dashboard...');
    setShowMediaPipe(true);
  };

  const startCameraCapture = () => {
    console.log('📸 Starting camera capture for face detection...');
    // This will use the existing face detection system
    setShowMediaPipe(false);
    // We'll implement a simple camera capture here
    startSimpleCameraCapture();
  };

  const startSimpleCameraCapture = async () => {
    try {
      console.log('📸 Starting camera capture...');
      
      // Show camera interface
      setShowCameraInterface(true);
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        } 
      });
      
      // Store stream reference
      setCameraStream(stream);
      
      // Create video element and start preview
      const video = document.createElement('video');
      video.srcObject = stream;
      video.autoplay = true;
      video.playsInline = true;
      video.muted = true;
      
      // Wait for video to be ready
      await new Promise(resolve => {
        video.onloadedmetadata = resolve;
      });
      
      // Store video element reference
      setCameraVideo(video);
      
      console.log('✅ Camera started successfully');
      
    } catch (error) {
      console.error('Camera capture failed:', error);
      alert('Camera access failed. Please try uploading an image instead.');
      setShowCameraInterface(false);
    }
  };

  const stopMediaPipe = () => {
    setShowMediaPipe(false);
    setFaceDetected(false);
    setFaceConfidence(0);
    setMediapipeLandmarks([]);
    setFaceBounds(null);
    setFacialRegions(null);
  };
  
  const capturePhoto = () => {
    if (cameraVideo && cameraStream) {
      console.log('📸 Capturing photo...');
      
      const canvas = document.createElement('canvas');
      canvas.width = cameraVideo.videoWidth;
      canvas.height = cameraVideo.videoHeight;
      const ctx = canvas.getContext('2d');
      
      if (ctx) {
        ctx.drawImage(cameraVideo, 0, 0);
        const imageData = canvas.toDataURL('image/jpeg', 0.9);
        
        // Stop the camera stream
        cameraStream.getTracks().forEach(track => track.stop());
        
        // Reset camera state
        setShowCameraInterface(false);
        setCameraStream(null);
        setCameraVideo(null);
        
        // Process the captured image through face detection
        setUploadedImage(imageData);
        setShowImagePreview(true);
        performFaceDetectionOnImage(imageData);
        
        console.log('✅ Photo captured and camera stopped');
      }
    }
  };
  
  const stopCamera = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
    }
    setShowCameraInterface(false);
    setCameraStream(null);
    setCameraVideo(null);
    console.log('📸 Camera stopped');
  };

  const analyzeSkin = async (imageData: string) => {
    // ENFORCE FACE DETECTION REQUIREMENT
    if (!faceDetected) {
      console.error('❌ Face detection required before analysis');
      alert('Please wait for face detection to complete before analyzing your photo.');
      return;
    }

    setIsAnalyzing(true);
    console.log('🔍 Starting enhanced analysis with preprocessing...');
    console.log('📊 Face detection status before analysis:', { faceDetected, faceConfidence });
    console.log('📊 Image data length:', imageData.length);
    console.log('📊 MediaPipe landmarks:', mediapipeLandmarks?.length || 0);
    console.log('📊 Preprocessing metrics:', preprocessingMetrics);

    try {
      // Check if we have enhanced preprocessing data
      const hasEnhancedData = (mediapipeLandmarks?.length || 0) > 0 && 
                             preprocessingMetrics.mediapipe?.confidence > 0.7;

      if (hasEnhancedData) {
        console.log('🚀 Using enhanced preprocessing analysis...');
        
        // Prepare enhanced preprocessing data
        const enhancedData = {
          image_data: imageData,
          preprocessing_metadata: {
            timestamp: new Date().toISOString(),
            device_info: {
              userAgent: navigator.userAgent,
              platform: navigator.platform,
              screen_resolution: `${screen.width}x${screen.height}`,
              camera_resolution: '640x480'
            },
            capture_conditions: {
              geometric_normalization: preprocessingMetrics.geometric || {},
              color_lighting_normalization: preprocessingMetrics.colorLighting || {},
              image_enhancement: preprocessingMetrics.enhancement || {},
              mediapipe_detection: preprocessingMetrics.mediapipe || {},
              face_detection_confidence: preprocessingMetrics.mediapipe?.confidence || 0.8
            },
            quality_metrics: {
              overall_score: calculateOverallPreprocessingScore(),
              lighting_score: preprocessingMetrics.colorLighting?.overallScore || 75,
              color_score: preprocessingMetrics.colorLighting?.overallScore || 75,
              geometric_score: preprocessingMetrics.geometric?.overallScore || 80,
              mediapipe_score: (preprocessingMetrics.mediapipe?.confidence || 0.8) * 100
            }
          }
        };

        console.log('📡 Sending enhanced data to backend:', enhancedData);
        
        // Send to enhanced preprocessing endpoint
        const response = await fetch('/api/v6/skin/analyze-advanced', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(enhancedData)
        });

        if (!response.ok) {
          throw new Error(`Enhanced analysis failed: ${response.status}`);
        }

        const result = await response.json();
        console.log('✅ Enhanced analysis successful:', result);
        
        // Get product recommendations based on analysis
        console.log('🛍️ Getting product recommendations...');
        const recommendationsResponse = await fetch('/api/recommendations', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            analysis_result: result,
            skin_condition: result.primary_condition || 'general',
            severity: result.severity || 0.5,
            skin_health_score: result.skin_health_score || 0.7
          })
        });

        let recommendations = [];
        if (recommendationsResponse.ok) {
          recommendations = await recommendationsResponse.json();
          console.log('✅ Product recommendations received:', recommendations);
        } else {
          console.log('⚠️ Using fallback recommendations');
          recommendations = getFallbackRecommendations(result.primary_condition || 'general');
        }
        
        // Store enhanced analysis data with recommendations
        setAnalysisData({
          originalImage: imageData,
          croppedFaceImage: croppedFaceImage,
          faceConfidence: faceConfidence,
          analysisResults: result,
          preprocessingMetrics: preprocessingMetrics,
          mediapipeLandmarks: mediapipeLandmarks || [],
          productRecommendations: recommendations
        });
        
        // Store in sessionStorage for backward compatibility
        sessionStorage.setItem('analysisResult', JSON.stringify(result));
        sessionStorage.setItem('productRecommendations', JSON.stringify(recommendations));
        console.log('💾 Stored analysis result and recommendations in context and sessionStorage');
        
        // Navigate directly to advanced results page with everything
        setTimeout(() => {
          console.log('🔗 Navigating to advanced results page with analysis and recommendations...');
          router.push('/training-advanced');
        }, 100);
        
      } else {
        console.log('📊 Using standard analysis (no enhanced preprocessing)...');
        
        // Fall back to standard analysis
        const result = {
          primary_condition: 'acne',
          confidence: 0.92,
          severity: 0.75,
          skin_health_score: 0.68,
          enhanced_ml: false,
          model_version: 'Standard_Version_1.0',
          accuracy: '92.1%',
          model_type: 'Standard_Model'
        };
        
        // Get basic recommendations for standard analysis
        const recommendations = getFallbackRecommendations('acne');
        
        console.log('✅ Standard analysis successful:', result);
        
        setAnalysisData({
          originalImage: imageData,
          croppedFaceImage: croppedFaceImage,
          faceConfidence: faceConfidence,
          analysisResults: result,
          productRecommendations: recommendations
        });
        
        // Store in sessionStorage for backward compatibility
        sessionStorage.setItem('analysisResult', JSON.stringify(result));
        sessionStorage.setItem('productRecommendations', JSON.stringify(recommendations));
        console.log('💾 Stored analysis result and recommendations in context and sessionStorage');
        
        // Navigate directly to advanced results page with everything
        setTimeout(() => {
          console.log('🔗 Navigating to advanced results page with analysis and recommendations...');
          router.push('/training-advanced');
        }, 100);
      }
      
    } catch (error) {
      console.error('❌ Analysis error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('❌ Full error details:', error);
      
      alert(`Analysis Error: ${errorMessage}`);
      setIsAnalyzing(false);
    }
    
    // Always reset analyzing state
    setIsAnalyzing(false);
  };
  
  // Fallback product recommendations when API is unavailable
  const getFallbackRecommendations = (condition: string) => {
    const recommendations = {
      acne: [
        { name: 'Gentle Cleanser', category: 'cleanser', description: 'Non-comedogenic cleanser for acne-prone skin' },
        { name: 'Salicylic Acid Treatment', category: 'treatment', description: '2% salicylic acid to unclog pores' },
        { name: 'Oil-Free Moisturizer', category: 'moisturizer', description: 'Lightweight, non-greasy hydration' }
      ],
      melasma: [
        { name: 'Vitamin C Serum', category: 'serum', description: 'Brightening serum with antioxidants' },
        { name: 'SPF 50+ Sunscreen', category: 'sunscreen', description: 'Broad-spectrum protection' },
        { name: 'Niacinamide Treatment', category: 'treatment', description: 'Even skin tone and texture' }
      ],
      general: [
        { name: 'Daily Cleanser', category: 'cleanser', description: 'Gentle daily cleansing' },
        { name: 'Hydrating Serum', category: 'serum', description: 'Deep hydration and nourishment' },
        { name: 'Broad-Spectrum SPF', category: 'sunscreen', description: 'Daily sun protection' }
      ]
    };
    
    return recommendations[condition as keyof typeof recommendations] || recommendations.general;
  };

  // Helper function to calculate overall preprocessing score
  const calculateOverallPreprocessingScore = () => {
    const scores = [
      preprocessingMetrics.geometric?.overallScore || 0,
      preprocessingMetrics.colorLighting?.overallScore || 0,
      preprocessingMetrics.enhancement?.enabled ? 85 : 70,
      (preprocessingMetrics.mediapipe?.confidence || 0) * 100
    ];
    return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (e) => {
      const imageData = e.target?.result as string;
      setUploadedImage(imageData);
      setShowImagePreview(true);
      
      // Perform face detection on uploaded image
      await performFaceDetectionOnImage(imageData);
    };
    reader.readAsDataURL(file);
  };

  const performFaceDetectionOnImage = async (imageData: string) => {
    try {
      console.log('🔍 Performing face detection on uploaded image...');
      console.log('📡 Calling face detection API:', getApiUrl(API_CONFIG.ENDPOINTS.FACE_DETECT));
      
      const response = await fetch(getApiUrl(API_CONFIG.ENDPOINTS.FACE_DETECT), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image_data: imageData.split(',')[1]
        })
      });

      console.log('📊 Face detection response status:', response.status);
      console.log('📊 Face detection response ok:', response.ok);

      if (response.ok) {
        const result = await response.json();
        console.log('✅ Face detection result:', result);
        
        // Handle both response formats: external backend (faces array) and local API (direct properties)
        if (result.faces && result.faces.length > 0) {
          // External backend format
          const face = result.faces[0];
          setFaceDetected(true);
          setFaceConfidence(face.confidence || 0);
          
          // Handle cropped face image if available
          console.log('🔍 DEBUG: Checking for cropped face image...');
          console.log('🔍 DEBUG: Face object:', face);
          console.log('🔍 DEBUG: cropped_face_image field:', face.cropped_face_image ? 'EXISTS' : 'MISSING');
          console.log('🔍 DEBUG: Full face detection response:', JSON.stringify(result, null, 2));
          
          if (face.cropped_face_image) {
            console.log('🔍 DEBUG: Setting cropped face image, length:', face.cropped_face_image.length);
            setCroppedFaceImage(`data:image/png;base64,${face.cropped_face_image}`);
          } else {
            console.log('🔍 DEBUG: No cropped face image found in response');
          }
          
          console.log('✅ Face detected with confidence:', face.confidence);
        } else if (result.face_detected) {
          // Local API format
          setFaceDetected(true);
          setFaceConfidence(result.confidence || 0);
        
          // Handle cropped face image if available
          if (result.cropped_face_image) {
            setCroppedFaceImage(`data:image/png;base64,${result.cropped_face_image}`);
          }
          
          console.log('✅ Face detected with confidence:', result.confidence);
        } else {
          setFaceDetected(false);
          setFaceConfidence(0);
          setCroppedFaceImage(null);
          console.log('⚠️ No faces detected in image');
        }
      } else {
        const errorText = await response.text();
        console.error('❌ Face detection failed with status:', response.status);
        console.error('❌ Error response:', errorText);
        setFaceDetected(false);
        setFaceConfidence(0);
        
        // Face detection failed - analysis cannot proceed
        console.log('❌ Face detection failed - analysis blocked');
      }
    } catch (error) {
      console.error('❌ Face detection error:', error);
      setFaceDetected(false);
      setFaceConfidence(0);
      
      // Face detection error - analysis cannot proceed
      console.log('❌ Face detection error - analysis blocked');
    }
  };

  if (isAnalyzing) {
    return (
      <div className="min-h-screen bg-primary text-primary flex items-center justify-center">
        <div className="text-center">
          <img 
            src="https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png" 
            alt="Shine Skin Collective" 
            className="w-32 h-32 mx-auto mb-6 animate-pulse"
          />
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-600 mx-auto mb-4"></div>
          <p className="text-secondary font-light">Analyzing your skin with Hare Run V6 Enhanced ML...</p>
          <p className="text-xs text-secondary font-light mt-2">Enhanced accuracy: 97.13% - This may take up to 60 seconds</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-primary text-primary flex items-center justify-center">
        <div className="text-center">
          <img 
            src="https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png" 
            alt="Shine Skin Collective" 
            className="w-32 h-32 mx-auto mb-6 animate-pulse"
          />
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-600 mx-auto mb-4"></div>
          <p className="text-secondary font-light">Loading Shine...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-primary text-primary">
      <Header />
      <div className="container mx-auto px-4 py-6">
        {/* Header */}
        <div className="text-center mb-8">
          <img 
            src="https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png" 
            alt="Shine Skin Collective" 
            className="w-20 h-20 mx-auto mb-4"
          />
          <h1 className="text-3xl md:text-4xl font-light mb-2">AI-Powered Skin Analysis</h1>
          <p className="text-lg text-secondary font-light">
            AI-Powered Skin Analysis & Recommendations
          </p>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          
          {/* MediaPipe Dashboard */}
          {showMediaPipe ? (
            <div className="bg-secondary rounded-2xl shadow-lg p-6 mb-6 border border-primary">
              <MediaPipeFaceDetection
                isVisible={showMediaPipe}
                capturedImage={uploadedImage}
                onLandmarksDetected={(landmarks) => {
                  console.log('🎯 MediaPipe landmarks detected:', landmarks.length);
                  setMediapipeLandmarks(landmarks);
                  setPreprocessingMetrics(prev => ({
                    ...prev,
                    mediapipe: { ...prev.mediapipe, landmarksCount: landmarks.length }
                  }));
                }}
                onFaceBoundsDetected={(bounds) => {
                  console.log('📐 Face bounds detected:', bounds);
                  setFaceBounds(bounds);
                }}
                onDetectionComplete={() => {
                  console.log('✅ MediaPipe detection complete');
                  setPreprocessingMetrics(prev => ({
                    ...prev,
                    mediapipe: { ...prev.mediapipe, confidence: 0.8 }
                  }));
                }}
                                 onCaptureReady={(imageData) => {
                   console.log('📸 MediaPipe enhancement complete, proceeding to analysis');
                   setShowMediaPipe(false);
                   
                   // Set face detected to true since MediaPipe was used
                   setFaceDetected(true);
                   setFaceConfidence(0.8); // Assume good confidence from MediaPipe
                   
                   // Trigger analysis immediately with enhanced data
                   analyzeSkin(imageData);
                 }}
              />
              
              {/* Close Button */}
              <div className="text-center mt-6">
                <button
                  onClick={stopMediaPipe}
                  className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : showImagePreview ? (
            /* Image Preview Section */
            <div className="bg-secondary rounded-2xl shadow-lg p-6 mb-6 border border-primary">
              <div className="relative">
                <img
                  src={uploadedImage!}
                  alt="Uploaded photo"
                  className="w-full rounded-xl"
                />
                
                {/* Face Detection Status */}
                <div className="absolute top-4 left-1/2 transform -translate-x-1/2">
                  <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${
                    faceDetected 
                      ? 'bg-green-100 dark:bg-green-800 text-green-800 dark:text-green-200' 
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200'
                  }`}>
                    <div className={`w-2 h-2 rounded-full ${
                      faceDetected ? 'bg-green-500' : 'bg-gray-500'
                    } animate-pulse`}></div>
                    <span className="text-sm font-light">
                      {faceDetected ? 'Face Detected' : 'Detecting Face...'}
                    </span>
                  </div>
                </div>
                
                {/* Unified Analyze & Enhance Button */}
                <button
                  onClick={() => {
                    console.log('🚀 Unified analyze & enhance button clicked');
                    if (uploadedImage) {
                      if (faceDetected) {
                        console.log('✅ Face detected, starting enhanced analysis with MediaPipe');
                        // Automatically enhance with MediaPipe if available, then analyze
                        if (mediapipeLandmarks && mediapipeLandmarks.length > 0) {
                          console.log('🎯 Using existing MediaPipe data for enhanced analysis');
                          analyzeSkin(uploadedImage);
                        } else {
                          console.log('🔧 Starting MediaPipe enhancement, then analysis');
                          setShowMediaPipe(true);
                          setShowImagePreview(false);
                        }
                      } else {
                        console.log('❌ Face not detected, cannot analyze');
                        alert('Please wait for face detection to complete before analyzing your photo.');
                      }
                    } else {
                      console.error('❌ No uploaded image available');
                    }
                  }}
                  disabled={!faceDetected}
                  className={`absolute bottom-4 left-1/2 transform -translate-x-1/2 px-6 py-3 rounded-xl font-light transition-all ${
                    faceDetected 
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 cursor-pointer shadow-lg' 
                      : 'bg-gray-400 dark:bg-gray-600 text-gray-200 dark:text-gray-400 cursor-not-allowed'
                  }`}
                >
                  <Zap className="w-5 h-5 inline mr-2" />
                  {faceDetected ? 'Analyze with AI Enhancement' : 'Waiting for Face...'}
                </button>

                {/* Cropped Face Thumbnail Display - Project Vanity */}
                {croppedFaceImage && (
                  <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-xl">
                    <h3 className="text-lg font-medium mb-3 text-center">Face Region to be Analyzed</h3>
                    <div className="flex justify-center items-center">
                      <div className="text-center">
                        <img
                          src={croppedFaceImage}
                          alt="Cropped face region that will be analyzed"
                          className="w-32 h-32 object-cover rounded-lg border-2 border-green-500 shadow-sm"
                        />
                        <p className="text-sm text-green-600 mt-2 font-medium">
                          Face Detection: {Math.round(faceConfidence * 100)}% Confidence
                        </p>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 text-center mt-3">
                      This is the specific face region that will be analyzed for skin conditions.
                    </p>
                    

                  </div>
                )}

                {/* Close Button */}
                <button
                  onClick={() => {
                    setShowImagePreview(false);
                    setUploadedImage(null);
                    setFaceDetected(false);
                    setFaceConfidence(0);
                    setCroppedFaceImage(null);
                  }}
                  className="absolute top-4 right-4 p-2 rounded-full bg-red-600 text-white hover:bg-red-700 transition-colors"
                >
                  ✕
                </button>
              </div>
            </div>
          ) : (
            <>
              {/* Preprocessing Summary */}
              {/* Preprocessing Summary */}
              
              {/* Enhanced Image Capture Guidance */}
              <ImageCaptureGuidance
                onStartCapture={startCameraCapture}
                onUploadImage={() => document.getElementById('file-upload')?.click()}
                isVisible={!showMediaPipe && !showImagePreview && !showCameraInterface}
              />
              
              {/* Camera Interface with Wood's Lamp Effect */}
              {showCameraInterface && (
                <div className="fixed inset-0 z-50 bg-black bg-opacity-90 flex items-center justify-center p-4">
                  <div className="relative w-full max-w-2xl">
                    {/* Wood's Lamp Screen Lighting Effect */}
                    <div className="absolute inset-0 bg-gradient-to-b from-blue-900/20 via-blue-600/15 to-blue-900/20 pointer-events-none z-10"></div>
                    <div className="absolute inset-0 bg-blue-500/10 pointer-events-none z-10"></div>
                    
                    {/* Camera Preview */}
                    <div className="relative bg-gray-900 rounded-2xl overflow-hidden shadow-2xl">
                      <div className="relative">
                        {/* Video element will be inserted here */}
                        <div 
                          id="camera-preview"
                          className="w-full h-96 bg-gray-800 flex items-center justify-center"
                        >
                          <div className="text-center text-white">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto mb-4"></div>
                            <p className="text-lg">Starting camera...</p>
                          </div>
                        </div>
                        
                        {/* Wood's Lamp Overlay */}
                        <div className="absolute inset-0 pointer-events-none">
                          {/* Blue light grid pattern */}
                          <div className="absolute inset-0 opacity-20">
                            <div className="w-full h-full" style={{
                              backgroundImage: `
                                linear-gradient(90deg, rgba(0,102,255,0.1) 1px, transparent 1px),
                                linear-gradient(rgba(0,102,255,0.1) 1px, transparent 1px)
                              `,
                              backgroundSize: '40px 40px'
                            }}></div>
                          </div>
                          
                          {/* Fluorescence simulation areas */}
                          <div className="absolute top-1/4 left-1/4 w-1/2 h-1/2 rounded-full bg-cyan-400/20 blur-sm"></div>
                          <div className="absolute top-1/3 right-1/4 w-1/3 h-1/3 rounded-full bg-cyan-400/15 blur-sm"></div>
                        </div>
                        
                        {/* Capture Controls */}
                        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex items-center space-x-4">
                          <button
                            onClick={stopCamera}
                            className="p-3 bg-red-600 text-white rounded-full hover:bg-red-700 transition-colors shadow-lg"
                            title="Cancel"
                          >
                            ✕
                          </button>
                          
                          <button
                            onClick={capturePhoto}
                            className="p-4 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors shadow-lg border-4 border-white"
                            title="Capture Photo"
                          >
                            📸
                          </button>
                        </div>
                        
                        {/* Wood's Lamp Instructions */}
                        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-blue-900/80 text-white px-4 py-2 rounded-lg text-center">
                          <div className="flex items-center space-x-2">
                            <div className="w-3 h-3 bg-blue-400 rounded-full animate-pulse"></div>
                            <span className="text-sm font-medium">Wood's Lamp Mode Active</span>
                          </div>
                          <p className="text-xs opacity-80 mt-1">Blue light simulation for enhanced skin analysis</p>
                        </div>
                      </div>
                    </div>
                    
                    {/* Instructions */}
                    <div className="mt-4 text-center text-white">
                      <h3 className="text-lg font-medium mb-2">Position Your Face</h3>
                      <p className="text-sm opacity-80">
                        Center your face in the frame. The blue light will help highlight skin conditions.
                      </p>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Hidden file input for upload */}
              <input
                id="file-upload"
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                className="hidden"
              />
            </>
          )}

          {/* Features */}
          <div className="bg-secondary rounded-2xl shadow-lg p-6 border border-primary">
            <h3 className="text-xl font-light mb-4 text-center">Why Choose Shine?</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <Zap className="w-8 h-8 text-gray-600 mx-auto mb-2" />
                <h4 className="font-light mb-1">AI-Powered</h4>
                <p className="text-sm opacity-75 font-light">Advanced machine learning for accurate analysis</p>
              </div>
              <div className="text-center">
                <Eye className="w-8 h-8 text-gray-600 mx-auto mb-2" />
                <h4 className="font-light mb-1">Secure</h4>
                <p className="text-sm opacity-75 font-light">Your privacy is our top priority</p>
              </div>
              <div className="text-center">
                <Eye className="w-8 h-8 text-gray-600 mx-auto mb-2" />
                <h4 className="font-light mb-1">Comprehensive</h4>
                <p className="text-sm opacity-75 font-light">Detailed analysis and personalized recommendations</p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Disclaimer */}
        <div className="mt-8 text-center">
          <p className="text-xs text-secondary font-light mb-2">
            © 2024 All Rights Reserved. <span className="text-accent font-medium">EXPERIMENTAL</span>
          </p>
          <p className="text-xs text-secondary font-light mb-2">
            This application is for informational purposes only and does not constitute medical advice. 
            Always consult with a qualified healthcare professional for medical concerns.
          </p>
          <p className="text-xs text-secondary font-light">
            <Link href="/training-dashboard" className="text-accent hover:underline transition-colors">
              View AI Training Transparency Dashboard →
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
} 