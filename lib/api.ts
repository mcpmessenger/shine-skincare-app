// API Client for Shine Skincare App
// Handles both real API calls and mock data for development

interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
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
    // Use environment variables for production, fallback to localhost for development
    this.baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
    
    // Debug: Log the actual URL being used
    console.log('🔧 API Client initialized with backend URL:', this.baseUrl);
    console.log('🔧 Environment variables:', {
      NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL,
      NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL
    });
    
    // If we're in production and the URL is still localhost, use the correct backend
    if (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && this.baseUrl.includes('localhost')) {
      this.baseUrl = 'https://Shine-backend-poc-env-new-env.eba-pwtuapns.us-east-1.elasticbeanstalk.com';
      console.log('🔧 Overriding to correct backend URL:', this.baseUrl);
    }
    
    // Fix case sensitivity issue - ensure we use the correct URL
    if (this.baseUrl.includes('shine-backend-poc-env-new-env')) {
      this.baseUrl = 'https://Shine-backend-poc-env-new-env.eba-pwtuapns.us-east-1.elasticbeanstalk.com';
      console.log('🔧 Fixed case sensitivity, using correct URL:', this.baseUrl);
    }
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

  // Enhanced Image Analysis API
  async analyzeSkinEnhanced(imageFile: File): Promise<ApiResponse<any>> {
    const formData = new FormData();
    formData.append('image', imageFile);

    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    const headers: Record<string, string> = {};
    if (token && token !== 'guest') {
      headers['Authorization'] = `Bearer ${token}`;
    }

    // Use guest endpoint if not authenticated
    const endpoint = token && token !== 'guest' ? '/api/v2/analyze' : '/api/v2/analyze/guest';

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'POST',
        body: formData,
        headers: headers,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Enhanced skin analysis failed:', error);
      throw error;
    }
  }

  // Enhanced Vector Analysis API
  async analyzeSkinVector(imageFile: File, ethnicity?: string, age?: string): Promise<ApiResponse<any>> {
    const formData = new FormData();
    formData.append('image', imageFile);
    
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

    try {
      const response = await fetch(`${this.baseUrl}/api/enhanced-skin/analyze/vector`, {
        method: 'POST',
        body: formData,
        headers: headers,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Enhanced vector analysis failed:', error);
      throw error;
    }
  }

  // Similarity Search API
  async findSimilarImages(imageId: string, k: number = 5): Promise<ApiResponse<any>> {
    return this.request<ApiResponse<any>>(`/api/v2/similar/${imageId}?k=${k}`);
  }

  // SCIN Dataset Integration APIs
  async getSCINStatus(): Promise<ApiResponse<any>> {
    return this.request<ApiResponse<any>>('/api/scin/status');
  }

  async getSCINDatasetInfo(): Promise<ApiResponse<any>> {
    return this.request<ApiResponse<any>>('/api/scin/dataset/info');
  }

  async searchSCINSimilar(queryImageFile: File, k: number = 5, conditions?: string[], skinTypes?: string[]): Promise<ApiResponse<any>> {
    const formData = new FormData();
    formData.append('query_image', queryImageFile);
    formData.append('k', k.toString());
    
    if (conditions) {
      formData.append('conditions', conditions.join(','));
    }
    if (skinTypes) {
      formData.append('skin_types', skinTypes.join(','));
    }

    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    const headers: Record<string, string> = {};
    if (token && token !== 'guest') {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(`${this.baseUrl}/api/scin/search`, {
        method: 'POST',
        body: formData,
        headers: headers,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('SCIN similarity search failed:', error);
      throw error;
    }
  }

  async getSCINSamples(n: number = 5, conditions?: string[]): Promise<ApiResponse<any>> {
    const params = new URLSearchParams();
    params.append('n', n.toString());
    if (conditions) {
      params.append('conditions', conditions.join(','));
    }
    
    return this.request<ApiResponse<any>>(`/api/scin/dataset/sample?${params.toString()}`);
  }

  // Build SCIN Index
  async buildSCINIndex(conditions?: string[], skinTypes?: string[], maxImages?: number): Promise<ApiResponse<any>> {
    const payload = {
      conditions: conditions || [],
      skin_types: skinTypes || [],
      max_images: maxImages || 1000
    };

    return this.request<ApiResponse<any>>('/api/scin/build-index', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  // Existing API methods (updated to use real backend)
  async getTrendingProducts(): Promise<ApiResponse<any[]>> {
    try {
      const response = await this.request<ApiResponse<any>>('/api/recommendations/trending');
      
      // Handle the new response structure from backend
      if (response && response.data && response.data.trending_products) {
        return {
          data: response.data.trending_products,
          success: response.success,
          message: response.message
        };
      }
      
      return response;
    } catch (error) {
      console.error('Failed to get trending products:', error);
      throw error;
    }
  }

  async getProductRecommendations(skinType: string): Promise<ApiResponse<any[]>> {
    return this.request<ApiResponse<any[]>>(`/api/recommendations?skinType=${skinType}`);
  }

  async createPaymentIntent(amount: number, currency: string = 'usd'): Promise<ApiResponse<any>> {
    return this.request<ApiResponse<any>>('/api/payments/create-intent', {
      method: 'POST',
      body: JSON.stringify({ amount, currency }),
    });
  }

  async getAuthUrl(): Promise<ApiResponse<{ url: string }>> {
    return this.request<ApiResponse<{ url: string }>>('/api/auth/login');
  }

  async getHealth(): Promise<ApiResponse<{ status: string; timestamp: string }>> {
    return this.request<ApiResponse<{ status: string; timestamp: string }>>('/api/health');
  }

  async getProfile(): Promise<ApiResponse<User>> {
    return this.request<ApiResponse<User>>('/api/auth/profile');
  }

  async login(): Promise<ApiResponse<{ authorization_url: string }>> {
    return this.request<ApiResponse<{ authorization_url: string }>>('/api/auth/login');
  }

  async logout(): Promise<ApiResponse<{ message: string }>> {
    return this.request<ApiResponse<{ message: string }>>('/api/auth/logout');
  }

  async updateProfile(data: Partial<User>): Promise<ApiResponse<User>> {
    return this.request<ApiResponse<User>>('/api/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // Legacy methods for backward compatibility
  private getMockData<T>(endpoint: string): T {
    // Keep mock data as fallback for development
    const mockData: Record<string, any> = {
      '/api/recommendations/trending': {
        data: [
          {
            id: '1',
            name: 'HydraBoost Serum',
            brand: 'AquaGlow',
            price: 39.99,
            rating: 4.5,
            image_urls: ['/placeholder.svg?height=200&width=300'],
            description: 'A powerful hydrating serum infused with hyaluronic acid and ceramides to deeply moisturize and plump the skin.',
            category: 'serum',
            subcategory: 'hydrating',
            ingredients: ['Hyaluronic Acid', 'Ceramides', 'Niacinamide'],
            currency: 'USD',
            availability_status: 'available',
            review_count: 127
          },
          {
            id: '2',
            name: 'ClearSkin Acne Treatment',
            brand: 'DermPure',
            price: 24.5,
            rating: 4.0,
            image_urls: ['/placeholder.svg?height=200&width=300'],
            description: 'Target stubborn breakouts with this salicylic acid and tea tree oil formula, designed to clear pores and reduce inflammation.',
            category: 'treatment',
            subcategory: 'acne',
            ingredients: ['Salicylic Acid', 'Tea Tree Oil', 'Zinc PCA'],
            currency: 'USD',
            availability_status: 'available',
            review_count: 89
          },
          {
            id: '3',
            name: 'Radiant C Cream',
            brand: 'VitaBright',
            price: 55.0,
            rating: 4.8,
            image_urls: ['/placeholder.svg?height=200&width=300'],
            description: 'Brighten and even skin tone with this potent Vitamin C cream, packed with antioxidants for a youthful glow.',
            category: 'moisturizer',
            subcategory: 'brightening',
            ingredients: ['Vitamin C', 'Ferulic Acid', 'Vitamin E'],
            currency: 'USD',
            availability_status: 'available',
            review_count: 203
          }
        ],
        success: true
      },
      '/recommendations/products': {
        data: [
          {
            id: '1',
            name: 'HydraBoost Serum',
            brand: 'AquaGlow',
            price: 39.99,
            rating: 4.5,
            image_urls: ['/placeholder.svg?height=200&width=300'],
            description: 'A powerful hydrating serum infused with hyaluronic acid and ceramides to deeply moisturize and plump the skin.',
            category: 'serum',
            subcategory: 'hydrating',
            ingredients: ['Hyaluronic Acid', 'Ceramides', 'Niacinamide'],
            currency: 'USD',
            availability_status: 'available',
            review_count: 127
          },
          {
            id: '2',
            name: 'ClearSkin Acne Treatment',
            brand: 'DermPure',
            price: 24.5,
            rating: 4.0,
            image_urls: ['/placeholder.svg?height=200&width=300'],
            description: 'Target stubborn breakouts with this salicylic acid and tea tree oil formula, designed to clear pores and reduce inflammation.',
            category: 'treatment',
            subcategory: 'acne',
            ingredients: ['Salicylic Acid', 'Tea Tree Oil', 'Zinc PCA'],
            currency: 'USD',
            availability_status: 'available',
            review_count: 89
          }
        ],
        success: true
      },
      '/skin-analysis': {
        data: {
          analysisId: 'mock-analysis-123',
          status: 'completed',
          results: {
            skinType: 'Combination',
            concerns: ['Acne', 'Hyperpigmentation'],
            recommendations: ['Gentle cleanser', 'Vitamin C serum']
          }
        },
        success: true
      }
    };

    // Simulate network delay
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(mockData[endpoint] || { data: null, success: false });
      }, 500);
    }) as T;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export for direct use
export default apiClient; 