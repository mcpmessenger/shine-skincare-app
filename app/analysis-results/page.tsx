'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Star, ShoppingCart } from "lucide-react";
import { useRouter } from 'next/navigation';

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

interface AnalysisResult {
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
}

export default function AnalysisResultsPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const analysisId = searchParams.get('analysisId');
  
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log('☠️ Operation Skully: Analysis Results Page - Received analysisId:', analysisId);
    console.log('☠️ Operation Skully: Analysis Results Page - All search params:', Object.fromEntries(searchParams.entries()));
    console.log('☠️ Operation Skully: Analysis Results Page - Current URL:', window.location.href);
    console.log('☠️ Operation Skully: Analysis Results Page - Search params type:', typeof searchParams);
    console.log('☠️ Operation Skully: Analysis Results Page - Search params entries:', Array.from(searchParams.entries()));
    
    if (!analysisId) {
      console.log('☠️ Operation Skully: Analysis Results Page - No analysisId found, setting error');
      setError('No analysis ID provided');
      setLoading(false);
      return;
    }

    // ☠️ Operation Skully: Get analysis result from localStorage
    try {
      console.log('☠️ Operation Skully: Looking for analysis result:', {
        analysisId,
        storage_key: `analysis_${analysisId}`,
        available_keys: Object.keys(localStorage).filter(key => key.startsWith('analysis_'))
      });
      
      const storedResult = localStorage.getItem(`analysis_${analysisId}`);
      if (storedResult) {
        const result = JSON.parse(storedResult);
        console.log('☠️ Operation Skully: Found analysis result:', result);
        
        // ☠️ Operation Skully Fix: Handle both old and new response structures
        let analysisData;
        if (result.data?.analysis) {
          // New structure: data.analysis contains the analysis
          analysisData = result.data.analysis;
        } else if (result.analysis) {
          // Alternative structure: analysis at top level
          analysisData = result.analysis;
        } else {
          // Fallback: use the result as-is
          analysisData = result;
        }
        
        console.log('☠️ Operation Skully: Extracted analysis data:', analysisData);
        setAnalysisResult(analysisData);
      } else {
        console.log('☠️ Operation Skully: Analysis result not found in localStorage');
        setError('Analysis result not found');
      }
    } catch (err) {
      console.error('☠️ Operation Skully: Failed to load analysis result:', err);
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
          <p className="mt-4 text-lg">☠️ Operation Skully: Loading analysis results...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle className="text-destructive">☠️ Operation Skully: Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-destructive mb-4">{error}</p>
            <Button onClick={() => router.push('/enhanced-skin-analysis')}>
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
            <CardTitle className="text-destructive">☠️ Operation Skully: No Results</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4">No analysis results found.</p>
            <Button onClick={() => router.push('/enhanced-skin-analysis')}>
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
          onClick={() => router.push('/enhanced-skin-analysis')}
          className="mb-4"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Analysis
        </Button>
        
        <h1 className="text-3xl font-bold mb-2">☠️ Operation Skully: Your Analysis Results</h1>
        <p className="text-muted-foreground">
          Based on {analysisResult.similar_profiles_analyzed} similar skin profiles
        </p>
      </div>

      {/* 💀☠️ Operation Skully: Analysis Summary */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>💀☠️ Operation Skully: Skin Analysis Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h3 className="font-semibold mb-2">Skin Type</h3>
              <Badge variant="secondary">{analysisResult.skinType}</Badge>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Confidence Score</h3>
              <Badge variant="secondary">{Math.round(analysisResult.confidence_score * 100)}%</Badge>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Primary Concerns</h3>
              <div className="flex flex-wrap gap-1">
                {analysisResult.concerns.map((concern, index) => (
                  <Badge key={index} variant="outline">{concern}</Badge>
                ))}
              </div>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Recommended Ingredients</h3>
              <div className="flex flex-wrap gap-1">
                {analysisResult.ingredient_analysis.primary_ingredients.map((ingredient, index) => (
                  <Badge key={index} variant="default">{ingredient}</Badge>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 💀☠️ Operation Skully: Product Recommendations */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-4">💀☠️ Operation Skully: Recommended Products</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {analysisResult.recommended_products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </div>

      {/* 💀☠️ Operation Skully: Ingredient Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>💀☠️ Operation Skully: Ingredient Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h3 className="font-semibold mb-2 text-green-600">Primary Ingredients</h3>
              <div className="flex flex-wrap gap-1">
                {analysisResult.ingredient_analysis.primary_ingredients.map((ingredient, index) => (
                  <Badge key={index} variant="default">{ingredient}</Badge>
                ))}
              </div>
            </div>
            <div>
              <h3 className="font-semibold mb-2 text-blue-600">Secondary Ingredients</h3>
              <div className="flex flex-wrap gap-1">
                {analysisResult.ingredient_analysis.secondary_ingredients.map((ingredient, index) => (
                  <Badge key={index} variant="secondary">{ingredient}</Badge>
                ))}
              </div>
            </div>
            <div>
              <h3 className="font-semibold mb-2 text-red-600">Avoid Ingredients</h3>
              <div className="flex flex-wrap gap-1">
                {analysisResult.ingredient_analysis.avoid_ingredients.map((ingredient, index) => (
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

// 💀☠️ Operation Skully: Product Card Component
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
            {Math.round(product.match_score * 100)}% Match
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
        <p className="text-sm font-medium mb-1">💀☠️ Operation Skully: Matching Ingredients:</p>
        <div className="flex flex-wrap gap-1">
          {product.matching_ingredients.map((ingredient, index) => (
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