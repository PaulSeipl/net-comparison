

import React, { useMemo } from 'react';
import { FilterState, ConnectionType, NormalizedOffer } from '@/types/api';
import { PriceRangeFilter } from '@/components/filters/PriceRangeFilter';
import { SpeedFilter } from '@/components/filters/SpeedFilter';
import { ConnectionTypeFilter } from '@/components/filters/ConnectionTypeFilter';
import { ContractDurationFilter } from '@/components/filters/ContractDurationFilter';
import { ProvidersFilter } from '@/components/filters/ProvidersFilter';
import { InstallationServiceFilter } from '@/components/filters/InstallationServiceFilter';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Filter, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface FilterSidebarProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  offers: NormalizedOffer[];
  priceRangeModified: boolean;
  onPriceRangeModified: (modified: boolean) => void;
}

export const FilterSidebar: React.FC<FilterSidebarProps> = ({
  filters,
  onFiltersChange,
  offers,
  priceRangeModified,
  onPriceRangeModified,
}) => {
  // Calculate dynamic price range from offers
  const priceRange = useMemo(() => {
    if (offers.length === 0) return { min: 0, max: 100 };
    
    const prices: number[] = [];
    
    offers
      .filter(offer => offer.price_details !== null)
      .forEach(offer => {
        const priceDetails = offer.price_details!;
        
        // Always include the monthly_cost
        prices.push(priceDetails.monthly_cost / 100);
        
        // Also include monthly_cost_with_discount if it exists and is different
        if (priceDetails.monthly_cost_with_discount !== null && 
            priceDetails.monthly_cost_with_discount !== priceDetails.monthly_cost) {
          prices.push(priceDetails.monthly_cost_with_discount / 100);
        }
      });
    
    if (prices.length === 0) return { min: 0, max: 100 }; // Fallback if no valid prices
    
    const min = Math.floor(Math.min(...prices));
    const max = Math.ceil(Math.max(...prices));
    
    return { min, max };
  }, [offers]);

  // Update price range automatically only if user hasn't modified it
  React.useEffect(() => {
    if (offers.length > 0 && !priceRangeModified) {
      onFiltersChange({
        ...filters,
        priceRange: [priceRange.min, priceRange.max],
      });
    }
  }, [priceRange, offers.length, filters, onFiltersChange, priceRangeModified]);

  // Check if any filters are active
  const hasActiveFilters = 
    filters.speedRequirement > 0 ||
    filters.connectionTypes.length > 0 ||
    filters.contractDuration.length > 0 ||
    filters.providers.length > 0 ||
    filters.installationService !== null ||
    priceRangeModified;

  const clearAllFilters = () => {
    onFiltersChange({
      priceRange: [priceRange.min, priceRange.max],
      speedRequirement: 0,
      contractDuration: [],
      connectionTypes: [],
      providers: [],
      installationService: null,
    });
    onPriceRangeModified(false);
  };

  const handlePriceRangeChange = (newPriceRange: [number, number]) => {
    onFiltersChange({
      ...filters,
      priceRange: newPriceRange,
    });
    onPriceRangeModified(true);
  };

  const handleSpeedRequirementChange = (speed: number) => {
    onFiltersChange({
      ...filters,
      speedRequirement: speed,
    });
  };

  const handleConnectionTypeChange = (type: ConnectionType, checked: boolean) => {
    const newTypes = checked
      ? [...filters.connectionTypes, type]
      : filters.connectionTypes.filter(t => t !== type);
    
    onFiltersChange({
      ...filters,
      connectionTypes: newTypes,
    });
  };

  const handleProviderChange = (provider: string, checked: boolean) => {
    const newProviders = checked
      ? [...filters.providers, provider]
      : filters.providers.filter(p => p !== provider);
    
    onFiltersChange({
      ...filters,
      providers: newProviders,
    });
  };

  const handleContractDurationChange = (duration: number, checked: boolean) => {
    const newDurations = checked
      ? [...filters.contractDuration, duration]
      : filters.contractDuration.filter(d => d !== duration);
    
    onFiltersChange({
      ...filters,
      contractDuration: newDurations,
    });
  };

  const handleInstallationServiceChange = (value: boolean | null) => {
    onFiltersChange({
      ...filters,
      installationService: value,
    });
  };

  return (
    <div className="space-y-3">
      {/* Filter Header */}
      <Card>
        <CardHeader className="pb-2 p-4">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base flex items-center gap-2">
              <Filter className="w-4 h-4 text-blue-600" />
              Filter
            </CardTitle>
            {hasActiveFilters && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearAllFilters}
                className="text-red-600 hover:text-red-700 hover:bg-red-50 h-7 px-2"
              >
                <X className="w-3 h-3 mr-1" />
                Zurücksetzen
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="pt-0 p-4">
          <p className="text-xs text-gray-600">
            Grenzen Sie Ihre Suche ein, um passende Angebote zu finden.
          </p>
        </CardContent>
      </Card>

      <PriceRangeFilter
        priceRange={filters.priceRange}
        onPriceRangeChange={handlePriceRangeChange}
        offers={offers}
      />

      <SpeedFilter
        speedRequirement={filters.speedRequirement}
        onSpeedRequirementChange={handleSpeedRequirementChange}
      />

      <ConnectionTypeFilter
        connectionTypes={filters.connectionTypes}
        onConnectionTypeChange={handleConnectionTypeChange}
      />

      <InstallationServiceFilter
        installationService={filters.installationService}
        onInstallationServiceChange={handleInstallationServiceChange}
      />

      <ContractDurationFilter
        contractDuration={filters.contractDuration}
        onContractDurationChange={handleContractDurationChange}
      />

      <ProvidersFilter
        providers={filters.providers}
        onProviderChange={handleProviderChange}
        offers={offers}
      />
    </div>
  );
};
