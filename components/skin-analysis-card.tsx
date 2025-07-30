'use client';

import { useState, useRef } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Camera, Upload, AlertCircle, CheckCircle, Loader2, User, Sparkles } from 'lucide-react';
import { apiClient } from '@/lib/api';

export default function SkinAnalysisCard() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [showCamera, setShowCamera] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [analysisStep, setAnalysisStep] = useState<string>('');
  const [ethnicity, setEthnicity] = useState<string>('');
  const [age, setAge] = useState<string>('');

  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const handleImageCapture = async () => {
    if (!capturedImage) return;

    setCapturedImage(capturedImage);
    setShowCamera(false);
    setAnalysisError(null);
    
    // Allow both authenticated and guest users to analyze
    setIsAnalyzing(true);
    setAnalysisStep('Preparing analysis...');
    
    try {
      // Convert base64 to blob
      const response = await fetch(capturedImage);
      const blob = await response.blob();
      
      // Create a File object from the blob
      const file = new File([blob], 'selfie.jpg', { type: 'image/jpeg' });
      
      // Call the enhanced analysis API
      setAnalysisStep('Detecting face...');
      const analysisResponse = await apiClient.analyzeSkinEnhanced(file, ethnicity, age);
      
      if (analysisResponse.success) {
        setAnalysisStep('Analysis complete!');
        
        // Store analysis ID and results in localStorage for the results page
        if (analysisResponse.data?.image_id) {
          localStorage.setItem('lastAnalysisId', analysisResponse.data.image_id);
          // Cache the full analysis results (store the entire response)
          localStorage.setItem(`analysis_${analysisResponse.data.image_id}`, JSON.stringify(analysisResponse));
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
        setAnalysisStep('Preparing analysis...');
        
        try {
          // Call the enhanced analysis API directly with the file
          setAnalysisStep('Detecting face...');
          const analysisResponse = await apiClient.analyzeSkinEnhanced(file, ethnicity, age);
          
          if (analysisResponse.success) {
            setAnalysisStep('Analysis complete!');
            
            // Store analysis ID and results in localStorage for the results page
            if (analysisResponse.data?.image_id) {
              localStorage.setItem('lastAnalysisId', analysisResponse.data.image_id);
              // Cache the full analysis results (store the entire response)
              localStorage.setItem(`analysis_${analysisResponse.data.image_id}`, JSON.stringify(analysisResponse));
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

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          facingMode: 'user',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        } 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setShowCamera(true);
      }
    } catch (error) {
      console.error('Error accessing camera:', error);
      setAnalysisError('Unable to access camera. Please upload a photo instead.');
    }
  };

  const capturePhoto = () => {
    if (videoRef.current) {
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(videoRef.current, 0, 0);
        const imageData = canvas.toDataURL('image/jpeg');
        setCapturedImage(imageData);
        setShowCamera(false);
        
        // Stop the camera stream
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
          streamRef.current = null;
        }
      }
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setShowCamera(false);
  };

  const resetAnalysis = () => {
    setCapturedImage(null);
    setAnalysisComplete(false);
    setAnalysisError(null);
    setAnalysisStep('');
    setEthnicity('');
    setAge('');
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          AI-Powered Skin Analysis
        </CardTitle>
        <CardDescription>
          Get personalized skin insights and recommendations using advanced AI technology
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Optional Demographics Input */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium mb-2 block">Age (Optional)</label>
            <input
              type="number"
              placeholder="Enter your age"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <div>
            <label className="text-sm font-medium mb-2 block">Ethnicity (Optional)</label>
            <select
              value={ethnicity}
              onChange={(e) => setEthnicity(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">Select ethnicity</option>
              <option value="african">African</option>
              <option value="east_asian">East Asian</option>
              <option value="south_asian">South Asian</option>
              <option value="caucasian">Caucasian</option>
              <option value="hispanic">Hispanic</option>
              <option value="middle_eastern">Middle Eastern</option>
              <option value="mixed">Mixed</option>
            </select>
          </div>
        </div>

        {/* Image Capture Section */}
        {!capturedImage && !isAnalyzing && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Button
                onClick={startCamera}
                className="w-full"
                variant="outline"
              >
                <Camera className="mr-2 h-4 w-4" />
                Take Photo
              </Button>
              
              <Button
                onClick={() => fileInputRef.current?.click()}
                className="w-full"
                variant="outline"
              >
                <Upload className="mr-2 h-4 w-4" />
                Upload Photo
              </Button>
            </div>
            
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileUpload}
              className="hidden"
            />
          </div>
        )}

        {/* Camera Interface */}
        {showCamera && (
          <div className="space-y-4">
            <div className="relative">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                className="w-full rounded-lg"
              />
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="border-2 border-white rounded-full w-48 h-48 opacity-50"></div>
              </div>
            </div>
            
            <div className="flex gap-2">
              <Button onClick={capturePhoto} className="flex-1">
                <Camera className="mr-2 h-4 w-4" />
                Capture
              </Button>
              <Button onClick={stopCamera} variant="outline" className="flex-1">
                Cancel
              </Button>
            </div>
          </div>
        )}

        {/* Captured Image Preview */}
        {capturedImage && !isAnalyzing && !analysisComplete && (
          <div className="space-y-4">
            <div className="relative">
              <img
                src={capturedImage}
                alt="Captured"
                className="w-full max-w-md mx-auto rounded-lg"
              />
              <div className="absolute top-2 right-2 bg-green-500 text-white rounded-full p-1">
                <CheckCircle className="h-4 w-4" />
              </div>
            </div>
            
            <div className="flex gap-2">
              <Button onClick={handleImageCapture} className="flex-1">
                <Sparkles className="mr-2 h-4 w-4" />
                Analyze Skin
              </Button>
              <Button onClick={resetAnalysis} variant="outline" className="flex-1">
                Retake Photo
              </Button>
            </div>
          </div>
        )}

        {/* Analysis Progress */}
        {isAnalyzing && (
          <div className="space-y-4">
            <div className="flex items-center justify-center">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
            
            <div className="text-center space-y-2">
              <p className="font-medium">{analysisStep}</p>
              <p className="text-sm text-muted-foreground">
                This may take a few moments...
              </p>
            </div>
            
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-primary h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {analysisError && (
          <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg">
            <AlertCircle className="h-5 w-5 text-red-500" />
            <p className="text-red-700">{analysisError}</p>
          </div>
        )}

        {/* Analysis Complete */}
        {analysisComplete && (
          <div className="flex items-center gap-2 p-4 bg-green-50 border border-green-200 rounded-lg">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <p className="text-green-700">Analysis complete! Redirecting to results...</p>
          </div>
        )}

        {/* Tips for Best Results */}
        {!capturedImage && !isAnalyzing && (
          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-medium mb-2">Tips for Best Results:</h4>
            <ul className="text-sm space-y-1 text-blue-700">
              <li>• Ensure good, even lighting</li>
              <li>• Remove makeup and glasses</li>
              <li>• Position your face in the center</li>
              <li>• Keep your head still during capture</li>
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
