'use client'

import { useState, useEffect } from 'react'
import { Brain, Eye, Shield, CheckCircle, TrendingUp } from 'lucide-react'

interface ConfidenceLoadingProps {
  isVisible: boolean
  onComplete?: () => void
}

interface LoadingStep {
  id: string
  title: string
  description: string
  icon: React.ReactNode
  duration: number
  confidence?: number
}

export function ConfidenceLoading({ isVisible, onComplete }: ConfidenceLoadingProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [stepProgress, setStepProgress] = useState(0)
  const [overallProgress, setOverallProgress] = useState(0)

  const loadingSteps: LoadingStep[] = [
    {
      id: 'preprocessing',
      title: 'Image Preprocessing',
      description: 'Optimizing image quality and preparing for analysis',
      icon: <Eye className="w-6 h-6" />,
      duration: 2000,
      confidence: 95
    },
    {
      id: 'face_detection',
      title: 'Face Detection',
      description: 'Identifying facial features and skin regions',
      icon: <Brain className="w-6 h-6" />,
      duration: 3000,
      confidence: 92
    },
    {
      id: 'skin_analysis',
      title: 'Skin Analysis',
      description: 'Analyzing skin texture, tone, and conditions',
      icon: <TrendingUp className="w-6 h-6" />,
      duration: 4000,
      confidence: 88
    },
    {
      id: 'recommendation_engine',
      title: 'Generating Recommendations',
      description: 'Matching your skin profile with optimal products',
      icon: <Shield className="w-6 h-6" />,
      duration: 2500,
      confidence: 94
    }
  ]

  useEffect(() => {
    if (!isVisible) {
      setCurrentStep(0)
      setStepProgress(0)
      setOverallProgress(0)
      return
    }

    const totalSteps = loadingSteps.length
    let stepTimer: NodeJS.Timeout
    let progressTimer: NodeJS.Timeout

    const runStep = (stepIndex: number) => {
      if (stepIndex >= totalSteps) {
        setOverallProgress(100)
        setTimeout(() => {
          onComplete?.()
        }, 500)
        return
      }

      setCurrentStep(stepIndex)
      setStepProgress(0)

      const step = loadingSteps[stepIndex]
      const progressInterval = 50 // Update every 50ms
      const progressIncrement = 100 / (step.duration / progressInterval)

      progressTimer = setInterval(() => {
        setStepProgress(prev => {
          const newProgress = Math.min(prev + progressIncrement, 100)
          
          // Update overall progress
          const baseProgress = (stepIndex / totalSteps) * 100
          const stepContribution = (newProgress / 100) * (100 / totalSteps)
          setOverallProgress(baseProgress + stepContribution)

          if (newProgress >= 100) {
            clearInterval(progressTimer)
            setTimeout(() => runStep(stepIndex + 1), 300)
          }

          return newProgress
        })
      }, progressInterval)
    }

    runStep(0)

    return () => {
      clearTimeout(stepTimer)
      clearInterval(progressTimer)
    }
  }, [isVisible, onComplete])

  if (!isVisible) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-gray-900 rounded-lg max-w-md w-full p-6">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mx-auto mb-4">
            <Brain className="w-8 h-8 text-blue-600" />
          </div>
          <h2 className="text-xl font-bold mb-2">AI Analysis in Progress</h2>
          <p className="text-gray-600 dark:text-gray-400 text-sm">
            Our advanced AI is analyzing your skin with complete transparency
          </p>
        </div>

        {/* Overall Progress */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium">Overall Progress</span>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {Math.round(overallProgress)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${overallProgress}%` }}
            />
          </div>
        </div>

        {/* Current Step */}
        <div className="space-y-4">
          {loadingSteps.map((step, index) => {
            const isActive = index === currentStep
            const isCompleted = index < currentStep
            const isUpcoming = index > currentStep

            return (
              <div
                key={step.id}
                className={`flex items-start space-x-3 p-3 rounded-lg transition-all duration-300 ${
                  isActive
                    ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800'
                    : isCompleted
                    ? 'bg-green-50 dark:bg-green-900/20'
                    : 'bg-gray-50 dark:bg-gray-800'
                }`}
              >
                <div
                  className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                    isCompleted
                      ? 'bg-green-500 text-white'
                      : isActive
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-300 dark:bg-gray-600 text-gray-600 dark:text-gray-400'
                  }`}
                >
                  {isCompleted ? (
                    <CheckCircle className="w-4 h-4" />
                  ) : (
                    step.icon
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h3
                      className={`text-sm font-medium ${
                        isActive || isCompleted
                          ? 'text-gray-900 dark:text-gray-100'
                          : 'text-gray-500 dark:text-gray-400'
                      }`}
                    >
                      {step.title}
                    </h3>
                    {step.confidence && (isActive || isCompleted) && (
                      <span className="text-xs text-green-600 dark:text-green-400 font-medium">
                        {step.confidence}% confidence
                      </span>
                    )}
                  </div>
                  <p
                    className={`text-xs mt-1 ${
                      isActive || isCompleted
                        ? 'text-gray-600 dark:text-gray-300'
                        : 'text-gray-400 dark:text-gray-500'
                    }`}
                  >
                    {step.description}
                  </p>

                  {isActive && (
                    <div className="mt-2">
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1">
                        <div
                          className="bg-blue-500 h-1 rounded-full transition-all duration-100 ease-out"
                          style={{ width: `${stepProgress}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        {/* Transparency Note */}
        <div className="mt-6 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <div className="flex items-center space-x-2">
            <Shield className="w-4 h-4 text-gray-600 dark:text-gray-400" />
            <span className="text-xs text-gray-600 dark:text-gray-400">
              Complete transparency: All analysis steps are shown in real-time
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

