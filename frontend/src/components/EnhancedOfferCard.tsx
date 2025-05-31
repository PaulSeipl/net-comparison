import React, { useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { NormalizedOffer } from '@/types/api';
import { formatPrice, getSpeedColor, getConnectionTypeIcon } from '@/utils/offerUtils';
import { Wifi, Clock, Euro, Plus, Check, Zap, ChevronDown, ChevronUp, Percent, Calendar, Tv, Smartphone, Shield, Users, Timer, AlertCircle, Info } from 'lucide-react';

interface EnhancedOfferCardProps {
  offer: NormalizedOffer;
  onAddToComparison: (offer: NormalizedOffer) => void;
  isInComparison: boolean;
}

export const EnhancedOfferCard: React.FC<EnhancedOfferCardProps> = ({
  offer,
  onAddToComparison,
  isInComparison,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
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
      {/* Discount badge */}
      {offer.price_details.discount_percentage && (
        <div className="absolute top-0 left-0 bg-red-500 text-white px-2 py-1 text-xs font-bold">
          -{offer.price_details.discount_percentage}%
        </div>
      )}

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
          
          {/* Connection type and speed badges */}
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
                {offer.price_details.monthly_savings && (
                  <div className="text-xs text-green-600 font-medium">
                    Ersparnis: €{formatPrice(offer.price_details.monthly_savings)}/Monat
                  </div>
                )}
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

        {/* Key features preview */}
        <div className="flex flex-wrap gap-1">
          {offer.installation_service && (
            <Badge variant="secondary" className="text-xs bg-green-100 text-green-800">
              Installation inklusive
            </Badge>
          )}
          {offer.tv_service && (
            <Badge variant="secondary" className="text-xs bg-purple-100 text-purple-800">
              TV inklusive
            </Badge>
          )}
          {offer.data_limit && (
            <div className="flex items-center space-x-1">
              <Badge variant="secondary" className="text-xs bg-blue-100 text-blue-800">
                {offer.data_limit}GB Limit
              </Badge>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Info className="w-3 h-3 text-gray-400 hover:text-gray-600 cursor-help" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="text-sm max-w-xs">Wenn das Datenlimit erreicht ist, wird ihre Verbindung gedrosselt.</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
          )}
          {offer.max_age && (
            <Badge variant="secondary" className="text-xs bg-orange-100 text-orange-800">
              Bis {offer.max_age} Jahre
            </Badge>
          )}
        </div>

        {/* Expandable details */}
        <Collapsible open={isExpanded} onOpenChange={setIsExpanded}>
          <CollapsibleTrigger asChild>
            <Button variant="ghost" className="w-full p-2 text-blue-600 hover:text-blue-700">
              <span className="text-xs">
                {isExpanded ? 'Weniger Details' : 'Mehr Details'}
              </span>
              {isExpanded ? (
                <ChevronUp className="w-3 h-3 ml-2" />
              ) : (
                <ChevronDown className="w-3 h-3 ml-2" />
              )}
            </Button>
          </CollapsibleTrigger>
          
          <CollapsibleContent className="space-y-2">
            <div className="border-t pt-2 space-y-2 text-xs">
              {offer.promotion_length && (
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Timer className="w-3 h-3 text-purple-600" />
                    <span>Aktionsdauer</span>
                  </div>
                  <span className="font-medium">{offer.promotion_length} Monate</span>
                </div>
              )}
              
              {offer.price_details.total_savings && (
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Percent className="w-3 h-3 text-green-600" />
                    <span>Gesamtersparnis</span>
                  </div>
                  <span className="font-medium text-green-600">
                    €{formatPrice(offer.price_details.total_savings)}
                  </span>
                </div>
              )}
              
              {offer.tv_service && (
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Tv className="w-3 h-3 text-purple-600" />
                    <span>TV-Paket</span>
                  </div>
                  <span className="font-medium">{offer.tv_service}</span>
                </div>
              )}
              
              {offer.data_limit && (
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Smartphone className="w-3 h-3 text-blue-600" />
                    <span>Datenlimit</span>
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Info className="w-3 h-3 text-gray-400 hover:text-gray-600 cursor-help" />
                        </TooltipTrigger>
                        <TooltipContent>
                          <p className="text-sm max-w-xs">Wenn das Datenlimit erreicht ist, wird ihre Verbindung gedrosselt.</p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </div>
                  <span className="font-medium">{offer.data_limit} GB</span>
                </div>
              )}

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Calendar className="w-3 h-3 text-gray-600" />
                  <span>Abgerufen am</span>
                </div>
                <span className="font-medium">
                  {new Date(offer.fetched_at).toLocaleDateString('de-DE')}
                </span>
              </div>
            </div>
          </CollapsibleContent>
        </Collapsible>

        {/* Action Button */}
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
