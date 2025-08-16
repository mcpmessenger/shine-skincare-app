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

interface RecommendedProduct {
  id: string;
  name: string;
  description: string;
  price: number;
  category: string;
  image: string;
  score: number;
  matchReason: string;
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
        // Don't clear the stored data - keep it for other pages to use
        console.log('💾 Keeping analysis data in sessionStorage for other pages');
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

  // Clean up analysis data when user leaves the page
  useEffect(() => {
    const handleBeforeUnload = () => {
      console.log('🚪 User leaving page, clearing analysis data');
      sessionStorage.removeItem('analysisResult');
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      // Only clear if user is actually navigating away, not just component unmounting
      console.log('🔄 Component unmounting, keeping analysis data for navigation');
    };
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

  // Generate intelligent recommendations based on analysis data
  const generateIntelligentRecommendations = (data: AnalysisResult): RecommendedProduct[] => {
    console.log('🧠 Starting enhanced recommendation generation for data:', data)
    console.log('🔍 Full data object keys:', Object.keys(data))
    
    // Extract data from the nested structure
    const conditions = data.result?.conditions || data.detected_conditions || data.primary_concerns || []
    const healthScore = data.result?.health_score || 50
    const primaryConcerns = data.result?.primary_concerns || data.primary_concerns || []
    const severityLevels = data.result?.severity_levels || {}
    
    console.log('📊 Extracted conditions:', conditions)
    console.log('📊 Extracted health score:', healthScore)
    console.log('📊 Primary concerns:', primaryConcerns)
    console.log('📊 Severity levels:', severityLevels)
    console.log('📊 Data.result exists:', !!data.result)
    
    if (!conditions || (Object.keys(conditions).length === 0 && primaryConcerns.length === 0)) {
      console.log('⚠️ No conditions found, cannot generate recommendations')
      console.log('🔍 Available data for debugging:', {
        result_conditions: data.result?.conditions,
        detected_conditions: data.detected_conditions,
        primary_concerns: data.primary_concerns,
        full_data: data
      })
      return []
    }
    
    console.log('✅ Conditions found, proceeding with intelligent scoring...')
    console.log('📦 Total products to score:', products.length)
    
    // Enhanced scoring system with better condition matching
    const scoredProducts = products.map(product => {
      let score = 0
      let reasons: string[] = []

      // Score based on health score (more nuanced)
      if (healthScore < 30) {
        // Very low health score needs intensive treatment
        if (product.category === 'treatment' || product.category === 'serum') {
          score += 10
          reasons.push('Intensive treatment for significant skin concerns')
        }
        if (product.category === 'cleanser') {
          score += 6
          reasons.push('Gentle cleansing for sensitive skin')
        }
      } else if (healthScore < 50) {
        // Low health score needs treatment + maintenance
        if (product.category === 'treatment' || product.category === 'serum') {
          score += 8
          reasons.push('Treatment for skin concerns')
        }
        if (product.category === 'moisturizer') {
          score += 6
          reasons.push('Moisturizing for compromised skin barrier')
        }
      } else if (healthScore < 70) {
        // Moderate health score - balanced approach
        if (product.category === 'moisturizer' || product.category === 'sunscreen') {
          score += 7
          reasons.push('Maintenance and protection for moderate skin health')
        }
        if (product.category === 'serum') {
          score += 5
          reasons.push('Targeted improvement for moderate concerns')
        }
      } else {
        // High health score - maintenance and enhancement
        if (product.category === 'sunscreen') {
          score += 8
          reasons.push('Protection for healthy skin')
        }
        if (product.category === 'moisturizer') {
          score += 6
          reasons.push('Maintenance for healthy skin')
        }
      }

      // Enhanced condition-based scoring using the new data structure
      if (data.result?.conditions) {
        // New structure: conditions object with severity levels
        Object.entries(data.result.conditions).forEach(([conditionKey, conditionData]) => {
          const conditionLower = conditionKey.toLowerCase()
          console.log(`🔍 Scoring product "${product.name}" for condition: ${conditionKey}`)
          
          // Acne-related conditions
          if (conditionLower.includes('acne')) {
            if (product.category === 'cleanser') {
              score += 9
              reasons.push('Gentle cleansing for acne-prone skin')
              console.log(`✅ ${product.name} scored +9 for acne condition (cleanser)`)
            }
            if (product.category === 'treatment' && product.description.toLowerCase().includes('salicylic')) {
              score += 10
              reasons.push('Salicylic acid treatment for acne')
              console.log(`✅ ${product.name} scored +10 for acne condition (salicylic acid)`)
            }
            if (product.description.toLowerCase().includes('gentle') || product.description.toLowerCase().includes('non-comedogenic')) {
              score += 4
              reasons.push('Non-irritating for acne-prone skin')
              console.log(`✅ ${product.name} scored +4 for acne condition (gentle/non-comedogenic)`)
            }
          }
          
          // Dark spots and hyperpigmentation
          if (conditionLower.includes('dark_spot') || conditionLower.includes('pigmentation')) {
            if (product.category === 'treatment' && (product.description.toLowerCase().includes('vitamin c') || product.description.toLowerCase().includes('niacinamide'))) {
              score += 10
              reasons.push('Targets hyperpigmentation with proven ingredients')
              console.log(`✅ ${product.name} scored +10 for dark spots (vitamin c/niacinamide)`)
            }
            if (product.category === 'serum' && product.description.toLowerCase().includes('brightening')) {
              score += 8
              reasons.push('Brightening serum for uneven skin tone')
              console.log(`✅ ${product.name} scored +8 for dark spots (brightening serum)`)
            }
          }
          
          // Pores
          if (conditionLower.includes('pore')) {
            if (product.category === 'cleanser' && product.description.toLowerCase().includes('deep')) {
              score += 8
              reasons.push('Deep cleansing for enlarged pores')
              console.log(`✅ ${product.name} scored +8 for pores (deep cleansing)`)
            }
            if (product.description.toLowerCase().includes('pore') || product.description.toLowerCase().includes('refining')) {
              score += 7
              reasons.push('Pore-refining treatment')
              console.log(`✅ ${product.name} scored +7 for pores (pore-refining)`)
            }
          }
          
          // Redness and rosacea
          if (conditionLower.includes('redness') || conditionLower.includes('rosacea')) {
            if (product.description.toLowerCase().includes('calming') || product.description.toLowerCase().includes('soothing')) {
              score += 9
              reasons.push('Calming and soothing for redness')
              console.log(`✅ ${product.name} scored +9 for redness (calming/soothing)`)
            }
            if (product.description.toLowerCase().includes('gentle') || product.description.toLowerCase().includes('fragrance-free')) {
              score += 6
              reasons.push('Gentle and fragrance-free for sensitive skin')
              console.log(`✅ ${product.name} scored +6 for redness (gentle/fragrance-free)`)
            }
          }
          
          // Wrinkles and aging
          if (conditionLower.includes('wrinkle') || conditionLower.includes('aging')) {
            if (product.category === 'serum' && product.description.toLowerCase().includes('retinol')) {
              score += 10
              reasons.push('Retinol for anti-aging benefits')
              console.log(`✅ ${product.name} scored +10 for wrinkles (retinol)`)
            }
            if (product.category === 'moisturizer' && product.description.toLowerCase().includes('anti-aging')) {
              score += 8
              reasons.push('Anti-aging moisturizer')
              console.log(`✅ ${product.name} scored +8 for wrinkles (anti-aging moisturizer)`)
            }
          }
        })
      } else {
        // Fallback to old structure: conditions array
        if (Array.isArray(conditions)) {
          conditions.forEach(condition => {
            // Handle both string and object conditions
            let conditionName: string;
            if (typeof condition === 'string') {
              conditionName = condition;
            } else if (condition && typeof condition === 'object' && 'name' in condition) {
              conditionName = condition.name;
            } else {
              return; // Skip invalid conditions
            }
            
            const conditionLower = conditionName.toLowerCase()
            console.log(`🔍 Scoring product "${product.name}" for condition: ${conditionName}`)
            
            // Acne-related conditions
            if (conditionLower.includes('acne') || conditionLower.includes('breakout')) {
              if (product.category === 'cleanser') {
                score += 9
                reasons.push('Gentle cleansing for acne-prone skin')
                console.log(`✅ ${product.name} scored +9 for acne condition (cleanser)`)
              }
              if (product.category === 'treatment' && product.description.toLowerCase().includes('salicylic')) {
                score += 10
                reasons.push('Salicylic acid treatment for acne')
                console.log(`✅ ${product.name} scored +10 for acne condition (salicylic acid)`)
              }
              if (product.description.toLowerCase().includes('gentle') || product.description.toLowerCase().includes('non-comedogenic')) {
                score += 4
                reasons.push('Non-irritating for acne-prone skin')
                console.log(`✅ ${product.name} scored +4 for acne condition (gentle/non-comedogenic)`)
              }
            }
            
            // Hyperpigmentation and dark spots
            if (conditionLower.includes('hyperpigmentation') || conditionLower.includes('dark spot') || conditionLower.includes('melasma')) {
              if (product.category === 'treatment' && (product.description.toLowerCase().includes('vitamin c') || product.description.toLowerCase().includes('niacinamide'))) {
                score += 10
                reasons.push('Targets hyperpigmentation with proven ingredients')
                console.log(`✅ ${product.name} scored +10 for hyperpigmentation (vitamin c/niacinamide)`)
              }
              if (product.category === 'serum' && product.description.toLowerCase().includes('brightening')) {
                score += 8
                reasons.push('Brightening serum for uneven skin tone')
                console.log(`✅ ${product.name} scored +8 for hyperpigmentation (brightening serum)`)
              }
            }
            
            // Dryness and dehydration
            if (conditionLower.includes('dry') || conditionLower.includes('dehydrated') || conditionLower.includes('flaky')) {
              if (product.category === 'moisturizer' && product.description.toLowerCase().includes('hydrating')) {
                score += 9
                reasons.push('Hydrating moisturizer for dry skin')
                console.log(`✅ ${product.name} scored +9 for dryness (hydrating moisturizer)`)
              }
              if (product.category === 'serum' && product.description.toLowerCase().includes('hyaluronic')) {
                score += 8
                reasons.push('Hyaluronic acid for hydration')
                console.log(`✅ ${product.name} scored +8 for dryness (hyaluronic acid)`)
              }
            }
            
            // Sensitivity and redness
            if (conditionLower.includes('sensitive') || conditionLower.includes('redness') || conditionLower.includes('irritated')) {
              if (product.description.toLowerCase().includes('gentle') || product.description.toLowerCase().includes('calming')) {
                score += 8
                reasons.push('Gentle and calming for sensitive skin')
                console.log(`✅ ${product.name} scored +8 for sensitivity (gentle/calming)`)
              }
              if (product.description.toLowerCase().includes('fragrance-free') || product.description.toLowerCase().includes('hypoallergenic')) {
                score += 6
                reasons.push('Fragrance-free for sensitive skin')
                console.log(`✅ ${product.name} scored +6 for sensitivity (fragrance-free/hypoallergenic)`)
              }
            }
            
            // Aging and fine lines
            if (conditionLower.includes('aging') || conditionLower.includes('fine line') || conditionLower.includes('wrinkle')) {
              if (product.category === 'serum' && product.description.toLowerCase().includes('retinol')) {
                score += 9
                reasons.push('Retinol for anti-aging benefits')
                console.log(`✅ ${product.name} scored +9 for aging (retinol)`)
              }
              if (product.category === 'moisturizer' && product.description.toLowerCase().includes('anti-aging')) {
                score += 7
                reasons.push('Anti-aging moisturizer')
                console.log(`✅ ${product.name} scored +7 for aging (anti-aging moisturizer)`)
              }
            }
            
            // Sun damage
            if (conditionLower.includes('sun damage') || conditionLower.includes('uv damage')) {
              if (product.category === 'sunscreen') {
                score += 10
                reasons.push('Essential protection for sun-damaged skin')
                console.log(`✅ ${product.name} scored +10 for sun damage (sunscreen)`)
              }
              if (product.description.toLowerCase().includes('repair') || product.description.toLowerCase().includes('recovery')) {
                score += 6
                reasons.push('Repair and recovery for sun damage')
                console.log(`✅ ${product.name} scored +6 for sun damage (repair/recovery)`)
              }
            }
          })
        }
      }

      // Category balance and essential products
      if (product.category === 'cleanser') score += 3
      if (product.category === 'sunscreen') score += 4
      if (product.category === 'moisturizer') score += 2
      
      // Brand reputation and quality indicators
      if (product.description.toLowerCase().includes('clinical') || product.description.toLowerCase().includes('medical-grade')) {
        score += 2
        reasons.push('Medical-grade formulation')
      }
      
      // Price consideration (affordability bonus)
      if (product.price < 50) score += 1

      console.log(`📊 ${product.name} final score: ${score}, reasons: ${reasons.join(', ')}`)

      return {
        ...product,
        score,
        matchReason: reasons.length > 0 ? reasons.join('; ') : 'Recommended for your skin profile'
      }
    })

    console.log('🎯 Enhanced scored products:', scoredProducts.map(p => ({ 
      name: p.name, 
      score: p.score, 
      reason: p.matchReason,
      category: p.category 
    })))

    // Sort by score and return top recommendations with category diversity
    const sortedByScore = scoredProducts.sort((a, b) => b.score - a.score)
    console.log('📊 Top 10 scored products:', sortedByScore.slice(0, 10).map(p => ({ name: p.name, score: p.score, category: p.category })))
    
    // Ensure we have a good mix of categories
    const topRecommendations = []
    const categoryCounts = { cleanser: 0, treatment: 0, serum: 0, moisturizer: 0, sunscreen: 0 }
    
    for (const product of sortedByScore) {
      if (topRecommendations.length >= 6) break
      
      const category = product.category as keyof typeof categoryCounts
      if (categoryCounts[category] < 2) { // Max 2 products per category
        topRecommendations.push(product)
        categoryCounts[category]++
        console.log(`✅ Added ${product.name} (${category}) to recommendations`)
      }
    }
    
    // Fill remaining slots with highest scoring products
    for (const product of sortedByScore) {
      if (topRecommendations.length >= 6) break
      if (!topRecommendations.find(p => p.id === product.id)) {
        topRecommendations.push(product)
        console.log(`✅ Added ${product.name} (${product.category}) to fill remaining slot`)
      }
    }
    
    console.log('🎯 Final enhanced recommendations:', topRecommendations.map(p => ({ 
      name: p.name, 
      score: p.score, 
      category: p.category 
    })))
    
    return topRecommendations
  }

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
  const recommendedProducts = generateIntelligentRecommendations(analysisResult);

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
                             {product.matchReason && (
                               <div className="mt-2 space-y-1">
                                 <div className="flex items-center justify-between text-xs">
                                   <span className="text-secondary">Reason:</span>
                                   <span className="font-medium text-primary">{product.matchReason}</span>
                                 </div>
                                 {product.score && (
                                   <div className="flex items-center justify-between text-xs">
                                     <span className="text-secondary">Score:</span>
                                     <span className="font-medium text-primary">
                                       {product.score}
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
          <div className="text-center space-x-4">
            <Link 
              href="/"
              className="inline-flex items-center px-6 py-3 bg-primary text-white rounded-xl hover:bg-primary/80 transition-colors"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back to Analysis
            </Link>
            
            <Link 
              href="/catalog"
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
            >
              <ShoppingCart className="w-5 h-5 mr-2" />
              View Full Catalog
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