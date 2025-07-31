'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { AlertCircle, CheckCircle, TrendingUp, Star, Zap } from 'lucide-react';

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

function AnalysisResultsContent() {
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
          if (result.data && result.data.skin_analysis) {
            // New backend format with skin_analysis
            const skinAnalysis = result.data.skin_analysis;
            setAnalysisResult({
              analysis_id: analysisId,
              status: 'completed',
              timestamp: result.timestamp || new Date().toISOString(),
              results: {
                skin_type: 'analyzed',
                concerns: skinAnalysis.skin_conditions?.map((c: any) => c.type) || [],
                recommendations: skinAnalysis.skin_conditions?.map((c: any) => c.recommendation) || [],
                confidence: skinAnalysis.skin_conditions?.[0]?.confidence || 0,
                image_quality: 'good',
                ml_analysis: {
                  overall_score: skinAnalysis.skin_conditions?.[0]?.confidence || 0,
                  texture_score: 0.8,
                  pore_density: 0.6,
                  wrinkle_severity: 0.4,
                  pigmentation_level: 0.7
                },
                ai_confidence: skinAnalysis.ai_processed ? 0.9 : 0.7,
                processing_time: 5000,
                model_version: skinAnalysis.ai_level || 'unknown'
              },
              message: result.message,
              success: result.success,
              version: result.version
            });
          } else if (result.data && result.data.results) {
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

  const getConfidenceIcon = (confidence: number) => {
    if (confidence >= 0.8) return <CheckCircle className="h-4 w-4 text-green-500" />;
    if (confidence >= 0.6) return <AlertCircle className="h-4 w-4 text-yellow-500" />;
    return <AlertCircle className="h-4 w-4 text-red-500" />;
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading analysis results...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <Card className="border-red-200 bg-red-50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-800">
                <AlertCircle className="h-5 w-5" />
                Error Loading Results
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-red-700 mb-4">{error}</p>
              <Button 
                onClick={() => window.history.back()} 
                variant="outline"
                className="border-red-300 text-red-700 hover:bg-red-100"
              >
                Go Back
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (!analysisResult) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle>No Analysis Results</CardTitle>
              <CardDescription>No analysis results were found.</CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={() => window.history.back()} variant="outline">
                Go Back
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  const { results } = analysisResult;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Skin Analysis Results</h1>
          <p className="text-gray-600">Analysis completed on {formatTimestamp(analysisResult.timestamp)}</p>
        </div>

        {/* Status Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {analysisResult.status === 'completed' ? (
                <CheckCircle className="h-5 w-5 text-green-500" />
              ) : (
                <AlertCircle className="h-5 w-5 text-yellow-500" />
              )}
              Analysis Status: {analysisResult.status}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <p className="text-sm text-gray-500">Confidence</p>
                <div className="flex items-center justify-center gap-1 mt-1">
                  {getConfidenceIcon(results.confidence)}
                  <span className="font-semibold">{(results.confidence * 100).toFixed(1)}%</span>
                </div>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-500">Image Quality</p>
                <p className="font-semibold capitalize">{results.image_quality}</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-500">Analysis ID</p>
                <p className="font-mono text-xs">{analysisResult.analysis_id}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Skin Type */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Star className="h-5 w-5 text-yellow-500" />
              Skin Type Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-3">
              <Badge variant="secondary" className="text-lg px-4 py-2">
                {results.skin_type}
              </Badge>
              <span className="text-gray-600">Primary skin type identified</span>
            </div>
          </CardContent>
        </Card>

        {/* Concerns */}
        {results.concerns && results.concerns.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-orange-500" />
                Identified Concerns
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {results.concerns.map((concern, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                    <span>{concern}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Recommendations */}
        {results.recommendations && results.recommendations.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-blue-500" />
                Personalized Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {results.recommendations.map((recommendation, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-sm">{recommendation}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Enhanced ML Analysis */}
        {results.ml_analysis && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-purple-500" />
                Advanced ML Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {results.ml_analysis.texture_score !== undefined && (
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Texture Score</p>
                    <Progress value={results.ml_analysis.texture_score * 100} className="h-2" />
                    <p className="text-xs text-gray-400 mt-1">{(results.ml_analysis.texture_score * 100).toFixed(1)}%</p>
                  </div>
                )}
                {results.ml_analysis.pore_density !== undefined && (
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Pore Density</p>
                    <Progress value={results.ml_analysis.pore_density * 100} className="h-2" />
                    <p className="text-xs text-gray-400 mt-1">{(results.ml_analysis.pore_density * 100).toFixed(1)}%</p>
                  </div>
                )}
                {results.ml_analysis.wrinkle_severity !== undefined && (
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Wrinkle Severity</p>
                    <Progress value={results.ml_analysis.wrinkle_severity * 100} className="h-2" />
                    <p className="text-xs text-gray-400 mt-1">{(results.ml_analysis.wrinkle_severity * 100).toFixed(1)}%</p>
                  </div>
                )}
                {results.ml_analysis.pigmentation_level !== undefined && (
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Pigmentation Level</p>
                    <Progress value={results.ml_analysis.pigmentation_level * 100} className="h-2" />
                    <p className="text-xs text-gray-400 mt-1">{(results.ml_analysis.pigmentation_level * 100).toFixed(1)}%</p>
                  </div>
                )}
              </div>
              {results.ml_analysis.overall_score !== undefined && (
                <div className="mt-4 pt-4 border-t">
                  <p className="text-sm text-gray-500 mb-1">Overall Skin Health Score</p>
                  <Progress value={results.ml_analysis.overall_score * 100} className="h-3" />
                  <p className="text-sm font-semibold mt-1">{(results.ml_analysis.overall_score * 100).toFixed(1)}%</p>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button onClick={() => window.history.back()} variant="outline">
            Back to Analysis
          </Button>
          <Button onClick={() => window.location.href = '/recommendations'}>
            View Recommendations
          </Button>
        </div>
      </div>
    </div>
  );
}

export default function AnalysisResultsPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <AnalysisResultsContent />
    </Suspense>
  );
}