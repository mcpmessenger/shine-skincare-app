'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  ArrowLeft, 
  Sparkles, 
  User, 
  TrendingUp, 
  Shield, 
  Droplets, 
  Zap,
  Eye,
  Heart,
  Star,
  AlertCircle
} from 'lucide-react';
import Link from 'next/link';

interface AnalysisResult {
  success: boolean;
  analysis_id: string;
  data: {
    skin_analysis: {
      status: string;
      skinType: string;
      fitzpatrick_type: string;
      monk_tone?: number;
      concerns: string[];
      hydration: number;
      oiliness: number;
      sensitivity: number;
      recommendations: string[];
      products: Array<{
        name: string;
        category: string;
        rating: number;
        price: number;
        image: string;
        suitable_for: string;
        benefits: string[];
      }>;
      face_detection: {
        faces_found: number;
        confidence: number;
        bounding_box: any;
        landmarks: any;
      };
      enhanced_features: {
        ethnicity_considered: boolean;
        confidence_breakdown: {
          skin_type: number;
          face_detection: number;
        };
      };
    };
    similar_scin_profiles: Array<{
      profile_id: string;
      similarity_score: number;
      skin_condition: string;
      image_url: string;
      metadata: {
        age_group: string;
        skin_type: string;
        ethnicity: string;
      };
    }>;
    demographic_insights: any[];
    confidence_scores: {
      overall: number;
      face_detection: number;
      demographic: number;
      similarity_search: boolean;
    };
    metadata: {
      analysis_type: string;
      ethnicity_considered: boolean;
      age_considered: boolean;
      face_detected: boolean;
      faces_found: number;
      timestamp: string;
    };
  };
}

export default function AnalysisResultsPage() {
  const searchParams = useSearchParams();
  const analysisId = searchParams.get('analysisId');
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!analysisId) {
      setError('No analysis ID provided');
      setLoading(false);
      return;
    }

    // Try to get cached analysis result
    const cachedResult = localStorage.getItem(`analysis_${analysisId}`);
    if (cachedResult) {
      try {
        const parsed = JSON.parse(cachedResult);
        setAnalysisResult(parsed);
        setLoading(false);
      } catch (e) {
        console.error('Failed to parse cached analysis:', e);
        setError('Failed to load analysis results');
        setLoading(false);
      }
    } else {
      setError('Analysis results not found');
      setLoading(false);
    }
  }, [analysisId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p>Loading analysis results...</p>
        </div>
      </div>
    );
  }

  if (error || !analysisResult) {
    return (
      <div className="min-h-screen bg-background p-4">
        <div className="max-w-4xl mx-auto">
          <Link href="/skin-analysis" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Analysis
          </Link>
          <Card>
            <CardContent className="p-8 text-center">
              <div className="text-red-500 mb-4">
                <AlertCircle className="h-12 w-12 mx-auto" />
              </div>
              <h2 className="text-xl font-semibold mb-2">Analysis Not Found</h2>
              <p className="text-muted-foreground mb-4">{error}</p>
              <Button asChild>
                <Link href="/skin-analysis">Start New Analysis</Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  const { skin_analysis, similar_scin_profiles, confidence_scores, metadata } = analysisResult.data;

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link href="/skin-analysis" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Analysis
          </Link>
          <div className="flex items-center gap-4 mb-4">
            <div className="flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-primary" />
              <h1 className="text-3xl font-bold">Analysis Results</h1>
            </div>
            <Badge variant="secondary" className="ml-auto">
              Analysis ID: {analysisId?.slice(-8)}
            </Badge>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Results */}
          <div className="lg:col-span-2 space-y-6">
            {/* Skin Analysis Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Skin Analysis Summary
                </CardTitle>
                <CardDescription>
                  AI-powered analysis of your skin characteristics
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Skin Type */}
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold">Skin Type</h3>
                    <p className="text-muted-foreground">{skin_analysis.skinType}</p>
                  </div>
                  <Badge variant="outline">
                    Fitzpatrick Type {skin_analysis.fitzpatrick_type}
                  </Badge>
                </div>

                {/* Skin Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Droplets className="h-4 w-4 text-blue-500" />
                      <span className="text-sm font-medium">Hydration</span>
                    </div>
                    <Progress value={skin_analysis.hydration} className="h-2" />
                    <p className="text-xs text-muted-foreground">{skin_analysis.hydration}%</p>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Zap className="h-4 w-4 text-yellow-500" />
                      <span className="text-sm font-medium">Oiliness</span>
                    </div>
                    <Progress value={skin_analysis.oiliness} className="h-2" />
                    <p className="text-xs text-muted-foreground">{skin_analysis.oiliness}%</p>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Shield className="h-4 w-4 text-red-500" />
                      <span className="text-sm font-medium">Sensitivity</span>
                    </div>
                    <Progress value={skin_analysis.sensitivity} className="h-2" />
                    <p className="text-xs text-muted-foreground">{skin_analysis.sensitivity}%</p>
                  </div>
                </div>

                {/* Concerns */}
                {skin_analysis.concerns.length > 0 && (
                  <div>
                    <h3 className="font-semibold mb-2">Primary Concerns</h3>
                    <div className="flex flex-wrap gap-2">
                      {skin_analysis.concerns.map((concern, index) => (
                        <Badge key={index} variant="secondary">
                          {concern}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Face Detection Info */}
                {metadata.face_detected && (
                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <Eye className="h-4 w-4 text-green-600" />
                      <span className="font-medium text-green-800">Face Detected</span>
                    </div>
                    <p className="text-sm text-green-700">
                      {metadata.faces_found} face(s) detected with {Math.round(skin_analysis.face_detection.confidence * 100)}% confidence
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Recommendations */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Personalized Recommendations
                </CardTitle>
                <CardDescription>
                  Based on your skin analysis and similar profiles
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {skin_analysis.recommendations.map((recommendation, index) => (
                    <div key={index} className="flex items-start gap-3 p-3 bg-muted rounded-lg">
                      <Heart className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                      <p className="text-sm">{recommendation}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Product Recommendations */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Star className="h-5 w-5" />
                  Recommended Products
                </CardTitle>
                <CardDescription>
                  Products tailored to your skin type and concerns
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {skin_analysis.products.map((product, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-start gap-3">
                        <div className="w-16 h-16 bg-muted rounded-lg flex items-center justify-center">
                          <span className="text-xs text-muted-foreground">Image</span>
                        </div>
                        <div className="flex-1">
                          <h4 className="font-medium">{product.name}</h4>
                          <p className="text-sm text-muted-foreground">{product.category}</p>
                          <div className="flex items-center gap-2 mt-2">
                            <div className="flex items-center gap-1">
                              <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                              <span className="text-xs">{product.rating}</span>
                            </div>
                            <span className="text-sm font-medium">${product.price}</span>
                          </div>
                          <div className="mt-2">
                            {product.benefits.slice(0, 2).map((benefit, idx) => (
                              <Badge key={idx} variant="outline" className="text-xs mr-1">
                                {benefit}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Confidence Scores */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Analysis Confidence</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm">Overall Confidence</span>
                  <span className="text-sm font-medium">{Math.round(confidence_scores.overall * 100)}%</span>
                </div>
                <Progress value={confidence_scores.overall * 100} className="h-2" />
                
                <div className="flex justify-between">
                  <span className="text-sm">Face Detection</span>
                  <span className="text-sm font-medium">{Math.round(confidence_scores.face_detection * 100)}%</span>
                </div>
                <Progress value={confidence_scores.face_detection * 100} className="h-2" />
                
                <div className="flex justify-between">
                  <span className="text-sm">Skin Classification</span>
                  <span className="text-sm font-medium">{Math.round(skin_analysis.enhanced_features.confidence_breakdown.skin_type * 100)}%</span>
                </div>
                <Progress value={skin_analysis.enhanced_features.confidence_breakdown.skin_type * 100} className="h-2" />
              </CardContent>
            </Card>

            {/* Similar SCIN Profiles */}
            {similar_scin_profiles.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Similar Profiles</CardTitle>
                  <CardDescription>
                    Found {similar_scin_profiles.length} similar skin profiles
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {similar_scin_profiles.slice(0, 3).map((profile, index) => (
                      <div key={index} className="flex items-center gap-3 p-2 bg-muted rounded">
                        <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center">
                          <span className="text-xs font-medium">{index + 1}</span>
                        </div>
                        <div className="flex-1">
                          <p className="text-sm font-medium">{profile.skin_condition}</p>
                          <p className="text-xs text-muted-foreground">
                            {Math.round(profile.similarity_score * 100)}% similarity
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Analysis Metadata */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Analysis Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Analysis Type</span>
                  <span className="font-medium">{metadata.analysis_type}</span>
                </div>
                <div className="flex justify-between">
                  <span>Ethnicity Considered</span>
                  <span className="font-medium">{metadata.ethnicity_considered ? 'Yes' : 'No'}</span>
                </div>
                <div className="flex justify-between">
                  <span>Age Considered</span>
                  <span className="font-medium">{metadata.age_considered ? 'Yes' : 'No'}</span>
                </div>
                <div className="flex justify-between">
                  <span>Timestamp</span>
                  <span className="font-medium">
                    {new Date(metadata.timestamp).toLocaleDateString()}
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
} 