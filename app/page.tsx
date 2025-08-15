'use client';

import { useState, useRef, useEffect } from 'react';
import { Camera, Upload, ArrowRight, Zap, Eye } from 'lucide-react';
import { Header } from '@/components/header';
import { getApiUrl, API_CONFIG } from '@/lib/config';
import Link from 'next/link';

export default function HomePage() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const [isCameraLoading, setIsCameraLoading] = useState(false);
  const [faceDetected, setFaceDetected] = useState(false);
  const [faceConfidence, setFaceConfidence] = useState(0);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [showImagePreview, setShowImagePreview] = useState(false);
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    // Set loading to false immediately for testing
    setIsLoading(false);
  }, []);

  const startCamera = async () => {
    try {
      console.log('Starting camera...');
      setIsCameraLoading(true);
      setShowCamera(true);
      
      // Use proper camera constraints that work across browsers
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          facingMode: 'user',
          width: { ideal: 640, min: 320, max: 1280 },
          height: { ideal: 480, min: 240, max: 720 }
        } 
      });
      
      console.log('Camera stream obtained:', stream);
      console.log('Stream tracks:', stream.getTracks().map(t => ({ kind: t.kind, enabled: t.enabled, readyState: t.readyState })));
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setIsCameraLoading(false);
        
        // Wait for video to load and play
        videoRef.current.onloadedmetadata = () => {
          console.log('Video metadata loaded');
          console.log('Video dimensions:', videoRef.current?.videoWidth, 'x', videoRef.current?.videoHeight);
          
          // Force play after metadata is loaded
          videoRef.current?.play().then(() => {
            console.log('Video play successful');
            setIsVideoPlaying(true);
          }).catch(e => {
            console.error('Video play error:', e);
            alert('Camera started but video playback failed. Please check camera permissions.');
          });
        };
      } else {
        console.error('Video ref is null');
        setIsCameraLoading(false);
      }
    } catch (error: any) {
      console.error('Error accessing camera:', error);
      setIsCameraLoading(false);
      setShowCamera(false);
      
      // More specific error messages
      if (error.name === 'NotAllowedError') {
        alert('Camera access denied. Please allow camera permissions and try again.');
      } else if (error.name === 'NotFoundError') {
        alert('No camera found. Please check if your device has a camera.');
      } else if (error.name === 'NotReadableError') {
        alert('Camera is in use by another application. Please close other apps using the camera.');
      } else {
        alert(`Camera error: ${error.message}. Please check camera permissions and try again.`);
      }
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setShowCamera(false);
    setShowImagePreview(false);
    setUploadedImage(null);
    setFaceDetected(false);
    setFaceConfidence(0);
    setIsVideoPlaying(false);
  };

  const performLiveFaceDetection = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    if (!ctx) return;

    // Check if video is ready
    if (video.videoWidth === 0 || video.videoHeight === 0) {
      console.log('Video not ready yet, retrying...');
      setTimeout(performLiveFaceDetection, 500);
      return;
    }

    // Set canvas size to match video display size
    const videoElement = video;
    const videoRect = videoElement.getBoundingClientRect();
    canvas.width = videoRect.width;
    canvas.height = videoRect.height;

    // Clear the canvas first
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    console.log('Canvas size set to:', canvas.width, 'x', canvas.height);
    console.log('Video element size:', videoRect.width, 'x', videoRect.height);
    console.log('Video resolution:', video.videoWidth, 'x', video.videoHeight);

    // Convert video frame to base64 for face detection
    const tempCanvas = document.createElement('canvas');
    const tempCtx = tempCanvas.getContext('2d');
    if (tempCtx) {
      tempCanvas.width = video.videoWidth;
      tempCanvas.height = video.videoHeight;
      tempCtx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);
      const imageData = tempCanvas.toDataURL('image/jpeg', 0.8);

             try {
         const response = await fetch(getApiUrl(API_CONFIG.ENDPOINTS.FACE_DETECT), {
           method: 'POST',
           headers: {
             'Content-Type': 'application/json',
           },
                     body: JSON.stringify({
            image: imageData.split(',')[1]
          })
         });

        if (response.ok) {
          const result = await response.json();
          console.log('Live face detection result:', result);
          
          if (result.faces && result.faces.length > 0) {
            const face = result.faces[0];
            setFaceDetected(true);
            setFaceConfidence(face.confidence || 0);
            
            console.log('FACE DETECTED! Face data:', face);
            console.log('Face bounds:', face.bounds);
            console.log('Face confidence:', face.confidence);
            
            // Draw face detection overlay
            const { x, y, width, height } = face.bounds;
            
            // Scale coordinates to match canvas display size
            const videoElement = videoRef.current;
            if (videoElement) {
              const videoRect = videoElement.getBoundingClientRect();
              const scaleX = videoRect.width / videoElement.videoWidth;
              const scaleY = videoRect.height / videoElement.videoHeight;
              
              const scaledX = x * scaleX;
              const scaledY = y * scaleY;
              const scaledWidth = width * scaleX;
              const scaledHeight = height * scaleY;
              
              console.log('Drawing matrix overlay over face at:', { scaledX, scaledY, scaledWidth, scaledHeight });
              
              // Check if coordinates are reasonable
              if (scaledX < 0 || scaledY < 0 || scaledWidth <= 0 || scaledHeight <= 0) {
                console.log('Invalid coordinates, drawing fallback rectangle');
                ctx.strokeStyle = '#00FF00';
                ctx.lineWidth = 3;
                ctx.strokeRect(100, 100, 200, 200);
                return;
              }
              
              // Draw an oval around the detected face
              ctx.strokeStyle = '#00FF00';
              ctx.lineWidth = 3;
              
              // Calculate center and radius for oval
              const centerX = scaledX + scaledWidth/2;
              const centerY = scaledY + scaledHeight/2;
              const radiusX = scaledWidth/2;
              const radiusY = scaledHeight/2;
              
              // Draw oval
              ctx.beginPath();
              ctx.ellipse(centerX, centerY, radiusX, radiusY, 0, 0, 2 * Math.PI);
              ctx.stroke();
              
              // Draw corner markers for better visibility
              const markerSize = 15;
              ctx.strokeStyle = '#00FF00';
              ctx.lineWidth = 2;
              
              // Top-left corner
              ctx.beginPath();
              ctx.moveTo(scaledX, scaledY + markerSize);
              ctx.lineTo(scaledX, scaledY);
              ctx.lineTo(scaledX + markerSize, scaledY);
              ctx.stroke();
              
              // Top-right corner
              ctx.beginPath();
              ctx.moveTo(scaledX + scaledWidth - markerSize, scaledY);
              ctx.lineTo(scaledX + scaledWidth, scaledY);
              ctx.lineTo(scaledX + scaledWidth, scaledY + markerSize);
              ctx.stroke();
              
              // Bottom-left corner
              ctx.beginPath();
              ctx.moveTo(scaledX, scaledY + scaledHeight - markerSize);
              ctx.lineTo(scaledX, scaledY + scaledHeight);
              ctx.lineTo(scaledX + markerSize, scaledY + scaledHeight);
              ctx.stroke();
              
              // Bottom-right corner
              ctx.beginPath();
              ctx.moveTo(scaledX + scaledWidth - markerSize, scaledY + scaledHeight);
              ctx.lineTo(scaledX + scaledWidth, scaledY + scaledHeight);
              ctx.lineTo(scaledX + scaledWidth, scaledY + scaledHeight - markerSize);
              ctx.stroke();
              
              // Draw confidence text with background
              const confidenceText = `${Math.round(face.confidence * 100)}%`;
              const textWidth = ctx.measureText(confidenceText).width;
              
              // Draw background for text
              ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
              ctx.fillRect(scaledX, scaledY - 25, textWidth + 10, 20);
              
              // Draw confidence text
              ctx.fillStyle = '#00FF00';
              ctx.font = 'bold 14px Arial';
              ctx.fillText(confidenceText, scaledX + 5, scaledY - 10);
              
              console.log('Drew simple overlay over detected face');
            }
            
            console.log('Face detected with confidence:', face.confidence);
          } else {
            setFaceDetected(false);
            setFaceConfidence(0);
            console.log('No faces detected in live mode');
            
            // Draw a test oval in the center to verify oval drawing works
            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;
            const radiusX = 100;
            const radiusY = 150;
            
            ctx.strokeStyle = '#00FF00';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.ellipse(centerX, centerY, radiusX, radiusY, 0, 0, 2 * Math.PI);
            ctx.stroke();
            
            console.log('Drew test oval in center - no face detected');
          }
        }
      } catch (error) {
        console.error('Live face detection error:', error);
      }
    }

    // Continue detection
    if (showCamera) {
      setTimeout(performLiveFaceDetection, 1000);
    }
  };

  const performFaceDetectionOnImage = async (imageData: string) => {
         try {
       console.log('Performing face detection on uploaded image...');
       const response = await fetch(getApiUrl(API_CONFIG.ENDPOINTS.FACE_DETECT), {
         method: 'POST',
         headers: {
           'Content-Type': 'application/json',
         },
         body: JSON.stringify({
           image_data: imageData.split(',')[1]
         })
       });

      if (response.ok) {
        const result = await response.json();
        console.log('Face detection result:', result);
        
        if (result.faces && result.faces.length > 0) {
          const face = result.faces[0];
          setFaceDetected(true);
          setFaceConfidence(face.confidence || 0);
          console.log('Face detected with confidence:', face.confidence);
        } else {
          setFaceDetected(false);
          setFaceConfidence(0);
          console.log('No faces detected');
        }
      } else {
        console.error('Face detection failed:', response.status);
        setFaceDetected(false);
        setFaceConfidence(0);
      }
    } catch (error) {
      console.error('Face detection error:', error);
      setFaceDetected(false);
      setFaceConfidence(0);
    }
  };

  const capturePhoto = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    console.log('📸 Capturing photo...');

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    if (!ctx) return;

    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame to canvas
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert canvas to base64
    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    console.log('📸 Photo captured, image data length:', imageData.length);

    // Stop camera
    stopCamera();

    // Start analysis
    console.log('🔍 Starting analysis of captured photo...');
    await analyzeSkin(imageData);
  };

  const analyzeSkin = async (imageData: string) => {
    setIsAnalyzing(true);
    console.log('🔍 Starting enhanced Hare Run V6 skin analysis...');

    try {
          // Use the enhanced Hare Run V6 endpoint
    console.log('📡 Calling Hare Run V6 enhanced ML endpoint...');
              const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'https://api.shineskincollective.com'}/api/v6/skin/analyze-hare-run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image: imageData.split(',')[1]
        })
      });

      console.log('📊 Response status:', response.status);
      console.log('📊 Response ok:', response.ok);

      if (response.ok) {
        const result = await response.json();
        console.log('✅ Analysis successful:', result);
        
        // Add Hare Run V6 enhanced ML metadata
        result.enhanced_ml = true;
        result.model_version = result.model_info?.version || 'Hare_Run_V6_Facial_v1.0';
        result.accuracy = result.model_info?.accuracy || '97.13%';
        result.model_type = 'Enhanced_Facial_ML';
        
        // Store analysis data in sessionStorage instead of URL parameter
        sessionStorage.setItem('analysisResult', JSON.stringify(result));
        console.log('💾 Stored analysis result in sessionStorage');
        window.location.href = '/suggestions';
      } else {
        const errorText = await response.text();
        console.error('❌ Analysis failed with status:', response.status);
        console.error('❌ Error response:', errorText);
        throw new Error(`Fixed ML analysis failed: ${response.status} - ${errorText}`);
      }
    } catch (error) {
              console.error('❌ Fixed ML analysis error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      alert(`Fixed ML analysis failed: ${errorMessage}. Please try again.`);
      setIsAnalyzing(false);
    }
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
        <div className="max-w-2xl mx-auto">
          
          {/* Camera Section */}
          {showCamera ? (
            <div className="bg-secondary rounded-2xl shadow-lg p-6 mb-6 border border-primary">
              <div className="relative">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full rounded-xl"
                  onLoadedMetadata={() => {
                    console.log('Video loaded');
                    console.log('Video dimensions:', videoRef.current?.videoWidth, 'x', videoRef.current?.videoHeight);
                  }}
                  onPlaying={() => {
                    console.log('Video is playing');
                    setIsVideoPlaying(true);
                    // Start live face detection when video starts playing
                    setTimeout(performLiveFaceDetection, 1000);
                  }}
                  style={{ 
                    display: 'block', 
                    minHeight: '600px', 
                    objectFit: 'cover'
                  }}
                />
                <canvas
                  ref={canvasRef}
                  className="absolute top-0 left-0 w-full h-full pointer-events-none"
                  style={{ zIndex: 10 }}
                />
                
                {/* Video Not Displaying Fallback */}
                {(!isVideoPlaying || !videoRef.current?.srcObject) && !isCameraLoading && (
                  <div className="absolute inset-0 flex items-center justify-center bg-gray-800 bg-opacity-75 rounded-xl">
                    <div className="text-center text-white">
                      <Camera className="w-12 h-12 mx-auto mb-2" />
                      <p className="text-sm">Camera not displaying</p>
                      <p className="text-xs opacity-75">Please check camera permissions</p>
                    </div>
                  </div>
                )}
                
                {/* Camera Loading Message */}
                {isCameraLoading && (
                  <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-50 rounded-xl">
                    <div className="text-center text-white">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-2"></div>
                      <p className="text-sm">Loading camera...</p>
                    </div>
                  </div>
                )}
                
                {/* Camera Instructions */}
                <div className="absolute top-4 left-4">
                  <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200">
                    <Camera className="w-4 h-4" />
                    <span className="text-sm font-light">
                      Position your face and tap Capture
                    </span>
                  </div>
                </div>
                
                {/* Camera Status */}
                <div className="absolute top-4 right-16">
                  <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200">
                    <Camera className="w-4 h-4" />
                    <span className="text-sm font-light">
                      Camera Active
                    </span>
                  </div>
                </div>
                
                {/* Face Detection Status */}
                <div className="absolute top-4 left-1/2 transform -translate-x-1/2">
                  <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${
                    faceDetected 
                      ? 'bg-green-100 dark:bg-green-800 text-green-800 dark:text-green-200' 
                      : 'bg-red-100 dark:bg-red-800 text-red-800 dark:text-red-200'
                  }`}>
                    <div className={`w-2 h-2 rounded-full ${
                      faceDetected ? 'bg-green-500' : 'bg-red-500'
                    } animate-pulse`}></div>
                    <span className="text-sm font-light">
                      {faceDetected ? 'Face Detected' : 'No Face'}
                    </span>
                  </div>
                </div>

                {/* Capture Button */}
                <button
                  onClick={capturePhoto}
                  className="absolute bottom-4 left-1/2 transform -translate-x-1/2 px-6 py-3 rounded-xl font-light transition-all bg-gray-900 dark:bg-white text-white dark:text-black hover:bg-gray-800 dark:hover:bg-gray-100"
                >
                  <Camera className="w-5 h-5 inline mr-2" />
                  Capture Photo
                </button>

                {/* Close Camera Button */}
                <button
                  onClick={stopCamera}
                  className="absolute top-4 right-4 p-2 rounded-full bg-red-600 text-white hover:bg-red-700 transition-colors"
                >
                  ✕
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
                
                                 {/* Analyze Button */}
                 <button
                   onClick={() => {
                     console.log('🔍 Analyze button clicked for uploaded image');
                     uploadedImage && analyzeSkin(uploadedImage);
                   }}
                   className="absolute bottom-4 left-1/2 transform -translate-x-1/2 px-6 py-3 rounded-xl font-light transition-all bg-gray-900 dark:bg-white text-white dark:text-black hover:bg-gray-800 dark:hover:bg-gray-100"
                 >
                   <ArrowRight className="w-5 h-5 inline mr-2" />
                   Analyze Photo
                 </button>

                {/* Close Button */}
                <button
                  onClick={() => {
                    setShowImagePreview(false);
                    setUploadedImage(null);
                    setFaceDetected(false);
                    setFaceConfidence(0);
                  }}
                  className="absolute top-4 right-4 p-2 rounded-full bg-red-600 text-white hover:bg-red-700 transition-colors"
                >
                  ✕
                </button>
              </div>
            </div>
          ) : (
            /* Upload Section */
            <div className="bg-secondary rounded-2xl shadow-lg p-8 mb-6 border border-primary">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-light mb-2">Start Your Skin Analysis</h2>
                <p className="text-secondary font-light">
                  Get personalized skincare recommendations based on AI analysis
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Camera Option */}
                <button
                  onClick={startCamera}
                  className="flex flex-col items-center p-6 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl hover:border-gray-400 dark:hover:border-gray-500 transition-colors group"
                >
                  <Camera className="w-12 h-12 text-gray-600 mb-4 group-hover:scale-110 transition-transform" />
                  <h3 className="font-light mb-2">Use Camera</h3>
                  <p className="text-sm opacity-75 text-center font-light">
                    Take a photo with your device camera
                  </p>
                </button>

                {/* Upload Option */}
                <label className="flex flex-col items-center p-6 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl hover:border-gray-400 dark:hover:border-gray-500 transition-colors group cursor-pointer">
                  <Upload className="w-12 h-12 text-gray-600 mb-4 group-hover:scale-110 transition-transform" />
                  <h3 className="font-light mb-2">Upload Photo</h3>
                  <p className="text-sm opacity-75 text-center font-light">
                    Upload an existing photo from your device
                  </p>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </label>
              </div>
            </div>
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