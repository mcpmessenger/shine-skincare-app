'use client';

import { useState, useRef, useEffect } from 'react';
import { Camera, Upload, ArrowRight, Zap, Eye } from 'lucide-react';
import { Header } from '@/components/header';

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
    // Set loading to false after initialization
    setTimeout(() => {
      setIsLoading(false);
    }, 1000); // Show logo for 1 second
  }, []);

  const startCamera = async () => {
    try {
      console.log('Starting camera...');
      setIsCameraLoading(true);
      setShowCamera(true); // Set this immediately to show the camera container
      
             const stream = await navigator.mediaDevices.getUserMedia({ 
         video: { 
           facingMode: 'user',
           width: { ideal: 720 },
           height: { ideal: 1280 }
         } 
       });
      
      console.log('Camera stream obtained:', stream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setIsCameraLoading(false);
        
                 // Wait for video to load
         videoRef.current.onloadedmetadata = () => {
           console.log('Video metadata loaded');
         };
        
        // Force video to play
        videoRef.current.play().catch(e => console.error('Video play error:', e));
      } else {
        console.error('Video ref is null');
        setIsCameraLoading(false);
      }
    } catch (error) {
      console.error('Error accessing camera:', error);
      setIsCameraLoading(false);
      setShowCamera(false); // Hide camera if there's an error
      alert('Unable to access camera. Please check permissions.');
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

    // Set canvas size to match video display size (not video resolution)
    const videoElement = video;
    const videoRect = videoElement.getBoundingClientRect();
    canvas.width = videoRect.width;
    canvas.height = videoRect.height;

    // Clear the canvas first
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    console.log('Canvas size set to:', canvas.width, 'x', canvas.height);
    console.log('Video element size:', videoRect.width, 'x', videoRect.height);
    console.log('Video resolution:', video.videoWidth, 'x', video.videoHeight);

    // Canvas is working - no need for test rectangle anymore

    // Convert video frame to base64 for face detection
    const tempCanvas = document.createElement('canvas');
    const tempCtx = tempCanvas.getContext('2d');
    if (tempCtx) {
      tempCanvas.width = video.videoWidth;
      tempCanvas.height = video.videoHeight;
      tempCtx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);
      const imageData = tempCanvas.toDataURL('image/jpeg', 0.8);

      try {
        const response = await fetch('http://localhost:5000/api/v3/face/detect', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            image_data: imageData.split(',')[1] // Remove data:image/jpeg;base64, prefix
          })
        });

                 if (response.ok) {
           const result = await response.json();
           console.log('Live face detection result:', result);
           console.log('Result structure:', JSON.stringify(result, null, 2));
          
          // Allow zero confidence - if faces array exists and has any elements, consider it detected
          if (result.faces && result.faces.length > 0) {
            const face = result.faces[0];
            setFaceDetected(true);
            setFaceConfidence(face.confidence || 0);
            
            console.log('FACE DETECTED! Face data:', face);
            console.log('Face bounds:', face.bounds);
            console.log('Face confidence:', face.confidence);
            
            // Draw face detection overlay on the main canvas
            console.log('Drawing overlay for face:', face);
            console.log('Canvas size:', canvas.width, 'x', canvas.height);
            console.log('Face bounds:', face.bounds);
            // Draw green matrix overlay over the detected face
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
              console.log('Canvas dimensions:', canvas.width, 'x', canvas.height);
              
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
      const response = await fetch('http://localhost:5000/api/v3/face/detect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image_data: imageData.split(',')[1] // Remove data:image/jpeg;base64, prefix
        })
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Face detection result:', result);
        
        // Allow zero confidence - if faces array exists and has any elements, consider it detected
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

  const drawFaceDetectionOverlay = (ctx: CanvasRenderingContext2D, face: any) => {
    const { x, y, width, height } = face.bounds;
    
    console.log('Original face bounds:', { x, y, width, height });
    console.log('Canvas size:', ctx.canvas.width, 'x', ctx.canvas.height);
    
    // Use a simpler approach - draw a matrix overlay in the center of the canvas
    const centerX = ctx.canvas.width / 2;
    const centerY = ctx.canvas.height / 2;
    const overlaySize = Math.min(ctx.canvas.width, ctx.canvas.height) * 0.6;
    
    console.log('Drawing overlay at center:', { centerX, centerY, overlaySize });
    
    // Draw matrix-style grid overlay
    ctx.strokeStyle = '#00FF00'; // Bright green for matrix effect
    ctx.lineWidth = 3;
    
    // Draw vertical lines
    for (let i = 0; i <= 4; i++) {
      const lineX = centerX - overlaySize/2 + (overlaySize * i / 4);
      ctx.beginPath();
      ctx.moveTo(lineX, centerY - overlaySize/2);
      ctx.lineTo(lineX, centerY + overlaySize/2);
      ctx.stroke();
    }
    
    // Draw horizontal lines
    for (let i = 0; i <= 4; i++) {
      const lineY = centerY - overlaySize/2 + (overlaySize * i / 4);
      ctx.beginPath();
      ctx.moveTo(centerX - overlaySize/2, lineY);
      ctx.lineTo(centerX + overlaySize/2, lineY);
      ctx.stroke();
    }
    
    // Draw corner markers
    ctx.strokeStyle = '#00FF00';
    ctx.lineWidth = 3;
    const markerSize = 20;
    
    // Top-left corner
    ctx.beginPath();
    ctx.moveTo(centerX - overlaySize/2, centerY - overlaySize/2 + markerSize);
    ctx.lineTo(centerX - overlaySize/2, centerY - overlaySize/2);
    ctx.lineTo(centerX - overlaySize/2 + markerSize, centerY - overlaySize/2);
    ctx.stroke();
    
    // Top-right corner
    ctx.beginPath();
    ctx.moveTo(centerX + overlaySize/2 - markerSize, centerY - overlaySize/2);
    ctx.lineTo(centerX + overlaySize/2, centerY - overlaySize/2);
    ctx.lineTo(centerX + overlaySize/2, centerY - overlaySize/2 + markerSize);
    ctx.stroke();
    
    // Bottom-left corner
    ctx.beginPath();
    ctx.moveTo(centerX - overlaySize/2, centerY + overlaySize/2 - markerSize);
    ctx.lineTo(centerX - overlaySize/2, centerY + overlaySize/2);
    ctx.lineTo(centerX - overlaySize/2 + markerSize, centerY + overlaySize/2);
    ctx.stroke();
    
    // Bottom-right corner
    ctx.beginPath();
    ctx.moveTo(centerX + overlaySize/2 - markerSize, centerY + overlaySize/2);
    ctx.lineTo(centerX + overlaySize/2, centerY + overlaySize/2);
    ctx.lineTo(centerX + overlaySize/2, centerY + overlaySize/2 - markerSize);
    ctx.stroke();
    
    // Draw face detection circle
    ctx.strokeStyle = '#00FF00';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(centerX, centerY, overlaySize/2, 0, 2 * Math.PI);
    ctx.stroke();
    
    // Draw confidence text with glowing effect
    const confidenceText = `${Math.round(faceConfidence * 100)}%`;
    const textWidth = ctx.measureText(confidenceText).width;
    
    // Draw glow effect
    ctx.shadowColor = '#00FF00';
    ctx.shadowBlur = 10;
    ctx.fillStyle = '#00FF00';
    ctx.font = 'bold 16px Arial';
    ctx.fillText(confidenceText, centerX - textWidth/2, centerY - overlaySize/2 - 10);
    
    // Reset shadow
    ctx.shadowBlur = 0;
    
    // Draw status text
    const statusText = 'FACE DETECTED';
    const statusWidth = ctx.measureText(statusText).width;
    
    // Draw background for status
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(centerX - statusWidth/2 - 5, centerY - overlaySize/2 - 40, statusWidth + 10, 20);
    
    // Draw status text
    ctx.fillStyle = '#00FF00';
    ctx.font = 'bold 12px Arial';
    ctx.fillText(statusText, centerX - statusWidth/2, centerY - overlaySize/2 - 25);
  };

  const capturePhoto = async () => {
    if (!videoRef.current || !canvasRef.current) return;

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

    // Stop camera
    stopCamera();

    // Start analysis (face detection will be performed during analysis)
    await analyzeSkin(imageData);
  };

  const analyzeSkin = async (imageData: string) => {
    setIsAnalyzing(true);

    try {
      const response = await fetch('http://localhost:5000/api/v3/skin/analyze-real', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image_data: imageData.split(',')[1], // Remove data:image/jpeg;base64, prefix
          user_demographics: {
            age: '25-35',
            ethnicity: 'caucasian',
            gender: 'female',
            fitzpatrick_type: '3'
          }
        })
      });

      if (response.ok) {
        const result = await response.json();
        
        // Navigate to results page with analysis data
        const analysisParam = encodeURIComponent(JSON.stringify(result));
        window.location.href = `/suggestions?analysis=${analysisParam}`;
      } else {
        throw new Error('Analysis failed');
      }
    } catch (error) {
      console.error('Analysis error:', error);
      alert('Analysis failed. Please try again.');
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
            <p className="text-secondary font-light">Analyzing your skin...</p>
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
                   onLoadedMetadata={() => console.log('Video loaded')}
                   onError={(e) => console.error('Video error:', e)}
                   onCanPlay={() => console.log('Video can play')}
                   onPlaying={() => {
                     console.log('Video is playing');
                     setIsVideoPlaying(true);
                     // Start live face detection when video starts playing
                     setTimeout(performLiveFaceDetection, 1000);
                   }}
                   onPause={() => setIsVideoPlaying(false)}
                   style={{ display: 'block', minHeight: '600px', objectFit: 'cover' }}
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
                   onClick={() => uploadedImage && analyzeSkin(uploadedImage)}
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
           <p className="text-xs text-secondary font-light">
             © 2024 All Rights Reserved. This application is for informational purposes only and does not constitute medical advice. 
             Always consult with a qualified healthcare professional for medical concerns.
           </p>
         </div>
       </div>
     </div>
   );
 } 