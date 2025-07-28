'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import EnhancedSkinAnalysisCard from '@/components/enhanced-skin-analysis-card';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, Sparkles, Database, Brain, Zap } from 'lucide-react';
import Link from 'next/link';

export default function EnhancedSkinAnalysisPage() {
  const { isAuthenticated, user, loading } = useAuth();
  const router = useRouter();
  const [analysisHistory, setAnalysisHistory] = useState([]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link href="/" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Home
          </Link>
          <div className="flex items-center gap-4 mb-4">
            <div className="flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-primary" />
              <h1 className="text-3xl font-bold">Enhanced Skin Analysis</h1>
            </div>
            {user && (
              <div className="ml-auto text-sm text-muted-foreground">
                Welcome back, {user.name}!
              </div>
            )}
          </div>
          <p className="text-muted-foreground">
            Experience the next generation of AI-powered skincare analysis with vector-based recommendations and scIN dataset integration.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Analysis Card */}
          <div className="lg:col-span-2">
            <EnhancedSkinAnalysisCard />
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Enhanced Features */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Zap className="h-5 w-5 text-yellow-500" />
                  Enhanced Features
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-sm">Vector-based skin condition detection</p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-sm">FAISS similarity search</p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-sm">scIN dataset integration</p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-sm">Optional demographic context</p>
                </div>
              </CardContent>
            </Card>

            {/* How It Works */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Brain className="h-5 w-5 text-blue-500" />
                  How It Works
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-2">
                  <p className="text-sm font-medium">1. Image Analysis</p>
                  <p className="text-xs text-muted-foreground">Google Vision API extracts facial features</p>
                </div>
                <div className="space-y-2">
                  <p className="text-sm font-medium">2. Condition Detection</p>
                  <p className="text-xs text-muted-foreground">AI model identifies skin conditions</p>
                </div>
                <div className="space-y-2">
                  <p className="text-sm font-medium">3. Vector Creation</p>
                  <p className="text-xs text-muted-foreground">Creates 2048-dimensional feature vector</p>
                </div>
                <div className="space-y-2">
                  <p className="text-sm font-medium">4. Similarity Search</p>
                  <p className="text-xs text-muted-foreground">FAISS finds similar skin profiles</p>
                </div>
                <div className="space-y-2">
                  <p className="text-sm font-medium">5. Recommendations</p>
                  <p className="text-xs text-muted-foreground">Personalized product suggestions</p>
                </div>
              </CardContent>
            </Card>

            {/* Dataset Info */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Database className="h-5 w-5 text-green-500" />
                  Powered by scIN Dataset
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground">
                  Our analysis is enhanced by the scIN (Skin Condition Image Network) dataset, 
                  containing thousands of dermatologist-annotated skin images with detailed condition labels.
                </p>
                <div className="text-xs text-muted-foreground">
                  <p>• Dermatologist-verified conditions</p>
                  <p>• Multiple skin types and tones</p>
                  <p>• Age and ethnicity diversity</p>
                  <p>• Continuous model improvement</p>
                </div>
              </CardContent>
            </Card>

            {/* Tips */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Tips for Best Results</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-sm">Ensure good, even lighting</p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-sm">Remove makeup and glasses</p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-sm">Position your face in the center</p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-sm">Provide optional demographic data for better accuracy</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
} 