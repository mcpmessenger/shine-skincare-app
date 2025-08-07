'use client';

import { useSearchParams } from 'next/navigation';
import { useState, useEffect } from 'react';
import { 
  CheckCircle, 
  AlertTriangle, 
  Circle, 
  ChevronDown, 
  Zap,
  TrendingUp,
  Eye,
  Sun,
  ShoppingCart,
  Star,
  ArrowLeft
} from 'lucide-react';
import Link from 'next/link';
import { products } from '@/lib/products';
import Image from 'next/image';
import { Header } from '@/components/header';

interface AnalysisResult {
  status: string;
  timestamp: string;
  analysis_type: string;
  demographics: any;
  face_detection: {
    detected: boolean;
    confidence: number;
    face_bounds: any;
    method: string;
    quality_metrics: any;
  };
  skin_analysis: {
    overall_health_score: number;
    texture: string;
    tone: string;
    conditions_detected: Array<{
      condition: string;
      severity: string;
      confidence: number;
      location: string;
      description: string;
    }>;
    analysis_confidence: number;
  };
  similarity_search: {
    dataset_used: string;
    similar_cases: Array<{
      condition: string;
      similarity_score: number;
      dataset_source: string;
      demographic_match: string;
      treatment_suggestions: string[];
    }>;
    cosine_similarities: {
      healthy_baseline: {
        utkface_similarity: number;
        confidence: number;
        demographic_match: string;
      };
      condition_similarities: {
        [key: string]: {
          similarity: number;
          confidence: number;
          dataset: string;
        };
      };
      variance_metrics: {
        similarity_std: number;
        confidence_range: string;
        dataset_coverage: string;
      };
    };
  };
  recommendations: {
    immediate_care: string[];
    long_term_care: string[];
    professional_consultation: boolean;
  };
  quality_assessment: {
    image_quality: string;
    confidence_reliability: string;
  };
}

export default function SuggestionsPage() {
  const searchParams = useSearchParams();
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [showTechnicalData, setShowTechnicalData] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const analysisParam = searchParams.get('analysis');
    if (analysisParam) {
      try {
        const decoded = decodeURIComponent(analysisParam);
        const result = JSON.parse(decoded);
        setAnalysisResult(result);
      } catch (error) {
        console.error('Error parsing analysis data:', error);
      }
    }
  }, [searchParams]);

  useEffect(() => {
    // Set loading to false after initialization
    setTimeout(() => {
      setIsLoading(false);
    }, 1000); // Show logo for 1 second
  }, []);

  const getConfidenceScore = (confidence: number): number => {
    if (confidence > 1) {
      return Math.min(100, confidence * 10);
    }
    return Math.round(confidence * 100);
  };

  const getConditionProbability = (condition: string): number => {
    if (!analysisResult?.similarity_search?.cosine_similarities?.condition_similarities) {
      return 0;
    }
    
    const conditionData = analysisResult.similarity_search.cosine_similarities.condition_similarities[condition];
    if (!conditionData) return 0;
    
    const similarity = Math.abs(conditionData.similarity);
    const confidence = conditionData.confidence;
    
    const probability = Math.min(100, (similarity * 0.7 + confidence * 0.3) * 100);
    return Math.round(probability);
  };

  const getConditionSeverity = (probability: number): string => {
    if (probability >= 70) return 'high';
    if (probability >= 40) return 'moderate';
    if (probability >= 20) return 'low';
    return 'minimal';
  };

  const getSeverityColor = (severity: string): string => {
    const baseColors = {
      high: 'text-red-600 bg-red-50 border-red-200 dark:text-red-400 dark:bg-red-900/20 dark:border-red-800',
      moderate: 'text-orange-600 bg-orange-50 border-orange-200 dark:text-orange-400 dark:bg-orange-900/20 dark:border-orange-800',
      low: 'text-yellow-600 bg-yellow-50 border-yellow-200 dark:text-yellow-400 dark:bg-yellow-900/20 dark:border-yellow-800',
      minimal: 'text-green-600 bg-green-50 border-green-200 dark:text-green-400 dark:bg-green-900/20 dark:border-green-800'
    };
    return baseColors[severity as keyof typeof baseColors] || baseColors.minimal;
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high': return <AlertTriangle className="w-5 h-5" />;
      case 'moderate': return <Zap className="w-5 h-5" />;
      case 'low': return <Circle className="w-4 h-4" />;
      default: return <CheckCircle className="w-4 h-4" />;
    }
  };

  const getRecommendedProducts = () => {
    if (!analysisResult) return [];
    
    const recommendedProducts: any[] = [];
    const conditions = analysisResult.similarity_search.cosine_similarities.condition_similarities;
    
    // Map conditions to product categories
    const conditionToCategory: { [key: string]: string[] } = {
      acne: ['cleanser', 'treatment', 'moisturizer'],
      rosacea: ['cleanser', 'moisturizer', 'sunscreen'],
      eczema: ['moisturizer', 'treatment'],
      actinic_keratosis: ['sunscreen', 'treatment'],
      basal_cell_carcinoma: ['sunscreen', 'treatment'],
      healthy: ['cleanser', 'moisturizer', 'sunscreen']
    };

    // Find products based on detected conditions
    Object.keys(conditions).forEach(condition => {
      const categories = conditionToCategory[condition] || [];
      categories.forEach(category => {
        const categoryProducts = products.filter(p => p.category === category);
        if (categoryProducts.length > 0) {
          recommendedProducts.push({
            ...categoryProducts[0],
            match: condition,
            reason: `Recommended for ${condition.replace('_', ' ')}`
          });
        }
      });
    });

    // Remove duplicates and limit to 6 products
    const unique = recommendedProducts.filter((product, index, self) =>
      index === self.findIndex(p => p.id === product.id)
    );

    return unique.slice(0, 6);
  };

  if (!analysisResult) {
    return (
      <div className="min-h-screen bg-primary text-primary flex items-center justify-center">
        <div className="text-center">
          <img 
            src="https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png" 
            alt="Shine Skin Collective" 
            className="w-32 h-32 mx-auto mb-6 animate-pulse"
          />
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-600 mx-auto mb-4"></div>
          <p className="text-secondary font-light">Analyzing your skin...</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-primary text-primary flex items-center justify-center">
        <div className="text-center">
          <img 
            src="https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png" 
            alt="Shine Skin Collective" 
            className="w-32 h-32 mx-auto mb-6 animate-pulse"
          />
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-600 mx-auto mb-4"></div>
          <p className="text-secondary font-light">Loading Shine...</p>
        </div>
      </div>
    );
  }

  const overallConfidence = getConfidenceScore(analysisResult.skin_analysis.analysis_confidence);
  const conditions = Object.keys(analysisResult.similarity_search.cosine_similarities.condition_similarities);
  const recommendedProducts = getRecommendedProducts();

  return (
    <div className="min-h-screen bg-primary text-primary">
      <Header />
      <div className="container mx-auto px-4 py-6">
        {/* Header */}
        <div className="text-center mb-8">
          <img 
            src="https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png" 
            alt="Shine Skin Collective" 
            className="w-16 h-16 mx-auto mb-4"
          />
          <h1 className="text-2xl md:text-3xl font-light mb-2">Skin Analysis Results</h1>
          <p className="text-sm text-secondary font-light">
            Comprehensive analysis completed with {overallConfidence}% confidence
          </p>
        </div>

        {/* Consolidated Results Section */}
        <div className="bg-secondary rounded-2xl shadow-lg p-6 mb-6 border border-primary">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-light">Analysis Summary</h2>
            <div className="flex items-center space-x-2">
              <Eye className="w-5 h-5 text-gray-600" />
              <span className="text-sm opacity-75 font-light text-gray-700 dark:text-gray-300">AI-Powered</span>
            </div>
          </div>
          
          {/* Health Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="text-center p-4 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
              <div className="text-2xl font-light text-gray-900 dark:text-white">{overallConfidence}%</div>
              <div className="text-sm opacity-75 font-light text-gray-700 dark:text-gray-300">Confidence</div>
            </div>
            <div className="text-center p-4 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
              <div className="text-xl font-light capitalize text-gray-900 dark:text-white">
                {analysisResult.skin_analysis.texture}
              </div>
              <div className="text-sm opacity-75 font-light text-gray-700 dark:text-gray-300">Skin Type</div>
            </div>
            <div className="text-center p-4 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
              <div className="text-xl font-light text-gray-900 dark:text-white">
                {analysisResult.skin_analysis.overall_health_score}/10
              </div>
              <div className="text-sm opacity-75 font-light text-gray-700 dark:text-gray-300">Health Score</div>
            </div>
          </div>

          {/* Condition Probabilities */}
          <div className="mb-6">
            <h3 className="font-light mb-4 flex items-center">
              <Eye className="w-4 h-4 mr-2" />
              Condition Analysis
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {conditions.map((condition) => {
                const probability = getConditionProbability(condition);
                const severity = getConditionSeverity(probability);
                const severityColor = getSeverityColor(severity);
                const severityIcon = getSeverityIcon(severity);
                
                return (
                  <div key={condition} className={`border-2 rounded-xl p-4 ${severityColor}`}>
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-light capitalize text-sm text-gray-900 dark:text-white">{condition.replace('_', ' ')}</h4>
                      {severityIcon}
                    </div>
                    
                    <div className="text-center mb-2">
                      <div className="text-2xl font-light text-gray-900 dark:text-white">{probability}%</div>
                      <div className="text-xs opacity-75 font-light text-gray-700 dark:text-gray-300">Probability</div>
                    </div>
                    
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-2">
                      <div 
                        className="bg-current h-2 rounded-full transition-all duration-300"
                        style={{ width: `${probability}%` }}
                      ></div>
                    </div>
                    
                    <div className="text-xs text-center capitalize font-light text-gray-700 dark:text-gray-300">
                      {severity} risk
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Technical Data Toggle */}
          <div>
            <button
              onClick={() => setShowTechnicalData(!showTechnicalData)}
              className="flex items-center justify-between w-full text-left p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              <div className="flex items-center space-x-2">
                <ChevronDown className="w-4 h-4" />
                <span className="text-sm font-light text-gray-700 dark:text-gray-300">Technical Data</span>
              </div>
              {showTechnicalData ? <ChevronDown className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
            
            {showTechnicalData && (
              <div className="mt-4 space-y-4 text-sm">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <span className="opacity-75 font-light text-gray-700 dark:text-gray-300">Healthy Baseline:</span>
                    <div className="font-light text-gray-900 dark:text-white">
                      {(analysisResult.similarity_search.cosine_similarities.healthy_baseline.utkface_similarity * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div>
                    <span className="opacity-75 font-light text-gray-700 dark:text-gray-300">Confidence:</span>
                    <div className="font-light text-gray-900 dark:text-white">
                      {(analysisResult.similarity_search.cosine_similarities.healthy_baseline.confidence * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div>
                    <span className="opacity-75 font-light text-gray-700 dark:text-gray-300">Coverage:</span>
                    <div className="font-light capitalize text-gray-900 dark:text-white">
                      {analysisResult.similarity_search.cosine_similarities.variance_metrics.dataset_coverage}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Consolidated Recommendations & Products */}
        <div className="bg-secondary rounded-2xl shadow-lg p-6 mb-6 border border-primary">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-light">Recommendations & Products</h2>
            <ShoppingCart className="w-5 h-5 text-gray-600" />
          </div>
          
          {/* Care Recommendations */}
          <div className="mb-6">
            <h3 className="font-light mb-4 flex items-center">
              <TrendingUp className="w-4 h-4 mr-2" />
              Care Recommendations
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-light mb-2 text-green-600 dark:text-green-400">Immediate Care</h4>
                <ul className="space-y-1 text-sm">
                  {analysisResult.recommendations.immediate_care.map((care, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <CheckCircle className="w-3 h-3 text-green-600 mt-0.5 flex-shrink-0" />
                      <span className="opacity-90 font-light">{care}</span>
                    </li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h4 className="font-light mb-2 text-blue-600 dark:text-blue-400">Long-term Care</h4>
                <ul className="space-y-1 text-sm">
                  {analysisResult.recommendations.long_term_care.map((care, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <CheckCircle className="w-3 h-3 text-blue-600 mt-0.5 flex-shrink-0" />
                      <span className="opacity-90 font-light">{care}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Recommended Products */}
          {recommendedProducts.length > 0 && (
            <div>
              <h3 className="font-light mb-4 flex items-center">
                <ShoppingCart className="w-4 h-4 mr-2" />
                Recommended Products
              </h3>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {recommendedProducts.map((product) => (
                  <div key={product.id} className="border rounded-xl p-4 bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
                    <div className="relative mb-3">
                      <Image
                        src={product.image}
                        alt={product.name}
                        width={200}
                        height={200}
                        className="w-full h-32 object-cover rounded-lg"
                      />
                    </div>
                    
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-light text-sm">{product.name}</h3>
                      <span className="text-xs px-2 py-1 rounded bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 font-light">
                        {product.category}
                      </span>
                    </div>
                    
                    <p className="text-xs opacity-75 mb-2 line-clamp-2 font-light">{product.description}</p>
                    
                    <div className="flex items-center justify-between">
                      <span className="font-light text-green-600 dark:text-green-400">
                        ${product.price}
                      </span>
                      <button className="flex items-center space-x-1 text-xs bg-gray-900 dark:bg-white text-white dark:text-black px-3 py-1 rounded-lg hover:bg-gray-800 dark:hover:bg-gray-100 transition-colors font-light">
                        <ShoppingCart className="w-3 h-3" />
                        <span>Add</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="text-center mt-4">
                <Link 
                  href="/catalog" 
                  className="inline-flex items-center space-x-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors font-light"
                >
                  <span>View All Products</span>
                  <ArrowLeft className="w-4 h-4 rotate-180" />
                </Link>
              </div>
            </div>
          )}
        </div>

                 {/* Action Buttons */}
         <div className="text-center space-y-3">
           <Link 
             href="/" 
             className="inline-flex items-center space-x-2 bg-gray-900 dark:bg-white text-white dark:text-black px-6 py-3 rounded-xl hover:bg-gray-800 dark:hover:bg-gray-100 transition-colors font-light"
           >
             <ArrowLeft className="w-4 h-4" />
             <span>New Analysis</span>
           </Link>
         </div>
         
         {/* Disclaimer */}
         <div className="mt-8 text-center">
           <p className="text-xs text-secondary font-light">
             © 2024 All Rights Reserved. This application is for informational purposes only and does not constitute medical advice. 
             Always consult with a qualified healthcare professional for medical concerns.
           </p>
         </div>
       </div>
     </div>
   );
 } 