import React, { useState, useEffect } from 'react';
import { SearchForm } from '@/components/SearchForm';
import { ResultsDisplay } from '@/components/ResultsDisplay';
import { ComparisonPanel } from '@/components/ComparisonPanel';
import { NormalizedOffer, NetworkRequestData } from '@/types/api';
import { decodeSearchState } from '@/utils/urlState';
import { useToast } from '@/hooks/use-toast';
import { useIsMobile } from '@/hooks/use-mobile';

const Index = () => {
  const [searchData, setSearchData] = useState<NetworkRequestData | null>(null);
  const [offers, setOffers] = useState<NormalizedOffer[]>([]);
  const [loading, setLoading] = useState(false);
  const [comparisonOffers, setComparisonOffers] = useState<NormalizedOffer[]>([]);
  const [showComparison, setShowComparison] = useState(false);
  const { toast } = useToast();
  const isMobile = useIsMobile();

  // Check for shared URL on component mount
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const sharedData = urlParams.get('shared');
    
    if (sharedData) {
      const decoded = decodeSearchState(sharedData);
      if (decoded) {
        setSearchData(decoded.searchData);
        setOffers(decoded.offers);
        toast({
          title: "Geteilte Ergebnisse geladen",
          description: "Die geteilten Internetangebote wurden erfolgreich geladen.",
        });
        
        // Clean up URL
        window.history.replaceState({}, '', '/');
      } else {
        toast({
          title: "Fehler",
          description: "Die geteilten Daten konnten nicht geladen werden.",
          variant: "destructive",
        });
      }
    }
  }, [toast]);

  const handleSearch = (data: NetworkRequestData) => {
    setSearchData(data);
    setLoading(true);
    console.log('Search initiated with data:', data);
  };

  const handleOffersReceived = (newOffers: NormalizedOffer[]) => {
    setOffers(newOffers);
    setLoading(false);
    console.log('Offers received:', newOffers);
  };

  const addToComparison = (offer: NormalizedOffer) => {
    if (comparisonOffers.length < 4 && !comparisonOffers.find(o => o.offer_id === offer.offer_id)) {
      setComparisonOffers([...comparisonOffers, offer]);
      toast({
        title: "Angebot hinzugefügt",
        description: `${offer.provider} wurde zum Vergleich hinzugefügt.`,
      });
    } else if (comparisonOffers.length >= 4) {
      toast({
        title: "Vergleich voll",
        description: "Sie können maximal 4 Angebote vergleichen.",
        variant: "destructive",
      });
    }
  };

  const removeFromComparison = (offerId: string) => {
    setComparisonOffers(comparisonOffers.filter(o => o.offer_id !== offerId));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <div className="bg-white shadow-sm">
        <div className={`max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 ${isMobile ? 'py-6' : 'py-12'}`}>
          <div className={`text-center ${isMobile ? 'mb-6' : 'mb-8'}`}>
            <h1 className={`font-bold text-gray-900 mb-4 ${isMobile ? 'text-2xl' : 'text-4xl'}`}>
              Internetanbieter Vergleich
            </h1>
            <p className={`text-gray-600 max-w-2xl mx-auto ${isMobile ? 'text-base' : 'text-xl'}`}>
              Finden Sie den besten Internetanbieter für Ihre Adresse. 
              Vergleichen Sie Preise, Geschwindigkeiten und Vertragsbedingungen.
            </p>
          </div>
          
          <SearchForm onSearch={handleSearch} />
        </div>
      </div>

      {/* Results Section */}
      {(searchData || loading) && (
        <div className={`max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 ${isMobile ? 'py-4' : 'py-8'}`}>
          <ResultsDisplay
            searchData={searchData}
            offers={offers}
            loading={loading}
            onOffersReceived={handleOffersReceived}
            onAddToComparison={addToComparison}
            comparisonOffers={comparisonOffers}
          />
        </div>
      )}

      {/* Comparison Panel - Mobile responsive */}
      {comparisonOffers.length > 0 && (
        <div className={`fixed bottom-0 left-0 right-0 bg-white border-t shadow-lg z-50 ${
          isMobile ? 'pb-safe' : ''
        }`}>
          <div className={`max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 ${isMobile ? 'py-3' : 'py-4'}`}>
            <div className={`flex items-center justify-between ${isMobile ? 'flex-col gap-3' : ''}`}>
              <div className={`flex items-center space-x-4 ${isMobile ? 'w-full justify-center' : ''}`}>
                <span className={`font-medium text-gray-900 ${isMobile ? 'text-sm' : ''}`}>
                  {comparisonOffers.length} Angebote zum Vergleich
                </span>
                <button
                  onClick={() => setShowComparison(true)}
                  className={`bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors ${
                    isMobile ? 'text-sm' : ''
                  }`}
                >
                  Vergleichen
                </button>
              </div>
              <div className={`flex space-x-2 ${isMobile ? 'w-full overflow-x-auto pb-1' : ''}`}>
                {comparisonOffers.map((offer) => (
                  <div key={offer.offer_id} className={`flex items-center bg-gray-100 rounded px-3 py-1 ${
                    isMobile ? 'flex-shrink-0' : ''
                  }`}>
                    <span className={`font-medium mr-2 ${isMobile ? 'text-xs' : 'text-sm'}`}>
                      {offer.name}
                    </span>
                    <button
                      onClick={() => removeFromComparison(offer.offer_id)}
                      className="text-gray-500 hover:text-red-500"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Comparison Modal */}
      {showComparison && (
        <ComparisonPanel
          offers={comparisonOffers}
          onClose={() => setShowComparison(false)}
          onRemove={removeFromComparison}
        />
      )}
    </div>
  );
};

export default Index;
