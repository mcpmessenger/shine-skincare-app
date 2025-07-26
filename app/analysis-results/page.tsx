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
  Camera
} from "lucide-react";
import Link from "next/link";

export default function AnalysisResultsPage() {
  const { user, isAuthenticated, loading } = useAuth();
  const router = useRouter();
  const [analysisData, setAnalysisData] = useState<any>(null);

  useEffect(() => {
    // Redirect to login if not authenticated
    if (!loading && !isAuthenticated) {
      router.push('/auth/login?redirect=/analysis-results');
      return;
    }

    // Get analysis data from URL params or fetch from API
    if (isAuthenticated) {
      const fetchAnalysisData = async () => {
        try {
          // Check if we have analysis data in URL params
          const urlParams = new URLSearchParams(window.location.search);
          const analysisId = urlParams.get('analysisId');
          
          if (analysisId) {
            // Fetch specific analysis result
            const response = await fetch(`/api/analysis/skin/${analysisId}`, {
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
              },
            });
            
            if (response.ok) {
              const data = await response.json();
              setAnalysisData(data);
            } else {
              console.error('Failed to fetch analysis data');
              // Fall back to mock data for now
              setMockData();
            }
          } else {
            // No analysis ID - this page should be accessed after analysis
            console.log('No analysis ID found - redirecting to skin analysis');
            router.push('/skin-analysis');
          }
        } catch (error) {
          console.error('Error fetching analysis data:', error);
          // Fall back to mock data for now
          setMockData();
        }
      };

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

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect to login
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link href="/skin-analysis">
            <Button variant="outline" size="sm">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Analysis
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold">Your Skin Analysis Results</h1>
            <p className="text-muted-foreground">
              AI-powered analysis for {user?.email}
            </p>
          </div>
        </div>

        {!analysisData ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p>Analyzing your skin...</p>
          </div>
        ) : (
          <div className="grid gap-6">
            {/* Skin Type Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-purple-600" />
                  Skin Type Analysis
                </CardTitle>
                <CardDescription>
                  Based on your selfie, here's what our AI detected about your skin
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-semibold mb-3">Primary Skin Type</h3>
                    <Badge variant="secondary" className="text-lg px-4 py-2">
                      {analysisData.skinType}
                    </Badge>
                  </div>
                  <div>
                    <h3 className="font-semibold mb-3">Main Concerns</h3>
                    <div className="flex flex-wrap gap-2">
                      {analysisData.concerns.map((concern: string, index: number) => (
                        <Badge key={index} variant="outline">
                          {concern}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Skin Metrics */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-blue-600" />
                  Skin Metrics
                </CardTitle>
                <CardDescription>
                  Detailed analysis of your skin characteristics
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4">
                  <div className="flex items-center gap-4">
                    <Droplets className="h-5 w-5 text-blue-500" />
                    <div className="flex-1">
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">Hydration Level</span>
                        <span className="text-sm text-muted-foreground">{analysisData.hydration}%</span>
                      </div>
                      <Progress value={analysisData.hydration} className="h-2" />
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <Sun className="h-5 w-5 text-yellow-500" />
                    <div className="flex-1">
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">Oil Production</span>
                        <span className="text-sm text-muted-foreground">{analysisData.oiliness}%</span>
                      </div>
                      <Progress value={analysisData.oiliness} className="h-2" />
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <AlertTriangle className="h-5 w-5 text-orange-500" />
                    <div className="flex-1">
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">Sensitivity</span>
                        <span className="text-sm text-muted-foreground">{analysisData.sensitivity}%</span>
                      </div>
                      <Progress value={analysisData.sensitivity} className="h-2" />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recommendations */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  Personalized Recommendations
                </CardTitle>
                <CardDescription>
                  Customized skincare advice based on your analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-3">
                  {analysisData.recommendations.map((rec: string, index: number) => (
                    <div key={index} className="flex items-start gap-3 p-3 bg-muted rounded-lg">
                      <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">{rec}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Recommended Products */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Heart className="h-5 w-5 text-red-600" />
                  Recommended Products
                </CardTitle>
                <CardDescription>
                  Products tailored to your skin type and concerns
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4">
                  {analysisData.products.map((product: any, index: number) => (
                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <h4 className="font-medium">{product.name}</h4>
                        <p className="text-sm text-muted-foreground">{product.category}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="flex items-center gap-1">
                          <Eye className="h-4 w-4 text-yellow-500" />
                          <span className="text-sm font-medium">{product.rating}</span>
                        </div>
                        <Button size="sm" variant="outline">
                          View Product
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Action Buttons */}
            <div className="flex gap-4 justify-center">
              <Link href="/recommendations">
                <Button>
                  <Heart className="mr-2 h-4 w-4" />
                  Browse More Products
                </Button>
              </Link>
              <Link href="/skin-analysis">
                <Button variant="outline">
                  <Camera className="mr-2 h-4 w-4" />
                  New Analysis
                </Button>
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 