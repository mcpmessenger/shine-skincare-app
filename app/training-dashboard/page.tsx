'use client'

import { useState, useEffect } from 'react'
import { Header } from '@/components/header'
import { 
  TrendingUp, 
  Database, 
  User, 
  CheckCircle,
  AlertCircle,
  Eye,
  Zap,
  Brain
} from 'lucide-react'
import Link from 'next/link'

interface TrainingStatus {
  status: 'completed' | 'idle'
  lastTrainingDate: string
  totalTrainingTime: string
  finalAccuracy: number
  finalLoss: number
  trainingRuns: number
}

interface DatasetMetrics {
  totalImages: number
  conditions: number
  ethnicities: number
  ageRanges: number
  qualityScore: number
  lastUpdated: string
}

interface ModelStats {
  name: string
  version: string
  accuracy: number
  trainingDate: string
  datasetSize: number
  performance: {
    precision: number
    recall: number
    f1Score: number
  }
}

export default function TrainingDashboard() {
  const [trainingStatus, setTrainingStatus] = useState<TrainingStatus>({
    status: 'completed',
    lastTrainingDate: '2025-08-14',
    totalTrainingTime: '4h 23m',
    finalAccuracy: 97.13,
    finalLoss: 0.023,
    trainingRuns: 12
  })

  const [datasetMetrics, setDatasetMetrics] = useState<DatasetMetrics>({
    totalImages: 2847,
    conditions: 12,
    ethnicities: 8,
    ageRanges: 6,
    qualityScore: 98.7,
    lastUpdated: '2025-08-14'
  })

  const [modelStats, setModelStats] = useState<ModelStats[]>([
    {
      name: 'Hare Run V6',
      version: '6.0.0',
      accuracy: 97.13,
      trainingDate: '2025-08-14',
      datasetSize: 2847,
      performance: {
        precision: 97.2,
        recall: 97.1,
        f1Score: 97.15
      }
    },
    {
      name: 'Enhanced V5',
      version: '5.2.1',
      accuracy: 96.8,
      trainingDate: '2025-08-10',
      datasetSize: 2847,
      performance: {
        precision: 96.9,
        recall: 96.7,
        f1Score: 96.8
      }
    }
  ])

  // No real-time updates needed - this is a transparency page

  // No training functions needed - this is a transparency page

  return (
    <div className="min-h-screen bg-primary text-primary">
      <Header title="Training Dashboard" showProductsTab={false} />
      
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <Brain className="w-12 h-12 text-primary mr-4" />
            <h1 className="text-4xl font-thin tracking-tight">
              AI Training Transparency
            </h1>
          </div>
          <p className="text-lg text-secondary max-w-2xl mx-auto">
            Complete transparency into our AI training processes, dataset quality, and model performance. 
            See exactly how we build trustworthy AI for your skin health.
          </p>
        </div>

        {/* Live Training Monitor */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {/* Training Status Card */}
          <div className="bg-secondary rounded-xl p-6 border border-border">
            <div className="mb-6">
              <h2 className="text-2xl font-light flex items-center">
                <TrendingUp className="w-6 h-6 mr-3 text-primary" />
                Training Status
              </h2>
            </div>

            {/* Training Status */}
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-hover rounded-lg">
                <span className="text-sm text-secondary">Status</span>
                <span className="text-lg font-medium text-green-500 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" />
                  {trainingStatus.status === 'completed' ? 'Completed' : 'Idle'}
                </span>
              </div>

              {/* Training Metrics */}
              <div className="grid grid-cols-2 gap-4 pt-4">
                <div className="text-center p-3 bg-hover rounded-lg">
                  <div className="text-2xl font-light text-primary">
                    {trainingStatus.finalAccuracy}%
                  </div>
                  <div className="text-xs text-tertiary">Final Accuracy</div>
                </div>
                <div className="text-center p-3 bg-hover rounded-lg">
                  <div className="text-2xl font-light text-primary">
                    {trainingStatus.finalLoss}
                  </div>
                  <div className="text-xs text-tertiary">Final Loss</div>
                </div>
                <div className="text-center p-3 bg-hover rounded-lg">
                  <div className="text-2xl font-light text-primary">
                    {trainingStatus.trainingRuns}
                  </div>
                  <div className="text-xs text-tertiary">Training Runs</div>
                </div>
                <div className="text-center p-3 bg-hover rounded-lg">
                  <div className="text-2xl font-light text-primary">
                    {trainingStatus.totalTrainingTime}
                  </div>
                  <div className="text-xs text-tertiary">Total Time</div>
                </div>
              </div>

              <div className="text-xs text-tertiary pt-2 text-center">
                Last training completed: {trainingStatus.lastTrainingDate}
              </div>
            </div>
          </div>

          {/* Dataset Quality Card */}
          <div className="bg-secondary rounded-xl p-6 border border-border">
            <h2 className="text-2xl font-light flex items-center mb-6">
              <Database className="w-6 h-6 mr-3 text-primary" />
              Dataset Quality
            </h2>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-secondary">Total Images</span>
                <span className="text-lg font-medium">{datasetMetrics.totalImages.toLocaleString()}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-secondary">Skin Conditions</span>
                <span className="text-lg font-medium">{datasetMetrics.conditions}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-secondary">Ethnicities</span>
                <span className="text-lg font-medium">{datasetMetrics.ethnicities}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-secondary">Age Ranges</span>
                <span className="text-lg font-medium">{datasetMetrics.ageRanges}</span>
              </div>
              
              <div className="pt-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-secondary">Quality Score</span>
                  <span className="text-lg font-medium text-primary">{datasetMetrics.qualityScore}%</span>
                </div>
                <div className="w-full bg-hover rounded-full h-2">
                  <div 
                    className="bg-primary h-2 rounded-full"
                    style={{ width: `${datasetMetrics.qualityScore}%` }}
                  />
                </div>
              </div>

              <div className="text-xs text-tertiary pt-2">
                Last updated: {datasetMetrics.lastUpdated}
              </div>
            </div>
          </div>
        </div>

        {/* Model Performance History */}
        <div className="bg-secondary rounded-xl p-6 border border-border mb-8">
                      <h2 className="text-2xl font-light flex items-center mb-6">
              <Zap className="w-6 h-6 mr-3 text-primary" />
              Model Performance History
            </h2>
          
          <div className="space-y-4">
            {modelStats.map((model, index) => (
              <div key={index} className="p-4 bg-hover rounded-lg border border-border">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h3 className="text-lg font-medium">{model.name}</h3>
                    <p className="text-sm text-secondary">Version {model.version}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-light text-primary">{model.accuracy}%</div>
                    <div className="text-xs text-tertiary">Accuracy</div>
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-sm font-medium">{model.performance.precision}%</div>
                    <div className="text-xs text-tertiary">Precision</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium">{model.performance.recall}%</div>
                    <div className="text-xs text-tertiary">Recall</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium">{model.performance.f1Score}%</div>
                    <div className="text-xs text-tertiary">F1 Score</div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between mt-3 pt-3 border-t border-border">
                  <div className="text-xs text-tertiary">
                    Trained: {model.trainingDate}
                  </div>
                  <div className="text-xs text-tertiary">
                    Dataset: {model.datasetSize.toLocaleString()} images
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Transparency Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-secondary rounded-xl p-6 border border-border text-center">
            <Eye className="w-12 h-12 text-primary mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">Complete Transparency</h3>
            <p className="text-sm text-secondary">
              View all training results, dataset metrics, and model performance data
            </p>
          </div>
          
          <div className="bg-secondary rounded-xl p-6 border border-border text-center">
            <Zap className="w-12 h-12 text-primary mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">Performance Tracking</h3>
            <p className="text-sm text-secondary">
              Track model improvements and accuracy gains over time
            </p>
          </div>
          
          <div className="bg-secondary rounded-xl p-6 border border-border text-center">
            <Eye className="w-12 h-12 text-primary mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">Quality Assurance</h3>
            <p className="text-sm text-secondary">
              See our dataset diversity, quality scores, and validation processes
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center">
          <p className="text-xs text-secondary font-light mb-2">
            © 2024 All Rights Reserved. <span className="text-primary font-medium">EXPERIMENTAL</span>
          </p>
          <p className="text-xs text-secondary font-light mb-2">
            This application is for informational purposes only and does not constitute medical advice. 
            Always consult with a qualified healthcare professional for medical concerns.
          </p>
          <p className="text-xs text-secondary font-light">
            <Link href="/" className="text-primary hover:underline transition-colors">
              ← Back to Main App
            </Link>
          </p>
        </div>
      </main>
    </div>
  )
}
