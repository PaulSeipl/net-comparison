
// Production configuration
export const PRODUCTION_CONFIG = {
  // API Configuration
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'https://localhost:8000',
  API_KEY: import.meta.env.VITE_API_KEY || 'secret',
  
  // Feature flags
  ENABLE_DEBUG_LOGS: import.meta.env.VITE_ENABLE_DEBUG_LOGS === 'true',
  
  // Error tracking
  SENTRY_DSN: import.meta.env.VITE_SENTRY_DSN,
  
  // Analytics
  GOOGLE_ANALYTICS_ID: import.meta.env.VITE_GOOGLE_ANALYTICS_ID,
  
  // Performance monitoring
  ENABLE_PERFORMANCE_MONITORING: import.meta.env.VITE_ENABLE_PERFORMANCE_MONITORING === 'true',
};

// Runtime environment check
export const IS_PRODUCTION = import.meta.env.PROD;
export const IS_DEVELOPMENT = import.meta.env.DEV;
