'use client';

import { useState, useRef } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Camera, Upload, FileImage, AlertTriangle, CheckCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface MedicalAnalysisResult {
  analysis_id: string;
  condition: {
    name: string;
    confidence: number;
    description: string;
  };
  treatments: string[];
  similar_conditions: any[];
  image_url: string;
  analysis_timestamp: string;
}

export default function MedicalAnalysisPage() {
  const { user, isAuthenticated } = useAuth();
  const { toast } = useToast();
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<MedicalAnalysisResult | null>(null);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setSelectedImage(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const captureImage = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');

      if (context) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0);
        
        const imageData = canvas.toDataURL('image/jpeg');
        setSelectedImage(imageData);
      }
    }
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          facingMode: 'environment',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        } 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (error) {
      toast({
        title: "Camera Error",
        description: "Unable to access camera. Please check permissions.",
        variant: "destructive",
      });
    }
  };

  const analyzeImage = async () => {
    if (!selectedImage) {
      toast({
        title: "No Image",
        description: "Please select or capture an image first.",
        variant: "destructive",
      });
      return;
    }

    setIsAnalyzing(true);
    setUploadProgress(0);

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const response = await fetch('/api/v2/medical/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(user && { 'Authorization': `Bearer ${user.id}` })
        },
        body: JSON.stringify({
          image_data: selectedImage
        })
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const result = await response.json();
      setAnalysisResult(result);

      toast({
        title: "Analysis Complete",
        description: `Identified: ${result.condition.name} (${(result.condition.confidence * 100).toFixed(1)}% confidence)`,
      });

    } catch (error) {
      toast({
        title: "Analysis Failed",
        description: "Unable to analyze image. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsAnalyzing(false);
      setUploadProgress(0);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-green-500';
    if (confidence >= 0.6) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getConditionColor = (condition: string) => {
    const colors: { [key: string]: string } = {
      'acne': 'bg-red-100 text-red-800',
      'eczema': 'bg-orange-100 text-orange-800',
      'psoriasis': 'bg-purple-100 text-purple-800',
      'rosacea': 'bg-pink-100 text-pink-800',
      'melasma': 'bg-brown-100 text-brown-800'
    };
    return colors[condition] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Medical Skin Analysis
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Analyze skin conditions for medical insights and treatment recommendations
        </p>
      </div>

      {!isAuthenticated && (
        <Alert className="mb-6">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            You're using the app as a guest. Sign up to save your analysis history.
          </AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Image Upload/Capture Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileImage className="h-5 w-5" />
              Upload or Capture Image
            </CardTitle>
            <CardDescription>
              Take a photo or upload an image of the skin area you want to analyze
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Camera Section */}
            <div className="space-y-2">
              <Button onClick={startCamera} variant="outline" className="w-full">
                <Camera className="h-4 w-4 mr-2" />
                Start Camera
              </Button>
              
              <div className="relative">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  className="w-full h-64 object-cover rounded-lg border"
                />
                <canvas ref={canvasRef} className="hidden" />
                
                {videoRef.current?.srcObject && (
                  <Button
                    onClick={captureImage}
                    className="absolute bottom-2 right-2"
                    size="sm"
                  >
                    Capture
                  </Button>
                )}
              </div>
            </div>

            {/* File Upload Section */}
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
                onChange={handleFileUpload}
                className="hidden"
              />
            </div>

            {/* Selected Image Preview */}
            {selectedImage && (
              <div className="space-y-2">
                <p className="text-sm font-medium">Selected Image:</p>
                <img
                  src={selectedImage}
                  alt="Selected"
                  className="w-full h-48 object-cover rounded-lg border"
                />
                <Button
                  onClick={analyzeImage}
                  disabled={isAnalyzing}
                  className="w-full"
                >
                  {isAnalyzing ? 'Analyzing...' : 'Analyze Skin Condition'}
                </Button>
              </div>
            )}

            {/* Progress Bar */}
            {isAnalyzing && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Analyzing image...</span>
                  <span>{uploadProgress}%</span>
                </div>
                <Progress value={uploadProgress} className="w-full" />
              </div>
            )}
          </CardContent>
        </Card>

        {/* Analysis Results */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5" />
              Analysis Results
            </CardTitle>
            <CardDescription>
              Detailed analysis of detected skin conditions
            </CardDescription>
          </CardHeader>
          <CardContent>
            {analysisResult ? (
              <div className="space-y-4">
                {/* Primary Condition */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold">Primary Condition</h3>
                    <Badge className={getConditionColor(analysisResult.condition.name)}>
                      {analysisResult.condition.name}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-600">Confidence:</span>
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${getConfidenceColor(analysisResult.condition.confidence)}`}
                        style={{ width: `${analysisResult.condition.confidence * 100}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium">
                      {(analysisResult.condition.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>

                {/* Description */}
                <div className="space-y-2">
                  <h4 className="font-medium">Description</h4>
                  <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                    {analysisResult.condition.description}
                  </p>
                </div>

                {/* Recommended Treatments */}
                <div className="space-y-2">
                  <h4 className="font-medium">Recommended Treatments</h4>
                  <ul className="space-y-1">
                    {analysisResult.treatments.map((treatment, index) => (
                      <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                        <span className="text-green-500 mt-1">•</span>
                        {treatment}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Similar Conditions */}
                {analysisResult.similar_conditions.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="font-medium">Similar Conditions</h4>
                    <div className="flex flex-wrap gap-2">
                      {analysisResult.similar_conditions.slice(0, 3).map((condition, index) => (
                        <Badge key={index} variant="outline">
                          {condition.name}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Analysis Timestamp */}
                <div className="text-xs text-gray-500 pt-2 border-t">
                  Analyzed on: {new Date(analysisResult.analysis_timestamp).toLocaleString()}
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <FileImage className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No analysis results yet</p>
                <p className="text-sm">Upload or capture an image to get started</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Medical Disclaimer */}
      <Card className="mt-6">
        <CardContent className="pt-6">
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              <strong>Medical Disclaimer:</strong> This analysis is for informational purposes only and should not replace professional medical advice. Always consult with a qualified healthcare provider for proper diagnosis and treatment.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    </div>
  );
} 