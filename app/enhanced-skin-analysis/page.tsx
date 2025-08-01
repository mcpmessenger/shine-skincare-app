'use client';

import React, { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Upload, Sparkles, AlertCircle, CheckCircle, Loader2, Search, Camera, Zap, Shield } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/hooks/use-toast';
import Image from 'next/image';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface EnhancedAnalysisResult {
  success: boolean;
  analysis: {
    skin_type: string;
    concerns: string[];
    recommendations: string[];
    metrics: {
      hydration: number;
      oiliness: number;
      sensitivity: number;
    };
    confidence_score: number;
    similar_conditions: Array<{
      id: string;
      similarity_score: number;
      condition_type: string;
      age_group: string;
      ethnicity: string;
      treatment_history: string;
      outcome: string;
    }>;
  };
  products: Array<{
    id: string;
    name: string;
    brand: string;
    price: number;
    rating: number;
    image_urls: string[];
    description: string;
    category: string;
    subcategory: string;
  }>;
  face_detected: boolean;
  ai_processed: boolean;
  enhanced_features: {
    openai_embeddings: boolean;
    google_vision: boolean;
    scin_dataset: boolean;
    face_isolation: boolean;
  };
}

export default function EnhancedSkinAnalysisPage() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<EnhancedAnalysisResult | null>(null);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [age, setAge] = useState<string>('');
  const [ethnicity, setEthnicity] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  const handleCameraCapture = () => {
    // Implement camera capture functionality
    toast({
      title: "Camera Feature",
      description: "Camera capture will be implemented in the next update.",
      variant: "default",
    });
  };

  const analyzeSkinImage = async () => {
    if (!selectedImage) {
      toast({
        title: "No Image Selected",
        description: "Please upload an image first.",
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
      const file = new File([blob], 'skin.jpg', { type: 'image/jpeg' });

      // Create FormData
      const formData = new FormData();
      formData.append('image', file);
      if (age) formData.append('age', age);
      if (ethnicity) formData.append('ethnicity', ethnicity);

      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 500);

      // Make API call to enhanced endpoint
      const apiResponse = await fetch('/api/v3/skin/analyze-enhanced', {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);
      setProgress(100);

      if (!apiResponse.ok) {
        const errorData = await apiResponse.json();
        throw new Error(errorData.error || 'Analysis failed');
      }

      const result: EnhancedAnalysisResult = await apiResponse.json();
      setAnalysisResult(result);

      toast({
        title: "Analysis Complete",
        description: "Your enhanced skin analysis is ready!",
        variant: "default",
      });

    } catch (error) {
      console.error('Analysis error:', error);
      toast({
        title: "Analysis Failed",
        description: error instanceof Error ? error.message : "Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsAnalyzing(false);
      setProgress(0);
    }
  };

  const getSkinTypeColor = (skinType: string) => {
    const colors = {
      'oily': 'bg-blue-100 text-blue-800',
      'dry': 'bg-orange-100 text-orange-800',
      'combination': 'bg-purple-100 text-purple-800',
      'sensitive': 'bg-red-100 text-red-800',
      'normal': 'bg-green-100 text-green-800',
      'mature': 'bg-gray-100 text-gray-800'
    };
    return colors[skinType as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Enhanced Skin Analysis
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Get AI-powered skin analysis using advanced OpenAI embeddings and medical-grade SCIN dataset matching.
        </p>
      </div>

      {/* Feature Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card className="text-center p-4">
          <Zap className="w-8 h-8 mx-auto mb-2 text-blue-600" />
          <h3 className="font-semibold">OpenAI Embeddings</h3>
          <p className="text-sm text-gray-600">Advanced AI analysis</p>
        </Card>
        <Card className="text-center p-4">
          <Shield className="w-8 h-8 mx-auto mb-2 text-green-600" />
          <h3 className="font-semibold">Medical Grade</h3>
          <p className="text-sm text-gray-600">SCIN dataset matching</p>
        </Card>
        <Card className="text-center p-4">
          <Search className="w-8 h-8 mx-auto mb-2 text-purple-600" />
          <h3 className="font-semibold">Face Isolation</h3>
          <p className="text-sm text-gray-600">Google Vision API</p>
        </Card>
        <Card className="text-center p-4">
          <Sparkles className="w-8 h-8 mx-auto mb-2 text-pink-600" />
          <h3 className="font-semibold">Smart Recommendations</h3>
          <p className="text-sm text-gray-600">Personalized results</p>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upload Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Camera className="w-5 h-5" />
              Upload Your Photo
            </CardTitle>
            <CardDescription>
              Take a clear, well-lit photo of your face for the most accurate analysis
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Image Upload */}
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              {selectedImage ? (
                <div className="space-y-4">
                  <Image
                    src={selectedImage}
                    alt="Selected skin"
                    width={300}
                    height={300}
                    className="mx-auto rounded-lg object-cover"
                  />
                  <Button
                    variant="outline"
                    onClick={() => setSelectedImage(null)}
                    className="w-full"
                  >
                    Remove Image
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  <Upload className="w-12 h-12 mx-auto text-gray-400" />
                  <div>
                    <Button
                      variant="outline"
                      onClick={() => fileInputRef.current?.click()}
                      className="w-full"
                    >
                      Choose Image
                    </Button>
                    <p className="text-sm text-gray-500 mt-2">
                      or drag and drop
                    </p>
                  </div>
                </div>
              )}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
              />
            </div>

            {/* Additional Information */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">Age (optional)</label>
                <input
                  type="number"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  placeholder="25"
                  className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              <div>
                <label className="text-sm font-medium">Ethnicity (optional)</label>
                <input
                  type="text"
                  value={ethnicity}
                  onChange={(e) => setEthnicity(e.target.value)}
                  placeholder="Asian"
                  className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
            </div>

            {/* Analyze Button */}
            <Button
              onClick={analyzeSkinImage}
              disabled={!selectedImage || isAnalyzing}
              className="w-full"
              size="lg"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  Analyze with AI
                </>
              )}
            </Button>

            {/* Progress Bar */}
            {isAnalyzing && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Processing...</span>
                  <span>{progress}%</span>
                </div>
                <Progress value={progress} className="w-full" />
              </div>
            )}
          </CardContent>
        </Card>

        {/* Results Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="w-5 h-5" />
              Analysis Results
            </CardTitle>
            <CardDescription>
              Your personalized skin analysis and recommendations
            </CardDescription>
          </CardHeader>
          <CardContent>
            {analysisResult ? (
              <Tabs defaultValue="overview" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="overview">Overview</TabsTrigger>
                  <TabsTrigger value="details">Details</TabsTrigger>
                  <TabsTrigger value="products">Products</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="space-y-4">
                  {/* Skin Type */}
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <h3 className="font-semibold">Skin Type</h3>
                      <p className="text-sm text-gray-600">Primary classification</p>
                    </div>
                    <Badge className={getSkinTypeColor(analysisResult.analysis.skin_type)}>
                      {analysisResult.analysis.skin_type}
                    </Badge>
                  </div>

                  {/* Confidence Score */}
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <h3 className="font-semibold">AI Confidence</h3>
                      <p className="text-sm text-gray-600">Analysis accuracy</p>
                    </div>
                    <Badge variant="secondary">
                      {(analysisResult.analysis.confidence_score * 100).toFixed(1)}%
                    </Badge>
                  </div>

                  {/* Concerns */}
                  <div className="space-y-2">
                    <h3 className="font-semibold">Primary Concerns</h3>
                    <div className="flex flex-wrap gap-2">
                      {analysisResult.analysis.concerns.map((concern, index) => (
                        <Badge key={index} variant="outline">
                          {concern}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* Metrics */}
                  <div className="space-y-2">
                    <h3 className="font-semibold">Skin Metrics</h3>
                    <div className="grid grid-cols-3 gap-4">
                      <div className="text-center p-3 bg-blue-50 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">
                          {analysisResult.analysis.metrics.hydration}%
                        </div>
                        <div className="text-sm text-gray-600">Hydration</div>
                      </div>
                      <div className="text-center p-3 bg-green-50 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">
                          {analysisResult.analysis.metrics.oiliness}%
                        </div>
                        <div className="text-sm text-gray-600">Oil Control</div>
                      </div>
                      <div className="text-center p-3 bg-orange-50 rounded-lg">
                        <div className="text-2xl font-bold text-orange-600">
                          {analysisResult.analysis.metrics.sensitivity}%
                        </div>
                        <div className="text-sm text-gray-600">Sensitivity</div>
                      </div>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="details" className="space-y-4">
                  {/* Recommendations */}
                  <div className="space-y-2">
                    <h3 className="font-semibold">Recommendations</h3>
                    <div className="space-y-2">
                      {analysisResult.analysis.recommendations.map((rec, index) => (
                        <div key={index} className="flex items-start gap-2 p-3 bg-blue-50 rounded-lg">
                          <CheckCircle className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                          <p className="text-sm">{rec}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Similar Cases */}
                  {analysisResult.analysis.similar_conditions.length > 0 && (
                    <div className="space-y-2">
                      <h3 className="font-semibold">Similar Medical Cases</h3>
                      <div className="space-y-2">
                        {analysisResult.analysis.similar_conditions.map((case_, index) => (
                          <div key={index} className="p-3 bg-gray-50 rounded-lg">
                            <div className="flex justify-between items-start mb-2">
                              <Badge variant="secondary">
                                {case_.condition_type}
                              </Badge>
                              <span className="text-sm text-gray-600">
                                {(case_.similarity_score * 100).toFixed(1)}% match
                              </span>
                            </div>
                            <p className="text-sm text-gray-600 mb-1">
                              Age: {case_.age_group} | Ethnicity: {case_.ethnicity}
                            </p>
                            <p className="text-sm text-gray-600 mb-1">
                              Treatment: {case_.treatment_history}
                            </p>
                            <p className="text-sm text-gray-600">
                              Outcome: {case_.outcome}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="products" className="space-y-4">
                  <h3 className="font-semibold">Recommended Products</h3>
                  <div className="space-y-4">
                    {analysisResult.products.map((product) => (
                      <div key={product.id} className="flex gap-4 p-4 border rounded-lg">
                        <div className="w-16 h-16 bg-gray-200 rounded-lg flex-shrink-0">
                          {product.image_urls[0] && (
                            <Image
                              src={product.image_urls[0]}
                              alt={product.name}
                              width={64}
                              height={64}
                              className="w-full h-full object-cover rounded-lg"
                            />
                          )}
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold">{product.name}</h4>
                          <p className="text-sm text-gray-600">{product.brand}</p>
                          <p className="text-sm text-gray-600 mt-1">{product.description}</p>
                          <div className="flex items-center gap-4 mt-2">
                            <span className="text-lg font-bold">${product.price}</span>
                            <div className="flex items-center gap-1">
                              <span className="text-sm">★</span>
                              <span className="text-sm">{product.rating}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </TabsContent>
              </Tabs>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Sparkles className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>Upload a photo to get your enhanced skin analysis</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 