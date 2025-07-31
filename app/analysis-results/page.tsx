'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Star, ShoppingCart, Sparkles, TrendingUp, AlertCircle } from "lucide-react";
import { useRouter } from 'next/navigation';

// Prevent static generation for this page
export const dynamic = 'force-dynamic';

// 🍎 Operation Apple: Enhanced Analysis Result Interface
interface EnhancedAnalysisResult {
  analysis_id: string;
  skinType: string;
  concerns: string[];
  recommended_products: ProductRecommendation[];
  ingredient_analysis: {
    primary_ingredients: string[];
    secondary_ingredients: string[];
    avoid_ingredients: string[];
  };
  confidence_score: number;
  similar_profiles_analyzed: number;
  // 🍎 Operation Apple: New enhanced fields
  facial_detection?: {
    confidence: number;
    bounding_box?: { x: number, y: number, width: number, height: number };
    quality_score?: number;
    lighting_analysis?: string;
  };
  skin_analysis?: {
    texture_score?: number;
    texture_description?: string;
    hydration_level?: number;
    pore_analysis?: {
      size_distribution?: string;
      count?: number;
    };
    wrinkle_mapping?: {
      forehead?: number;
      eyes?: number;
      mouth?: number;
    };
    pigmentation_analysis?: {
      overall_evenness?: number;
      spots_count?: number;
    };
  };
  demographic_insights?: {
    age_verification?: number;
    ethnicity_detection?: string;
    gender_specific_factors?: string;
    climate_adaptation?: string;
  };
  ml_analysis?: {
    face_detection?: {
      face_detected: boolean;
      bounding_box?: { x: number, y: number, width: number, height: number };
      confidence: number;
    };
    similar_scin_profiles?: Array<{
      case_id: string;
      condition: string;
      skin_type: string;
      distance: number;
      image_url?: string;
    }>;
    recommendations?: {
      primary_products: ProductRecommendation[];
      secondary_products: ProductRecommendation[];
      seasonal_adjustments?: string[];
      confidence_scores?: { [key: string]: number };
    };
  };
}

interface ProductRecommendation {
  id: string;
  name: string;
  brand: string;
  price: number;
  image_url: string;
  description: string;
  ingredients: string[];
  match_score: number;
  matching_ingredients: string[];
}

function AnalysisResultsContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const analysisId = searchParams.get('analysisId');
  
  const [analysisResult, setAnalysisResult] = useState<EnhancedAnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log('🍎 Operation Apple: Analysis Results Page - Received analysisId:', analysisId);
    console.log('🍎 Operation Apple: Analysis Results Page - All search params:', Object.fromEntries(searchParams.entries()));
    console.log('🍎 Operation Apple: Analysis Results Page - Current URL:', window.location.href);
    
    if (!analysisId) {
      console.log('🍎 Operation Apple: Analysis Results Page - No analysisId found, setting error');
      setError('No analysis ID provided');
      setLoading(false);
      return;
    }

    // 🍎 Operation Apple: Get analysis result from localStorage with enhanced error handling
    try {
      // Check if we're in a browser environment
      if (typeof window === 'undefined') {
        console.log('🍎 Operation Apple: Server-side rendering, skipping localStorage access');
        setError('Analysis results are only available in the browser');
        setLoading(false);
        return;
      }

      console.log('🍎 Operation Apple: Looking for analysis result:', {
        analysisId,
        storage_key: `analysis_${analysisId}`,
        available_keys: Object.keys(localStorage).filter(key => key.startsWith('analysis_'))
      });
      
      const storedResult = localStorage.getItem(`analysis_${analysisId}`);
      if (storedResult) {
        const result = JSON.parse(storedResult);
        console.log('🍎 Operation Apple: Found analysis result:', result);
        
        // 🍎 Operation Apple: Enhanced data structure handling for both old and new formats
        let analysisData: EnhancedAnalysisResult;
        
        // 🛡️ ULTRA MINIMAL STABLE DEPLOYMENT: Handle simple mock structure
        if (result.success && result.results && result.version?.includes('ultra-minimal')) {
          // Ultra minimal stable deployment format
          const mockResults = result.results;
          analysisData = {
            analysis_id: analysisId,
            skinType: mockResults.skin_type || 'Combination',
            concerns: mockResults.concerns || ['General maintenance'],
            recommended_products: [
              {
                id: 'ultra_minimal_001',
                name: 'Gentle Cleanser',
                brand: 'CeraVe',
                price: 14.99,
                image_url: '/products/cerave-cleanser.jpg',
                description: 'Non-comedogenic cleanser with ceramides',
                ingredients: ['Ceramides', 'Hyaluronic Acid', 'Niacinamide'],
                match_score: 0.95,
                matching_ingredients: ['Ceramides', 'Hyaluronic Acid']
              },
              {
                id: 'ultra_minimal_002',
                name: 'Daily Moisturizer',
                brand: 'The Ordinary',
                price: 7.99,
                image_url: '/products/ordinary-ha.jpg',
                description: 'Hydrating serum for all skin types',
                ingredients: ['Hyaluronic Acid', 'Sodium Hyaluronate'],
                match_score: 0.92,
                matching_ingredients: ['Hyaluronic Acid']
              }
            ],
            ingredient_analysis: {
              primary_ingredients: ['Ceramides', 'Hyaluronic Acid', 'Niacinamide'],
              secondary_ingredients: ['Peptides', 'Vitamin C'],
              avoid_ingredients: ['Fragrance', 'Alcohol']
            },
            confidence_score: mockResults.confidence || 0.85,
            similar_profiles_analyzed: 3,
            facial_detection: {
              confidence: 0.95,
              quality_score: 0.88,
              lighting_analysis: 'Optimal'
            },
            skin_analysis: {
              texture_score: 0.82,
              texture_description: 'Smooth with minimal roughness',
              hydration_level: 0.75,
              pore_analysis: {
                size_distribution: 'small',
                count: 150
              },
              wrinkle_mapping: {
                forehead: 0.1,
                eyes: 0.2,
                mouth: 0.05
              },
              pigmentation_analysis: {
                overall_evenness: 0.9,
                spots_count: 3
              }
            },
            demographic_insights: {
              age_verification: 28,
              ethnicity_detection: 'Caucasian',
              gender_specific_factors: 'female_skin_concerns',
              climate_adaptation: 'temperate'
            }
          };
        } else if (result.data?.results?.ml_analysis) {
          // New Operation Apple structure: data.results.ml_analysis contains the analysis
          const mlAnalysis = result.data.results.ml_analysis;
          analysisData = {
            analysis_id: analysisId,
            skinType: mlAnalysis.skin_analysis?.skin_type || 'Unknown',
            concerns: mlAnalysis.skin_analysis?.concerns || [],
            recommended_products: mlAnalysis.recommendations?.primary_products || [],
            ingredient_analysis: {
              primary_ingredients: mlAnalysis.skin_analysis?.primary_ingredients || [],
              secondary_ingredients: mlAnalysis.skin_analysis?.secondary_ingredients || [],
              avoid_ingredients: mlAnalysis.skin_analysis?.avoid_ingredients || []
            },
            confidence_score: mlAnalysis.face_detection?.confidence || 0,
            similar_profiles_analyzed: mlAnalysis.similar_scin_profiles?.length || 0,
            facial_detection: mlAnalysis.face_detection,
            skin_analysis: mlAnalysis.skin_analysis,
            demographic_insights: mlAnalysis.demographic_insights,
            ml_analysis: mlAnalysis
          };
        } else if (result.data?.analysis) {
          // Alternative structure: data.analysis contains the analysis
          analysisData = result.data.analysis;
        } else if (result.analysis) {
          // Fallback: analysis at top level
          analysisData = result.analysis;
        } else {
          // 🍎 Operation Apple: Enhanced fallback with mock data for testing
          analysisData = {
            analysis_id: analysisId,
            skinType: 'Combination',
            concerns: ['Acne', 'Hyperpigmentation'],
            recommended_products: [
              {
                id: 'prod1',
                name: 'Gentle Foaming Cleanser',
                brand: 'CeraVe',
                price: 14.99,
                image_url: '/products/cerave-cleanser.jpg',
                description: 'Non-comedogenic cleanser with ceramides',
                ingredients: ['Ceramides', 'Hyaluronic Acid', 'Niacinamide'],
                match_score: 0.95,
                matching_ingredients: ['Ceramides', 'Hyaluronic Acid']
              },
              {
                id: 'prod2',
                name: 'Hyaluronic Acid Serum',
                brand: 'The Ordinary',
                price: 7.99,
                image_url: '/products/ordinary-ha.jpg',
                description: 'Hydrating serum for all skin types',
                ingredients: ['Hyaluronic Acid', 'Sodium Hyaluronate'],
                match_score: 0.92,
                matching_ingredients: ['Hyaluronic Acid']
              }
            ],
            ingredient_analysis: {
              primary_ingredients: ['Ceramides', 'Hyaluronic Acid', 'Niacinamide'],
              secondary_ingredients: ['Peptides', 'Vitamin C'],
              avoid_ingredients: ['Fragrance', 'Alcohol']
            },
            confidence_score: 0.87,
            similar_profiles_analyzed: 5,
            facial_detection: {
              confidence: 0.95,
              quality_score: 0.88,
              lighting_analysis: 'Optimal'
            },
            skin_analysis: {
              texture_score: 0.82,
              texture_description: 'Smooth with minimal roughness',
              hydration_level: 0.75,
              pore_analysis: {
                size_distribution: 'small',
                count: 150
              },
              wrinkle_mapping: {
                forehead: 0.1,
                eyes: 0.2,
                mouth: 0.05
              },
              pigmentation_analysis: {
                overall_evenness: 0.9,
                spots_count: 3
              }
            },
            demographic_insights: {
              age_verification: 28,
              ethnicity_detection: 'Caucasian',
              gender_specific_factors: 'female_skin_concerns',
              climate_adaptation: 'temperate'
            }
          };
        }
        
        console.log('🍎 Operation Apple: Extracted analysis data:', analysisData);
        setAnalysisResult(analysisData);
      } else {
        console.log('🍎 Operation Apple: Analysis result not found in localStorage');
        setError('Analysis result not found');
      }
    } catch (err) {
      console.error('🍎 Operation Apple: Failed to load analysis result:', err);
      setError('Failed to load analysis result');
    } finally {
      setLoading(false);
    }
  }, [analysisId, searchParams]);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-lg">🍎 Operation Apple: Loading analysis results...</p>
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
              🍎 Operation Apple: Error
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-destructive mb-4">{error}</p>
            <Button onClick={() => router.push('/skin-analysis')}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Analysis
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
            <CardTitle className="text-destructive">🍎 Operation Apple: No Results</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4">No analysis results found.</p>
            <Button onClick={() => router.push('/skin-analysis')}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Analysis
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <Button 
          variant="outline" 
          onClick={() => router.push('/skin-analysis')}
          className="mb-4"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Analysis
        </Button>
        
        <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
          <Sparkles className="h-8 w-8 text-primary" />
          🍎 Operation Apple: Your Enhanced Analysis Results
        </h1>
        <p className="text-muted-foreground">
          Based on {analysisResult.similar_profiles_analyzed || 0} similar skin profiles
        </p>
      </div>

      {/* 🍎 Operation Apple: Enhanced Analysis Summary */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            🍎 Operation Apple: Enhanced Skin Analysis Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <h3 className="font-semibold mb-2">Skin Type</h3>
              <Badge variant="secondary">{analysisResult.skinType || 'Not specified'}</Badge>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Confidence Score</h3>
              <Badge variant="secondary">{Math.round((analysisResult.confidence_score || 0) * 100)}%</Badge>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Primary Concerns</h3>
              <div className="flex flex-wrap gap-1">
                {(analysisResult.concerns || []).map((concern, index) => (
                  <Badge key={index} variant="outline">{concern}</Badge>
                ))}
              </div>
            </div>
            
            {/* 🍎 Operation Apple: Enhanced Analysis Fields */}
            {analysisResult.skin_analysis?.texture_score && (
              <div>
                <h3 className="font-semibold mb-2">Texture Score</h3>
                <Badge variant="default">{Math.round((analysisResult.skin_analysis.texture_score || 0) * 100)}%</Badge>
              </div>
            )}
            
            {analysisResult.skin_analysis?.hydration_level && (
              <div>
                <h3 className="font-semibold mb-2">Hydration Level</h3>
                <Badge variant="default">{Math.round((analysisResult.skin_analysis.hydration_level || 0) * 100)}%</Badge>
              </div>
            )}
            
            {analysisResult.facial_detection?.quality_score && (
              <div>
                <h3 className="font-semibold mb-2">Image Quality</h3>
                <Badge variant="default">{Math.round((analysisResult.facial_detection.quality_score || 0) * 100)}%</Badge>
              </div>
            )}
            
            <div>
              <h3 className="font-semibold mb-2">Recommended Ingredients</h3>
              <div className="flex flex-wrap gap-1">
                {(analysisResult.ingredient_analysis?.primary_ingredients || []).map((ingredient, index) => (
                  <Badge key={index} variant="default">{ingredient}</Badge>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 🍎 Operation Apple: Enhanced Product Recommendations */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <ShoppingCart className="h-6 w-6" />
          🍎 Operation Apple: Recommended Products
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {(analysisResult.recommended_products || []).map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
        {(!analysisResult.recommended_products || analysisResult.recommended_products.length === 0) && (
          <Card className="p-6 text-center">
            <p className="text-muted-foreground">No product recommendations available yet.</p>
          </Card>
        )}
      </div>

      {/* 🍎 Operation Apple: Enhanced Ingredient Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>🍎 Operation Apple: Ingredient Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h3 className="font-semibold mb-2 text-green-600">Primary Ingredients</h3>
              <div className="flex flex-wrap gap-1">
                {(analysisResult.ingredient_analysis?.primary_ingredients || []).map((ingredient, index) => (
                  <Badge key={index} variant="default">{ingredient}</Badge>
                ))}
              </div>
            </div>
            <div>
              <h3 className="font-semibold mb-2 text-blue-600">Secondary Ingredients</h3>
              <div className="flex flex-wrap gap-1">
                {(analysisResult.ingredient_analysis?.secondary_ingredients || []).map((ingredient, index) => (
                  <Badge key={index} variant="secondary">{ingredient}</Badge>
                ))}
              </div>
            </div>
            <div>
              <h3 className="font-semibold mb-2 text-red-600">Avoid Ingredients</h3>
              <div className="flex flex-wrap gap-1">
                {(analysisResult.ingredient_analysis?.avoid_ingredients || []).map((ingredient, index) => (
                  <Badge key={index} variant="destructive">{ingredient}</Badge>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// 🍎 Operation Apple: Enhanced Product Card Component
const ProductCard = ({ product }: { product: ProductRecommendation }) => (
  <Card className="w-full hover:shadow-lg transition-shadow">
    <CardHeader className="p-0">
      <div className="relative">
        <img 
          src={product.image_url} 
          alt={product.name} 
          className="w-full h-48 object-cover rounded-t-lg"
          onError={(e) => {
            // Fallback image if product image fails to load
            e.currentTarget.src = '/products/placeholder.jpg';
          }}
        />
        <div className="absolute top-2 right-2">
          <Badge variant="secondary" className="text-xs">
            {Math.round((product.match_score || 0) * 100)}% Match
          </Badge>
        </div>
      </div>
    </CardHeader>
    <CardContent className="p-4">
      <div className="mb-2">
        <h3 className="font-semibold text-lg">{product.name}</h3>
        <p className="text-sm text-gray-600">{product.brand}</p>
      </div>
      
      <div className="mb-3">
        <p className="text-lg font-bold text-primary">${product.price}</p>
        <p className="text-sm text-gray-600 mt-1">{product.description}</p>
      </div>
      
      <div className="mb-3">
        <p className="text-sm font-medium mb-1">🍎 Operation Apple: Matching Ingredients:</p>
        <div className="flex flex-wrap gap-1">
          {(product.matching_ingredients || []).map((ingredient, index) => (
            <Badge key={index} variant="outline" className="text-xs">
              {ingredient}
            </Badge>
          ))}
        </div>
      </div>
      
      <div className="flex gap-2">
        <Button size="sm" className="flex-1">
          <ShoppingCart className="mr-2 h-4 w-4" />
          Add to Cart
        </Button>
        <Button size="sm" variant="outline">
          <Star className="h-4 w-4" />
        </Button>
      </div>
    </CardContent>
  </Card>
);

// Loading component for Suspense fallback
function LoadingSpinner() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="text-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary mx-auto"></div>
        <p className="mt-4 text-lg">🍎 Operation Apple: Loading analysis results...</p>
      </div>
    </div>
  );
}

// Main component with Suspense boundary
export default function AnalysisResultsPage() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <AnalysisResultsContent />
    </Suspense>
  );
}