
import React from 'react';
import { NormalizedOffer } from '@/types/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { Euro } from 'lucide-react';

interface PriceRangeFilterProps {
  priceRange: [number, number];
  onPriceRangeChange: (range: [number, number]) => void;
  offers: NormalizedOffer[];
}

export const PriceRangeFilter: React.FC<PriceRangeFilterProps> = ({
  priceRange,
  onPriceRangeChange,
  offers,
}) => {
  // Calculate dynamic price range from offers
  const { min, max } = React.useMemo(() => {
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
    
    const minPrice = Math.floor(Math.min(...prices));
    const maxPrice = Math.ceil(Math.max(...prices));
    
    return { min: minPrice, max: maxPrice };
  }, [offers]);

  return (
    <Card>
      <CardHeader className="pb-2 p-4">
        <CardTitle className="text-sm flex items-center gap-2">
          <Euro className="w-4 h-4 text-blue-600" />
          Preisspanne
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 p-4 pt-0">
        <div className="px-2">
          <Slider
            value={priceRange}
            onValueChange={(value) => onPriceRangeChange(value as [number, number])}
            min={min}
            max={max}
            step={1}
            className="w-full"
          />
        </div>
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>€{priceRange[0]}</span>
          <span>€{priceRange[1]}</span>
        </div>
        <div className="text-xs text-gray-500 text-center">
          Monatliche Kosten (inkl. Rabatte)
        </div>
      </CardContent>
    </Card>
  );
};
