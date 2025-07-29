'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Camera, Upload, Loader2, CheckCircle, AlertCircle, Sparkles, RefreshCw, Wifi, WifiOff, ArrowDown } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { CameraCapture } from "@/components/camera-capture";
import { apiClient } from "@/lib/api";
import { serviceDegradationManager } from "@/lib/service-degradation";

export default function EnhancedSkinAnalysisCard() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const [showCamera, setShowCamera] = useState(false);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [analysisStep, setAnalysisStep] = useState('');
  const [isOnline, setIsOnline] = useState(true);
  const [retryCount, setRetryCount] = useState(0);
  const [fallbackMode, setFallbackMode] = useState(false);
  const [serviceStatus, setServiceStatus] = useState({
    enhancedAnalysis: true,
    vectorSearch: true,
    scinDataset: true,
    googleVision: true
  });
  
  // Optional inputs
  const [ethnicity, setEthnicity] = useState('');
  const [age, setAge] = useState('');
  const [showOptionalInputs, setShowOptionalInputs] = useState(false);

  // Monitor service status
  useEffect(() => {
    const unsubscribers = [
      serviceDegradationManager.onServiceStatusChange('enhanced-analysis', (isAvailable) => {
        setServiceStatus(prev => ({ ...prev, enhancedAnalysis: isAvailable }));
      }),
      serviceDegradationManager.onServiceStatusChange('vector-search', (isAvailable) => {
        setServiceStatus(prev => ({ ...prev, vectorSearch: isAvailable }));
      }),
      serviceDegradationManager.onServiceStatusChange('scin-dataset', (isAvailable) => {
        setServiceStatus(prev => ({ ...prev, scinDataset: isAvailable }));
      }),
      serviceDegradationManager.onServiceStatusChange('google-vision', (isAvailable) => {
        setServiceStatus(prev => ({ ...prev, googleVision: isAvailable }));
      })
    ];

    return () => {
      unsubscribers.forEach(unsubscribe => unsubscribe());
    };
  }, []);

  // Check online status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Simulate analysis progress
  const simulateProgress = () => {
    const steps = [
      { progress: 10, step: 'Uploading image...' },
      { progress: 25, step: 'Processing with Google Vision API...' },
      { progress: 45, step: 'Analyzing skin features...' },
      { progress: 65, step: 'Searching FAISS vector database...' },
      { progress: 80, step: 'Matching with SCIN dataset...' },
      { progress: 95, step: 'Generating recommendations...' },
      { progress: 100, step: 'Analysis complete!' }
    ];

    let currentStep = 0;
    const interval = setInterval(() => {
      if (currentStep < steps.length) {
        setAnalysisProgress(steps[currentStep].progress);
        setAnalysisStep(steps[currentStep].step);
        currentStep++;
      } else {
        clearInterval(interval);
      }
    }, 1000);

    return interval;
  };

  const performAnalysis = async (file: File, attempt: number = 1): Promise<void> => {
    const maxRetries = 3;
    
    try {
      setAnalysisProgress(0);
      setAnalysisStep('Initializing analysis...');
      
      // Check if enhanced analysis is available
      if (!serviceDegradationManager.isServiceAvailable('enhanced-analysis')) {
        throw new Error('Enhanced analysis service is temporarily unavailable');
      }
      
      // Start progress simulation
      const progressInterval = simulateProgress();
      
      // Use enhanced analysis for better results
      const analysisResponse = await apiClient.analyzeSkinEnhanced(file);
      
      clearInterval(progressInterval);
      
      if (analysisResponse.success) {
        // Record successful service usage
        serviceDegradationManager.recordSuccess('enhanced-analysis');
        
        // Store analysis ID and results in localStorage for the results page
        if (analysisResponse.data?.analysis_id) {
          localStorage.setItem('lastAnalysisId', analysisResponse.data.analysis_id);
          // Cache the full analysis results
          localStorage.setItem(`analysis_${analysisResponse.data.analysis_id}`, JSON.stringify(analysisResponse));
        }
        
        setAnalysisProgress(100);
        setAnalysisStep('Analysis complete!');
        setIsAnalyzing(false);
        setAnalysisComplete(true);
        setRetryCount(0);
        
        // Redirect to results page
        setTimeout(() => {
          router.push(`/analysis-results?analysisId=${analysisResponse.data.analysis_id}`);
        }, 1000);
      } else {
        throw new Error(analysisResponse.message || 'Analysis failed');
      }
    } catch (error) {
      console.error(`Enhanced analysis attempt ${attempt} failed:`, error);
      
      // Record service failure
      serviceDegradationManager.recordFailure('enhanced-analysis');
      
      if (attempt < maxRetries && isOnline && serviceDegradationManager.isServiceAvailable('enhanced-analysis')) {
        setRetryCount(attempt);
        setAnalysisStep(`Retrying enhanced analysis (${attempt}/${maxRetries})...`);
        
        // Exponential backoff
        const delay = Math.pow(2, attempt) * 1000;
        setTimeout(() => {
          performAnalysis(file, attempt + 1);
        }, delay);
      } else {
        // Try fallback to legacy analysis
        await performLegacyAnalysis(file);
      }
    }
  };

  const performLegacyAnalysis = async (file: File): Promise<void> => {
    try {
      setAnalysisStep('Falling back to standard analysis...');
      setAnalysisProgress(50);
      
      // Call the legacy analysis API
      const analysisResponse = await apiClient.analyzeSkinEnhanced(file);
      
      if (analysisResponse.success) {
        // Store analysis ID and results in localStorage for the results page
        if (analysisResponse.data?.image_id) {
          localStorage.setItem('lastAnalysisId', analysisResponse.data.image_id);
          // Cache the full analysis results
          localStorage.setItem(`analysis_${analysisResponse.data.image_id}`, JSON.stringify(analysisResponse));
        }
        
        setAnalysisProgress(100);
        setAnalysisStep('Standard analysis complete!');
        setIsAnalyzing(false);
        setAnalysisComplete(true);
        setRetryCount(0);
        
        // Show degradation notice
        setAnalysisError('Enhanced features are temporarily unavailable. Standard analysis completed successfully.');
        
        // Redirect to results page
        setTimeout(() => {
          router.push(`/analysis-results?analysisId=${analysisResponse.data.image_id}`);
        }, 2000);
      } else {
        throw new Error(analysisResponse.message || 'Legacy analysis failed');
      }
    } catch (error) {
      console.error('Legacy analysis also failed:', error);
      setIsAnalyzing(false);
      setAnalysisProgress(0);
      setAnalysisStep('');
      
      if (!isOnline) {
        setAnalysisError('No internet connection. Please check your network and try again.');
      } else {
        setAnalysisError('Both enhanced and standard analysis are currently unavailable. Please try again later.');
        setFallbackMode(true);
      }
    }
  };

  const handleImageCapture = async (imageData: string) => {
    setCapturedImage(imageData);
    setShowCamera(false);
    setAnalysisError(null);
    setFallbackMode(false);
    
    // Allow both authenticated and guest users to analyze
    setIsAnalyzing(true);
    
    try {
      // Convert base64 to blob
      const response = await fetch(imageData);
      const blob = await response.blob();
      
      // Create a File object from the blob
      const file = new File([blob], 'selfie.jpg', { type: 'image/jpeg' });
      
      await performAnalysis(file);
    } catch (error) {
      console.error('Error preparing image for analysis:', error);
      setIsAnalyzing(false);
      setAnalysisError('Failed to process image. Please try again.');
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
        setFallbackMode(false);
        
        // Allow both authenticated and guest users to analyze
        setIsAnalyzing(true);
        
        try {
          await performAnalysis(file);
        } catch (error) {
          console.error('Error during file upload analysis:', error);
          setIsAnalyzing(false);
          setAnalysisError('Failed to process uploaded file. Please try again.');
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const handleAnalyze = () => {
    if (capturedImage) {
      // Trigger analysis with the captured image
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = img.width;
        canvas.height = img.height;
        ctx?.drawImage(img, 0, 0);
        
        canvas.toBlob(async (blob) => {
          if (blob) {
            const file = new File([blob], 'selfie.jpg', { type: 'image/jpeg' });
            setIsAnalyzing(true);
            setAnalysisError(null);
            setFallbackMode(false);
            
            try {
              await performAnalysis(file);
            } catch (error) {
              console.error('Error during manual analysis:', error);
              setIsAnalyzing(false);
              setAnalysisError('Failed to process image. Please try again.');
            }
          }
        }, 'image/jpeg');
      };
      img.src = capturedImage;
    }
  };

  const handleFallbackToLegacy = () => {
    // Redirect to legacy skin analysis page
    router.push('/skin-analysis');
  };

  const handleRetryAnalysis = () => {
    setAnalysisError(null);
    setFallbackMode(false);
    setRetryCount(0);
    handleAnalyze();
  };

  const resetAnalysis = () => {
    setCapturedImage(null);
    setAnalysisComplete(false);
    setAnalysisError(null);
    setEthnicity('');
    setAge('');
    setShowOptionalInputs(false);
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          Enhanced Skin Analysis
        </CardTitle>
        <CardDescription>
          Get AI-powered insights with vector-based recommendations. 
          Optional demographic data helps improve accuracy.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Optional Inputs Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Label className="text-sm font-medium">Optional Demographic Data</Label>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowOptionalInputs(!showOptionalInputs)}
            >
              {showOptionalInputs ? 'Hide' : 'Show'} Optional Data
            </Button>
          </div>
          
          {showOptionalInputs && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 border rounded-lg bg-muted/50">
              <div className="space-y-2">
                <Label htmlFor="ethnicity">Ethnicity (Optional)</Label>
                <Select value={ethnicity} onValueChange={setEthnicity}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select ethnicity..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Not specified</SelectItem>
                    <SelectItem value="asian">Asian</SelectItem>
                    <SelectItem value="black">Black</SelectItem>
                    <SelectItem value="hispanic">Hispanic/Latino</SelectItem>
                    <SelectItem value="middle_eastern">Middle Eastern</SelectItem>
                    <SelectItem value="white">White</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="age">Age (Optional)</Label>
                <Input
                  id="age"
                  type="number"
                  placeholder="Enter your age"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  min="0"
                  max="120"
                />
              </div>
            </div>
          )}
        </div>

        {/* Image Capture Section */}
        {!capturedImage ? (
          <div className="space-y-4">
            <div className="flex gap-4">
              <Button
                onClick={() => setShowCamera(true)}
                className="flex-1"
                disabled={isAnalyzing}
              >
                <Camera className="mr-2 h-4 w-4" />
                Take Photo
              </Button>
              
              <div className="relative flex-1">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  disabled={isAnalyzing}
                />
                <Button variant="outline" className="w-full" disabled={isAnalyzing}>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload Photo
                </Button>
              </div>
            </div>
            
                         {showCamera && (
               <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center">
                 <div className="bg-background p-4 rounded-lg max-w-md w-full mx-4">
                   <CameraCapture 
                     onImageCapture={handleImageCapture} 
                     onClose={() => setShowCamera(false)}
                   />
                 </div>
               </div>
             )}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="relative">
              <img
                src={capturedImage}
                alt="Captured"
                className="w-full h-64 object-cover rounded-lg"
              />
              <Button
                variant="outline"
                size="sm"
                onClick={resetAnalysis}
                className="absolute top-2 right-2"
                disabled={isAnalyzing}
              >
                Retake
              </Button>
            </div>
            
            <Button
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className="w-full"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Analyze with AI
                </>
              )}
            </Button>
          </div>
        )}

        {/* Network Status Indicator */}
        {!isOnline && (
          <div className="flex items-center gap-2 p-3 bg-orange-50 border border-orange-200 rounded-lg">
            <WifiOff className="h-4 w-4 text-orange-600" />
            <p className="text-sm text-orange-800">No internet connection detected</p>
          </div>
        )}

        {/* Analysis Progress */}
        {isAnalyzing && (
          <div className="space-y-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
              <span className="text-sm font-medium text-blue-900">Processing Analysis</span>
              {retryCount > 0 && (
                <span className="text-xs text-blue-700">(Retry {retryCount}/3)</span>
              )}
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-xs text-blue-700">{analysisStep}</span>
                <span className="text-xs text-blue-700">{analysisProgress}%</span>
              </div>
              <Progress value={analysisProgress} className="h-2" />
            </div>
            
            {!isOnline && (
              <div className="flex items-center gap-1 text-xs text-orange-600">
                <WifiOff className="h-3 w-3" />
                <span>Waiting for connection...</span>
              </div>
            )}
          </div>
        )}

        {/* Error Display with Enhanced Actions */}
        {analysisError && (
          <div className="space-y-3 p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
            <div className="flex items-start gap-2">
              <AlertCircle className="h-4 w-4 text-destructive mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm text-destructive">{analysisError}</p>
                
                {fallbackMode && (
                  <div className="mt-3 space-y-2">
                    <p className="text-xs text-muted-foreground">
                      Enhanced analysis is temporarily unavailable. You can:
                    </p>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={handleRetryAnalysis}
                        disabled={isAnalyzing}
                      >
                        <RefreshCw className="h-3 w-3 mr-1" />
                        Retry Enhanced
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={handleFallbackToLegacy}
                      >
                        Use Legacy Analysis
                      </Button>
                    </div>
                  </div>
                )}
                
                {!fallbackMode && retryCount === 0 && (
                  <div className="mt-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={handleRetryAnalysis}
                      disabled={isAnalyzing || !isOnline}
                    >
                      <RefreshCw className="h-3 w-3 mr-1" />
                      Try Again
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Success Display */}
        {analysisComplete && (
          <div className="flex items-center gap-2 p-4 bg-green-50 border border-green-200 rounded-lg">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <p className="text-sm text-green-800">Analysis complete! Redirecting to results...</p>
          </div>
        )}

        {/* Service Status Indicator */}
        <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg">
          <h4 className="font-medium text-slate-900 mb-3 flex items-center gap-2">
            <Wifi className="h-4 w-4" />
            Service Status
          </h4>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${serviceStatus.enhancedAnalysis ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className={serviceStatus.enhancedAnalysis ? 'text-green-700' : 'text-red-700'}>
                Enhanced Analysis
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${serviceStatus.vectorSearch ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className={serviceStatus.vectorSearch ? 'text-green-700' : 'text-red-700'}>
                Vector Search
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${serviceStatus.scinDataset ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className={serviceStatus.scinDataset ? 'text-green-700' : 'text-red-700'}>
                SCIN Dataset
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${serviceStatus.googleVision ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className={serviceStatus.googleVision ? 'text-green-700' : 'text-red-700'}>
                Google Vision
              </span>
            </div>
          </div>
          
          {/* Degradation Notice */}
          {(!serviceStatus.enhancedAnalysis || !serviceStatus.vectorSearch || !serviceStatus.scinDataset || !serviceStatus.googleVision) && (
            <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs">
              <div className="flex items-center gap-1 text-yellow-800">
                <AlertCircle className="h-3 w-3" />
                <span className="font-medium">Some enhanced features are temporarily unavailable</span>
              </div>
              <p className="text-yellow-700 mt-1">
                Analysis will automatically fall back to standard features when needed.
              </p>
            </div>
          )}
        </div>

        {/* Enhanced Features Info */}
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 className="font-medium text-blue-900 mb-2">Enhanced Features:</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Vector-based skin condition detection</li>
            <li>• FAISS similarity search for recommendations</li>
            <li>• scIN dataset integration</li>
            <li>• Optional demographic context</li>
            <li>• Enhanced accuracy with AI models</li>
          </ul>
          
          {/* Fallback Notice */}
          <div className="mt-3 p-2 bg-blue-100 border border-blue-300 rounded text-xs">
            <div className="flex items-center gap-1 text-blue-800">
              <ArrowDown className="h-3 w-3" />
              <span className="font-medium">Automatic Fallback</span>
            </div>
            <p className="text-blue-700 mt-1">
              If enhanced features are unavailable, the system automatically uses standard analysis to ensure you always get results.
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
} 