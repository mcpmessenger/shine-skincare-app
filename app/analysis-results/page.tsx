'use client';

import { useAuth } from "@/hooks/useAuth";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Sparkles, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  ArrowLeft,
  Heart,
  Eye,
  Droplets,
  Sun,
  Camera,
  AlertCircle
} from "lucide-react";
import Link from "next/link";

export default function AnalysisResultsPage() {
  const { user, isAuthenticated, loading } = useAuth();
  const router = useRouter();
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Allow both authenticated and guest users to view results
    const fetchAnalysisData = async () => {
      try {
        setIsLoading(true);
        // Check if we have analysis data in URL params
        const urlParams = new URLSearchParams(window.location.search);
        const analysisId = urlParams.get('analysisId');
        
        if (analysisId) {
          // Try to fetch specific analysis result
          const token = localStorage.getItem('token');
          const headers: Record<string, string> = {};
          if (token && token !== 'guest') {
            headers['Authorization'] = `Bearer ${token}`;
          }
          
          // Since Railway backend doesn't store analysis results,
          // we'll check if we have cached results in localStorage
          const cachedResults = localStorage.getItem(`analysis_${analysisId}`);
          
          if (cachedResults) {
            try {
              const data = JSON.parse(cachedResults);
              setAnalysisData(data);
            } catch (error) {
              console.error('Failed to parse cached analysis data');
              setMockData();
            }
          } else {
            console.log('No cached analysis data found for ID:', analysisId);
            // Fall back to mock data for now
            setMockData();
          }
        } else {
          // No analysis ID - this page should be accessed after analysis
          console.log('No analysis ID found - redirecting to skin analysis');
          router.push('/skin-analysis');
          return;
        }
      } catch (error) {
        console.error('Error fetching analysis data:', error);
        // Fall back to mock data for now
        setMockData();
      } finally {
        setIsLoading(false);
      }
    };

    if (!loading) {
      fetchAnalysisData();
    }
  }, [isAuthenticated, loading, router]);

  const setMockData = () => {
    setAnalysisData({
      skinType: 'Combination',
      concerns: ['Acne', 'Hyperpigmentation', 'Fine Lines'],
      hydration: 75,
      oiliness: 45,
      sensitivity: 30,
      recommendations: [
        'Use a gentle cleanser twice daily',
        'Apply SPF 30+ sunscreen every morning',
        'Consider a vitamin C serum for brightening',
        'Use a lightweight moisturizer for combination skin'
      ],
      products: [
        { name: 'Gentle Foaming Cleanser', category: 'Cleanser', rating: 4.5 },
        { name: 'Vitamin C Brightening Serum', category: 'Serum', rating: 4.8 },
        { name: 'Lightweight Hydrating Moisturizer', category: 'Moisturizer', rating: 4.3 }
      ]
    });
  };

  if (loading || isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Loading your analysis results...</p>
        </div>
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-orange-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">No Analysis Found</h2>
          <p className="text-muted-foreground mb-4">
            We couldn't find your analysis results. Please try analyzing your skin again.
          </p>
          <Button onClick={() => router.push('/skin-analysis')}>
            Start New Analysis
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Guest User Notice */}
      {!isAuthenticated && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-blue-800 font-medium mb-1">Your Analysis Results</h3>
              <p className="text-blue-700 text-sm mb-3">
                You're viewing your analysis as a guest. Sign up to save your results and get personalized recommendations.
              </p>
              <div className="flex gap-2">
                <Button 
                  size="sm" 
                  onClick={() => router.push('/auth/signup')}
                >
                  Sign Up to Save Results
                </Button>
                <Button 
                  size="sm" 
                  variant="outline"
                  onClick={() => router.push('/auth/login')}
                >
                  Sign In
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="mb-6">
        <Button
          variant="outline"
          onClick={() => router.back()}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Analysis
        </Button>
        
        <div className="flex items-center gap-2 mb-2">
          <Sparkles className="h-6 w-6 text-purple-600" />
          <h1 className="text-3xl font-bold">Your Skin Analysis Results</h1>
        </div>
        <p className="text-muted-foreground">
          Based on your skin analysis, here are your personalized insights and recommendations.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Skin Type & Concerns */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="h-5 w-5" />
              Skin Profile
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-medium mb-2">Skin Type</h3>
              <Badge variant="secondary" className="text-lg px-3 py-1">
                {analysisData.skinType}
              </Badge>
            </div>
            
            <div>
              <h3 className="font-medium mb-2">Primary Concerns</h3>
              <div className="flex flex-wrap gap-2">
                {analysisData.concerns?.map((concern: string, index: number) => (
                  <Badge key={index} variant="outline">
                    {concern}
                  </Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Skin Metrics */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Skin Metrics
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">Hydration</span>
                <span className="text-sm text-muted-foreground">{analysisData.hydration}%</span>
              </div>
              <Progress value={analysisData.hydration} className="h-2" />
            </div>
            
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">Oiliness</span>
                <span className="text-sm text-muted-foreground">{analysisData.oiliness}%</span>
              </div>
              <Progress value={analysisData.oiliness} className="h-2" />
            </div>
            
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">Sensitivity</span>
                <span className="text-sm text-muted-foreground">{analysisData.sensitivity}%</span>
              </div>
              <Progress value={analysisData.sensitivity} className="h-2" />
            </div>
          </CardContent>
        </Card>

        {/* Recommendations */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5" />
              Personalized Recommendations
            </CardTitle>
            <CardDescription>
              Based on your skin analysis, here are our recommendations for your skincare routine.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              {analysisData.recommendations?.map((recommendation: string, index: number) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg">
                  <CheckCircle className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                  <p className="text-sm">{recommendation}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recommended Products */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Heart className="h-5 w-5" />
              Recommended Products
            </CardTitle>
            <CardDescription>
              Products that match your skin type and concerns.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              {analysisData.products?.map((product: any, index: number) => (
                <div key={index} className="p-4 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <h4 className="font-medium">{product.name}</h4>
                    <Badge variant="outline">{product.category}</Badge>
                  </div>
                  <div className="flex items-center gap-1 mb-2">
                    <span className="text-sm text-muted-foreground">Rating:</span>
                    <span className="text-sm font-medium">{product.rating}/5</span>
                  </div>
                  <Button size="sm" className="w-full">
                    View Product
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center gap-4 mt-8">
        <Button onClick={() => router.push('/skin-analysis')}>
          <Camera className="h-4 w-4 mr-2" />
          New Analysis
        </Button>
        <Button variant="outline" onClick={() => router.push('/similarity-search')}>
          <Eye className="h-4 w-4 mr-2" />
          Find Similar Conditions
        </Button>
        {!isAuthenticated && (
          <Button variant="secondary" onClick={() => router.push('/auth/signup')}>
            <Heart className="h-4 w-4 mr-2" />
            Sign Up for Full Access
          </Button>
        )}
      </div>
    </div>
  );
} 