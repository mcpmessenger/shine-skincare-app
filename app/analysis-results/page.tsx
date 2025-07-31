'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { AlertCircle, CheckCircle, TrendingUp, Star, Zap, Shield, Target, Users, Clock, Award } from 'lucide-react';

// Enhanced Analysis Result Interface
interface EnhancedAnalysisResult {
  analysis_id: string;
  status: string;
  timestamp: string;
  results: {
    skin_type: string;
    concerns: string[];
    recommendations: string[];
    confidence: number;
    image_quality: string;
    // Enhanced fields
    ml_analysis?: {
      texture_score?: number;
      pore_density?: number;
      wrinkle_severity?: number;
      pigmentation_level?: number;
      overall_score?: number;
    };
    ai_confidence?: number;
    processing_time?: number;
    model_version?: string;
  };
  message?: string;
  success?: boolean;
  version?: string;
}

export default function AnalysisResultsPage() {
  const [analysisResult, setAnalysisResult] = useState<EnhancedAnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const searchParams = useSearchParams();

  useEffect(() => {
    const loadAnalysisResult = async () => {
      try {
        const analysisId = searchParams.get('analysisId');
        
        console.log('Analysis Results Page - Received analysisId:', analysisId);
        console.log('Analysis Results Page - All search params:', Object.fromEntries(searchParams.entries()));
        console.log('Analysis Results Page - Current URL:', window.location.href);

        if (!analysisId) {
          console.log('Analysis Results Page - No analysisId found, setting error');
          setError('No analysis ID provided');
          setLoading(false);
          return;
        }

        // Get analysis result from localStorage with enhanced error handling
        if (typeof window === 'undefined') {
          console.log('Analysis Results Page - Server-side rendering, skipping localStorage access');
          setLoading(false);
          return;
        }

        console.log('Analysis Results Page - Looking for analysis result:', {
          analysisId,
          localStorageKeys: Object.keys(localStorage).filter(key => key.startsWith('analysis_'))
        });

        const storedResult = localStorage.getItem(`analysis_${analysisId}`);
        
        if (storedResult) {
          console.log('Analysis Results Page - Found analysis result:', storedResult);
          const result = JSON.parse(storedResult);
          
          // Enhanced data structure handling for both old and new formats
          if (result.data && result.data.results) {
            setAnalysisResult(result.data);
          } else if (result.results) {
            setAnalysisResult(result);
          } else {
            setError('Invalid analysis result format');
          }
        } else {
          setError('Analysis result not found');
        }
      } catch (err) {
        console.error('Analysis Results Page - Failed to load analysis result:', err);
        setError('Failed to load analysis result');
      } finally {
        setLoading(false);
      }
    };

    loadAnalysisResult();
  }, [searchParams]);

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceIcon = (confidence: number) => {
    if (confidence >= 0.8) return <CheckCircle className="h-4 w-4" />;
    if (confidence >= 0.6) return <AlertCircle className="h-4 w-4" />;
    return <AlertCircle className="h-4 w-4" />;
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="mt-4 text-lg">Loading analysis results...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle className="text-destructive flex items-center gap-2">
              <AlertCircle className="h-5 w-5" />
              Error
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">{error}</p>
            <Button 
              onClick={() => window.history.back()} 
              className="mt-4"
            >
              Go Back
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!analysisResult) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle className="text-destructive">No Results</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">No analysis results found.</p>
            <Button 
              onClick={() => window.history.back()} 
              className="mt-4"
            >
              Go Back
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Extract analysis data with fallback handling
  let analysisData = analysisResult.results;
  
  // Handle different response formats
  if (analysisResult.data && analysisResult.data.results) {
    analysisData = analysisResult.data.results;
  } else if (analysisResult.results) {
    analysisData = analysisResult.results;
  }

  console.log('Extracted analysis data:', analysisData);

  if (!analysisData) {
    console.log('Analysis result not found in localStorage');
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle className="text-destructive">No Analysis Data</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">No analysis data found.</p>
            <Button 
              onClick={() => window.history.back()} 
              className="mt-4"
            >
              Go Back
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  try {
    console.error('Failed to load analysis result:', err);
  } catch (err) {
    console.error('Failed to load analysis result:', err);
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-2">Your Enhanced Analysis Results</h1>
          <p className="text-muted-foreground">
            Analysis completed on {formatTimestamp(analysisResult.timestamp)}
          </p>
        </div>

        {/* Enhanced Analysis Summary */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-primary" />
              Enhanced Skin Analysis Summary
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="font-semibold mb-2">Skin Type</h3>
                <Badge variant="secondary" className="text-sm">
                  {analysisData.skin_type || 'Not detected'}
                </Badge>
              </div>
              <div>
                <h3 className="font-semibold mb-2">Confidence Score</h3>
                <div className="flex items-center gap-2">
                  {getConfidenceIcon(analysisData.confidence || 0)}
                  <span className={getConfidenceColor(analysisData.confidence || 0)}>
                    {(analysisData.confidence || 0) * 100}%
                  </span>
                </div>
              </div>
            </div>

            {/* Enhanced Analysis Fields */}
            {analysisData.ml_analysis && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <Target className="h-6 w-6 text-blue-600 mx-auto mb-2" />
                  <p className="text-sm font-medium">Texture Score</p>
                  <p className="text-lg font-bold text-blue-600">
                    {analysisData.ml_analysis.texture_score?.toFixed(2) || 'N/A'}
                  </p>
                </div>
                <div className="text-center p-3 bg-green-50 rounded-lg">
                  <Shield className="h-6 w-6 text-green-600 mx-auto mb-2" />
                  <p className="text-sm font-medium">Pore Density</p>
                  <p className="text-lg font-bold text-green-600">
                    {analysisData.ml_analysis.pore_density?.toFixed(2) || 'N/A'}
                  </p>
                </div>
                <div className="text-center p-3 bg-yellow-50 rounded-lg">
                  <TrendingUp className="h-6 w-6 text-yellow-600 mx-auto mb-2" />
                  <p className="text-sm font-medium">Wrinkle Severity</p>
                  <p className="text-lg font-bold text-yellow-600">
                    {analysisData.ml_analysis.wrinkle_severity?.toFixed(2) || 'N/A'}
                  </p>
                </div>
                <div className="text-center p-3 bg-purple-50 rounded-lg">
                  <Star className="h-6 w-6 text-purple-600 mx-auto mb-2" />
                  <p className="text-sm font-medium">Overall Score</p>
                  <p className="text-lg font-bold text-purple-600">
                    {analysisData.ml_analysis.overall_score?.toFixed(2) || 'N/A'}
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Enhanced Product Recommendations */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="h-5 w-5 text-primary" />
              Recommended Products
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analysisData.recommendations?.map((rec, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                  <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                  <p className="text-sm">{rec}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Enhanced Ingredient Analysis */}
        <Card>
          <CardHeader>
            <CardTitle>Ingredient Analysis</CardTitle>
            <CardDescription>
              Based on your skin analysis, here are the ingredients that would benefit you most
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {analysisData.concerns?.map((concern, index) => (
                <div key={index} className="p-4 border rounded-lg">
                  <h4 className="font-semibold mb-2">{concern}</h4>
                  <p className="text-sm text-muted-foreground">
                    Recommended ingredients for this concern
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Enhanced Product Card Component */}
        <Card>
          <CardHeader>
            <CardTitle>Product Matching</CardTitle>
            <CardDescription>
              Products that match your skin profile
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold">Gentle Cleanser</h4>
                  <Badge variant="outline">95% Match</Badge>
                </div>
                <p className="text-sm text-muted-foreground mb-2">
                  Matching Ingredients:
                </p>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="secondary" className="text-xs">Hyaluronic Acid</Badge>
                  <Badge variant="secondary" className="text-xs">Ceramides</Badge>
                  <Badge variant="secondary" className="text-xs">Niacinamide</Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex gap-4 justify-center">
          <Button onClick={() => window.history.back()}>
            Back to Analysis
          </Button>
          <Button variant="outline">
            Save Results
          </Button>
        </div>
      </div>
    </div>
  );
}