export interface SensitivitySettings {
  acneDetection: number;        // 0-100
  severityThreshold: number;    // 0-100
  confidenceMinimum: number;    // 0-100
  ageAdjustment: number;        // 0-100
  skinTypeCalibration: number;  // 0-100
}

export interface ImageAnalysisResults {
  originalImage: string;
  rgbChannels: {
    red: string;
    green: string;
    blue: string;
    grayscale: string;
  };
  gaborFiltered: string;
  dermatoscopic: string;
  surfaceMap: string;
  landmarks: MediaPipeLandmark[];
  confidence: ConfidenceMetrics;
  processingTime: number;
  technologiesUsed: string[];
  qualityMetrics: QualityAssessment;
  
  // Real API integration fields
  apiResult?: any; // Raw API response
  isRealAnalysis: boolean; // True if real analysis, false if fallback/mock
  analysisType: 'advanced_skin_analysis' | 'fallback_data' | 'error_state';
  fallbackReason?: string; // Why fallback was used
  error?: string; // Error message if analysis failed
}

export interface MediaPipeLandmark {
  x: number;
  y: number;
  z: number;
  visibility: number;
  presence: number;
}

export interface ConfidenceMetrics {
  overall: number;
  acne: number;
  severity: number;
  age: number;
  ethnicity: number;
  gender: number;
}

export interface QualityAssessment {
  imageQuality: number;
  faceDetection: number;
  lightingScore: number;
  resolutionScore: number;
  blurScore: number;
}

export interface TechnologyStack {
  name: string;
  version: string;
  description: string;
  accuracy: number;
  processingTime: number;
}

export interface ProcessingStep {
  id: string;
  name: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  duration: number;
  description: string;
}

export interface DiagnosticResult {
  condition: string;
  confidence: number;
  severity: 'mild' | 'moderate' | 'severe';
  recommendations: string[];
  clinicalNotes: string;
}

export interface SensitivityPreset {
  name: string;
  description: string;
  settings: SensitivitySettings;
  useCase: string;
  recommendedFor: string[];
}
