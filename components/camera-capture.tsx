'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Camera, RotateCcw, Upload, X } from 'lucide-react';

interface CameraCaptureProps {
  onImageCapture: (imageData: string) => void;
  onClose: () => void;
}

export function CameraCapture({ onImageCapture, onClose }: CameraCaptureProps) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('user');
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
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

      // Get camera stream
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: facingMode,
          width: { ideal: 720 },
          height: { ideal: 1280 }
        }
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setIsStreaming(true);
      }
    } catch (err) {
      console.error('Camera access error:', err);
      setError('Unable to access camera. Please check permissions.');
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
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Take a Selfie</CardTitle>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="h-8 w-8"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          <CardDescription>
            Position your face in the center for best results
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {error ? (
            <div className="text-center py-8">
              <p className="text-red-500 mb-4">{error}</p>
              <Button onClick={startCamera} variant="outline">
                <Camera className="mr-2 h-4 w-4" />
                Try Again
              </Button>
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
                  className="w-full h-64 object-cover"
                />
                {!isStreaming && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
                  </div>
                )}
              </div>

              {/* Camera Controls */}
              <div className="flex justify-center gap-4">
                <Button
                  variant="outline"
                  size="icon"
                  onClick={switchCamera}
                  disabled={!isStreaming}
                >
                  <RotateCcw className="h-4 w-4" />
                </Button>
                
                <Button
                  onClick={captureImage}
                  disabled={!isStreaming}
                  className="h-12 w-12 rounded-full"
                >
                  <Camera className="h-6 w-6" />
                </Button>
                
                <label htmlFor="file-upload">
                  <Button variant="outline" size="icon" asChild>
                    <div>
                      <Upload className="h-4 w-4" />
                    </div>
                  </Button>
                </label>
                <input
                  id="file-upload"
                  type="file"
                  accept="image/*"
                  capture="user"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </div>

              {/* Instructions */}
              <div className="text-center text-sm text-muted-foreground">
                <p>• Ensure good lighting</p>
                <p>• Keep your face centered</p>
                <p>• Remove glasses if possible</p>
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