/**
 * Configuration for API endpoints and environment variables
 */

// Backend API configuration
export const API_CONFIG = {
  // Backend base URL - use production backend or localhost for development
  BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'https://shineskincollective.com',
  
  // API endpoints
  ENDPOINTS: {
    // V5 endpoints (latest - production)
    SKIN_ANALYZE_FIXED: '/api/v5/skin/analyze-fixed',
    SKIN_MODEL_STATUS: '/api/v5/skin/model-status',
    SKIN_HEALTH: '/api/v5/skin/health',
    
    // V4 endpoints
    FACE_DETECT: '/api/v4/face/detect',
    SKIN_ANALYZE_ENHANCED: '/api/v4/skin/analyze-enhanced',
    
    // V3 endpoints (legacy)
    V3_FACE_DETECT: '/api/v3/face/detect',
    V3_FACE_DETECT_DIRECT: '/api/v3/face/detect-direct',
    V3_FACE_DEBUG: '/api/v3/face/debug',
    V3_SKIN_ANALYZE_BASIC: '/api/v3/skin/analyze-basic',
    V3_SKIN_ANALYZE_ENHANCED: '/api/v3/skin/analyze-enhanced',
    V3_SKIN_ANALYZE_EMBEDDINGS: '/api/v3/skin/analyze-enhanced-embeddings',
    V3_SKIN_ANALYZE_DATABASE: '/api/v3/skin/analyze-real-database',
    
    // Health check
    HEALTH: '/api/health',
  }
} as const;

/**
 * Get full URL for an API endpoint
 */
export function getApiUrl(endpoint: string): string {
  return `${API_CONFIG.BACKEND_URL}${endpoint}`;
}

/**
 * Environment configuration
 */
export const ENV_CONFIG = {
  // Deployment environment
  IS_PRODUCTION: process.env.NODE_ENV === 'production',
  IS_DEVELOPMENT: process.env.NODE_ENV === 'development',
  
  // Backend configuration
  BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL,
  
  // Authentication
  GOOGLE_CLIENT_ID: process.env.GOOGLE_CLIENT_ID,
  GOOGLE_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET,
  
  // Supabase
  SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL,
  SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
  SUPABASE_SERVICE_ROLE_KEY: process.env.SUPABASE_SERVICE_ROLE_KEY,
  
  // Google Vision API
  GOOGLE_VISION_API_KEY: process.env.GOOGLE_VISION_API_KEY,
  
  // Stripe
  STRIPE_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY,
  STRIPE_SECRET_KEY: process.env.STRIPE_SECRET_KEY,
  
  // Deployment URL
  VERCEL_URL: process.env.NEXT_PUBLIC_VERCEL_URL,
} as const;

/**
 * Validate required environment variables
 */
export function validateEnvironment(): { isValid: boolean; missing: string[] } {
  const required = [
    'NEXT_PUBLIC_BACKEND_URL',
  ];
  
  const missing = required.filter(key => !process.env[key]);
  
  return {
    isValid: missing.length === 0,
    missing
  };
}

/**
 * Get environment info for debugging
 */
export function getEnvironmentInfo() {
  return {
    NODE_ENV: process.env.NODE_ENV,
    BACKEND_URL: API_CONFIG.BACKEND_URL,
    IS_PRODUCTION: ENV_CONFIG.IS_PRODUCTION,
    HAS_BACKEND_URL: !!ENV_CONFIG.BACKEND_URL,
    HAS_GOOGLE_CLIENT_ID: !!ENV_CONFIG.GOOGLE_CLIENT_ID,
    HAS_SUPABASE_URL: !!ENV_CONFIG.SUPABASE_URL,
    HAS_GOOGLE_VISION_API_KEY: !!ENV_CONFIG.GOOGLE_VISION_API_KEY,
  };
}
