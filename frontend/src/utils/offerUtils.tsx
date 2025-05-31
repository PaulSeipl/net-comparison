
import { NormalizedOffer, FilterState, SortOption, ConnectionType } from '@/types/api';
import { Wifi, Cable, Router, Smartphone } from 'lucide-react';

export const formatPrice = (cents: number): string => {
  return (cents / 100).toFixed(2);
};

export const getSpeedColor = (speed: number): string => {
  if (speed >= 250) return 'bg-blue-500';
  if (speed < 25) return 'bg-red-500';
  if (speed < 100) return 'bg-yellow-500';
  return 'bg-green-500';
};

export const getConnectionTypeIcon = (type: ConnectionType) => {
  switch (type) {
    case 'Fiber':
      return Wifi;
    case 'Cable':
      return Cable;
    case 'DSL':
      return Router;
    case 'Mobile':
      return Smartphone;
    default:
      return Wifi;
  }
};

export const filterOffers = (offers: NormalizedOffer[], filters: FilterState, priceRangeModified: boolean): NormalizedOffer[] => {
  return offers.filter((offer) => {
    // Only apply price filtering if user has manually modified the price range
    if (priceRangeModified && offer.price_details !== null) {
      // Price range filter - use discounted price if available, otherwise use regular price
      const price = offer.price_details.monthly_cost_with_discount ?? offer.price_details.monthly_cost;
      const monthlyPrice = price / 100;
      if (monthlyPrice < filters.priceRange[0] || monthlyPrice > filters.priceRange[1]) {
        return false;
      }
    }

    // Speed requirement filter
    if (filters.speedRequirement > 0 && offer.speed < filters.speedRequirement) {
      return false;
    }

    // Connection type filter
    if (filters.connectionTypes.length > 0 && !filters.connectionTypes.includes(offer.connection_type)) {
      return false;
    }

    // Contract duration filter
    if (filters.contractDuration.length > 0 && !filters.contractDuration.includes(offer.contract_duration)) {
      return false;
    }

    // Provider filter
    if (filters.providers.length > 0 && !filters.providers.includes(offer.provider)) {
      return false;
    }

    // Installation service filter
    if (filters.installationService !== null && offer.installation_service !== filters.installationService) {
      return false;
    }

    return true;
  });
};

export const sortOffers = (offers: NormalizedOffer[], sortOption: SortOption): NormalizedOffer[] => {
  const sorted = [...offers];

  switch (sortOption) {
    case 'lowest_price':
      return sorted.sort((a, b) => {
        // Handle null price_details by putting them at the end
        if (!a.price_details && !b.price_details) return 0;
        if (!a.price_details) return 1;
        if (!b.price_details) return -1;
        
        const priceA = a.price_details.monthly_cost_with_discount || a.price_details.monthly_cost;
        const priceB = b.price_details.monthly_cost_with_discount || b.price_details.monthly_cost;
        return priceA - priceB;
      });
    
    case 'fastest_speed':
      return sorted.sort((a, b) => b.speed - a.speed);
    
    case 'shortest_contract':
      return sorted.sort((a, b) => a.contract_duration - b.contract_duration);
    
    case 'best_value':
    default:
      // Calculate value score: speed per euro
      return sorted.sort((a, b) => {
        // Handle null price_details by putting them at the end
        if (!a.price_details && !b.price_details) return 0;
        if (!a.price_details) return 1;
        if (!b.price_details) return -1;
        
        const priceA = a.price_details.monthly_cost_with_discount || a.price_details.monthly_cost;
        const priceB = b.price_details.monthly_cost_with_discount || b.price_details.monthly_cost;
        const scoreA = a.speed / (priceA / 100);
        const scoreB = b.speed / (priceB / 100);
        return scoreB - scoreA;
      });
  }
};

export const calculateSavings = (offer: NormalizedOffer): number | null => {
  return offer.price_details?.monthly_savings || null;
};
