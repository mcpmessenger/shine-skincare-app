// API Client for Shine Skincare App
// Handles both real API calls and mock data for development

const API_BASE_URL = typeof window !== 'undefined' 
  ? window.location.origin 
  : 'https://shine-skincare-app.vercel.app';

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

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const defaultHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Add authorization header if token exists
    const token = typeof window !== 'undefined' ? localStorage.getItem('shine_token') : null;
    if (token) {
      defaultHeaders['Authorization'] = `Bearer ${token}`;
    }

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      // For development, use mock data instead of real API calls
      // BUT NOT for authentication endpoints
      if (process.env.NODE_ENV === 'development' && !endpoint.includes('/auth/')) {
        return this.getMockData<T>(endpoint);
      }

      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      
      // Fallback to mock data if API fails (but not for auth endpoints)
      if (process.env.NODE_ENV === 'development' && !endpoint.includes('/auth/')) {
        console.log('Falling back to mock data...');
        return this.getMockData<T>(endpoint);
      }
      
      throw error;
    }
  }

  private getMockData<T>(endpoint: string): T {
    // Mock data for development
    const mockData: Record<string, any> = {
      '/recommendations/trending': {
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
            name: 'Radiance Vitamin C Serum',
            brand: 'GlowEssence',
            price: 45.0,
            rating: 4.8,
            image_urls: ['/placeholder.svg?height=200&width=300'],
            description: 'Brighten and even skin tone with this potent vitamin C serum that targets dark spots and promotes collagen production.',
            category: 'serum',
            subcategory: 'brightening',
            ingredients: ['Vitamin C', 'Ferulic Acid', 'Vitamin E'],
            currency: 'USD',
            availability_status: 'available',
            review_count: 203
          },
          {
            id: '4',
            name: 'Gentle Foaming Cleanser',
            brand: 'PureSkin',
            price: 18.99,
            rating: 4.2,
            image_urls: ['/placeholder.svg?height=200&width=300'],
            description: 'A gentle yet effective cleanser that removes impurities without stripping the skin of its natural moisture.',
            category: 'cleanser',
            subcategory: 'gentle',
            ingredients: ['Glycerin', 'Aloe Vera', 'Chamomile Extract'],
            currency: 'USD',
            availability_status: 'available',
            review_count: 156
          },
          {
            id: '5',
            name: 'Retinol Night Cream',
            brand: 'AgeDefy',
            price: 52.0,
            rating: 4.6,
            image_urls: ['/placeholder.svg?height=200&width=300'],
            description: 'Advanced anti-aging night cream with encapsulated retinol to reduce fine lines and improve skin texture.',
            category: 'cream',
            subcategory: 'anti-aging',
            ingredients: ['Retinol', 'Peptides', 'Hyaluronic Acid'],
            currency: 'USD',
            availability_status: 'available',
            review_count: 178
          },
          {
            id: '6',
            name: 'SPF 50+ Sunscreen',
            brand: 'SunShield',
            price: 28.5,
            rating: 4.4,
            image_urls: ['/placeholder.svg?height=200&width=300'],
            description: 'Broad-spectrum sunscreen with lightweight, non-greasy formula that provides superior UV protection.',
            category: 'sunscreen',
            subcategory: 'broad-spectrum',
            ingredients: ['Zinc Oxide', 'Titanium Dioxide', 'Niacinamide'],
            currency: 'USD',
            availability_status: 'available',
            review_count: 234
          },
          {
            id: '7',
            name: 'Hydrating Face Mask',
            brand: 'MoistureMax',
            price: 15.99,
            rating: 4.3,
            image_urls: ['/placeholder.svg?height=200&width=300'],
            description: 'Intensive hydrating mask with hyaluronic acid and ceramides for instant moisture boost and skin plumping.',
            category: 'mask',
            subcategory: 'hydrating',
            ingredients: ['Hyaluronic Acid', 'Ceramides', 'Aloe Vera'],
            currency: 'USD',
            availability_status: 'available',
            review_count: 92
          },
          {
            id: '8',
            name: 'Exfoliating Toner',
            brand: 'GlowTonic',
            price: 22.0,
            rating: 4.1,
            image_urls: ['/placeholder.svg?height=200&width=300'],
            description: 'Gentle exfoliating toner with glycolic acid to remove dead skin cells and reveal brighter, smoother skin.',
            category: 'toner',
            subcategory: 'exfoliating',
            ingredients: ['Glycolic Acid', 'Witch Hazel', 'Aloe Vera'],
            currency: 'USD',
            availability_status: 'available',
            review_count: 145
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

  // Auth endpoints - ALWAYS use real API calls
  async login(): Promise<{ authorization_url: string; state: string; expires_in: number }> {
    console.log('API Client: Calling login endpoint...');
    const response = await this.request<{ authorization_url: string; state: string; expires_in: number }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ client_type: 'web' }),
    });
    console.log('API Client: Login response:', response);
    return response;
  }

  async oauthCallback(code: string, state: string): Promise<{ access_token: string; refresh_token: string; user_profile: User; expires_in: number }> {
    const response = await this.request<{ access_token: string; refresh_token: string; user_profile: User; expires_in: number }>('/api/auth/callback', {
      method: 'POST',
      body: JSON.stringify({ code, state }),
    });

    // Store tokens in localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('shine_token', response.access_token);
      localStorage.setItem('shine_refresh_token', response.refresh_token);
    }

    return response;
  }

  async getProfile(): Promise<User> {
    return this.request<User>('/api/auth/profile');
  }

  async logout(): Promise<void> {
    try {
      await this.request<void>('/api/auth/logout', {
        method: 'POST',
      });
    } finally {
      // Always clear tokens on logout
      if (typeof window !== 'undefined') {
        localStorage.removeItem('shine_token');
        localStorage.removeItem('shine_refresh_token');
      }
    }
  }

  async getCurrentUser(): Promise<ApiResponse<any>> {
    return this.request<ApiResponse<any>>('/api/auth/me');
  }

  // Product endpoints
  async getTrendingProducts(limit: number = 3): Promise<ApiResponse<any[]>> {
    return this.request<ApiResponse<any[]>>(`/api/recommendations/trending?limit=${limit}`);
  }

  async getProductRecommendations(skinType: string): Promise<ApiResponse<any[]>> {
    return this.request<ApiResponse<any[]>>(`/api/recommendations?skinType=${skinType}`);
  }

  // Skin analysis endpoints
  async submitSkinAnalysis(imageData: string): Promise<ApiResponse<any>> {
    return this.request<ApiResponse<any>>('/api/analysis/upload', {
      method: 'POST',
      body: JSON.stringify({ image: imageData }),
    });
  }

  async getAnalysisResults(analysisId: string): Promise<ApiResponse<any>> {
    return this.request<ApiResponse<any>>(`/api/analysis/${analysisId}`);
  }

  // User profile endpoints
  async getUserProfile(): Promise<ApiResponse<any>> {
    return this.request<ApiResponse<any>>('/api/user/profile');
  }

  async updateProfile(profileData: Partial<User>): Promise<User> {
    return this.request<User>('/api/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  }

  // MVP Skin Analysis endpoint
  async analyzeSkinMVP(imageData: string, ethnicity?: string): Promise<ApiResponse<any>> {
    const formData = await this.createFormData(imageData);
    if (ethnicity) {
      formData.append('ethnicity', ethnicity);
    }
    
    return this.request<ApiResponse<any>>('/api/analysis/skin', {
      method: 'POST',
      body: formData
    });
  }

  private async createFormData(imageData: string): Promise<FormData> {
    const formData = new FormData();
    
    // Convert base64 to blob
    const response = await fetch(imageData);
    const blob = await response.blob();
    
    formData.append('image', blob, 'selfie.jpg');
    return formData;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export for direct use
export default apiClient; 