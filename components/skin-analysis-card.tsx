'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Camera, Upload, Loader2, CheckCircle, AlertCircle } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { CameraCapture } from "@/components/camera-capture";
import { apiClient } from "@/lib/api";

export default function SkinAnalysisCard() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const [showCamera, setShowCamera] = useState(false);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  const handleImageCapture = async (imageData: string) => {
    setCapturedImage(imageData);
    setShowCamera(false);
    setAnalysisError(null);
    
    // Allow both authenticated and guest users to analyze
    setIsAnalyzing(true);
    
    try {
      // Convert base64 to blob
      const response = await fetch(imageData);
      const blob = await response.blob();
      
      // Create a File object from the blob
      const file = new File([blob], 'selfie.jpg', { type: 'image/jpeg' });
      
      // Call the enhanced analysis API
      const analysisResponse = await apiClient.analyzeSkinEnhanced(file);
      
      if (analysisResponse.success) {
        // Store analysis ID in localStorage for the results page
        if (analysisResponse.data?.image_id) {
          localStorage.setItem('lastAnalysisId', analysisResponse.data.image_id);
        }
        
        setIsAnalyzing(false);
        setAnalysisComplete(true);
        
        // Redirect to results page
        router.push(`/analysis-results?analysisId=${analysisResponse.data.image_id}`);
      } else {
        console.error('Analysis failed:', analysisResponse);
        setIsAnalyzing(false);
        setAnalysisError('Analysis failed. Please try again.');
      }
    } catch (error) {
      console.error('Error during analysis:', error);
      setIsAnalyzing(false);
      setAnalysisError('Network error. Please check your connection and try again.');
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const result = e.target?.result as string;
        setCapturedImage(result);
        setAnalysisError(null);
        
        // Allow both authenticated and guest users to analyze
        setIsAnalyzing(true);
        
        try {
          // Call the enhanced analysis API directly with the file
          const analysisResponse = await apiClient.analyzeSkinEnhanced(file);
          
          if (analysisResponse.success) {
            // Store analysis ID in localStorage for the results page
            if (analysisResponse.data?.image_id) {
              localStorage.setItem('lastAnalysisId', analysisResponse.data.image_id);
            }
            
            setIsAnalyzing(false);
            setAnalysisComplete(true);
            
            // Redirect to results page
            router.push(`/analysis-results?analysisId=${analysisResponse.data.image_id}`);
          } else {
            console.error('Analysis failed:', analysisResponse);
            setIsAnalyzing(false);
            setAnalysisError('Analysis failed. Please try again.');
          }
        } catch (error) {
          console.error('Error during analysis:', error);
          setIsAnalyzing(false);
          setAnalysisError('Network error. Please check your connection and try again.');
        }
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Camera className="h-5 w-5" />
          Skin Analysis
        </CardTitle>
        <CardDescription>
          Upload a photo or take a selfie to get personalized skincare recommendations
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {!capturedImage ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Button
                onClick={() => setShowCamera(true)}
                className="flex items-center gap-2"
                disabled={isAnalyzing}
              >
                <Camera className="h-4 w-4" />
                Take Photo
              </Button>
              <div className="relative">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  disabled={isAnalyzing}
                />
                <Button
                  variant="outline"
                  className="flex items-center gap-2 w-full"
                  disabled={isAnalyzing}
                >
                  <Upload className="h-4 w-4" />
                  Upload Photo
                </Button>
              </div>
            </div>
            {!isAuthenticated && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <div className="flex items-start gap-2">
                  <AlertCircle className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                  <div className="text-sm">
                    <p className="text-blue-800 font-medium">Try our service for free!</p>
                    <p className="text-blue-700">
                      You can test the skin analysis now. Sign up for personalized recommendations and save your results.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="relative">
              <img
                src={capturedImage}
                alt="Captured skin"
                className="w-full h-64 object-cover rounded-lg"
              />
              {isAnalyzing && (
                <div className="absolute inset-0 bg-black/50 flex items-center justify-center rounded-lg">
                  <div className="text-center text-white">
                    <Loader2 className="h-8 w-8 animate-spin mx-auto mb-2" />
                    <p>Analyzing your skin...</p>
                  </div>
                </div>
              )}
              {analysisComplete && (
                <div className="absolute inset-0 bg-green-500/20 flex items-center justify-center rounded-lg">
                  <div className="text-center text-green-600">
                    <CheckCircle className="h-8 w-8 mx-auto mb-2" />
                    <p>Analysis complete!</p>
                  </div>
                </div>
              )}
            </div>
            
            {analysisError && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                <div className="flex items-start gap-2">
                  <AlertCircle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
                  <div className="text-sm text-red-800">
                    {analysisError}
                  </div>
                </div>
              </div>
            )}
            
            <div className="flex gap-2">
              <Button
                onClick={() => {
                  setCapturedImage(null);
                  setAnalysisComplete(false);
                  setAnalysisError(null);
                }}
                variant="outline"
                className="flex-1"
              >
                Try Again
              </Button>
              {analysisComplete && (
                <Button
                  onClick={() => router.push('/analysis-results')}
                  className="flex-1"
                >
                  View Results
                </Button>
              )}
            </div>
            
            {!isAuthenticated && analysisComplete && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <div className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <div className="text-sm">
                    <p className="text-green-800 font-medium">Great! Your analysis is ready.</p>
                    <p className="text-green-700">
                      Sign up to save your results and get personalized recommendations.
                    </p>
                    <Button 
                      size="sm" 
                      className="mt-2"
                      onClick={() => router.push('/auth/signup')}
                    >
                      Sign Up Now
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
        
        {showCamera && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-4 max-w-md w-full mx-4">
              <CameraCapture
                onImageCapture={handleImageCapture}
                onClose={() => setShowCamera(false)}
              />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
