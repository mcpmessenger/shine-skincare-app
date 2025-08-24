import { NextResponse } from 'next/server'
import { readFileSync, existsSync } from 'fs'
import { join } from 'path'

export async function GET() {
  try {
    // Path to the V7 training results
    const trainingDir = join(process.cwd(), 'backend', 'v7_unified_model')
    const historyFile = join(trainingDir, 'training_history.json')
    const evalFile = join(trainingDir, 'evaluation_results.json')
    
    let trainingHistory = null
    let evaluationResults = null
    
    // Try to load training history
    if (existsSync(historyFile)) {
      try {
        const historyData = readFileSync(historyFile, 'utf-8')
        trainingHistory = JSON.parse(historyData)
      } catch (e) {
        console.log('Could not parse training history:', e)
      }
    }
    
    // Try to load evaluation results
    if (existsSync(evalFile)) {
      try {
        const evalData = readFileSync(evalFile, 'utf-8')
        evaluationResults = JSON.parse(evalData)
      } catch (e) {
        console.log('Could not parse evaluation results:', e)
      }
    }
    
    // Return the training results
    return NextResponse.json({
      success: true,
      message: 'V7 Training Results Loaded',
      trainingHistory,
      evaluationResults,
      modelLocation: 'backend/v7_unified_model/',
      status: 'completed',
      lastUpdated: new Date().toISOString()
    })
    
  } catch (error) {
    console.error('Error loading training results:', error)
    return NextResponse.json({
      success: false,
      error: 'Failed to load training results',
      message: 'V7 training completed but results could not be loaded'
    }, { status: 500 })
  }
}
