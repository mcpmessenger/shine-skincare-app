import { NextRequest, NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { trainingType = 'v7_unified', datasetPath = './v7_cleaned_features' } = body

    // Validate training type
    if (!['v7_unified', 'v7_condition', 'v7_age'].includes(trainingType)) {
      return NextResponse.json(
        { error: 'Invalid training type. Must be v7_unified, v7_condition, or v7_age' },
        { status: 400 }
      )
    }

    console.log(`🚀 Starting V7 ${trainingType} training...`)

    // Execute the training script
    try {
      const { stdout, stderr } = await execAsync(
        `cd backend && python start_v7_training.py --type ${trainingType} --dataset ${datasetPath}`,
        { timeout: 30000 } // 30 second timeout for startup
      )

      console.log('Training script output:', stdout)
      if (stderr) console.log('Training script stderr:', stderr)

      // Parse the output to extract training ID and status
      const trainingIdMatch = stdout.match(/Training ID: ([^\n]+)/)
      const outputDirMatch = stdout.match(/Output Directory: ([^\n]+)/)
      const statusFileMatch = stdout.match(/Status File: ([^\n]+)/)

      const trainingJob = {
        id: trainingIdMatch ? trainingIdMatch[1] : `training_${Date.now()}`,
        type: trainingType,
        dataset: datasetPath,
        status: 'running',
        startTime: new Date().toISOString(),
        estimatedDuration: '2-4 hours',
        progress: 0,
        outputDirectory: outputDirMatch ? outputDirMatch[1] : 'Unknown',
        statusFile: statusFileMatch ? statusFileMatch[1] : 'Unknown'
      }

      return NextResponse.json({
        success: true,
        message: `V7 ${trainingType} training started successfully`,
        job: trainingJob,
        nextSteps: [
          'Training job started in background',
          'Monitor progress via training dashboard',
          `Check status file: ${trainingJob.statusFile}`,
          `View output directory: ${trainingJob.outputDirectory}`,
          'Training will run for 2-4 hours depending on dataset size'
        ]
      })

    } catch (execError: any) {
      console.error('Training execution error:', execError)
      
      // Check if it's a timeout (training started but we couldn't wait for full output)
      if (execError.code === 'ETIMEDOUT') {
        return NextResponse.json({
          success: true,
          message: `V7 ${trainingType} training started (startup timeout)`,
          job: {
            id: `training_${Date.now()}`,
            type: trainingType,
            dataset: datasetPath,
            status: 'starting',
            startTime: new Date().toISOString(),
            estimatedDuration: '2-4 hours',
            progress: 0
          },
          nextSteps: [
            'Training job started in background',
            'Check backend directory for training output',
            'Monitor progress via training dashboard',
            'Training will run for 2-4 hours'
          ]
        })
      }

      return NextResponse.json(
        { error: 'Failed to start training', details: execError.message },
        { status: 500 }
      )
    }

  } catch (error) {
    console.error('Training start error:', error)
    return NextResponse.json(
      { error: 'Failed to start training', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    )
  }
}

export async function GET() {
  return NextResponse.json({
    message: 'V7 Training API',
    availableTypes: ['v7_unified', 'v7_condition', 'v7_age'],
    defaultDataset: './v7_cleaned_features',
    status: 'ready',
    instructions: [
      'Use POST /api/training/start to start training',
      'Training types: v7_unified, v7_condition, v7_age',
      'Training runs in background for 2-4 hours',
      'Monitor progress via dashboard or status files'
    ]
  })
}
