// Direct Backend Communication Utility
// This bypasses the Next.js API routes to communicate directly with the Flask backend

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://api.shineskincollective.com';

export interface BackendResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  status: number;
}

export class DirectBackendClient {
  private baseUrl: string;

  constructor(baseUrl: string = BACKEND_URL) {
    this.baseUrl = baseUrl;
  }

  async healthCheck(): Promise<BackendResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v3/system/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      
      return {
        success: response.ok,
        data: response.ok ? data : undefined,
        error: response.ok ? undefined : data.error || 'Health check failed',
        status: response.status,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      };
    }
  }

  async enhancedAnalysis(payload: {
    image_data: string;
    analysis_type?: string;
    user_parameters?: any;
    face_detection_result?: any;
  }): Promise<BackendResponse> {
    try {
      console.log('🔍 Direct Backend: Enhanced Analysis Request');
      console.log('Backend URL:', `${this.baseUrl}/api/v3/skin/analyze-enhanced-embeddings`);
      console.log('Payload keys:', Object.keys(payload));
      console.log('Payload size:', JSON.stringify(payload).length);

      const response = await fetch(`${this.baseUrl}/api/v3/skin/analyze-enhanced-embeddings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      console.log('Direct Backend Response Status:', response.status);
      console.log('Direct Backend Response Headers:', Object.fromEntries(response.headers.entries()));

      const data = await response.json();
      
      return {
        success: response.ok,
        data: response.ok ? data : undefined,
        error: response.ok ? undefined : data.error || 'Enhanced analysis failed',
        status: response.status,
      };
    } catch (error) {
      console.error('❌ Direct Backend Enhanced Analysis Error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      };
    }
  }

  async basicAnalysis(payload: {
    image_data: string;
    analysis_type?: string;
    user_parameters?: any;
    face_detection_result?: any;
  }): Promise<BackendResponse> {
    try {
      console.log('🔍 Direct Backend: Basic Analysis Request');
      console.log('Backend URL:', `${this.baseUrl}/api/v3/skin/analyze-basic`);
      console.log('Payload keys:', Object.keys(payload));
      console.log('Payload size:', JSON.stringify(payload).length);

      const response = await fetch(`${this.baseUrl}/api/v3/skin/analyze-basic`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      console.log('Direct Backend Response Status:', response.status);
      console.log('Direct Backend Response Headers:', Object.fromEntries(response.headers.entries()));

      const data = await response.json();
      
      return {
        success: response.ok,
        data: response.ok ? data : undefined,
        error: response.ok ? undefined : data.error || 'Basic analysis failed',
        status: response.status,
      };
    } catch (error) {
      console.error('❌ Direct Backend Basic Analysis Error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      };
    }
  }

  async faceDetection(payload: {
    image_data: string;
  }): Promise<BackendResponse> {
    try {
      console.log('🔍 Direct Backend: Face Detection Request');
      console.log('Backend URL:', `${this.baseUrl}/api/v3/face/detect`);

      const response = await fetch(`${this.baseUrl}/api/v3/face/detect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      console.log('Direct Backend Face Detection Response Status:', response.status);

      const data = await response.json();
      
      return {
        success: response.ok,
        data: response.ok ? data : undefined,
        error: response.ok ? undefined : data.error || 'Face detection failed',
        status: response.status,
      };
    } catch (error) {
      console.error('❌ Direct Backend Face Detection Error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      };
    }
  }
}

// Create a singleton instance
export const directBackendClient = new DirectBackendClient();

// Utility function to check if direct backend is available
export async function isDirectBackendAvailable(): Promise<boolean> {
  const healthCheck = await directBackendClient.healthCheck();
  return healthCheck.success;
} 