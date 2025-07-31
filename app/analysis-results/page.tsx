'use client';

import { useEffect, useState, Suspense } from 'react';
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

function AnalysisResultsContent() {
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

    // Get analysis result from localStorage
    try {
      console.log('🔍 Looking for analysis result:', {
        analysisId,
        storage_key: `analysis_${analysisId}`,
        available_keys: Object.keys(localStorage).filter(key => key.startsWith('analysis_'))
      });
      
      const storedResult = localStorage.getItem(`analysis_${analysisId}`);
      if (storedResult) {
        const result = JSON.parse(storedResult);
        console.log('🔍 Found analysis result:', result);
        setAnalysisResult(result);
      } else {
        console.log('🔍 Analysis result not found in localStorage');
        setError('Analysis result not found');
      }
    } catch (err) {
      console.error('🔍 Error loading analysis result:', err);
      setError('Failed to load analysis result');
    } finally {
      setLoading(false);
    }
  }, [analysisId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading analysis results...</p>
        </div>
      </div>
    );
  }

  if (error || !analysisResult) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-5 w-5" />
              Error
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">{error || 'Analysis result not found'}</p>
            <Link href="/skin-analysis">
              <Button className="w-full">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Analysis
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  const { data } = analysisResult;
  const { skin_analysis, similar_scin_profiles, confidence_scores, metadata } = data;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link href="/skin-analysis">
            <Button variant="ghost" className="mb-4">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Analysis
            </Button>
          </Link>
          <div className="flex items-center gap-3 mb-4">
            <Sparkles className="h-8 w-8 text-purple-600" />
            <h1 className="text-3xl font-bold text-gray-900">AI-Powered Skin Analysis Results</h1>
          </div>
          <p className="text-gray-600">Comprehensive analysis of your skin using advanced AI technology</p>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Main Analysis Results */}
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
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Skin Type</p>
                    <p className="text-lg font-semibold">{skin_analysis.skinType}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">Fitzpatrick Type</p>
                    <p className="text-lg font-semibold">{skin_analysis.fitzpatrick_type}</p>
                  </div>
                </div>

                {/* Skin Metrics */}
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Hydration</span>
                      <span>{skin_analysis.hydration}%</span>
                    </div>
                    <Progress value={skin_analysis.hydration} className="h-2" />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Oiliness</span>
                      <span>{skin_analysis.oiliness}%</span>
                    </div>
                    <Progress value={skin_analysis.oiliness} className="h-2" />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Sensitivity</span>
                      <span>{skin_analysis.sensitivity}%</span>
                    </div>
                    <Progress value={skin_analysis.sensitivity} className="h-2" />
                  </div>
                </div>

                {/* Primary Concerns */}
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-2">Primary Concerns</p>
                  <div className="flex flex-wrap gap-2">
                    {skin_analysis.concerns.map((concern, index) => (
                      <Badge key={index} variant="secondary">
                        {concern}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Face Detection Info */}
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Eye className="h-4 w-4 text-blue-600" />
                    <span className="font-medium text-blue-900">Face Detection</span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Faces Found:</span>
                      <span className="ml-2 font-medium">{skin_analysis.face_detection.faces_found}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Confidence:</span>
                      <span className="ml-2 font-medium">{(skin_analysis.face_detection.confidence * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Personalized Recommendations */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5" />
                  Personalized Recommendations
                </CardTitle>
                <CardDescription>
                  AI-generated recommendations based on your skin analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {skin_analysis.recommendations.map((recommendation, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <div className="w-2 h-2 bg-purple-600 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-gray-700">{recommendation}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            {/* Recommended Products */}
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
                <div className="grid gap-4 md:grid-cols-2">
                  {skin_analysis.products.map((product, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-start gap-3">
                        <div className="w-16 h-16 bg-gray-200 rounded-lg flex-shrink-0"></div>
                        <div className="flex-1">
                          <h4 className="font-semibold">{product.name}</h4>
                          <p className="text-sm text-gray-600">{product.category}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <div className="flex">
                              {[...Array(5)].map((_, i) => (
                                <Star key={i} className={`h-3 w-3 ${i < product.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`} />
                              ))}
                            </div>
                            <span className="text-sm text-gray-600">${product.price}</span>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">Suitable for: {product.suitable_for}</p>
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
            {/* Analysis Confidence */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Analysis Confidence
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Overall</span>
                    <span>{(confidence_scores.overall * 100).toFixed(1)}%</span>
                  </div>
                  <Progress value={confidence_scores.overall * 100} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Face Detection</span>
                    <span>{(confidence_scores.face_detection * 100).toFixed(1)}%</span>
                  </div>
                  <Progress value={confidence_scores.face_detection * 100} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Skin Classification</span>
                    <span>{(confidence_scores.demographic * 100).toFixed(1)}%</span>
                  </div>
                  <Progress value={confidence_scores.demographic * 100} className="h-2" />
                </div>
              </CardContent>
            </Card>

            {/* Similar SCIN Profiles */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Heart className="h-5 w-5" />
                  Similar Profiles
                </CardTitle>
                <CardDescription>
                  Matching skin profiles from our database
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {similar_scin_profiles.map((profile, index) => (
                    <div key={index} className="border rounded-lg p-3">
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-medium text-sm">{profile.skin_condition}</span>
                        <Badge variant="outline" className="text-xs">
                          {(profile.similarity_score * 100).toFixed(0)}% match
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-600">
                        Age: {profile.metadata.age_group} • Type: {profile.metadata.skin_type}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Analysis Details */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Analysis Details
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Analysis Type:</span>
                    <span className="font-medium">{metadata.analysis_type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Ethnicity Considered:</span>
                    <span className="font-medium">{metadata.ethnicity_considered ? 'Yes' : 'No'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Age Considered:</span>
                    <span className="font-medium">{metadata.age_considered ? 'Yes' : 'No'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Face Detected:</span>
                    <span className="font-medium">{metadata.face_detected ? 'Yes' : 'No'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Timestamp:</span>
                    <span className="font-medium text-xs">
                      {new Date(metadata.timestamp).toLocaleString()}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function AnalysisResultsPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading analysis results...</p>
        </div>
      </div>
    }>
      <AnalysisResultsContent />
    </Suspense>
  );
} 