'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { Loader2, Star, ShoppingCart } from "lucide-react";

interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  rating: number;
  image: string;
  category: string;
  skinType: string[];
}

export default function RecommendationsPage() {
  const { isAuthenticated, user } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Simulate loading recommended products
    const loadRecommendations = async () => {
      try {
        setLoading(true);
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock data for demonstration
        const mockProducts: Product[] = [
          {
            id: '1',
            name: 'Hydrating Face Serum',
            description: 'Deeply hydrating serum with hyaluronic acid for all skin types',
            price: 45.99,
            rating: 4.8,
            image: '/placeholder.jpg',
            category: 'Serum',
            skinType: ['Dry', 'Normal', 'Combination']
          },
          {
            id: '2',
            name: 'Gentle Cleanser',
            description: 'pH-balanced cleanser that removes impurities without stripping',
            price: 28.99,
            rating: 4.6,
            image: '/placeholder.jpg',
            category: 'Cleanser',
            skinType: ['Sensitive', 'Normal', 'Dry']
          },
          {
            id: '3',
            name: 'Vitamin C Brightening Cream',
            description: 'Brightening cream with stable vitamin C for radiant skin',
            price: 52.99,
            rating: 4.9,
            image: '/placeholder.jpg',
            category: 'Moisturizer',
            skinType: ['Normal', 'Combination', 'Oily']
          }
        ];
        
        setProducts(mockProducts);
      } catch (err) {
        setError('Failed to load recommendations');
        console.error('Error loading recommendations:', err);
      } finally {
        setLoading(false);
      }
    };

    loadRecommendations();
  }, []);

  if (!isAuthenticated) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle>Authentication Required</CardTitle>
            <CardDescription>
              Please log in to view your personalized skincare recommendations.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full">
              <a href="/auth/login?redirect=/recommendations">Login to Continue</a>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
            <p>Loading your personalized recommendations...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle>Error</CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => window.location.reload()}>
              Try Again
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Your Recommendations</h1>
        <p className="text-muted-foreground">
          Personalized skincare products based on your skin analysis
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {products.map((product) => (
          <Card key={product.id} className="overflow-hidden">
            <div className="aspect-square bg-muted flex items-center justify-center">
              <div className="text-muted-foreground text-sm">Product Image</div>
            </div>
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-lg">{product.name}</CardTitle>
                  <CardDescription className="mt-1">{product.description}</CardDescription>
                </div>
                <Badge variant="secondary">{product.category}</Badge>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-1">
                  <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                  <span className="text-sm font-medium">{product.rating}</span>
                </div>
                <span className="text-lg font-bold">${product.price}</span>
              </div>
              
              <div className="flex flex-wrap gap-1 mb-4">
                {product.skinType.map((type) => (
                  <Badge key={type} variant="outline" className="text-xs">
                    {type}
                  </Badge>
                ))}
              </div>
              
              <Button className="w-full" size="sm">
                <ShoppingCart className="h-4 w-4 mr-2" />
                Add to Cart
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
} 