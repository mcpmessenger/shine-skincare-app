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
  status: 'idle' | 'training' | 'completed' | 'error'
  progress: number
  currentEpoch: number
  totalEpochs: number
  accuracy: number
  loss: number
  eta: string
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
    status: 'idle',
    progress: 0,
    currentEpoch: 0,
    totalEpochs: 100,
    accuracy: 0,
    loss: 0,
    eta: '--'
  })

  const [datasetMetrics, setDatasetMetrics] = useState<DatasetMetrics>({
    totalImages: 1045,
    conditions: 8,
    ethnicities: 6,
    ageRanges: 5,
    qualityScore: 97.2,
    lastUpdated: '2025-08-12'
  })

  const [modelStats, setModelStats] = useState<ModelStats[]>([
    {
      name: 'Hare Run V6',
      version: '6.0.0',
      accuracy: 97.13,
      trainingDate: '2025-08-12',
      datasetSize: 1045,
      performance: {
        precision: 96.8,
        recall: 97.4,
        f1Score: 97.1
      }
    }
  ])

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      if (trainingStatus.status === 'training') {
        setTrainingStatus(prev => ({
          ...prev,
          progress: Math.min(prev.progress + Math.random() * 2, 100),
          currentEpoch: Math.floor(prev.progress / 100 * prev.totalEpochs),
          accuracy: prev.accuracy + Math.random() * 0.5,
          loss: Math.max(prev.loss - Math.random() * 0.1, 0.01)
        }))
      }
    }, 1000)

    return () => clearInterval(interval)
  }, [trainingStatus.status])

  const startTraining = () => {
    setTrainingStatus(prev => ({ ...prev, status: 'training', progress: 0 }))
  }

  const stopTraining = () => {
    setTrainingStatus(prev => ({ ...prev, status: 'idle' }))
  }

  return (
    <div className="min-h-screen bg-primary text-primary">
      <Header title="Training Dashboard" showProductsTab={false} />
      
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <Brain className="w-12 h-12 text-accent mr-4" />
            <h1 className="text-4xl font-thin tracking-tight">
              AI Training Transparency
            </h1>
          </div>
          <p className="text-lg text-secondary max-w-2xl mx-auto">
            Real-time monitoring of our AI training processes, dataset quality, and model performance. 
            See exactly how we build trustworthy AI for your skin health.
          </p>
        </div>

        {/* Live Training Monitor */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {/* Training Status Card */}
          <div className="bg-secondary rounded-xl p-6 border border-border">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-light flex items-center">
                <TrendingUp className="w-6 h-6 mr-3 text-accent" />
                Live Training Monitor
              </h2>
              <div className="flex gap-2">
                {trainingStatus.status === 'training' ? (
                  <button
                    onClick={stopTraining}
                    className="btn btn-primary flex items-center gap-2"
                  >
                    <AlertCircle className="w-4 h-4" />
                    Stop Training
                  </button>
                ) : (
                  <button
                    onClick={startTraining}
                    className="btn btn-primary flex items-center gap-2"
                  >
                    <CheckCircle className="w-4 h-4" />
                    Start Training
                  </button>
                )}
              </div>
            </div>

            {/* Training Progress */}
            <div className="space-y-4">
              <div className="flex justify-between text-sm">
                <span>Progress</span>
                <span>{trainingStatus.progress.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-hover rounded-full h-2">
                <div 
                  className="bg-accent h-2 rounded-full transition-all duration-300"
                  style={{ width: `${trainingStatus.progress}%` }}
                />
              </div>

              {/* Training Metrics */}
              <div className="grid grid-cols-2 gap-4 pt-4">
                <div className="text-center p-3 bg-hover rounded-lg">
                  <div className="text-2xl font-light text-accent">
                    {trainingStatus.currentEpoch}
                  </div>
                  <div className="text-xs text-tertiary">Current Epoch</div>
                </div>
                <div className="text-center p-3 bg-hover rounded-lg">
                  <div className="text-2xl font-light text-accent">
                    {trainingStatus.accuracy.toFixed(2)}%
                  </div>
                  <div className="text-xs text-tertiary">Accuracy</div>
                </div>
                <div className="text-center p-3 bg-hover rounded-lg">
                  <div className="text-2xl font-light text-accent">
                    {trainingStatus.loss.toFixed(3)}
                  </div>
                  <div className="text-xs text-tertiary">Loss</div>
                </div>
                <div className="text-center p-3 bg-hover rounded-lg">
                  <div className="text-2xl font-light text-accent">
                    {trainingStatus.eta}
                  </div>
                  <div className="text-xs text-tertiary">ETA</div>
                </div>
              </div>
            </div>
          </div>

          {/* Dataset Quality Card */}
          <div className="bg-secondary rounded-xl p-6 border border-border">
            <h2 className="text-2xl font-light flex items-center mb-6">
              <Database className="w-6 h-6 mr-3 text-accent" />
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
                  <span className="text-lg font-medium text-accent">{datasetMetrics.qualityScore}%</span>
                </div>
                <div className="w-full bg-hover rounded-full h-2">
                  <div 
                    className="bg-accent h-2 rounded-full"
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
            <Zap className="w-6 h-6 mr-3 text-accent" />
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
                    <div className="text-2xl font-light text-accent">{model.accuracy}%</div>
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
            <Eye className="w-12 h-12 text-accent mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">Live Monitoring</h3>
            <p className="text-sm text-secondary">
              Watch real-time training progress and metrics as we improve our AI models
            </p>
          </div>
          
          <div className="bg-secondary rounded-xl p-6 border border-border text-center">
            <Zap className="w-12 h-12 text-accent mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">Performance Tracking</h3>
            <p className="text-sm text-secondary">
              Track model improvements and accuracy gains over time
            </p>
          </div>
          
          <div className="bg-secondary rounded-xl p-6 border border-border text-center">
            <Eye className="w-12 h-12 text-accent mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">Quality Assurance</h3>
            <p className="text-sm text-secondary">
              See our dataset diversity, quality scores, and validation processes
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center">
          <p className="text-xs text-secondary font-light mb-2">
            © 2024 All Rights Reserved. <span className="text-accent font-medium">EXPERIMENTAL</span>
          </p>
          <p className="text-xs text-secondary font-light mb-2">
            This application is for informational purposes only and does not constitute medical advice. 
            Always consult with a qualified healthcare professional for medical concerns.
          </p>
          <p className="text-xs text-secondary font-light">
            <Link href="/" className="text-accent hover:underline transition-colors">
              ← Back to Main App
            </Link>
          </p>
        </div>
      </main>
    </div>
  )
}
