
// Production configuration
export const PRODUCTION_CONFIG = {
  // API Configuration
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'https://localhost:8000',
  API_KEY: import.meta.env.VITE_API_KEY || 'secret',
};

// Runtime environment check
