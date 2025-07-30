'use client';

import { useEffect, useState } from 'react';

import SkinAnalysisCard from "@/components/skin-analysis-card"
import ProductRecommendationCard from "@/components/product-recommendation-card"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { useAuth } from "@/hooks/useAuth"
import { apiClient, Product } from "@/lib/api"

export default function HomePage() {
  const { user } = useAuth();
  const [trendingProducts, setTrendingProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Use the Unicorn Alpha backend URL
    if (typeof window !== 'undefined') {
      // Use the Unicorn Alpha backend
      const correctBackendUrl = 'http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com';
      console.log('🔧 Using Unicorn Alpha backend URL:', correctBackendUrl);
      
      // Update the API client base URL
      (apiClient as any).baseUrl = correctBackendUrl;
    }
    
    loadTrendingProducts();
  }, []);

  const loadTrendingProducts = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('🔧 Loading trending products...');
      
      const response = await apiClient.getTrendingProducts();
      console.log('🔧 API Response:', response);
      
      // Handle the API response structure
      if (response && response.data && Array.isArray(response.data)) {
        setTrendingProducts(response.data);
      } else if (response && response.data && typeof response.data === 'object' && 'trending_products' in response.data) {
        // Handle the new response structure from backend
        setTrendingProducts((response.data as any).trending_products);
      } else {
        console.warn('Invalid response structure, using fallback data');
        // Fallback to mock data if API fails
        setTrendingProducts([
          {
            id: "1",
            name: "HydraBoost Serum",
            brand: "AquaGlow",
            price: 39.99,
            rating: 4.5,
            image_urls: ["/placeholder.svg?height=200&width=300"],
            description: "A powerful hydrating serum infused with hyaluronic acid and ceramides to deeply moisturize and plump the skin.",
            category: "serum",
            subcategory: "hydrating",
            ingredients: ["Hyaluronic Acid", "Ceramides", "Niacinamide"],
            currency: "USD",
            availability_status: "available",
            review_count: 127
          },
          {
            id: "2",
            name: "ClearSkin Acne Treatment",
            brand: "DermPure",
            price: 24.5,
            rating: 4.0,
            image_urls: ["/placeholder.svg?height=200&width=300"],
            description: "Target stubborn breakouts with this salicylic acid and tea tree oil formula, designed to clear pores and reduce inflammation.",
            category: "treatment",
            subcategory: "acne",
            ingredients: ["Salicylic Acid", "Tea Tree Oil", "Zinc PCA"],
            currency: "USD",
            availability_status: "available",
            review_count: 89
          },
          {
            id: "3",
            name: "Radiant C Cream",
            brand: "VitaBright",
            price: 55.0,
            rating: 4.8,
            image_urls: ["/placeholder.svg?height=200&width=300"],
            description: "Brighten and even skin tone with this potent Vitamin C cream, packed with antioxidants for a youthful glow.",
            category: "moisturizer",
            subcategory: "brightening",
            ingredients: ["Vitamin C", "Ferulic Acid", "Vitamin E"],
            currency: "USD",
            availability_status: "available",
            review_count: 203
          }
        ]);
      }
    } catch (error) {
      console.error('Failed to load trending products:', error);
      setError('Failed to load recommendations. Please try again.');
      // Fallback to mock data if API fails
      setTrendingProducts([
        {
          id: "1",
          name: "HydraBoost Serum",
          brand: "AquaGlow",
          price: 39.99,
          rating: 4.5,
          image_urls: ["/placeholder.svg?height=200&width=300"],
          description: "A powerful hydrating serum infused with hyaluronic acid and ceramides to deeply moisturize and plump the skin.",
          category: "serum",
          subcategory: "hydrating",
          ingredients: ["Hyaluronic Acid", "Ceramides", "Niacinamide"],
          currency: "USD",
          availability_status: "available",
          review_count: 127
        },
        {
          id: "2",
          name: "ClearSkin Acne Treatment",
          brand: "DermPure",
          price: 24.5,
          rating: 4.0,
          image_urls: ["/placeholder.svg?height=200&width=300"],
          description: "Target stubborn breakouts with this salicylic acid and tea tree oil formula, designed to clear pores and reduce inflammation.",
          category: "treatment",
          subcategory: "acne",
          ingredients: ["Salicylic Acid", "Tea Tree Oil", "Zinc PCA"],
          currency: "USD",
          availability_status: "available",
          review_count: 89
        },
        {
          id: "3",
          name: "Radiant C Cream",
          brand: "VitaBright",
          price: 55.0,
          rating: 4.8,
          image_urls: ["/placeholder.svg?height=200&width=300"],
          description: "Brighten and even skin tone with this potent Vitamin C cream, packed with antioxidants for a youthful glow.",
          category: "moisturizer",
          subcategory: "brightening",
          ingredients: ["Vitamin C", "Ferulic Acid", "Vitamin E"],
          currency: "USD",
          availability_status: "available",
          review_count: 203
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Show error state if there's an error
  if (error) {
    return (
      <div className="flex flex-col min-h-[100dvh] items-center justify-center">
        <div className="text-center space-y-4">
          <h1 className="text-2xl font-bold text-red-600">Something went wrong</h1>
          <p className="text-muted-foreground">{error}</p>
          <Button onClick={loadTrendingProducts}>Try Again</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-[100dvh]">
      <main className="flex-1 py-12 px-4 md:px-6 lg:py-24">
        <section className="container mx-auto grid gap-12">
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl">
              Your Personalized Skincare Journey Starts Here
            </h1>
            <p className="mx-auto max-w-[700px] text-muted-foreground md:text-xl">
              Get AI-powered skin analysis and tailored product recommendations.
            </p>
            <div className="flex justify-center gap-4">
              <Link href="/skin-analysis">
                <Button size="lg">Start Skin Analysis</Button>
              </Link>
              <Link href="/similarity-search">
                <Button size="lg" variant="outline">
                  Find Similar Conditions
                </Button>
              </Link>
              <Link href="/recommendations">
                <Button size="lg" variant="outline">
                  Explore Products
                </Button>
              </Link>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-8 items-start">
            <div className="space-y-6">
              <h2 className="text-3xl font-bold tracking-tighter">Get Your Skin Analyzed</h2>
              <SkinAnalysisCard />
            </div>
            <div className="space-y-6">
              <h2 className="text-3xl font-bold tracking-tighter">Top Recommendations for You</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-6">
                {loading ? (
                  <div className="col-span-2 text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
                    <p className="mt-2 text-muted-foreground">Loading recommendations...</p>
                  </div>
                ) : trendingProducts && trendingProducts.length > 0 ? (
                  trendingProducts.map((product, index) => (
                    <ProductRecommendationCard key={`${product.id}-${index}`} product={product} />
                  ))
                ) : (
                  <div className="col-span-2 text-center py-8">
                    <p className="text-muted-foreground">No recommendations available</p>
                  </div>
                )}
              </div>
              <div className="flex justify-center">
                <Link href="/recommendations">
                  <Button variant="secondary">View All Recommendations</Button>
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>
      <footer className="flex flex-col gap-2 sm:flex-row py-6 w-full shrink-0 items-center px-4 md:px-6 border-t">
        <p className="text-xs text-muted-foreground">&copy; 2025 Shine. All rights reserved.</p>
        <nav className="sm:ml-auto flex gap-4 sm:gap-6">
          <Link href="#" className="text-xs hover:underline underline-offset-4" prefetch={false}>
            Terms of Service
          </Link>
          <Link href="#" className="text-xs hover:underline underline-offset-4" prefetch={false}>
            Privacy
          </Link>
          <Link href="#" className="text-xs hover:underline underline-offset-4" prefetch={false}>
            Contact
          </Link>
        </nav>
      </footer>
    </div>
  )
}
