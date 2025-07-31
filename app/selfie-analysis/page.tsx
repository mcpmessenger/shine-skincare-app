'use client';

import React, { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Camera, Upload, Sparkles, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { analyzeSelfie } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import Image from 'next/image';
import { CameraCapture } from '@/components/camera-capture';
import { FacialMatrixOverlay } from '@/components/facial-matrix-overlay';

interface FacialFeature {
  type: string;
  x: number;
  y: number;
}

interface SkinCondition {
  id: string;
  type: string;
  confidence: number;
  location: { x: number; y: number; width: number; height: number };
  characteristics: {
    severity: string;
    type?: string;
    color?: string;
    size?: string;
    texture?: string; // Added texture
  };
  scin_match_score: number;
  recommendation: string;
}

interface ScinCase {
  id: string;
  similarity_score: number;
  condition_type: string;
  age_group: string;
  ethnicity: string;
  treatment_history: string;
  outcome: string;
}

interface SelfieAnalysisResult {
  facial_features: {
    face_detected: boolean;
    face_isolated: boolean;
    landmarks: FacialFeature[];
    face_bounds: { x: number; y: number; width: number; height: number };
    isolation_complete: boolean;
  };
  skin_conditions: SkinCondition[];
  scin_similar_cases: ScinCase[];
  total_conditions: number;
  ai_processed: boolean;
  image_size: number[];
  ai_level: string;
  google_vision_api: boolean;
  scin_dataset: boolean;
  enhanced_features: {
    face_isolation: boolean;
    skin_condition_detection: boolean;
    scin_dataset_query: boolean;
    facial_landmarks: boolean;
    treatment_recommendations: boolean;
  };
}

export default function SelfieAnalysisPage() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<SelfieAnalysisResult | null>(null);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [showCamera, setShowCamera] = useState(false); // Added state for camera modal
  const [matrixActive, setMatrixActive] = useState(false); // Added state for matrix overlay

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setSelectedImage(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleCameraCapture = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
    } catch (error) {
      toast({
        title: "Camera Error",
        description: "Unable to access camera. Please upload an image instead.",
        variant: "destructive",
      });
    }
  };

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const context = canvasRef.current.getContext('2d');
      if (context) {
        canvasRef.current.width = videoRef.current.videoWidth;
        canvasRef.current.height = videoRef.current.videoHeight;
        context.drawImage(videoRef.current, 0, 0);
        
        const imageData = canvasRef.current.toDataURL('image/jpeg');
        setSelectedImage(imageData);
        
        // Stop camera stream
        const stream = videoRef.current.srcObject as MediaStream;
        stream?.getTracks().forEach(track => track.stop());
      }
    }
  };

  const analyzeSelfieImage = async () => {
    if (!selectedImage) {
      toast({
        title: "No Image Selected",
        description: "Please upload or capture an image first.",
        variant: "destructive",
      });
      return;
    }

    setIsAnalyzing(true);
    setProgress(0);

    try {
      // Convert base64 to file
      const response = await fetch(selectedImage);
      const blob = await response.blob();
      const file = new File([blob], 'selfie.jpg', { type: 'image/jpeg' });

      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // Use the selfie analysis API
      const result = await analyzeSelfie(file);

      clearInterval(progressInterval);
      setProgress(100);

      if (!result.success) {
        throw new Error(result.message || 'Analysis failed');
      }

      const data = result.data;
      console.log('Selfie analysis result:', data);
      
      if (data.selfie_analysis) {
        setAnalysisResult(data.selfie_analysis);
        
        toast({
          title: "Analysis Complete",
          description: `Found ${data.selfie_analysis.total_conditions || 0} skin conditions with ${data.selfie_analysis.ai_level || 'unknown'} AI processing.`,
          variant: "default",
        });
      } else {
        throw new Error('Invalid analysis result format');
      }

    } catch (error) {
      console.error('Analysis error:', error);
      toast({
        title: "Analysis Failed",
        description: "Unable to analyze image. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsAnalyzing(false);
      setProgress(0);
    }
  };

  return (
    <div className="container mx-auto px-4 py-4 max-w-4xl">
      <div className="text-center mb-6">
        <h1 className="text-2xl md:text-3xl font-bold mb-2">Selfie Analysis</h1>
        <p className="text-sm md:text-base text-muted-foreground px-4">
          Take a selfie for facial skin analysis with Google Vision face isolation
        </p>
      </div>

      {/* Camera/Upload Section */}
      <Card className="mb-4">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-2 text-lg md:text-xl">
            <Camera className="h-5 w-5" />
            Take Selfie or Upload Photo
          </CardTitle>
          <CardDescription className="text-sm">
            Use your camera or upload a photo for facial skin analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Camera/Upload Options */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <Button 
              onClick={() => setShowCamera(true)}
              variant="outline" 
              className="h-12 md:h-10 text-base"
            >
              <Camera className="h-5 w-5 mr-2" />
              Take Selfie
            </Button>
            <Button 
              onClick={() => fileInputRef.current?.click()} 
              variant="outline" 
              className="h-12 md:h-10 text-base"
            >
              <Upload className="h-5 w-5 mr-2" />
              Upload Photo
            </Button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="hidden"
            />
          </div>

          {/* Selected Image Preview */}
          {selectedImage && (
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground">Selected Image:</p>
              <div className="relative w-full max-w-sm mx-auto">
                <Image
                  src={selectedImage}
                  alt="Selected selfie"
                  width={400}
                  height={300}
                  className="rounded-lg border w-full h-auto"
                />
                <Button 
                  onClick={analyzeSelfieImage}
                  disabled={isAnalyzing}
                  className="mt-3 w-full h-12 text-base"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-5 w-5 mr-2" />
                      Analyze Selfie
                    </>
                  )}
                </Button>
              </div>
            </div>
          )}

          {/* Progress Bar */}
          {isAnalyzing && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Processing with Google Vision...</span>
                <span>{progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="bg-green-600 h-3 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analysisResult && (
        <div className="space-y-4">
          {/* Skin Conditions */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-lg">
                <AlertCircle className="h-5 w-5 text-orange-500" />
                Detected Skin Conditions ({analysisResult?.total_conditions || 0})
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="space-y-3">
                {analysisResult.skin_conditions.map((condition, index) => (
                  <div key={condition.id} className="border rounded-lg p-3 md:p-4">
                    <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-2 mb-2">
                      <h4 className="font-medium capitalize text-base">{condition.type}</h4>
                      <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded self-start">
                        {Math.round(condition.confidence * 100)}% confidence
                      </span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-muted-foreground">
                      <div>Severity: <span className="capitalize">{condition.characteristics.severity}</span></div>
                      <div>SCIN Match: {Math.round(condition.scin_match_score * 100)}%</div>
                      {condition.characteristics.type && (
                        <div>Type: <span className="capitalize">{condition.characteristics.type}</span></div>
                      )}
                      {condition.characteristics.color && (
                        <div>Color: <span className="capitalize">{condition.characteristics.color}</span></div>
                      )}
                      {condition.characteristics.size && (
                        <div>Size: <span className="capitalize">{condition.characteristics.size}</span></div>
                      )}
                      {condition.characteristics.texture && (
                        <div>Texture: <span className="capitalize">{condition.characteristics.texture}</span></div>
                      )}
                    </div>
                    <div className="mt-3 p-3 bg-blue-50 rounded">
                      <p className="text-sm font-medium text-blue-900">Recommendation:</p>
                      <p className="text-sm text-blue-800">{condition.recommendation}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* SCIN Similar Cases */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-lg">
                <Sparkles className="h-5 w-5 text-purple-500" />
                Similar Cases from SCIN Dataset
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {analysisResult.scin_similar_cases.map((scinCase) => (
                  <div key={scinCase.id} className="border rounded-lg p-3">
                    <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-2 mb-2">
                      <h4 className="font-medium capitalize text-base">{scinCase.condition_type}</h4>
                      <span className="text-sm bg-purple-100 text-purple-800 px-2 py-1 rounded self-start">
                        {Math.round(scinCase.similarity_score * 100)}% similar
                      </span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-muted-foreground">
                      <div>Age Group: {scinCase.age_group}</div>
                      <div>Ethnicity: {scinCase.ethnicity}</div>
                      <div className="md:col-span-2">Treatment: {scinCase.treatment_history}</div>
                      <div className="md:col-span-2">Outcome: {scinCase.outcome}</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* AI Processing Info */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">Processing Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="font-medium">Google Vision:</span>
                  <span className={`ml-2 ${analysisResult.google_vision_api ? 'text-green-600' : 'text-red-600'}`}>
                    {analysisResult.google_vision_api ? 'Available' : 'Not Available'}
                  </span>
                </div>
                <div>
                  <span className="font-medium">Image Size:</span>
                  <span className="ml-2">{analysisResult.image_size[0]}x{analysisResult.image_size[1]}</span>
                </div>
                <div>
                  <span className="font-medium">AI Level:</span>
                  <span className="ml-2 capitalize">{analysisResult.ai_level}</span>
                </div>
                <div>
                  <span className="font-medium">AI Processed:</span>
                  <span className={`ml-2 ${analysisResult.ai_processed ? 'text-green-600' : 'text-red-600'}`}>
                    {analysisResult.ai_processed ? 'Yes' : 'No'}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Medical Disclaimer */}
      <Card className="mt-4 border-orange-200 bg-orange-50">
        <CardContent className="pt-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-orange-600 mt-0.5 flex-shrink-0" />
            <div>
              <h4 className="font-medium text-orange-900 mb-1 text-sm md:text-base">Medical Disclaimer</h4>
              <p className="text-xs md:text-sm text-orange-800">
                This analysis is for informational purposes only and should not replace professional medical advice. 
                Always consult with a healthcare provider for proper diagnosis and treatment of skin conditions.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Camera Modal */}
      {showCamera && (
        <CameraCapture
          onImageCapture={(imageData: string) => {
            setSelectedImage(imageData);
            setShowCamera(false);
          }}
          onClose={() => setShowCamera(false)}
        />
      )}
    </div>
  );
} 