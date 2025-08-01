'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Camera, RotateCcw, Upload, X } from 'lucide-react';
import { FacialMatrixOverlay } from './facial-matrix-overlay';

interface CameraCaptureProps {
  onImageCapture: (imageData: string) => void;
  onClose: () => void;
}

export function CameraCapture({ onImageCapture, onClose }: CameraCaptureProps) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('user');
  const [isMobile, setIsMobile] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    // Detect mobile device
    const checkMobile = () => {
      const userAgent = navigator.userAgent || navigator.vendor || (window as any).opera;
      const isMobileDevice = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent.toLowerCase());
      setIsMobile(isMobileDevice);
    };
    
    checkMobile();
    startCamera();
    return () => {
      stopCamera();
    };
  }, [facingMode]);

  const startCamera = async () => {
    try {
      setError(null);
      
      // Stop any existing stream
      if (streamRef.current) {
        stopCamera();
      }

      // Check if mediaDevices is available
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.error('Camera access not available:', {
          mediaDevices: !!navigator.mediaDevices,
          getUserMedia: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)
        });
        throw new Error('Camera access not available in this browser/environment. Please use HTTPS or localhost.');
      }

      console.log('Attempting to access camera...');
      
      // Mobile-optimized camera constraints
      const constraints = {
        video: {
          facingMode: facingMode,
          width: { ideal: isMobile ? 1280 : 720 },
          height: { ideal: isMobile ? 720 : 1280 },
          // Mobile-specific optimizations
          ...(isMobile && {
            aspectRatio: { ideal: 1 },
            frameRate: { ideal: 30 }
          })
        }
      };
      
      console.log('Camera constraints:', constraints);
      
      // Get camera stream
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      
      console.log('Camera stream obtained successfully');

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setIsStreaming(true);
      }
    } catch (err) {
      console.error('Camera access error:', err);
      
      // Enhanced error messages for mobile
      if (isMobile) {
        setError('Unable to access camera on mobile. Please check camera permissions and try again.');
      } else {
        setError('Unable to access camera. Please check permissions.');
      }
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setIsStreaming(false);
  };

  const captureImage = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    if (!context) return;

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to base64
    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    onImageCapture(imageData);
  };

  const switchCamera = () => {
    setFacingMode(prev => prev === 'user' ? 'environment' : 'user');
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        onImageCapture(result);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 p-2 md:p-4">
      <Card className="w-full max-w-sm md:max-w-md">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base md:text-lg">Take a Selfie</CardTitle>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="h-8 w-8"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          <CardDescription className="text-sm">
            Position your face in the center circle for best results
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-3">
          {error ? (
            <div className="text-center py-6">
              <p className="text-red-500 mb-4 text-sm">{error}</p>
              <div className="space-y-2">
                <Button onClick={startCamera} variant="outline" className="w-full h-12 text-base">
                  <Camera className="mr-2 h-4 w-4" />
                  Try Again
                </Button>
                {isMobile && (
                  <p className="text-xs text-muted-foreground px-4">
                    Make sure camera permissions are enabled in your browser settings
                  </p>
                )}
              </div>
            </div>
          ) : (
            <>
              {/* Camera Preview */}
              <div className="relative bg-black rounded-lg overflow-hidden">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-48 md:h-64 object-cover"
                />
                {!isStreaming && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
                  </div>
                )}
                
                {/* Facial Matrix Overlay */}
                {isStreaming && (
                  <FacialMatrixOverlay 
                    isActive={isStreaming}
                    onScanComplete={() => {
                      // Auto-capture after matrix scan completes
                      setTimeout(() => {
                        captureImage();
                      }, 500);
                    }}
                  />
                )}
              </div>

              {/* Camera Controls */}
              <div className="flex justify-center gap-3">
                <Button
                  variant="outline"
                  size="icon"
                  onClick={switchCamera}
                  className="h-10 w-10"
                >
                  <RotateCcw className="h-4 w-4" />
                </Button>
                <Button
                  onClick={captureImage}
                  disabled={!isStreaming}
                  className="h-12 w-12 rounded-full bg-blue-600 hover:bg-blue-700"
                >
                  <Camera className="h-6 w-6" />
                </Button>
                <Button
                  variant="outline"
                  onClick={handleFileUpload}
                  className="h-10 px-3 text-sm"
                >
                  <Upload className="h-4 w-4 mr-1" />
                  Upload
                </Button>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </div>

              {/* Instructions */}
              <div className="text-center text-xs text-muted-foreground px-4">
                <p className="font-medium mb-1">📸 Face Positioning Guide</p>
                <p>• Center your face within the white circle</p>
                <p>• Keep your face steady during the scan</p>
                <p>• Ensure good lighting for clear results</p>
                {isMobile && (
                  <p className="mt-1 text-blue-500">📱 Hold your phone steady for best results</p>
                )}
              </div>
            </>
          )}
        </CardContent>
      </Card>
      
      {/* Hidden canvas for image capture */}
      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
} 