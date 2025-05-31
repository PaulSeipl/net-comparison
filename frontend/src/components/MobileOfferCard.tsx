import React, { useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { NormalizedOffer } from '@/types/api';
import { formatPrice, getSpeedColor, getConnectionTypeIcon } from '@/utils/offerUtils';
import { Plus, Check, Zap, Clock, Euro, ChevronDown, ChevronUp, Wrench, CreditCard, AlertCircle, Info } from 'lucide-react';

interface MobileOfferCardProps {
  offer: NormalizedOffer;
  onAddToComparison: (offer: NormalizedOffer) => void;
  isInComparison: boolean;
}

export const MobileOfferCard: React.FC<MobileOfferCardProps> = ({
  offer,
  onAddToComparison,
  isInComparison,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const speedColor = getSpeedColor(offer.speed);
  const ConnectionIcon = getConnectionTypeIcon(offer.connection_type);
  
  // Handle null price_details safely
  const monthlyPrice = offer.price_details ? formatPrice(offer.price_details.monthly_cost) : 'N/A';
  const discountPrice = offer.price_details?.monthly_cost_with_discount 
    ? formatPrice(offer.price_details.monthly_cost_with_discount) 
    : null;
  const setupPrice = offer.price_details?.setup_fee ? formatPrice(offer.price_details.setup_fee) : null;
  const afterPromotionPrice = offer.price_details?.monthly_cost_after_promotion 
    ? formatPrice(offer.price_details.monthly_cost_after_promotion) 
    : null;

  return (
    <Card className="hover:shadow-lg transition-all duration-300 border hover:border-blue-200 relative">
      {/* Compact header */}
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
              <span className="font-bold text-white text-xs">
                {offer.provider.substring(0, 2)}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="font-bold text-sm text-gray-900 truncate">{offer.provider}</h3>
              <h4 className="text-blue-600 font-medium text-xs truncate">{offer.name}</h4>
            </div>
          </div>
          <div className="text-right">
            <div className="text-lg font-bold text-gray-900">
              {offer.price_details ? `€${discountPrice || monthlyPrice}` : 'Preis auf Anfrage'}
            </div>
            {offer.price_details && <div className="text-xs text-gray-500">/Monat</div>}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-3 pt-0">
        {/* Key info in compact layout */}
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="flex items-center space-x-1">
            <Zap className="w-3 h-3 text-green-600" />
            <span className="font-medium">{offer.speed} Mbps</span>
          </div>
          <div className="flex items-center space-x-1">
            <ConnectionIcon className="w-3 h-3 text-gray-600" />
            <span className="text-gray-600 text-xs">{offer.connection_type}</span>
          </div>
          <div className="flex items-center space-x-1">
            <Clock className="w-3 h-3 text-yellow-600" />
            <span className="text-gray-600 text-xs">
              {offer.contract_duration} {offer.contract_duration === 1 ? 'Monat' : 'Monate'}
            </span>
          </div>
          {offer.installation_service && (
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-xs text-green-600">Installation inkl.</span>
            </div>
          )}
        </div>

        {/* Data limit with tooltip */}
        {offer.data_limit && (
          <div className="flex items-center justify-between p-2 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-medium text-gray-700">Datenlimit</span>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Info className="w-4 h-4 text-gray-400 hover:text-gray-600 cursor-help" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="text-sm max-w-xs">Wenn das Datenlimit erreicht ist, wird ihre Verbindung gedrosselt.</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
            <span className="font-medium text-gray-900 text-sm">{offer.data_limit} GB</span>
          </div>
        )}

        {/* Aktionsangebot - Promotional offer highlight */}
        {discountPrice && offer.price_details && (
          <div className="bg-green-50 p-3 rounded-lg border border-green-200">
            <div className="text-sm font-semibold text-green-700 mb-1">Aktionsangebot</div>
            <div className="text-xs text-gray-500 line-through mb-1">Regulär: €{monthlyPrice}</div>
            {offer.price_details.monthly_savings && (
              <div className="text-xs text-green-600 font-medium">
                Sparen Sie €{formatPrice(offer.price_details.monthly_savings)} monatlich
              </div>
            )}
            {offer.promotion_length && afterPromotionPrice && (
              <div className="mt-2 p-2 bg-orange-50 rounded border border-orange-200">
                <div className="flex items-center space-x-1 mb-1">
                  <AlertCircle className="w-3 h-3 text-orange-600" />
                  <span className="text-xs font-medium text-orange-700">Nach {offer.promotion_length} Monaten</span>
                </div>
                <div className="text-xs font-bold text-orange-800">€{afterPromotionPrice}/Monat</div>
              </div>
            )}
          </div>
        )}

        {/* Expandable details */}
        {isExpanded && (
          <div className="space-y-3 border-t pt-3">
            <div className="grid grid-cols-1 gap-2 text-sm">
              {setupPrice && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Einrichtungsgebühr:</span>
                  <span className={`font-medium ${setupPrice === '0.00' ? 'text-green-600' : 'text-gray-900'}`}>
                    {setupPrice === '0.00' ? 'Kostenlos' : `€${setupPrice}`}
                  </span>
                </div>
              )}
              {offer.price_details?.total_savings && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Gesamtersparnis:</span>
                  <span className="font-medium text-green-600">€{formatPrice(offer.price_details.total_savings)}</span>
                </div>
              )}
              {offer.tv_service && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">TV-Service:</span>
                  <span className="font-medium text-blue-600">{offer.tv_service}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Expand/Collapse button */}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full text-xs text-gray-600 hover:text-gray-900"
        >
          {isExpanded ? (
            <>
              Weniger anzeigen <ChevronUp className="w-3 h-3 ml-1" />
            </>
          ) : (
            <>
              Mehr Details <ChevronDown className="w-3 h-3 ml-1" />
            </>
          )}
        </Button>

        {/* Action button - compact */}
        <Button
          onClick={() => onAddToComparison(offer)}
          disabled={isInComparison}
          size="sm"
          className={`w-full font-medium text-sm ${
            isInComparison 
              ? 'bg-green-600 hover:bg-green-700 text-white' 
              : 'bg-blue-600 hover:bg-blue-700 text-white'
          }`}
        >
          {isInComparison ? (
            <>
              <Check className="w-4 h-4 mr-1" />
              Ausgewählt
            </>
          ) : (
            <>
              <Plus className="w-4 h-4 mr-1" />
              Vergleichen
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
};
