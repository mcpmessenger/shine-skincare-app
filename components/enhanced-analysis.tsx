'use client'

import { useState } from 'react'
import { Brain, Users, Activity, Shield, Camera, Upload, Sparkles, CheckCircle, X } from 'lucide-react'

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

interface EnhancedAnalysisProps {
  onAnalysisComplete: (result: any, type: string) => void
  onError: (error: string) => void
}

export function EnhancedAnalysis({ onAnalysisComplete, onError }: EnhancedAnalysisProps) {
  const [analysisType, setAnalysisType] = useState<'enhanced' | 'demographic' | 'condition'>('enhanced')
  const [demographicInfo, setDemographicInfo] = useState({
    age: '',
    gender: '',
    ethnicity: ''
  })
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [imageData, setImageData] = useState<string | null>(null)

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      const base64 = await fileToBase64(file)
      setImageData(base64)
    }
  }

  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.readAsDataURL(file)
      reader.onload = () => resolve(reader.result as string)
      reader.onerror = error => reject(error)
    })
  }

  const handleAnalysis = async () => {
    if (!imageData) {
      onError('No image data provided')
      return
    }

    setIsAnalyzing(true)

    try {
      let response
      let result

      switch (analysisType) {
        case 'demographic':
          response = await fetch('/api/v3/skin/analyze-demographic', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              image_data: imageData,
              age: demographicInfo.age,
              gender: demographicInfo.gender,
              ethnicity: demographicInfo.ethnicity
            })
          })
          
          if (response.ok) {
            result = await response.json()
            onAnalysisComplete(result, 'demographic')
          } else {
            throw new Error(`Demographic analysis failed: ${response.statusText}`)
          }
          break

        case 'condition':
          response = await fetch('/api/v3/skin/analyze-conditions', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              image_data: imageData
            })
          })
          
          if (response.ok) {
            result = await response.json()
            onAnalysisComplete(result, 'condition')
          } else {
            throw new Error(`Condition analysis failed: ${response.statusText}`)
          }
          break

        case 'enhanced':
        default:
          response = await fetch('/api/v3/skin/analyze-enhanced-embeddings', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              image_data: imageData,
              analysis_type: 'comprehensive'
            })
          })
          
          if (response.ok) {
            result = await response.json()
            onAnalysisComplete(result, 'enhanced')
          } else {
            throw new Error(`Enhanced analysis failed: ${response.statusText}`)
          }
          break
      }

    } catch (error) {
      console.error('Analysis error:', error)
      onError(error instanceof Error ? error.message : 'Analysis failed')
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="enhanced-analysis-container">
      <div className="analysis-type-selector">
        <h3 className="text-lg font-semibold mb-4">Choose Analysis Type</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <button
            onClick={() => setAnalysisType('enhanced')}
            className={`p-4 rounded-lg border-2 transition-all ${
              analysisType === 'enhanced'
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-blue-300'
            }`}
          >
            <Brain className="w-8 h-8 mb-2 text-blue-500" />
            <h4 className="font-medium">Enhanced Analysis</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Advanced skin analysis with multiple datasets
            </p>
          </button>

          <button
            onClick={() => setAnalysisType('demographic')}
            className={`p-4 rounded-lg border-2 transition-all ${
              analysisType === 'demographic'
                ? 'border-green-500 bg-green-50 dark:bg-green-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-green-300'
            }`}
          >
            <Users className="w-8 h-8 mb-2 text-green-500" />
            <h4 className="font-medium">Demographic Analysis</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Age, gender, and ethnicity-specific analysis
            </p>
          </button>

          <button
            onClick={() => setAnalysisType('condition')}
            className={`p-4 rounded-lg border-2 transition-all ${
              analysisType === 'condition'
                ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-purple-300'
            }`}
          >
            <Activity className="w-8 h-8 mb-2 text-purple-500" />
            <h4 className="font-medium">Condition Analysis</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Specific skin condition identification
            </p>
          </button>
        </div>
      </div>

      {/* Demographic Information Form */}
      {analysisType === 'demographic' && (
        <div className="demographic-form mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <h4 className="font-medium mb-3">Demographic Information</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Age</label>
              <input
                type="text"
                value={demographicInfo.age}
                onChange={(e) => setDemographicInfo(prev => ({ ...prev, age: e.target.value }))}
                placeholder="e.g., 25"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Gender</label>
              <select
                value={demographicInfo.gender}
                onChange={(e) => setDemographicInfo(prev => ({ ...prev, gender: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="">Select gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Ethnicity</label>
              <select
                value={demographicInfo.ethnicity}
                onChange={(e) => setDemographicInfo(prev => ({ ...prev, ethnicity: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="">Select ethnicity</option>
                <option value="caucasian">Caucasian</option>
                <option value="african_american">African American</option>
                <option value="asian">Asian</option>
                <option value="hispanic">Hispanic/Latino</option>
                <option value="middle_eastern">Middle Eastern</option>
                <option value="native_american">Native American</option>
                <option value="mixed">Mixed/Other</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Image Upload */}
      <div className="image-upload-section mb-6">
        <h4 className="font-medium mb-3">Upload Image</h4>
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
          <input
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
            id="image-upload"
          />
          <label htmlFor="image-upload" className="cursor-pointer">
            <Upload className="w-12 h-12 mx-auto mb-2 text-gray-400" />
            <p className="text-gray-600 dark:text-gray-400">
              Click to upload an image or drag and drop
            </p>
            <p className="text-sm text-gray-500 mt-1">
              Supports JPG, PNG, GIF up to 10MB
            </p>
          </label>
        </div>
        
        {selectedFile && (
          <div className="mt-4 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <div className="flex items-center">
              <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
              <span className="text-sm">{selectedFile.name}</span>
              <button
                onClick={() => {
                  setSelectedFile(null)
                  setImageData(null)
                }}
                className="ml-auto text-gray-400 hover:text-gray-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Analysis Button */}
      <button
        onClick={handleAnalysis}
        disabled={!imageData || isAnalyzing}
        className={`w-full py-3 px-6 rounded-lg font-medium transition-all ${
          isAnalyzing
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700 text-white'
        }`}
      >
        {isAnalyzing ? (
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
            Analyzing...
          </div>
        ) : (
          <div className="flex items-center justify-center">
            <Sparkles className="w-5 h-5 mr-2" />
            Start Analysis
          </div>
        )}
      </button>
    </div>
  )
} 