import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const image = formData.get('image') as File;
    const ethnicity = formData.get('ethnicity') as string;
    const age = formData.get('age') as string;

    if (!image) {
      return NextResponse.json(
        { error: 'No image provided' },
        { status: 400 }
      );
    }

    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Mock analysis result matching backend structure
    const analysisResult = {
      skin_conditions: [
        {
          id: 'condition_001',
          type: 'acne',
          confidence: 0.85,
          location: { x: 150, y: 200, width: 30, height: 25 },
          characteristics: {
            severity: 'moderate',
            type: 'inflammatory'
          },
          scin_match_score: 0.80,
          recommendation: 'Benzoyl peroxide treatment'
        }
      ],
      scin_similar_cases: [
        {
          id: 'scin_case_001',
          similarity_score: 0.80,
          condition_type: 'acne',
          age_group: '20-30',
          ethnicity: ethnicity || 'not_specified',
          treatment_history: 'Benzoyl peroxide',
          outcome: 'Improvement'
        }
      ],
      total_conditions: 1,
      ai_processed: true,
      image_size: [400, 300, 3],
      ai_level: 'mock',
      scin_dataset: false,
      enhanced_features: {
        skin_condition_detection: true,
        scin_dataset_query: false,
        treatment_recommendations: true,
        similar_case_analysis: true
      }
    };

    return NextResponse.json({
      data: analysisResult,
      success: true,
      message: "Mock analysis completed successfully"
    });

  } catch (error) {
    console.error('Mock analysis error:', error);
    return NextResponse.json(
      { 
        error: 'Internal server error', 
        details: error instanceof Error ? error.message : 'Unknown error',
        success: false,
        message: "Mock analysis failed"
      },
      { status: 500 }
    );
  }
} 