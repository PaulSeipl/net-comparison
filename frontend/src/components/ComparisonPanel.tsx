
import React, { useEffect, useRef } from 'react';
import { NormalizedOffer } from '@/types/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { X, Wifi, Zap, Clock, Euro, Wrench, Tv, Smartphone, Info } from 'lucide-react';
import { formatPrice, getConnectionTypeIcon } from '@/utils/offerUtils';
import { useIsMobile } from '@/hooks/use-mobile';

interface ComparisonPanelProps {
  offers: NormalizedOffer[];
  onClose: () => void;
  onRemove: (offerId: string) => void;
}

export const ComparisonPanel: React.FC<ComparisonPanelProps> = ({
  offers,
  onClose,
  onRemove,
}) => {
  const isMobile = useIsMobile();
  const panelRef = useRef<HTMLDivElement>(null);

  // Handle click outside to close
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    // Handle escape key
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [onClose]);

  const comparisonFeatures = [
    { key: 'provider', label: 'Anbieter', icon: Wifi },
    { key: 'speed', label: 'Geschwindigkeit', icon: Zap },
    { key: 'price', label: 'Monatlicher Preis', icon: Euro },
    { key: 'contract_duration', label: 'Vertragslaufzeit', icon: Clock },
    { key: 'connection_type', label: 'Anschlussart', icon: Wifi },
    { key: 'installation_service', label: 'Installation', icon: Wrench },
    { key: 'tv_service', label: 'TV-Service', icon: Tv },
    { key: 'data_limit', label: 'Datenlimit', icon: Smartphone, tooltip: 'Wenn das Datenlimit erreicht ist, wird ihre Verbindung gedrosselt.' },
  ];

  const renderFeatureValue = (offer: NormalizedOffer, feature: string) => {
    switch (feature) {
      case 'provider':
        return offer.provider;
      case 'speed':
        return `${offer.speed} Mbps`;
      case 'price':
        if (!offer.price_details) return 'Preis auf Anfrage';
        const price = offer.price_details.monthly_cost_with_discount || offer.price_details.monthly_cost;
        return `€${formatPrice(price)}`;
      case 'contract_duration':
        return `${offer.contract_duration} Monate`;
      case 'connection_type':
        return offer.connection_type;
      case 'installation_service':
        return offer.installation_service ? 'Ja' : 'Nein';
      case 'tv_service':
        return offer.tv_service || 'Nicht verfügbar';
      case 'data_limit':
        return offer.data_limit ? `${offer.data_limit} GB` : 'Unbegrenzt';
      default:
        return '-';
    }
  };

  const renderFeatureLabel = (feature: any) => {
    const Icon = feature.icon;
    return (
      <div className="flex items-center gap-2">
        <Icon className={`${isMobile ? 'w-4 h-4' : 'w-5 h-5'} text-blue-600`} />
        <span className={isMobile ? 'text-sm text-gray-600' : 'font-medium text-gray-900'}>{feature.label}</span>
        {feature.tooltip && (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Info className="w-4 h-4 text-gray-400 hover:text-gray-600 cursor-help" />
              </TooltipTrigger>
              <TooltipContent>
                <p className="text-sm max-w-xs">{feature.tooltip}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        )}
      </div>
    );
  };

  if (isMobile) {
    return (
      <div className="fixed inset-0 bg-white z-50 overflow-auto">
        {/* Sticky header with close button */}
        <div className="sticky top-0 bg-white border-b p-4 flex items-center justify-between z-10 shadow-sm">
          <h2 className="text-lg font-bold text-gray-900">Vergleich</h2>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        <div className="p-4 space-y-4">
          {offers.map((offer, index) => (
            <Card key={offer.offer_id} className="relative">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-base">{offer.name}</CardTitle>
                    <Badge variant="secondary" className="mt-1">{offer.provider}</Badge>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onRemove(offer.offer_id)}
                    className="text-red-500 hover:text-red-700"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {comparisonFeatures.map((feature) => (
                  <div key={feature.key} className="flex items-center justify-between">
                    {renderFeatureLabel(feature)}
                    <span className="font-medium text-sm">
                      {renderFeatureValue(offer, feature.key)}
                    </span>
                  </div>
                ))}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div ref={panelRef} className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden relative">
        {/* Sticky header with close button */}
        <div className="sticky top-0 bg-white border-b p-6 z-10 shadow-sm">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">Angebote vergleichen</h2>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

        {/* Scrollable content */}
        <div className="p-6 overflow-auto max-h-[calc(90vh-80px)]">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {offers.map((offer) => (
              <Card key={offer.offer_id} className="relative">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{offer.name}</CardTitle>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onRemove(offer.offer_id)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                  <Badge variant="secondary">{offer.provider}</Badge>
                </CardHeader>
              </Card>
            ))}
          </div>

          <div className="space-y-4">
            {comparisonFeatures.map((feature) => (
              <div key={feature.key} className="border rounded-lg p-4">
                {renderFeatureLabel(feature)}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-3">
                  {offers.map((offer) => (
                    <div key={offer.offer_id} className="text-center p-3 bg-gray-50 rounded">
                      <span className="font-medium">
                        {renderFeatureValue(offer, feature.key)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
