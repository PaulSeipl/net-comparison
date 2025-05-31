import React from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { NormalizedOffer } from '@/types/api';
import { formatPrice, getSpeedColor, getConnectionTypeIcon } from '@/utils/offerUtils';
import { Wifi, Clock, Euro, Plus, Check, Zap, Upload, Download, AlertCircle, Info } from 'lucide-react';

interface OfferCardProps {
  offer: NormalizedOffer;
  onAddToComparison: (offer: NormalizedOffer) => void;
  isInComparison: boolean;
}

export const OfferCard: React.FC<OfferCardProps> = ({
  offer,
  onAddToComparison,
  isInComparison,
}) => {
  const speedColor = getSpeedColor(offer.speed);
  const ConnectionIcon = getConnectionTypeIcon(offer.connection_type);
  const monthlyPrice = formatPrice(offer.price_details.monthly_cost);
  const discountPrice = offer.price_details.monthly_cost_with_discount 
    ? formatPrice(offer.price_details.monthly_cost_with_discount) 
    : null;
  const setupPrice = offer.price_details.setup_fee ? formatPrice(offer.price_details.setup_fee) : null;
  const afterPromotionPrice = offer.price_details.monthly_cost_after_promotion 
    ? formatPrice(offer.price_details.monthly_cost_after_promotion) 
    : null;

  return (
    <Card className="hover:shadow-xl transition-all duration-300 border-2 hover:border-blue-200 relative overflow-hidden">
      {/* Price highlight banner */}
      <div className="absolute top-0 right-0 bg-blue-600 text-white px-3 py-1 text-sm font-bold">
        €{discountPrice || monthlyPrice}/Monat
      </div>

      <CardHeader className="pb-2 p-3">
        {/* Provider and offer name */}
        <div className="space-y-2">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-md">
              <span className="font-bold text-white text-xs">
                {offer.provider.substring(0, 2)}
              </span>
            </div>
            <div className="flex-1">
              <h3 className="font-bold text-base text-gray-900">{offer.provider}</h3>
              <h4 className="text-blue-600 font-medium text-sm">{offer.name}</h4>
            </div>
          </div>
          
          {/* Connection type badge */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 bg-gray-100 rounded-full px-2 py-1">
              <ConnectionIcon className="w-3 h-3 text-gray-600" />
              <span className="text-xs font-medium text-gray-700">{offer.connection_type}</span>
            </div>
            <Badge className={`${speedColor} border-0 text-white font-bold text-xs`}>
              <Zap className="w-3 h-3 mr-1" />
              {offer.speed} Mbps
            </Badge>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-3 p-3 pt-0">
        {/* Speed information - prominent display */}
        <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-3 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Download className="w-4 h-4 text-green-600" />
              <span className="font-medium text-gray-700 text-sm">Geschwindigkeit</span>
            </div>
            <span className="text-lg font-bold text-gray-900">{offer.speed} Mbps</span>
          </div>
        </div>

        {/* Pricing section */}
        <div className="border-2 border-dashed border-gray-200 rounded-lg p-3 bg-gray-50">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-2">
              <Euro className="w-4 h-4 text-gray-600" />
              <span className="text-sm font-medium text-gray-600">Monatliche Kosten</span>
            </div>
            {discountPrice ? (
              <div>
                <div className="text-2xl font-bold text-green-600 mb-1">€{discountPrice}</div>
                <div className="text-xs text-gray-500 line-through">Regulär: €{monthlyPrice}</div>
                {offer.promotion_length && afterPromotionPrice && (
                  <div className="mt-2 p-2 bg-orange-50 rounded border border-orange-200">
                    <div className="flex items-center justify-center space-x-1 mb-1">
                      <AlertCircle className="w-3 h-3 text-orange-600" />
                      <span className="text-xs font-medium text-orange-700">Nach {offer.promotion_length} Monaten</span>
                    </div>
                    <div className="text-sm font-bold text-orange-800">€{afterPromotionPrice}/Monat</div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-2xl font-bold text-gray-900 mb-1">€{monthlyPrice}</div>
            )}
          </div>
          
          {setupPrice && (
            <div className="mt-2 pt-2 border-t border-gray-300 text-center">
              <span className="text-xs text-gray-600">Einrichtung: </span>
              <span className={`font-semibold text-xs ${setupPrice === '0.00' ? 'text-green-600' : 'text-gray-900'}`}>
                {setupPrice === '0.00' ? 'Kostenlos' : `€${setupPrice}`}
              </span>
            </div>
          )}
        </div>

        {/* Contract duration */}
        <div className="flex items-center justify-between p-2 bg-yellow-50 rounded-lg border border-yellow-200">
          <div className="flex items-center space-x-2">
            <Clock className="w-3 h-3 text-yellow-600" />
            <span className="text-xs font-medium text-gray-700">Laufzeit</span>
          </div>
          <span className="font-bold text-gray-900 text-sm">
            {offer.contract_duration} {offer.contract_duration === 1 ? 'Monat' : 'Monate'}
          </span>
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
            <span className="font-bold text-gray-900 text-sm">{offer.data_limit} GB</span>
          </div>
        )}

        {/* Special features */}
        {offer.tv_service && (
          <div className="space-y-1">
            <span className="text-xs font-semibold text-gray-700">Inklusivleistungen:</span>
            <div className="flex flex-wrap gap-1">
              <Badge variant="secondary" className="text-xs bg-green-100 text-green-800 border-green-200">
                {offer.tv_service}
              </Badge>
              {offer.installation_service && (
                <Badge variant="secondary" className="text-xs bg-blue-100 text-blue-800">
                  Installation inklusive
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* Action Button - most prominent */}
        <Button
          onClick={() => onAddToComparison(offer)}
          disabled={isInComparison}
          className={`w-full h-10 font-semibold text-sm transition-all duration-200 ${
            isInComparison 
              ? 'bg-green-600 hover:bg-green-700 text-white' 
              : 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-xl'
          }`}
        >
          {isInComparison ? (
            <>
              <Check className="w-4 h-4 mr-2" />
              Im Vergleich ausgewählt
            </>
          ) : (
            <>
              <Plus className="w-4 h-4 mr-2" />
              Zum Vergleich hinzufügen
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
};
