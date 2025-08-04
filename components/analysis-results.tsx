'use client'

import { CheckCircle, AlertCircle, TrendingUp, Users, Activity, Brain, Shield, X } from 'lucide-react'

interface DemographicAnalysisResult {
  status: string
  timestamp: string
  analysis_type: string
  dataset_used: string
  model_used: string
  demographic_info: {
    age_category: string
    gender: string
    ethnicity: string
  }
  health_score: number
  demographic_baseline: {
    age_group: string
    gender: string
    ethnicity: string
    baseline_health_score: number
    sample_count: number
  }
  comparison_metrics: {
    similarity_to_baseline: number
    percentile_rank: number
    confidence_level: string
  }
  recommendations: {
    demographic_specific: string[]
    general_health: string[]
    professional_consultation: boolean
  }
}

interface ConditionAnalysisResult {
  status: string
  timestamp: string
  analysis_type: string
  dataset_used: string
  model_used: string
  best_match: string
  best_similarity: number
  assessment: string
  condition_results: {
    [condition: string]: {
      similarity: number
      confidence: number
      sample_count: number
    }
  }
  recommendations: string[]
}

interface EnhancedAnalysisResult {
  status: string
  timestamp: string
  analysis_type: string
  demographics: {
    age_category: string | null
    race_category: string | null
  }
  face_detection: {
    detected: boolean
    confidence: number
    face_bounds: {
      x: number
      y: number
      width: number
      height: number
    }
    method: string
    quality_metrics: {
      overall_quality: string
      quality_score: number
    }
  }
  skin_analysis: {
    overall_health_score: number
    texture: string
    tone: string
    conditions_detected: Array<{
      condition: string
      severity: string
      confidence: number
      location: string
      description: string
    }>
    analysis_confidence: number
  }
  similarity_search: {
    dataset_used: string
    similar_cases: Array<{
      condition: string
      similarity_score: number
      dataset_source: string
      demographic_match: string
      treatment_suggestions: string[]
    }>
  }
  recommendations: {
    immediate_care: string[]
    long_term_care: string[]
    professional_consultation: boolean
  }
  quality_assessment: {
    image_quality: string
    confidence_reliability: string
  }
}

interface AnalysisResultsProps {
  result: DemographicAnalysisResult | ConditionAnalysisResult | EnhancedAnalysisResult
  type: 'demographic' | 'condition' | 'enhanced'
  onClose: () => void
}

export function AnalysisResults({ result, type, onClose }: AnalysisResultsProps) {
  const getHealthScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600'
    if (score >= 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getHealthScoreLabel = (score: number) => {
    if (score >= 0.8) return 'Excellent'
    if (score >= 0.6) return 'Good'
    if (score >= 0.4) return 'Fair'
    return 'Poor'
  }

  const renderDemographicResults = (result: DemographicAnalysisResult) => (
    <div className="space-y-6">
      {/* Health Score */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border">
        <div className="flex items-center mb-4">
          <Users className="w-6 h-6 text-green-500 mr-2" />
          <h3 className="text-lg font-semibold">Demographic Health Score</h3>
        </div>
        
        <div className="text-center mb-4">
          <div className={`text-4xl font-bold ${getHealthScoreColor(result.health_score)}`}>
            {Math.round(result.health_score * 100)}%
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            {getHealthScoreLabel(result.health_score)}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 className="font-medium mb-2">Your Demographics</h4>
            <div className="space-y-1 text-sm">
              <div>Age: {result.demographic_info.age_category}</div>
              <div>Gender: {result.demographic_info.gender}</div>
              <div>Ethnicity: {result.demographic_info.ethnicity}</div>
            </div>
          </div>
          
          <div>
            <h4 className="font-medium mb-2">Baseline Comparison</h4>
            <div className="space-y-1 text-sm">
              <div>Baseline Score: {Math.round(result.demographic_baseline.baseline_health_score * 100)}%</div>
              <div>Similarity: {Math.round(result.comparison_metrics.similarity_to_baseline * 100)}%</div>
              <div>Percentile: {Math.round(result.comparison_metrics.percentile_rank)}%</div>
            </div>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border">
        <h3 className="text-lg font-semibold mb-4">Recommendations</h3>
        
        {result.recommendations.demographic_specific.length > 0 && (
          <div className="mb-4">
            <h4 className="font-medium mb-2 text-green-600">Demographic-Specific Care</h4>
            <ul className="space-y-1">
              {result.recommendations.demographic_specific.map((rec, index) => (
                <li key={index} className="flex items-start">
                  <CheckCircle className="w-4 h-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span className="text-sm">{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {result.recommendations.general_health.length > 0 && (
          <div>
            <h4 className="font-medium mb-2 text-blue-600">General Health Tips</h4>
            <ul className="space-y-1">
              {result.recommendations.general_health.map((rec, index) => (
                <li key={index} className="flex items-start">
                  <CheckCircle className="w-4 h-4 text-blue-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span className="text-sm">{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {result.recommendations.professional_consultation && (
          <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-yellow-600 mr-2" />
              <span className="text-sm font-medium">Consider consulting a dermatologist for professional evaluation.</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )

  const renderConditionResults = (result: ConditionAnalysisResult) => (
    <div className="space-y-6">
      {/* Best Match */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border">
        <div className="flex items-center mb-4">
          <Activity className="w-6 h-6 text-purple-500 mr-2" />
          <h3 className="text-lg font-semibold">Condition Analysis</h3>
        </div>
        
        <div className="text-center mb-4">
          <div className="text-2xl font-bold text-purple-600 capitalize">
            {result.best_match.replace('_', ' ')}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Similarity: {Math.round(result.best_similarity * 100)}%
          </div>
        </div>

        <div className="mb-4">
          <h4 className="font-medium mb-2">Assessment</h4>
          <p className="text-sm text-gray-700 dark:text-gray-300">{result.assessment}</p>
        </div>

        {/* All Conditions */}
        <div>
          <h4 className="font-medium mb-2">All Conditions Analyzed</h4>
          <div className="space-y-2">
            {Object.entries(result.condition_results).map(([condition, data]) => (
              <div key={condition} className="flex justify-between items-center p-2 bg-gray-50 dark:bg-gray-700 rounded">
                <span className="text-sm capitalize">{condition.replace('_', ' ')}</span>
                <div className="text-right">
                  <div className="text-sm font-medium">{Math.round(data.similarity * 100)}%</div>
                  <div className="text-xs text-gray-500">{data.sample_count} samples</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border">
        <h3 className="text-lg font-semibold mb-4">Recommendations</h3>
        <ul className="space-y-2">
          {result.recommendations.map((rec, index) => (
            <li key={index} className="flex items-start">
              <CheckCircle className="w-4 h-4 text-purple-500 mr-2 mt-0.5 flex-shrink-0" />
              <span className="text-sm">{rec}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )

  const renderEnhancedResults = (result: EnhancedAnalysisResult) => (
    <div className="space-y-6">
      {/* Health Score */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border">
        <div className="flex items-center mb-4">
          <Brain className="w-6 h-6 text-blue-500 mr-2" />
          <h3 className="text-lg font-semibold">Enhanced Analysis Results</h3>
        </div>
        
        <div className="text-center mb-4">
          <div className={`text-4xl font-bold ${getHealthScoreColor(result.skin_analysis.overall_health_score)}`}>
            {Math.round(result.skin_analysis.overall_health_score * 100)}%
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            {getHealthScoreLabel(result.skin_analysis.overall_health_score)}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 className="font-medium mb-2">Skin Characteristics</h4>
            <div className="space-y-1 text-sm">
              <div>Texture: {result.skin_analysis.texture}</div>
              <div>Tone: {result.skin_analysis.tone}</div>
              <div>Confidence: {Math.round(result.skin_analysis.analysis_confidence * 100)}%</div>
            </div>
          </div>
          
          <div>
            <h4 className="font-medium mb-2">Face Detection</h4>
            <div className="space-y-1 text-sm">
              <div>Detected: {result.face_detection.detected ? 'Yes' : 'No'}</div>
              <div>Confidence: {Math.round(result.face_detection.confidence * 100)}%</div>
              <div>Quality: {result.face_detection.quality_metrics.overall_quality}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Conditions Detected */}
      {result.skin_analysis.conditions_detected.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border">
          <h3 className="text-lg font-semibold mb-4">Conditions Detected</h3>
          <div className="space-y-3">
            {result.skin_analysis.conditions_detected.map((condition, index) => (
              <div key={index} className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="font-medium text-red-700 dark:text-red-300">
                      {condition.condition}
                    </div>
                    <div className="text-sm text-red-600 dark:text-red-400">
                      Severity: {condition.severity} • Location: {condition.location}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {condition.description}
                    </div>
                  </div>
                  <div className="text-sm text-gray-500">
                    {Math.round(condition.confidence * 100)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border">
        <h3 className="text-lg font-semibold mb-4">Recommendations</h3>
        
        {result.recommendations.immediate_care.length > 0 && (
          <div className="mb-4">
            <h4 className="font-medium mb-2 text-orange-600">Immediate Care</h4>
            <ul className="space-y-1">
              {result.recommendations.immediate_care.map((rec, index) => (
                <li key={index} className="flex items-start">
                  <CheckCircle className="w-4 h-4 text-orange-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span className="text-sm">{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {result.recommendations.long_term_care.length > 0 && (
          <div>
            <h4 className="font-medium mb-2 text-blue-600">Long-term Care</h4>
            <ul className="space-y-1">
              {result.recommendations.long_term_care.map((rec, index) => (
                <li key={index} className="flex items-start">
                  <CheckCircle className="w-4 h-4 text-blue-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span className="text-sm">{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {result.recommendations.professional_consultation && (
          <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-yellow-600 mr-2" />
              <span className="text-sm font-medium">Consider consulting a dermatologist for professional evaluation.</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-gray-100 dark:bg-gray-900 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold">Analysis Results</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {type === 'demographic' && renderDemographicResults(result as DemographicAnalysisResult)}
          {type === 'condition' && renderConditionResults(result as ConditionAnalysisResult)}
          {type === 'enhanced' && renderEnhancedResults(result as EnhancedAnalysisResult)}
        </div>
      </div>
    </div>
  )
} 