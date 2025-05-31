import React, { useEffect, useState } from 'react';
import { NormalizedOffer, NetworkRequestData } from '@/types/api';
import { EnhancedOfferCard } from '@/components/EnhancedOfferCard';
import { MobileOfferCard } from '@/components/MobileOfferCard';
import { FilterSidebar } from '@/components/FilterSidebar';
import { MobileFilterSidebar } from '@/components/MobileFilterSidebar';
import { SortingControls } from '@/components/SortingControls';
import { apiService } from '@/services/apiService';
import { filterOffers, sortOffers } from '@/utils/offerUtils';
import { FilterState, SortOption } from '@/types/api';
import { Loader2 } from 'lucide-react';
import { useIsMobile } from '@/hooks/use-mobile';

interface ResultsDisplayProps {
  searchData: NetworkRequestData | null;
  offers: NormalizedOffer[];
  loading: boolean;
  onOffersReceived: (offers: NormalizedOffer[]) => void;
  onAddToComparison: (offer: NormalizedOffer) => void;
  comparisonOffers: NormalizedOffer[];
}

export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({
  searchData,
  offers,
  loading,
  onOffersReceived,
  onAddToComparison,
  comparisonOffers,
}) => {
  const isMobile = useIsMobile();
  const [filteredOffers, setFilteredOffers] = useState<NormalizedOffer[]>([]);
  const [filters, setFilters] = useState<FilterState>({
    priceRange: [20, 100],
    speedRequirement: 0,
    contractDuration: [],
    connectionTypes: [],
    providers: [],
    installationService: null,
  });
  const [sortOption, setSortOption] = useState<SortOption>('best_value');
  const [providerLoadingStates, setProviderLoadingStates] = useState<Record<string, boolean>>({});
  const [priceRangeModified, setPriceRangeModified] = useState(false);

  useEffect(() => {
    if (searchData) {
      fetchOffers(searchData);
      // Reset price range modification state when starting a new search
      setPriceRangeModified(false);
    }
  }, [searchData]);

  useEffect(() => {
    if (offers.length > 0) {
      const filtered = filterOffers(offers, filters, priceRangeModified);
      const sorted = sortOffers(filtered, sortOption);
      setFilteredOffers(sorted);
    }
  }, [offers, filters, sortOption, priceRangeModified]);

  const fetchOffers = async (data: NetworkRequestData) => {
    const providers = ['WebWunder', 'ByteMe', 'Ping Perfect', 'VerbynDich', 'Servus Speed'];
    const allOffers: NormalizedOffer[] = [];
    
    // Initialize loading states
    const loadingStates: Record<string, boolean> = {};
    providers.forEach(provider => {
      loadingStates[provider] = true;
    });
    setProviderLoadingStates(loadingStates);

    // Fetch from all providers in parallel
    const promises = providers.map(async (provider) => {
      try {
        const providerOffers = await apiService.getProviderOffers(provider, data);
        allOffers.push(...providerOffers);
        
        // Update loading state for this provider
        setProviderLoadingStates(prev => ({
          ...prev,
          [provider]: false,
        }));
        
        // Update offers immediately as they come in
        onOffersReceived([...allOffers]);
        
        return providerOffers;
      } catch (error) {
        console.error(`Error fetching offers from ${provider}:`, error);
        setProviderLoadingStates(prev => ({
          ...prev,
          [provider]: false,
        }));
        return [];
      }
    });

    await Promise.allSettled(promises);
  };

  if (!searchData && !loading) {
    return null;
  }

  return (
    <div className={`flex flex-col ${isMobile ? 'gap-4' : 'lg:flex-row gap-6'}`}>
      {/* Filter Sidebar - Mobile responsive with sticky positioning */}
      {isMobile ? (
        <MobileFilterSidebar
          filters={filters}
          onFiltersChange={setFilters}
          offers={offers}
          resultCount={filteredOffers.length}
          sortOption={sortOption}
          onSortChange={setSortOption}
          searchData={searchData}
          filteredOffers={filteredOffers}
          priceRangeModified={priceRangeModified}
          onPriceRangeModified={setPriceRangeModified}
        />
      ) : (
        <div className="lg:w-64 flex-shrink-0">
          <FilterSidebar
            filters={filters}
            onFiltersChange={setFilters}
            offers={offers}
            priceRangeModified={priceRangeModified}
            onPriceRangeModified={setPriceRangeModified}
          />
        </div>
      )}

      {/* Results Content */}
      <div className="flex-1 min-w-0">
        {/* Sorting Controls - Hidden on mobile in favor of sidebar */}
        {!isMobile && (
          <div className="mb-6">
            <SortingControls
              sortOption={sortOption}
              onSortChange={setSortOption}
              resultCount={filteredOffers.length}
              searchData={searchData}
              offers={filteredOffers}
            />
          </div>
        )}

        {/* Provider Loading States */}
        {Object.keys(providerLoadingStates).some(provider => providerLoadingStates[provider]) && (
          <div className={`mb-6 bg-white rounded-lg p-4 shadow-sm ${isMobile ? 'p-3' : ''}`}>
            <h3 className={`font-medium text-gray-900 mb-3 ${isMobile ? 'text-sm' : ''}`}>
              Angebote werden geladen...
            </h3>
            <div className={`grid gap-3 ${isMobile ? 'grid-cols-2 gap-2' : 'grid-cols-2 md:grid-cols-5'}`}>
              {Object.entries(providerLoadingStates).map(([provider, isLoading]) => (
                <div key={provider} className="flex items-center space-x-2">
                  {isLoading ? (
                    <Loader2 className={`animate-spin text-blue-600 ${isMobile ? 'w-3 h-3' : 'w-4 h-4'}`} />
                  ) : (
                    <div className={`bg-green-500 rounded-full flex items-center justify-center ${isMobile ? 'w-3 h-3' : 'w-4 h-4'}`}>
                      <div className={`bg-white rounded-full ${isMobile ? 'w-1 h-1' : 'w-2 h-2'}`}></div>
                    </div>
                  )}
                  <span className={`text-gray-600 ${isMobile ? 'text-xs' : 'text-sm'}`}>{provider}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Offers Grid - Mobile responsive with proper spacing */}
        <div className={`grid gap-6 ${
          isMobile 
            ? 'grid-cols-1 gap-4 pb-32' 
            : 'grid-cols-1 md:grid-cols-2 xl:grid-cols-3'
        }`}>
          {filteredOffers.map((offer) => 
            isMobile ? (
              <MobileOfferCard
                key={offer.offer_id}
                offer={offer}
                onAddToComparison={onAddToComparison}
                isInComparison={comparisonOffers.some(o => o.offer_id === offer.offer_id)}
              />
            ) : (
              <EnhancedOfferCard
                key={offer.offer_id}
                offer={offer}
                onAddToComparison={onAddToComparison}
                isInComparison={comparisonOffers.some(o => o.offer_id === offer.offer_id)}
              />
            )
          )}
        </div>

        {/* No Results */}
        {!loading && filteredOffers.length === 0 && offers.length > 0 && (
          <div className={`text-center py-12 ${isMobile ? 'py-8' : ''}`}>
            <h3 className={`font-medium text-gray-900 mb-2 ${isMobile ? 'text-base' : 'text-lg'}`}>
              Keine Angebote gefunden
            </h3>
            <p className={`text-gray-600 ${isMobile ? 'text-sm' : ''}`}>
              Versuchen Sie, Ihre Filter anzupassen, um mehr Ergebnisse zu erhalten.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
