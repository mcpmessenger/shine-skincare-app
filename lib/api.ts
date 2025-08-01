'use client';

import { ImageCompressor } from './image-compression';

interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  version?: string;
  timestamp?: string;
  analysis_id?: string; // Add analysis_id at top level for backward compatibility
}

interface ApiError {
  message: string;
  status?: number;
}

export interface User {
  id: string;
  email: string;
  name: string;
  profile_picture_url?: string;
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: string;
  name: string;
  brand?: string;
  price?: number;
  rating?: number;
  image_urls?: string[];
  description?: string;
  currency?: string;
  availability_status?: string;
  review_count?: number;
  category?: string;
  subcategory?: string;
  ingredients?: string[];
}

// New interfaces for advanced ML features
export interface AdvancedMLAnalysis {
  ai_level: 'advanced_ml' | 'basic' | 'mock';
  feature_vector_dim?: number;
  enhanced_features?: {
    deep_feature_extraction?: boolean;
    texture_analysis?: boolean;
    color_analysis?: boolean;
    skin_condition_detection?: boolean;
    scin_dataset_query?: boolean;
    treatment_recommendations?: boolean;
    similar_case_analysis?: boolean;
  };
  treatment_recommendations?: Array<{
    condition: string;
    severity: string;
    primary_treatment: string;
    expected_outcome: string;
    confidence: number;
    source: 'scin_dataset' | 'general_knowledge';
  }>;
}

export interface SCINSearchResult {
  case_id: string;
  similarity_score: number;
  condition_type: string;
  age_group: string;
  treatment_history: string;
  outcome: string;
}

export interface AIStatus {
  core_ai: boolean;
  heavy_ai: boolean;
  full_ai: boolean;
  scin_dataset: boolean;
  google_vision: boolean;
  operation_left_brain: boolean;
  advanced_ml: boolean;
}

class ApiClient {
  private baseUrl: string;

  constructor() {
    // SSL Certificate Issue: Using HTTP until certificate is fixed
    this.baseUrl = 'http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com';
    
    // Debug: Log the actual URL being used
    console.log('🔧 API Client initialized with backend URL:', this.baseUrl);
    console.log('🔧 Environment variables:', {
      NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL,
      NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
      NODE_ENV: process.env.NODE_ENV
    });
    
    // Log a clear message about the URL being used
    console.log('🔒 SSL Certificate Issue: Using HTTP until certificate is fixed');
    console.log('🚀 BUILD TRIGGER - Backend URL updated for SSL certificate fix');
    console.log('🔧 BACKEND HTTP: Using working Elastic Beanstalk backend');
    console.log('🔄 CACHE BUSTING: Timestamp:', new Date().toISOString());
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Add auth token if available
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    if (token && token !== 'guest') {
      defaultHeaders['Authorization'] = `Bearer ${token}`;
    }

    // Merge with options headers
    const finalHeaders = {
      ...defaultHeaders,
      ...(options.headers as Record<string, string>),
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers: finalHeaders,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // NEW: Advanced ML Selfie Analysis
  async analyzeSelfieAdvanced(imageFile: File): Promise<ApiResponse<{
    selfie_analysis: {
      facial_features: any;
      skin_conditions: any[];
      scin_similar_cases: SCINSearchResult[];
      treatment_recommendations?: any[];
      total_conditions: number;
      ai_processed: boolean;
      image_size: number[];
      ai_level: string;
      google_vision_api: boolean;
      scin_dataset: boolean;
      advanced_ml: boolean;
      feature_vector_dim?: number;
      enhanced_features?: any;
    } & AdvancedMLAnalysis;
    message: string;
    version: string;
    timestamp: string;
    ml_available: boolean;
    dual_skin_analysis: boolean;
    google_vision_api: boolean;
    scin_dataset: boolean;
    advanced_ml: boolean;
    proven_stable: boolean;
  }>> {
    const formData = new FormData();
    formData.append('image', imageFile);

    console.log('🧠 Advanced ML Selfie Analysis - Starting...');
    console.log('📊 File size:', imageFile.size, 'bytes');
    console.log('📊 File type:', imageFile.type);

    return this.request('/api/v2/selfie/analyze', {
      method: 'POST',
      body: formData,
    });
  }

  // NEW: Advanced ML Skin Analysis
  async analyzeSkinAdvanced(imageFile: File): Promise<ApiResponse<{
    skin_analysis: {
      skin_conditions: any[];
      scin_similar_cases: SCINSearchResult[];
      treatment_recommendations?: any[];
      total_conditions: number;
      ai_processed: boolean;
      image_size: number[];
      ai_level: string;
      scin_dataset: boolean;
      advanced_ml: boolean;
      feature_vector_dim?: number;
      enhanced_features?: any;
    } & AdvancedMLAnalysis;
    message: string;
    version: string;
    timestamp: string;
    ml_available: boolean;
    dual_skin_analysis: boolean;
    google_vision_api: boolean;
    scin_dataset: boolean;
    advanced_ml: boolean;
    proven_stable: boolean;
  }>> {
    const formData = new FormData();
    formData.append('image', imageFile);

    console.log('🧠 Advanced ML Skin Analysis - Starting...');
    console.log('📊 File size:', imageFile.size, 'bytes');
    console.log('📊 File type:', imageFile.type);

    return this.request('/api/v2/skin/analyze', {
      method: 'POST',
      body: formData,
    });
  }

  // NEW: SCIN Dataset Search with Image
  async searchSCINWithImage(imageFile: File, k: number = 5): Promise<ApiResponse<{
    data: {
      similar_cases: SCINSearchResult[];
      query_features_dim?: number;
      search_method: string;
      ai_level: string;
    };
    message: string;
    operation: string;
    status: string;
    note?: string;
  }>> {
    const formData = new FormData();
    formData.append('image', imageFile);

    console.log('🔍 SCIN Dataset Search - Starting...');
    console.log('📊 File size:', imageFile.size, 'bytes');
    console.log('📊 Search k:', k);

    return this.request('/api/scin/search', {
      method: 'POST',
      body: formData,
    });
  }

  // NEW: AI Services Status
  async getAIStatus(): Promise<ApiResponse<{
    operation: string;
    status: AIStatus;
    message: string;
  }>> {
    console.log('🤖 Getting AI Services Status...');
    return this.request('/api/v2/ai/status');
  }

  // NEW: AI Health Check
  async getAIHealth(): Promise<ApiResponse<{
    status: 'healthy' | 'degraded';
    operation: string;
    message: string;
    services: {
      core_ai: string;
      heavy_ai: string;
      operation_left_brain: string;
      advanced_ml: string;
    };
  }>> {
    console.log('🏥 Getting AI Health Status...');
    return this.request('/api/v2/ai/health');
  }

  // NEW: Test Endpoint with Advanced ML
  async testAdvancedML(): Promise<ApiResponse<{
    message: string;
    version: string;
    operation: string;
    timestamp: string;
    ml_available: boolean;
    dual_skin_analysis: boolean;
    selfie_analysis: boolean;
    general_skin_analysis: boolean;
    google_vision_api: boolean;
    scin_dataset: boolean;
    operation_left_brain: boolean;
    advanced_ml: boolean;
    ai_services: AIStatus;
    proven_stable: boolean;
  }>> {
    console.log('🧪 Testing Advanced ML Features...');
    return this.request('/api/test');
  }

  // Legacy methods (keeping for backward compatibility)
  async analyzeSkinEnhanced(imageFile: File, ethnicity?: string, age?: string): Promise<ApiResponse<any>> {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    if (ethnicity) formData.append('ethnicity', ethnicity);
    if (age) formData.append('age', age);

    console.log('🔬 Enhanced Skin Analysis - Starting...');
    console.log('📊 File size:', imageFile.size, 'bytes');
    console.log('📊 Ethnicity:', ethnicity);
    console.log('📊 Age:', age);

    return this.request('/api/v2/skin/analyze', {
      method: 'POST',
      body: formData,
    });
  }

  // SCIN Search API - Uses real backend endpoint with compression
  async searchSCINSimilar(queryImageFile: File, k: number = 5, conditions?: string[], skinTypes?: string[]): Promise<ApiResponse<any>> {
    try {
      // Compress image if needed
      let fileToUpload = queryImageFile;
      
      if (ImageCompressor.needsCompression(queryImageFile, 1.0)) {
        console.log(`🖼️ Compressing SCIN search image from ${ImageCompressor.formatFileSize(queryImageFile.size)}...`);
        
        const compressed = await ImageCompressor.compressImage(queryImageFile, {
          maxWidth: 1920,
          maxHeight: 1920,
          quality: 0.8,
          maxSizeMB: 1.0
        });
        
        fileToUpload = compressed.file;
        console.log(`✅ SCIN image compressed: ${ImageCompressor.formatFileSize(compressed.originalSize)} → ${ImageCompressor.formatFileSize(compressed.compressedSize)}`);
      }
      
      const formData = new FormData();
      formData.append('query_image', fileToUpload);
      formData.append('k', k.toString());
      
      if (conditions && conditions.length > 0) {
        formData.append('conditions', conditions.join(','));
      }
      if (skinTypes && skinTypes.length > 0) {
        formData.append('skin_types', skinTypes.join(','));
      }

      const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
      const headers: Record<string, string> = {};
      if (token && token !== 'guest') {
        headers['Authorization'] = `Bearer ${token}`;
      }

      // Create AbortController for timeout management
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minutes timeout

      console.log('🔍 Starting SCIN analysis with 5-minute timeout...');
      const startTime = Date.now();

      const response = await fetch(`${this.baseUrl}/api/scin/search`, {
        method: 'POST',
        body: formData,
        headers: headers,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      const elapsedTime = Date.now() - startTime;
      console.log(`✅ SCIN analysis completed in ${elapsedTime}ms`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error: unknown) {
      console.error('SCIN analysis failed:', error);
      
      // Check if it was a timeout error
      if (error instanceof Error && error.name === 'AbortError') {
        console.error('⏰ SCIN analysis timed out after 5 minutes');
        return {
          data: {
            analysis_id: `timeout_scin_analysis_${Date.now()}`,
            status: "timeout",
            skin_analysis: {
              skinType: "processing_timeout",
              fitzpatrick_type: "unknown",
              concerns: ["Analysis timed out"],
              hydration: 0,
              oiliness: 0,
              sensitivity: 0,
              confidence: 0.0,
              similarity_score: 0.0
            },
            similar_images: [],
            recommendations: ["Please try again or contact support"]
          },
          success: false,
          message: "SCIN analysis timed out after 5 minutes - please try again"
        };
      }
      
      // Return error response for other errors
      return {
        data: {
          analysis_id: `error_scin_analysis_${Date.now()}`,
          status: "error",
          skin_analysis: {
            skinType: "error",
            fitzpatrick_type: "unknown",
            concerns: ["Analysis failed"],
            hydration: 0,
            oiliness: 0,
            sensitivity: 0,
            confidence: 0.0,
            similarity_score: 0.0
          },
          similar_images: [],
          recommendations: ["Please try again"]
        },
        success: false,
        message: "SCIN analysis failed - please try again"
      };
    }
  }

  // Trending Products API - Uses Next.js API route
  async getTrendingProducts(): Promise<ApiResponse<any[]>> {
    try {
      // Call the Next.js API route instead of backend
      const response = await fetch('/api/recommendations/trending');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Trending products failed:', error);
      return {
        data: [],
        success: false,
        message: 'Failed to fetch trending products'
      };
    }
  }

  // Health Check API - Uses real backend endpoint
  async getHealth(): Promise<ApiResponse<{ status: string; timestamp: string }>> {
    try {
      return this.request<ApiResponse<{ status: string; timestamp: string }>>('/api/health');
    } catch (error) {
      console.error('Health check failed:', error);
      return {
        data: { status: 'unavailable', timestamp: new Date().toISOString() },
        success: false,
        message: 'Health check failed'
      };
    }
  }

  // NEW: Operation Left Brain - Advanced ML Endpoints
  async analyzeSelfieV2(imageFile: File): Promise<ApiResponse<{
    facial_features: any;
    skin_conditions: any[];
    scin_similar_cases: any[];
    treatment_recommendations: any[];
    analysis_confidence: number;
    processing_time: number;
    ai_model_version: string;
  }>> {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    try {
      const response = await this.request<any>('/api/v2/selfie/analyze', {
        method: 'POST',
        body: formData,
        headers: {
          // Remove Content-Type for FormData
        },
      });
      
      return {
        data: response,
        success: true,
        message: 'Advanced selfie analysis completed',
        version: 'v2.2',
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Advanced selfie analysis failed:', error);
      throw error;
    }
  }

  async analyzeSkinV2(imageFile: File): Promise<ApiResponse<{
    skin_conditions: any[];
    texture_analysis: any;
    color_analysis: any;
    condition_confidence: number;
    processing_time: number;
    ai_model_version: string;
  }>> {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    try {
      const response = await this.request<any>('/api/v2/skin/analyze', {
        method: 'POST',
        body: formData,
        headers: {
          // Remove Content-Type for FormData
        },
      });
      
      return {
        data: response,
        success: true,
        message: 'Advanced skin analysis completed',
        version: 'v2.2',
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Advanced skin analysis failed:', error);
      throw error;
    }
  }

  async getAIStatusV2(): Promise<ApiResponse<{
    operation: string;
    status: string;
    features: {
      ai_services: {
        core_ai: boolean;
        full_ai: boolean;
        google_vision: boolean;
        heavy_ai: boolean;
        operation_left_brain: boolean;
        scin_dataset: boolean;
      };
      cors_fixed: boolean;
      dual_skin_analysis: boolean;
      file_size_limit: string;
      general_skin_analysis: boolean;
      google_vision_api: boolean;
      ml_available: boolean;
      no_duplication: boolean;
      proven_stable: boolean;
      selfie_analysis: boolean;
      structural_fix: boolean;
    };
    health_check: string;
    message: string;
    timestamp: string;
    version: string;
  }>> {
    try {
      const response = await this.request<any>('/api/v2/ai/status');
      
      return {
        data: response,
        success: true,
        message: 'AI status retrieved',
        version: 'v2.2',
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error('AI status check failed:', error);
      throw error;
    }
  }

  async getAIHealthV2(): Promise<ApiResponse<{
    status: string;
    services: {
      google_vision: boolean;
      faiss_search: boolean;
      skin_detection: boolean;
      embedding_service: boolean;
    };
    timestamp: string;
    version: string;
  }>> {
    try {
      const response = await this.request<any>('/api/v2/ai/health');
      
      return {
        data: response,
        success: true,
        message: 'AI health check completed',
        version: 'v2.2',
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error('AI health check failed:', error);
      throw error;
    }
  }

  // Enhanced SCIN Search with Advanced ML
  async searchSCINAdvanced(
    queryImageFile: File, 
    k: number = 5, 
    conditions?: string[], 
    skinTypes?: string[]
  ): Promise<ApiResponse<{
    similar_cases: any[];
    search_confidence: number;
    processing_time: number;
    faiss_index_status: string;
    total_cases_searched: number;
  }>> {
    const formData = new FormData();
    formData.append('image', queryImageFile);
    formData.append('k', k.toString());
    
    if (conditions && conditions.length > 0) {
      formData.append('conditions', JSON.stringify(conditions));
    }
    
    if (skinTypes && skinTypes.length > 0) {
      formData.append('skin_types', JSON.stringify(skinTypes));
    }
    
    try {
      const response = await this.request<any>('/api/scin/search', {
        method: 'POST',
        body: formData,
        headers: {
          // Remove Content-Type for FormData
        },
      });
      
      return {
        data: response,
        success: true,
        message: 'Advanced SCIN search completed',
        version: 'v2.2',
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Advanced SCIN search failed:', error);
      throw error;
    }
  }
}

// Create and export a single instance
export const apiClient = new ApiClient();

// Dual Skin Analysis API functions
export const analyzeSelfie = async (file: File): Promise<ApiResponse<{
  selfie_analysis: any;
  message: string;
  dual_skin_analysis: boolean;
  google_vision_api: boolean;
  scin_dataset: boolean;
  proven_stable: boolean;
}>> => {
  try {
    const formData = new FormData();
    formData.append('image', file);

    const response = await fetch('https://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com/api/v2/selfie/analyze', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    if (response.ok) {
      return { 
        success: true, 
        data: data, 
        message: 'Analysis completed' 
      };
    } else {
      return { 
        success: false, 
        data: {
          selfie_analysis: null,
          message: data.error || 'Request failed',
          dual_skin_analysis: false,
          google_vision_api: false,
          scin_dataset: false,
          proven_stable: false
        }, 
        message: data.error || 'Request failed' 
      };
    }
  } catch (error) {
    return { 
      success: false, 
      data: {
        selfie_analysis: null,
        message: 'Network error',
        dual_skin_analysis: false,
        google_vision_api: false,
        scin_dataset: false,
        proven_stable: false
      }, 
      message: 'Network error' 
    };
  }
};

export const analyzeSkin = async (file: File): Promise<ApiResponse<{
  skin_analysis: any;
  message: string;
  dual_skin_analysis: boolean;
  google_vision_api: boolean;
  scin_dataset: boolean;
  proven_stable: boolean;
}>> => {
  try {
    const formData = new FormData();
    formData.append('image', file);

    const response = await fetch('https://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com/api/v2/skin/analyze', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    if (response.ok) {
      return { 
        success: true, 
        data: data, 
        message: 'Analysis completed' 
      };
    } else {
      return { 
        success: false, 
        data: {
          skin_analysis: null,
          message: data.error || 'Request failed',
          dual_skin_analysis: false,
          google_vision_api: false,
          scin_dataset: false,
          proven_stable: false
        }, 
        message: data.error || 'Request failed' 
      };
    }
  } catch (error) {
    return { 
      success: false, 
      data: {
        skin_analysis: null,
        message: 'Network error',
        dual_skin_analysis: false,
        google_vision_api: false,
        scin_dataset: false,
        proven_stable: false
      }, 
      message: 'Network error' 
    };
  }
};

// Medical Analysis API functions
export const analyzeMedical = async (file: File, ethnicity?: string, age?: string): Promise<ApiResponse<{
  medical_analysis: any;
  message: string;
  has_medical_analysis: boolean;
  google_vision_api: boolean;
  scin_dataset: boolean;
  cosine_similarity: boolean;
  proven_stable: boolean;
}>> => {
  try {
    const formData = new FormData();
    formData.append('image', file);
    
    if (ethnicity) {
      formData.append('ethnicity', ethnicity);
    }
    if (age) {
      formData.append('age', age);
    }

    const response = await fetch(`${this.baseUrl}/api/v2/medical/analyze`, {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    return { 
      success: response.ok, 
      data: response.ok ? data : null, 
      error: response.ok ? null : data.error || 'Request failed' 
    };
  } catch (error) {
    return { 
      success: false, 
      data: null, 
      error: 'Network error' 
    };
  }
};

export const getMedicalHistory = async (user_id?: string, limit?: number): Promise<ApiResponse<{
  medical_history: any[];
  total_analyses: number;
  user_id: string;
}>> => {
  try {
    const params = new URLSearchParams();
    if (user_id) params.append('user_id', user_id);
    if (limit) params.append('limit', limit.toString());

    const response = await fetch(`${this.baseUrl}/api/v2/medical/history?${params}`);
    const data = await response.json();
    
    return { 
      success: response.ok, 
      data: response.ok ? data : null, 
      error: response.ok ? null : data.error || 'Request failed' 
    };
  } catch (error) {
    return { 
      success: false, 
      data: null, 
      error: 'Network error' 
    };
  }
};

export const getMedicalAnalysisDetails = async (analysis_id: string): Promise<ApiResponse<{
  analysis_details: any;
}>> => {
  try {
    const response = await fetch(`${this.baseUrl}/api/v2/medical/analysis/${analysis_id}`);
    const data = await response.json();
    
    return { 
      success: response.ok, 
      data: response.ok ? data : null, 
      error: response.ok ? null : data.error || 'Request failed' 
    };
  } catch (error) {
    return { 
      success: false, 
      data: null, 
      error: 'Network error' 
    };
  }
};

// NEW: Operation Left Brain v2 API Functions
export const analyzeSelfieV2 = async (file: File): Promise<ApiResponse<{
  facial_features: any;
  skin_conditions: any[];
  scin_similar_cases: any[];
  treatment_recommendations: any[];
  analysis_confidence: number;
  processing_time: number;
  ai_model_version: string;
}>> => {
  return apiClient.analyzeSelfieV2(file);
};

export const analyzeSkinV2 = async (file: File): Promise<ApiResponse<{
  skin_conditions: any[];
  texture_analysis: any;
  color_analysis: any;
  condition_confidence: number;
  processing_time: number;
  ai_model_version: string;
}>> => {
  return apiClient.analyzeSkinV2(file);
};

export const getAIStatusV2 = async (): Promise<ApiResponse<{
  operation: string;
  status: string;
  features: {
    ai_services: {
      core_ai: boolean;
      full_ai: boolean;
      google_vision: boolean;
      heavy_ai: boolean;
      operation_left_brain: boolean;
      scin_dataset: boolean;
    };
    cors_fixed: boolean;
    dual_skin_analysis: boolean;
    file_size_limit: string;
    general_skin_analysis: boolean;
    google_vision_api: boolean;
    ml_available: boolean;
    no_duplication: boolean;
    proven_stable: boolean;
    selfie_analysis: boolean;
    structural_fix: boolean;
  };
  health_check: string;
  message: string;
  timestamp: string;
  version: string;
}>> => {
  return apiClient.getAIStatusV2();
};

export const getAIHealthV2 = async (): Promise<ApiResponse<{
  status: string;
  services: {
    google_vision: boolean;
    faiss_search: boolean;
    skin_detection: boolean;
    embedding_service: boolean;
  };
  timestamp: string;
  version: string;
}>> => {
  return apiClient.getAIHealthV2();
};

export const searchSCINAdvanced = async (
  file: File, 
  k: number = 5, 
  conditions?: string[], 
  skinTypes?: string[]
): Promise<ApiResponse<{
  similar_cases: any[];
  search_confidence: number;
  processing_time: number;
  faiss_index_status: string;
  total_cases_searched: number;
}>> => {
  return apiClient.searchSCINAdvanced(file, k, conditions, skinTypes);
};