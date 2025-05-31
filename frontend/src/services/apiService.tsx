
import { NormalizedOffer, NetworkRequestData } from '@/types/api';
import { PRODUCTION_CONFIG } from '@/config/production';

const BASE_URL = PRODUCTION_CONFIG.API_BASE_URL;
const API_KEY = PRODUCTION_CONFIG.API_KEY;

class ApiService {
  private readonly providerEndpoints = {
    'WebWunder': 'webWunder',
    'ByteMe': 'byteMe', 
    'Ping Perfect': 'pingPerfect',
    'VerbynDich': 'verbynDich',
    'Servus Speed': 'servusSpeed',
  };

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    if (API_KEY) {
      headers['X-API-Key'] = API_KEY;
    }
    
    return headers;
  }

  private logError(message: string, error: unknown) {
    if (PRODUCTION_CONFIG.ENABLE_DEBUG_LOGS) {
      console.error(message, error);
    }
  }

  async getProviders(): Promise<string[]> {
    try {
      const response = await fetch(`${BASE_URL}/api/v1/providers`, {
        headers: this.getHeaders(),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      this.logError('Error fetching providers:', error);
      return Object.keys(this.providerEndpoints);
    }
  }

  async getAllOffers(data: NetworkRequestData): Promise<NormalizedOffer[]> {
    const providers = Object.keys(this.providerEndpoints);
    const allOffers: NormalizedOffer[] = [];

    const promises = providers.map(async (provider) => {
      try {
        const offers = await this.getProviderOffers(provider, data);
        return offers;
      } catch (error) {
        this.logError(`Error fetching offers from ${provider}:`, error);
        return [];
      }
    });

    const results = await Promise.allSettled(promises);
    results.forEach((result) => {
      if (result.status === 'fulfilled') {
        allOffers.push(...result.value);
      }
    });

    return allOffers;
  }

  async getProviderOffers(provider: string, data: NetworkRequestData): Promise<NormalizedOffer[]> {
    const endpoint = this.providerEndpoints[provider as keyof typeof this.providerEndpoints];
    if (!endpoint) {
      throw new Error(`Unknown provider: ${provider}`);
    }

    const response = await fetch(`${BASE_URL}/api/v1/providers/offers/${endpoint}`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status} for provider ${provider}`);
    }

    return await response.json();
  }
}

export const apiService = new ApiService();
