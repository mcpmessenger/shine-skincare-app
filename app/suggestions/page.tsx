'use client';

/**
 * Product Recommendations Page
 * 
 * Features:
 * - Personalized skin analysis results
 * - Product recommendations based on analysis
 * - Add to cart functionality
 * - Clean, production-ready interface
 */

import { useSearchParams } from 'next/navigation';
import { useState, useEffect, Suspense } from 'react';
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
  face_detection: {
    detected: boolean;
    confidence: number;
    face_bounds: any;
    image_dimensions: number[];
  };
  confidence_score: number;
  analysis_summary: string;
  primary_concerns: string[];
  detected_conditions: Array<{
    name: string;
    confidence: number;
    severity: string;
    source: string;
    description: string;
  }>;
  severity_level: string;
  top_recommendations: string[];
  immediate_actions: string[];
  lifestyle_changes: string[];
  medical_advice: string[];
  prevention_tips: string[];
  best_match: {
    condition: string;
    similarity_score: number;
    confidence: number;
    description: string;
    symptoms: string[];
    severity: string;
  };
  condition_matches: Array<{
    condition: string;
    similarity_score: number;
    confidence: number;
    description: string;
    symptoms: string[];
    severity: string;
  }>;
  system_capabilities?: {
    real_dataset_conditions: number;
    computer_vision_algorithms: boolean;
    condition_matching: boolean;
    severity_scoring: boolean;
    personalized_recommendations: boolean;
  };
  // Enhanced ML model properties
  confidence?: {
    condition_detection: number;
    overall: number;
  };
  primary_condition?: {
    condition: string;
    confidence: number;
    condition_id: number;
    all_probabilities: number[];
  };
  model_version?: string;
  enhanced_ml?: boolean;
  fixed_ml?: boolean;
  accuracy?: string;
  summary?: string;
  recommendations?: {
    immediate_actions: string[];
    products: string[];
    lifestyle_changes: string[];
    professional_advice: string[];
  };
  severity?: {
    description: string;
    level: string;
  };
  technical_details?: {
    attention_mechanisms: boolean;
    fairness_mitigation: boolean;
    model_used: string;
  };
  frontend_metadata?: {
    endpoint: string;
    timestamp: string;
    enhanced_ml_model: boolean;
    fixed_ml_model: boolean;
    model_version: string;
    accuracy: string;
  };
  // New fixed model properties (as additional fields)
  primary_condition_name?: string;
  confidence_score_new?: number;
  percentage?: number;
  severity_level_new?: string;
  top_3_predictions?: Array<{
    condition: string;
    confidence: number;
    percentage: number;
  }>;
  all_predictions?: {
    [key: string]: number;
  };
  result?: {
    health_score: number;
    primary_concerns: string[];
    severity_levels: { [key: string]: string };
    conditions: { [key: string]: { confidence: number; severity: string; description?: string } };
  };
}

function SuggestionsPageContent() {
  
  const searchParams = useSearchParams();
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [showTechnicalData, setShowTechnicalData] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [cartItems, setCartItems] = useState<string[]>([]);
  
  // Cart and analysis result state management
  useEffect(() => {
    // Cart items and analysis result are managed here
  }, [cartItems, analysisResult]);

  useEffect(() => {
    console.log('🔍 Suggestions page loading...');
    // Try to get analysis data from sessionStorage first
    const storedAnalysis = sessionStorage.getItem('analysisResult');
    console.log('📦 Stored analysis data:', storedAnalysis ? 'Found' : 'Not found');
    
    if (storedAnalysis) {
      try {
        const result = JSON.parse(storedAnalysis);
        console.log('✅ Successfully parsed analysis result:', result);
        setAnalysisResult(result);
        // Clear the stored data after retrieving it
        sessionStorage.removeItem('analysisResult');
        console.log('🗑️ Cleared analysis data from sessionStorage');
      } catch (error) {
        console.error('❌ Error parsing analysis data from sessionStorage:', error);
      }
    } else {
      // Fallback to URL parameter for backward compatibility
      const analysisParam = searchParams.get('analysis');
      console.log('🔗 URL analysis parameter:', analysisParam ? 'Found' : 'Not found');
      
      if (analysisParam) {
        try {
          const decoded = decodeURIComponent(analysisParam);
          const result = JSON.parse(decoded);
          console.log('✅ Successfully parsed analysis result from URL:', result);
          setAnalysisResult(result);
        } catch (error) {
          console.error('❌ Error parsing analysis data from URL:', error);
        }
      } else {
        console.log('⚠️ No analysis data found in sessionStorage or URL');
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

  // Enhanced ML model compatibility
  const getEnhancedConfidence = (): number => {
    // Handle new fixed model format
    if (analysisResult?.percentage) {
      return Math.round(analysisResult.percentage);
    }
    if (analysisResult?.confidence_score_new) {
      return Math.round(analysisResult.confidence_score_new * 100);
    }
    if (analysisResult?.confidence?.overall) {
      return Math.round(analysisResult.confidence.overall * 100);
    }
    if (analysisResult?.confidence?.condition_detection) {
      return Math.round(analysisResult.confidence.condition_detection * 100);
    }
    if (analysisResult?.primary_condition?.confidence) {
      return Math.round(analysisResult.primary_condition.confidence * 100);
    }
    // NEW: Handle Hare Run V6 enhanced analyzer response
    if (analysisResult?.result?.health_score) {
      return Math.round(analysisResult.result.health_score);
    }
    return analysisResult?.confidence_score ? getConfidenceScore(analysisResult.confidence_score) : 0;
  };

  // NEW: Extract primary condition from Hare Run V6 response
  const getPrimaryCondition = () => {
    if (analysisResult?.result?.primary_concerns && analysisResult.result.primary_concerns.length > 0) {
      const primary = analysisResult.result.primary_concerns[0];
      return {
        name: primary,
        confidence: analysisResult.result.health_score || 0,
        severity: analysisResult.result.severity_levels?.[primary] || 'moderate'
      };
    }
    return null;
  };

  // NEW: Extract detected conditions from Hare Run V6 response
  const getDetectedConditions = () => {
    if (analysisResult?.result?.conditions) {
      const conditions = [];
      for (const [condition, data] of Object.entries(analysisResult.result.conditions)) {
        if (data && typeof data === 'object' && 'severity' in data) {
          conditions.push({
            name: condition,
            confidence: data.confidence || 0,
            severity: data.severity || 'moderate',
            description: data.description || `Detected ${condition}`
          });
        }
      }
      return conditions;
    }
    return [];
  };

  // NEW: Generate analysis summary from Hare Run V6 response
  const getAnalysisSummary = () => {
    if (analysisResult?.result?.primary_concerns && analysisResult.result.health_score) {
      const concerns = analysisResult.result.primary_concerns.join(', ');
      return `Analysis detected: ${concerns}. Overall health score: ${analysisResult.result.health_score}/100`;
    }
    return analysisResult?.analysis_summary || 'Analysis completed successfully';
  };

  // NEW: Get severity assessment from Hare Run V6 response
  const getSeverityAssessment = () => {
    if (analysisResult?.result?.severity_levels) {
      const levels = analysisResult.result.severity_levels;
      const overallSeverity = Object.values(levels).reduce((max, current) => {
        const severityOrder: { [key: string]: number } = { 'none': 0, 'minimal': 1, 'low': 2, 'moderate': 3, 'severe': 4 };
        return severityOrder[current] > severityOrder[max] ? current : max;
      }, 'none');
      
      return {
        level: overallSeverity,
        description: `Overall severity: ${overallSeverity}`
      };
    }
    return { level: 'unknown', description: 'Severity assessment unavailable' };
  };

  const getConditionProbability = (condition: string): number => {
    // Handle new fixed model format
    if (analysisResult?.all_predictions && analysisResult.all_predictions[condition]) {
      return Math.round(analysisResult.all_predictions[condition] * 100);
    }
    
    // Enhanced ML model compatibility
    if (analysisResult?.primary_condition?.condition === condition) {
      return Math.round((analysisResult.primary_condition.confidence || 0) * 100);
    }
    
    if (!analysisResult?.condition_matches) {
      return 0;
    }
    
    const conditionMatch = analysisResult.condition_matches.find(match => match.condition === condition);
    if (!conditionMatch) return 0;
    
    return Math.round(conditionMatch.confidence);
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

  const addToCart = (productId: string) => {
    setCartItems(prev => {
      if (prev.includes(productId)) {
        return prev.filter(id => id !== productId);
      } else {
        return [...prev, productId];
      }
    });
  };

  const getRecommendedProducts = () => {
    if (!analysisResult) return [];
    
    const recommendedProducts: any[] = [];
    
    // PRIORITY 1: Handle Hare Run V6 detected_conditions array (actual data structure)
    if (analysisResult.detected_conditions && analysisResult.detected_conditions.length > 0) {
      // Map conditions to product categories
      const conditionToCategory: { [key: string]: string[] } = {
        acne: ['cleanser', 'treatment', 'moisturizer'],
        rosacea: ['cleanser', 'moisturizer', 'sunscreen'],
        eczema: ['moisturizer', 'treatment'],
        actinic_keratosis: ['sunscreen', 'treatment'],
        basal_cell_carcinoma: ['sunscreen', 'treatment'],
        healthy: ['cleanser', 'moisturizer', 'sunscreen'],
        // Add more condition mappings as needed
        'skin_cancer': ['sunscreen', 'treatment'],
        'melanoma': ['sunscreen', 'treatment'],
        'dermatitis': ['moisturizer', 'treatment'],
        'psoriasis': ['moisturizer', 'treatment'],
        'hyperpigmentation': ['treatment', 'sunscreen'],
        'aging': ['moisturizer', 'treatment', 'sunscreen'],
        'dark_spots': ['treatment', 'sunscreen'],
        'pores': ['cleanser', 'treatment'],
        'wrinkles': ['moisturizer', 'treatment'],
        'bags': ['treatment', 'moisturizer'],
        'redness': ['cleanser', 'moisturizer', 'sunscreen']
      };

      // Process each detected condition from the array
      analysisResult.detected_conditions.forEach((conditionData) => {
        if (conditionData && conditionData.name && conditionData.confidence) {
          const conditionName = conditionData.name.toLowerCase();
          const confidence = conditionData.confidence || 0;
          const severity = conditionData.severity || 'moderate';
          
          // Only recommend products for conditions with reasonable confidence
          if (confidence > 0.1) { // 10% confidence threshold
            const categories = conditionToCategory[conditionName] || [];
            categories.forEach((category: string) => {
              const categoryProducts = products.filter(p => p.category === category);
              if (categoryProducts.length > 0) {
                recommendedProducts.push({
                  ...categoryProducts[0],
                  match: conditionName,
                  reason: `Recommended for ${conditionName.replace('_', ' ')} (${Math.round(confidence * 100)}% confidence)`,
                  confidence: confidence,
                  severity: severity
                });
              }
            });
          }
        }
      });
    }
    
    // PRIORITY 2: Handle Hare Run V6 result.conditions (alternative structure)
    if (recommendedProducts.length === 0 && analysisResult.result?.conditions) {
      // Map conditions to product categories
      const conditionToCategory: { [key: string]: string[] } = {
        acne: ['cleanser', 'treatment', 'moisturizer'],
        rosacea: ['cleanser', 'moisturizer', 'sunscreen'],
        eczema: ['moisturizer', 'treatment'],
        actinic_keratosis: ['sunscreen', 'treatment'],
        basal_cell_carcinoma: ['sunscreen', 'treatment'],
        healthy: ['cleanser', 'moisturizer', 'sunscreen'],
        'skin_cancer': ['sunscreen', 'treatment'],
        'melanoma': ['sunscreen', 'treatment'],
        'dermatitis': ['moisturizer', 'treatment'],
        'psoriasis': ['moisturizer', 'treatment'],
        'hyperpigmentation': ['treatment', 'sunscreen'],
        'aging': ['moisturizer', 'treatment', 'sunscreen']
      };

      // Process each detected condition
      Object.entries(analysisResult.result.conditions).forEach(([condition, data]) => {
        if (data && typeof data === 'object' && 'confidence' in data) {
          const conditionName = condition.toLowerCase();
          const confidence = data.confidence || 0;
          const severity = data.severity || 'moderate';
          
          // Only recommend products for conditions with reasonable confidence
          if (confidence > 0.1) { // 10% confidence threshold
            const categories = conditionToCategory[conditionName] || [];
            categories.forEach((category: string) => {
              const categoryProducts = products.filter(p => p.category === category);
              if (categoryProducts.length > 0) {
                recommendedProducts.push({
                  ...categoryProducts[0],
                  match: conditionName,
                  reason: `Recommended for ${conditionName.replace('_', ' ')} (${Math.round(confidence * 100)}% confidence)`,
                  confidence: confidence,
                  severity: severity
                });
              }
            });
          }
        }
      });
    }
    
    // PRIORITY 3: Handle new fixed model format (fallback)
    if (recommendedProducts.length === 0 && analysisResult.primary_condition) {
      let condition: string;
      
      // Handle both string and object formats
      if (typeof analysisResult.primary_condition === 'string') {
        condition = analysisResult.primary_condition;
      } else if (analysisResult.primary_condition.condition) {
        condition = analysisResult.primary_condition.condition;
      } else {
        return recommendedProducts;
      }
      
      // Map conditions to product categories
      const conditionToCategory: { [key: string]: string[] } = {
        acne: ['cleanser', 'treatment', 'moisturizer'],
        rosacea: ['cleanser', 'moisturizer', 'sunscreen'],
        eczema: ['moisturizer', 'treatment'],
        actinic_keratosis: ['sunscreen', 'treatment'],
        basal_cell_carcinoma: ['sunscreen', 'treatment'],
        healthy: ['cleanser', 'moisturizer', 'sunscreen']
      };

      const categories = conditionToCategory[condition] || [];
      categories.forEach((category: string) => {
        const categoryProducts = products.filter(p => p.category === category);
        if (categoryProducts.length > 0) {
          recommendedProducts.push({
            ...categoryProducts[0],
            match: condition,
            reason: `Recommended for ${condition.replace('_', ' ')}`
          });
        }
      });
    }

    // Remove duplicates and limit to 6 products
    const unique = recommendedProducts.filter((product, index, self) =>
      index === self.findIndex(p => p.id === product.id)
    );

    // FALLBACK: If no specific recommendations, show general products
    if (unique.length === 0) {
      const generalProducts = products.slice(0, 6).map(product => ({
        ...product,
        match: 'general',
        reason: 'General skincare recommendation',
        confidence: 0.5,
        severity: 'moderate'
      }));
      return generalProducts;
    }

    return unique.slice(0, 6);
  };

  if (!analysisResult) {
    return (
      <div className="min-h-screen bg-transparent text-primary flex items-center justify-center">
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
      <div className="min-h-screen bg-transparent text-primary flex items-center justify-center">
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

  const overallConfidence = getEnhancedConfidence();
  const conditions = analysisResult.detected_conditions?.map(condition => condition.name) || [];
  const recommendedProducts = getRecommendedProducts();

  return (
    <div className="min-h-screen bg-transparent text-primary">
      <Header />
      <div className="container mx-auto px-4 py-6">
                 {/* Header */}
         <div className="text-center mb-8">
           <img 
             src="https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png" 
             alt="Shine Skin Collective" 
             className="w-20 h-20 mx-auto mb-4"
           />
           <h1 className="text-3xl md:text-4xl font-light mb-2">Analysis Results</h1>
           <p className="text-lg text-secondary font-light">
             Your personalized skin analysis and recommendations
           </p>
           

         </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          
          {/* Analysis Summary */}
          <div className="bg-secondary/50 backdrop-blur-sm rounded-2xl shadow-lg p-6 mb-6 border border-primary/20">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-light">Analysis Summary</h2>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-secondary">Confidence:</span>
                <span className="text-lg font-semibold text-primary">{overallConfidence}%</span>
              </div>
            </div>
            
            {/* Primary Condition */}
            <div className="mb-6">
              <h3 className="text-lg font-light mb-2">Primary Condition</h3>
              <div className="bg-primary/10 rounded-xl p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-xl font-medium capitalize">
                      {getPrimaryCondition()?.name || 
                       (typeof analysisResult.primary_condition === 'string' 
                        ? analysisResult.primary_condition 
                        : analysisResult.primary_condition?.condition || 'Healthy')}
                    </h4>
                    <p className="text-secondary text-sm mt-1">
                      {getAnalysisSummary() || 
                       analysisResult.summary || 
                       'Your skin appears to be in good condition.'}
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-primary">
                      {overallConfidence}%
                    </div>
                    <div className="text-sm text-secondary">Confidence</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Top 3 Predictions */}
            {analysisResult.top_3_predictions && (
              <div className="mb-6">
                <h3 className="text-lg font-light mb-3">Top Predictions</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {analysisResult.top_3_predictions.map((prediction, index) => (
                    <div key={index} className="bg-primary/5 rounded-lg p-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium capitalize">
                          {prediction.condition.replace('_', ' ')}
                        </span>
                        <span className="text-sm text-secondary">
                          {Math.round(prediction.percentage)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-primary h-2 rounded-full" 
                          style={{ width: `${prediction.percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Severity */}
            {analysisResult.severity && (
              <div className="mb-6">
                <h3 className="text-lg font-light mb-2">Severity Assessment</h3>
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm ${getSeverityColor(typeof analysisResult.severity === 'string' ? analysisResult.severity : analysisResult.severity.level)}`}>
                  {getSeverityIcon(typeof analysisResult.severity === 'string' ? analysisResult.severity : analysisResult.severity.level)}
                  <span className="ml-2 capitalize">
                    {typeof analysisResult.severity === 'string' ? analysisResult.severity : analysisResult.severity.level} Severity
                  </span>
                </div>
              </div>
            )}

            {/* NEW: Hare Run V6 Detected Conditions */}
            {getDetectedConditions().length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-light mb-3">Detected Conditions</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {getDetectedConditions().map((condition, index) => (
                    <div key={index} className="bg-primary/5 rounded-lg p-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium capitalize">
                          {condition.name.replace('_', ' ')}
                        </span>
                        <span className={`text-xs px-2 py-1 rounded-full ${getSeverityColor(condition.severity)}`}>
                          {condition.severity}
                        </span>
                      </div>
                      <p className="text-xs text-secondary">{condition.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* NEW: Hare Run V6 Severity Assessment */}
            {getSeverityAssessment().level !== 'unknown' && (
              <div className="mb-6">
                <h3 className="text-lg font-light mb-2">Overall Severity Assessment</h3>
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm ${getSeverityColor(getSeverityAssessment().level)}`}>
                  {getSeverityIcon(getSeverityAssessment().level)}
                  <span className="ml-2 capitalize">
                    {getSeverityAssessment().level} Severity
                  </span>
                </div>
                <p className="text-sm text-secondary mt-2">{getSeverityAssessment().description}</p>
              </div>
            )}


            {cartItems.length > 0 && (
              <div className="mt-6 text-center">
                <button 
                  className="px-6 py-3 bg-green-500 text-white rounded-xl hover:bg-green-600 transition-colors font-medium"
                >
                  🛒 Checkout ({cartItems.length} items)
                </button>
              </div>
            )}
          </div>

                     {/* Recommendations */}
           <div className="bg-secondary/50 backdrop-blur-sm rounded-2xl shadow-lg p-6 mb-6 border border-primary/20">
             <div className="flex items-center justify-between mb-4">
               <h2 className="text-2xl font-light">Recommendations</h2>
               {cartItems.length > 0 && (
                 <div className="flex items-center space-x-2">
                   <div className="bg-primary/10 px-3 py-1 rounded-full text-sm">
                     <span className="text-primary font-medium">{cartItems.length}</span>
                     <span className="text-secondary ml-1">items in cart</span>
                   </div>
                   <button 
                     onClick={() => setCartItems([])}
                     className="text-sm text-secondary hover:text-primary transition-colors"
                   >
                     Clear Cart
                   </button>
                 </div>
               )}
             </div>
             
             {/* Immediate Actions */}
             {analysisResult.recommendations && analysisResult.recommendations.immediate_actions && analysisResult.recommendations.immediate_actions.length > 0 && (
               <div className="mb-6">
                 <h3 className="text-lg font-light mb-3 flex items-center">
                   <Zap className="w-5 h-5 mr-2" />
                   Immediate Actions
                 </h3>
                 <ul className="space-y-2">
                   {analysisResult.recommendations.immediate_actions.map((action, index) => (
                     <li key={index} className="flex items-start">
                       <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 mr-2 flex-shrink-0" />
                       <span className="text-sm">{action}</span>
                     </li>
                   ))}
                 </ul>
               </div>
             )}

             {/* Lifestyle Changes */}
             {analysisResult.recommendations && analysisResult.recommendations.lifestyle_changes && analysisResult.recommendations.lifestyle_changes.length > 0 && (
               <div className="mb-6">
                 <h3 className="text-lg font-light mb-3 flex items-center">
                   <TrendingUp className="w-5 h-5 mr-2" />
                   Lifestyle Changes
                 </h3>
                 <ul className="space-y-2">
                   {analysisResult.recommendations.lifestyle_changes.map((change, index) => (
                     <li key={index} className="flex items-start">
                       <Circle className="w-4 h-4 text-blue-500 mt-0.5 mr-2 flex-shrink-0" />
                       <span className="text-sm">{change}</span>
                     </li>
                   ))}
                 </ul>
               </div>
             )}

             {/* Professional Advice */}
             {analysisResult.recommendations && analysisResult.recommendations.professional_advice && analysisResult.recommendations.professional_advice.length > 0 && (
               <div className="mb-6">
                 <h3 className="text-lg font-light mb-3 flex items-center">
                   <AlertTriangle className="w-5 h-5 mr-2" />
                   Professional Advice
                 </h3>
                 <ul className="space-y-2">
                   {analysisResult.recommendations.professional_advice.map((advice, index) => (
                     <li key={index} className="flex items-start">
                       <AlertTriangle className="w-4 h-4 text-orange-500 mt-0.5 mr-2 flex-shrink-0" />
                       <span className="text-sm">{advice}</span>
                     </li>
                   ))}
                 </ul>
               </div>
             )}

             {/* Product Recommendations - Integrated into Recommendations section */}
             <div className="mb-6">
               <h3 className="text-lg font-light mb-3 flex items-center">
                 <ShoppingCart className="w-5 h-5 mr-2" />
                 Recommended Products
               </h3>
               {recommendedProducts.length > 0 ? (
                 <div>
                   <div className="mb-4 p-3 bg-primary/5 rounded-lg border border-primary/20">
                     <div className="flex items-center justify-between">
                       <div>
                         <h4 className="font-medium text-primary">Found {recommendedProducts.length} recommended products</h4>
                         <p className="text-sm text-secondary">
                           Based on your skin analysis results
                         </p>
                       </div>
                       <div className="text-right">
                         <div className="text-xl font-bold text-primary">{recommendedProducts.length}</div>
                         <div className="text-xs text-secondary">products</div>
                       </div>
                     </div>
                   </div>

                   <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                     {recommendedProducts.map((product) => {
                       console.log('🛒 Rendering product:', product.name, 'with ID:', product.id, 'Image:', product.image);
                       return (
                         <div key={product.id} className={`rounded-xl p-4 transition-colors relative ${
                           cartItems.includes(product.id) 
                             ? 'bg-green-50 border-2 border-green-200 dark:bg-green-900/20 dark:border-green-800' 
                             : 'bg-primary/5 hover:bg-primary/10'
                         }`}>
                           {cartItems.includes(product.id) && (
                             <div className="absolute top-2 left-2">
                               <div className="bg-green-500 text-white rounded-full w-6 h-6 flex items-center justify-center">
                                 <CheckCircle className="w-4 h-4" />
                               </div>
                             </div>
                           )}
                           <div className="relative mb-3">
                             <Image
                               src={product.image}
                               alt={product.name}
                               width={200}
                               height={200}
                               className="w-full h-32 object-cover rounded-lg"
                               onError={(e) => {
                                 console.log('🖼️ Image failed to load:', product.image);
                                 const target = e.target as HTMLImageElement;
                                 target.src = 'https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png';
                               }}
                               onLoad={() => {
                                 console.log('🖼️ Image loaded successfully:', product.image);
                               }}
                             />
                             <div className="absolute top-2 right-2">
                               <div className="bg-primary/90 text-white px-2 py-1 rounded-full text-xs font-medium">
                                 {product.category}
                               </div>
                             </div>
                           </div>
                           <div className="mb-3">
                             <h4 className="font-medium text-lg mb-1">{product.name}</h4>
                             <p className="text-sm text-secondary line-clamp-2">{product.description}</p>
                             
                             {/* Hare Run V6 Analysis Info */}
                             {product.match && product.match !== 'general' && (
                               <div className="mt-2 space-y-1">
                                 <div className="flex items-center justify-between text-xs">
                                   <span className="text-secondary">Condition:</span>
                                   <span className="font-medium capitalize text-primary">
                                     {product.match.replace('_', ' ')}
                                   </span>
                                 </div>
                                 {product.confidence && (
                                   <div className="flex items-center justify-between text-xs">
                                     <span className="text-secondary">Confidence:</span>
                                     <span className="font-medium text-primary">
                                       {Math.round(product.confidence * 100)}%
                                     </span>
                                   </div>
                                 )}
                                 {product.severity && (
                                   <div className="flex items-center justify-between text-xs">
                                     <span className="text-secondary">Severity:</span>
                                     <span className={`font-medium capitalize px-2 py-1 rounded-full text-xs ${getSeverityColor(product.severity)}`}>
                                       {product.severity}
                                     </span>
                                   </div>
                                 )}
                               </div>
                             )}
                           </div>
                           <div className="flex items-center justify-between">
                             <span className="text-lg font-semibold text-primary">${product.price}</span>
                             <button 
                               onClick={() => addToCart(product.id)}
                               className={`btn btn-primary px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 flex items-center space-x-2 ${
                                 cartItems.includes(product.id)
                                   ? '!bg-green-500 !text-white hover:!bg-green-600'
                                   : '!bg-accent-color !text-white hover:!bg-accent-hover'
                               }`}
                               style={{
                                 borderRadius: '24px',
                                 minHeight: '44px',
                                 border: 'none',
                                 boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
                               }}
                             >
                               {cartItems.includes(product.id) ? (
                                 <>
                                   <CheckCircle className="w-4 h-4" />
                                   <span>Added to Cart</span>
                                 </>
                               ) : (
                                 <>
                                   <ShoppingCart className="w-4 h-4" />
                                   <span>Add to Cart</span>
                                 </>
                               )}
                             </button>
                           </div>
                         </div>
                       );
                     })}
                   </div>
                 </div>
               ) : (
                 <div className="text-center py-6">
                   <ShoppingCart className="w-12 h-12 text-secondary mx-auto mb-4" />
                   <p className="text-secondary font-light">Loading product recommendations...</p>
                 </div>
               )}
             </div>
           </div>

                      

            

          {/* Back Button */}
          <div className="text-center">
            <Link 
              href="/"
              className="inline-flex items-center px-6 py-3 bg-primary text-white rounded-xl hover:bg-primary/80 transition-colors"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back to Analysis
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function SuggestionsPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-transparent text-primary flex items-center justify-center">
        <div className="text-center">
          <img 
            src="https://muse2025.s3.us-east-1.amazonaws.com/shine_logo_option3.png" 
            alt="Shine Skin Collective" 
            className="w-32 h-32 mx-auto mb-6 animate-pulse"
          />
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-600 mx-auto mb-4"></div>
          <p className="text-secondary font-light">Loading...</p>
        </div>
      </div>
    }>
      <SuggestionsPageContent />
    </Suspense>
  );
} 