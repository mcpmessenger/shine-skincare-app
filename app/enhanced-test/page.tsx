'use client'

import { useState } from 'react'
import { EnhancedAnalysis } from '@/components/enhanced-analysis'
import { AnalysisResults } from '@/components/analysis-results'

export default function EnhancedTestPage() {
  const [analysisResult, setAnalysisResult] = useState<any>(null)
  const [analysisType, setAnalysisType] = useState<'demographic' | 'condition' | 'enhanced'>('enhanced')
  const [showResults, setShowResults] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleAnalysisComplete = (result: any, type: string) => {
    setAnalysisResult(result)
    setAnalysisType(type as 'demographic' | 'condition' | 'enhanced')
    setShowResults(true)
    setError(null)
  }

  const handleError = (errorMessage: string) => {
    setError(errorMessage)
    setShowResults(false)
  }

  const handleCloseResults = () => {
    setShowResults(false)
    setAnalysisResult(null)
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Enhanced Skin Analysis
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              Test the new UTKFace demographic analysis and Facial Skin Diseases condition analysis
            </p>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <div className="flex items-center">
                <div className="text-red-600 dark:text-red-400 font-medium">
                  Error: {error}
                </div>
              </div>
            </div>
          )}

          {/* Enhanced Analysis Component */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <EnhancedAnalysis
              onAnalysisComplete={handleAnalysisComplete}
              onError={handleError}
            />
          </div>

          {/* Results Modal */}
          {showResults && analysisResult && (
            <AnalysisResults
              result={analysisResult}
              type={analysisType}
              onClose={handleCloseResults}
            />
          )}
        </div>
      </div>
    </div>
  )
} 