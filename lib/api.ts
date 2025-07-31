'use client';

import { ImageCompressor } from './image-compression';

interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  version?: string;
  timestamp?: string;
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

class ApiClient {
  private baseUrl: string;

  constructor() {
    // SSL Certificate Fixed: Using correct certificate ARN
    this.baseUrl = 'https://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com';
    
    // Debug: Log the actual URL being used
    console.log('🔧 API Client initialized with backend URL:', this.baseUrl);
    console.log('🔧 Environment variables:', {
      NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL,
      NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
      NODE_ENV: process.env.NODE_ENV
    });
    
    // Log a clear message about the URL being used
    console.log('🔒 SSL Certificate Fixed: Using HTTPS with correct certificate');
    console.log('🚀 BUILD TRIGGER - Backend URL updated for SSL certificate fix');
    console.log('🔧 BACKEND HTTPS: Using working Elastic Beanstalk backend');
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

  // Enhanced Image Analysis API - Uses real backend endpoint with compression
  async analyzeSkinEnhanced(imageFile: File, ethnicity?: string, age?: string): Promise<ApiResponse<any>> {
    try {
      // Compress image if needed (target 1MB for reliable uploads)
      let fileToUpload = imageFile;
      let compressionInfo = null;
      
      if (ImageCompressor.needsCompression(imageFile, 1.0)) {
        console.log(`🖼️ Compressing image from ${ImageCompressor.formatFileSize(imageFile.size)} to fit upload limits...`);
        
        const compressed = await ImageCompressor.compressImage(imageFile, {
          maxWidth: 1920,
          maxHeight: 1920,
          quality: 0.8,
          maxSizeMB: 1.0
        });
        
        fileToUpload = compressed.file;
        compressionInfo = {
          originalSize: ImageCompressor.formatFileSize(compressed.originalSize),
          compressedSize: ImageCompressor.formatFileSize(compressed.compressedSize),
          compressionRatio: Math.round((1 - compressed.compressionRatio) * 100)
        };
        
        console.log(`✅ Image compressed: ${compressionInfo.originalSize} → ${compressionInfo.compressedSize} (${compressionInfo.compressionRatio}% reduction)`);
      }
      
      const formData = new FormData();
      formData.append('image', fileToUpload);
      
      // Add optional demographics if provided
      if (ethnicity) {
        formData.append('ethnicity', ethnicity);
      }
      if (age) {
        formData.append('age', age);
      }

      const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
      const headers: Record<string, string> = {};
      if (token && token !== 'guest') {
        headers['Authorization'] = `Bearer ${token}`;
      }

      // Use the correct endpoint that exists in our backend
      const endpoint = '/api/v2/analyze/guest';

      // Create AbortController for timeout management
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minutes timeout

      console.log('🔍 Starting enhanced ML analysis with 5-minute timeout...');
      console.log('📊 Demographics:', { ethnicity, age });
      if (compressionInfo) {
        console.log('📦 Compression applied:', compressionInfo);
      }
      const startTime = Date.now();

      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'POST',
        body: formData,
        headers: headers,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      const elapsedTime = Date.now() - startTime;
      console.log(`✅ Enhanced ML analysis completed in ${elapsedTime}ms`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Log the API response for debugging
      console.log('API Response:', result);
      
      // Return the result as-is since the backend already provides the correct structure
      return result;
    } catch (error: unknown) {
      console.error('Enhanced skin analysis failed:', error);
      
      // Check if it was a timeout error
      if (error instanceof Error && error.name === 'AbortError') {
        console.error('⏰ Enhanced ML analysis timed out after 5 minutes');
        return {
          data: {
            analysis_id: `timeout_analysis_${Date.now()}`,
            status: "timeout",
            results: {
              skin_type: "processing_timeout",
              concerns: ["Analysis timed out"],
              recommendations: ["Please try again or contact support"],
              confidence: 0.0,
              image_quality: "unknown"
            },
            timestamp: new Date().toISOString()
          },
          success: false,
          message: "Enhanced ML analysis timed out after 5 minutes - please try again"
        };
      }
      
      // Return error response for other errors
      return {
        data: {
          analysis_id: `error_analysis_${Date.now()}`,
          status: "error",
          results: {
            skin_type: "error",
            concerns: ["Analysis failed"],
            recommendations: ["Please try again"],
            confidence: 0.0,
            image_quality: "unknown"
          },
          timestamp: new Date().toISOString()
        },
        success: false,
        message: "Enhanced analysis failed - please try again"
      };
    }
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

  // Trending Products API - Uses real backend endpoint
  async getTrendingProducts(): Promise<ApiResponse<any[]>> {
    try {
      const response = await this.request<ApiResponse<any[]>>('/api/recommendations/trending');
      return response;
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
}

// Create and export a single instance
export const apiClient = new ApiClient();