
import { NetworkRequestData, NormalizedOffer } from '@/types/api';

export const encodeSearchState = (searchData: NetworkRequestData, offers: NormalizedOffer[]): string => {
  const state = {
    search: searchData,
    offers: offers,
    timestamp: Date.now()
  };
  
  const encoded = btoa(JSON.stringify(state));
  return encoded;
};

export const decodeSearchState = (encoded: string): { searchData: NetworkRequestData; offers: NormalizedOffer[] } | null => {
  try {
    const decoded = atob(encoded);
    const state = JSON.parse(decoded);
    
    // Validate the structure
    if (state.search && state.offers && Array.isArray(state.offers)) {
      return {
        searchData: state.search,
        offers: state.offers
      };
    }
    
    return null;
  } catch (error) {
    console.error('Error decoding share state:', error);
    return null;
  }
};

export const generateShareableUrl = (searchData: NetworkRequestData, offers: NormalizedOffer[]): string => {
  const encoded = encodeSearchState(searchData, offers);
  const baseUrl = window.location.origin;
  return `${baseUrl}/?shared=${encoded}`;
};

export const getWhatsAppShareUrl = (shareUrl: string, searchData: NetworkRequestData): string => {
  const message = `Ich habe Internetangebote für ${searchData.address.city} verglichen. Schau dir die Ergebnisse an: ${shareUrl}`;
  return `https://wa.me/?text=${encodeURIComponent(message)}`;
};
