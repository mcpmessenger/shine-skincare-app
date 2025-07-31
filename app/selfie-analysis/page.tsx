'use client';

import React, { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Camera, Upload, Sparkles, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { analyzeSelfie } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import Image from 'next/image';

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

      const result = await analyzeSelfie(file);
      
      clearInterval(progressInterval);
      setProgress(100);
      
      setAnalysisResult(result.selfie_analysis);
      
      toast({
        title: "Analysis Complete",
        description: `Found ${result.selfie_analysis.total_conditions} skin conditions with ${result.selfie_analysis.ai_level} AI processing.`,
        variant: "default",
      });

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
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-2">Selfie Skin Analysis</h1>
        <p className="text-muted-foreground">
          Upload a selfie for advanced skin condition analysis with Google Vision API face isolation
        </p>
      </div>

      {/* Image Upload/Capture Section */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Camera className="h-5 w-5" />
            Capture or Upload Selfie
          </CardTitle>
          <CardDescription>
            Take a photo or upload an image for skin condition analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Camera Capture */}
          <div className="space-y-2">
            <Button onClick={handleCameraCapture} variant="outline" className="w-full">
              <Camera className="h-4 w-4 mr-2" />
              Open Camera
            </Button>
            
            {videoRef.current?.srcObject && (
              <div className="relative">
                <video
                  ref={videoRef}
                  className="w-full max-w-md mx-auto border rounded-lg"
                  autoPlay
                  playsInline
                />
                <Button onClick={capturePhoto} className="mt-2">
                  Capture Photo
                </Button>
                <canvas ref={canvasRef} className="hidden" />
              </div>
            )}
          </div>

          {/* File Upload */}
          <div className="space-y-2">
            <Button 
              onClick={() => fileInputRef.current?.click()} 
              variant="outline" 
              className="w-full"
            >
              <Upload className="h-4 w-4 mr-2" />
              Upload Image
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
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Selected Image:</p>
              <div className="relative w-full max-w-md mx-auto">
                <Image
                  src={selectedImage}
                  alt="Selected selfie"
                  width={400}
                  height={300}
                  className="rounded-lg border"
                />
                <Button 
                  onClick={analyzeSelfieImage}
                  disabled={isAnalyzing}
                  className="mt-2 w-full"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4 mr-2" />
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
                <span>Processing with Google Vision API...</span>
                <span>{progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analysisResult && (
        <div className="space-y-6">
          {/* Facial Features */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-500" />
                Face Detection Results
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">Face Detected:</span>
                  <span className={`ml-2 ${analysisResult.facial_features.face_detected ? 'text-green-600' : 'text-red-600'}`}>
                    {analysisResult.facial_features.face_detected ? 'Yes' : 'No'}
                  </span>
                </div>
                <div>
                  <span className="font-medium">Face Isolated:</span>
                  <span className={`ml-2 ${analysisResult.facial_features.face_isolated ? 'text-green-600' : 'text-red-600'}`}>
                    {analysisResult.facial_features.face_isolated ? 'Yes' : 'No'}
                  </span>
                </div>
                <div>
                  <span className="font-medium">Landmarks Found:</span>
                  <span className="ml-2">{analysisResult.facial_features.landmarks.length}</span>
                </div>
                <div>
                  <span className="font-medium">AI Level:</span>
                  <span className="ml-2 capitalize">{analysisResult.ai_level}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Skin Conditions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-orange-500" />
                Detected Skin Conditions ({analysisResult.total_conditions})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analysisResult.skin_conditions.map((condition, index) => (
                  <div key={condition.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-medium capitalize">{condition.type}</h4>
                      <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        {Math.round(condition.confidence * 100)}% confidence
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-sm text-muted-foreground">
                      <div>Severity: <span className="capitalize">{condition.characteristics.severity}</span></div>
                      <div>SCIN Match: {Math.round(condition.scin_match_score * 100)}%</div>
                      {condition.characteristics.type && (
                        <div>Type: <span className="capitalize">{condition.characteristics.type}</span></div>
                      )}
                      {condition.characteristics.color && (
                        <div>Color: <span className="capitalize">{condition.characteristics.color}</span></div>
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
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-purple-500" />
                Similar Cases from SCIN Dataset
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {analysisResult.scin_similar_cases.map((scinCase) => (
                  <div key={scinCase.id} className="border rounded-lg p-3">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-medium capitalize">{scinCase.condition_type}</h4>
                      <span className="text-sm bg-purple-100 text-purple-800 px-2 py-1 rounded">
                        {Math.round(scinCase.similarity_score * 100)}% similar
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-sm text-muted-foreground">
                      <div>Age Group: {scinCase.age_group}</div>
                      <div>Ethnicity: {scinCase.ethnicity}</div>
                      <div className="col-span-2">Treatment: {scinCase.treatment_history}</div>
                      <div className="col-span-2">Outcome: {scinCase.outcome}</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* AI Processing Info */}
          <Card>
            <CardHeader>
              <CardTitle>Processing Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">Google Vision API:</span>
                  <span className={`ml-2 ${analysisResult.google_vision_api ? 'text-green-600' : 'text-red-600'}`}>
                    {analysisResult.google_vision_api ? 'Available' : 'Not Available'}
                  </span>
                </div>
                <div>
                  <span className="font-medium">SCIN Dataset:</span>
                  <span className={`ml-2 ${analysisResult.scin_dataset ? 'text-green-600' : 'text-red-600'}`}>
                    {analysisResult.scin_dataset ? 'Available' : 'Not Available'}
                  </span>
                </div>
                <div>
                  <span className="font-medium">Image Size:</span>
                  <span className="ml-2">{analysisResult.image_size[0]}x{analysisResult.image_size[1]}</span>
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
      <Card className="mt-6 border-orange-200 bg-orange-50">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-orange-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-orange-900 mb-1">Medical Disclaimer</h4>
              <p className="text-sm text-orange-800">
                This analysis is for informational purposes only and should not replace professional medical advice. 
                Always consult with a healthcare provider for proper diagnosis and treatment of skin conditions.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 