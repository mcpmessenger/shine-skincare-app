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

    // Mock analysis result
    const analysisResult = {
      analysis_id: `mock_analysis_${Date.now()}`,
      status: "completed",
      results: {
        skin_type: "combination",
        concerns: [
          "Minor texture irregularities detected",
          "Slight uneven skin tone",
          "Some areas of dryness"
        ],
        recommendations: [
          "Use a gentle cleanser twice daily",
          "Apply moisturizer with hyaluronic acid",
          "Consider a vitamin C serum for brightening",
          "Use SPF 30+ daily"
        ],
        confidence: 0.85,
        image_quality: "good",
        demographics: {
          ethnicity: ethnicity || "not_specified",
          age: age || "not_specified"
        }
      },
      timestamp: new Date().toISOString(),
      processing_time_ms: 2000,
      ai_level: "mock",
      backend_available: false
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