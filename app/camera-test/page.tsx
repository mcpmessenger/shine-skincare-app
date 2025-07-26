'use client';

import { useState } from 'react';
import { CameraCapture } from '@/components/camera-capture';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Camera, Smartphone, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';

export default function CameraTestPage() {
  const [showCamera, setShowCamera] = useState(false);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);

  const handleImageCapture = (imageData: string) => {
    setCapturedImage(imageData);
    setShowCamera(false);
  };

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-md mx-auto">
        {/* Header */}
        <div className="mb-6">
          <Link href="/" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Home
          </Link>
          <div className="flex items-center gap-2 mb-2">
            <Camera className="h-6 w-6 text-primary" />
            <h1 className="text-2xl font-bold">Camera Test</h1>
          </div>
          <p className="text-muted-foreground">
            Test the mobile camera functionality for skin analysis
          </p>
        </div>

        {/* Camera Test Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Smartphone className="h-5 w-5" />
              Mobile Camera Test
            </CardTitle>
            <CardDescription>
              Test camera access and image capture on your mobile device
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Image Preview */}
            <div className="relative w-full h-64 bg-muted rounded-lg flex items-center justify-center overflow-hidden">
              {capturedImage ? (
                <Image
                  src={capturedImage}
                  alt="Captured Image"
                  width={300}
                  height={300}
                  className="object-cover w-full h-full"
                />
              ) : (
                <div className="text-center text-muted-foreground">
                  <Camera className="h-12 w-12 mx-auto mb-2" />
                  <p>No image captured yet</p>
                </div>
              )}
            </div>

            {/* Camera Controls */}
            <div className="space-y-2">
              <Button 
                className="w-full" 
                onClick={() => setShowCamera(true)}
              >
                <Camera className="mr-2 h-4 w-4" />
                Open Camera
              </Button>
              
              {capturedImage && (
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={() => setCapturedImage(null)}
                >
                  Clear Image
                </Button>
              )}
            </div>

            {/* Test Results */}
            {capturedImage && (
              <div className="p-4 bg-green-50 rounded-lg">
                <h3 className="font-semibold text-green-800 mb-2">✅ Camera Test Successful!</h3>
                <p className="text-sm text-green-700">
                  Your device camera is working correctly. You can now use the skin analysis feature.
                </p>
              </div>
            )}

            {/* Instructions */}
            <div className="text-sm text-muted-foreground space-y-2">
              <p><strong>Instructions:</strong></p>
              <ul className="list-disc list-inside space-y-1">
                <li>Allow camera permissions when prompted</li>
                <li>Position your face in the center</li>
                <li>Ensure good lighting</li>
                <li>Tap the camera button to capture</li>
              </ul>
            </div>
          </CardContent>
        </Card>

        {/* Camera Modal */}
        {showCamera && (
          <CameraCapture
            onImageCapture={handleImageCapture}
            onClose={() => setShowCamera(false)}
          />
        )}
      </div>
    </div>
  );
} 