import React, { useMemo } from 'react';
import { NormalizedOffer } from '@/types/api';

interface PriceDistributionChartProps {
  offers: NormalizedOffer[];
  selectedRange: [number, number];
  minPrice: number;
  maxPrice: number;
}

export const PriceDistributionChart: React.FC<PriceDistributionChartProps> = ({
  offers,
  selectedRange,
  minPrice,
  maxPrice,
}) => {
  const bucketData = useMemo(() => {
    console.log('PriceDistributionChart - offers:', offers.length);
    console.log('PriceDistributionChart - price range:', minPrice, 'to', maxPrice);
    
    const bucketCount = 8; // Number of price buckets
    const bucketSize = (maxPrice - minPrice) / bucketCount;
    const buckets = Array(bucketCount).fill(0);
    
    offers.forEach(offer => {
      const price = offer.price_details.monthly_cost / 100;
      const bucketIndex = Math.min(
        Math.floor((price - minPrice) / bucketSize),
        bucketCount - 1
      );
      if (bucketIndex >= 0) {
        buckets[bucketIndex]++;
      }
    });
    
    const maxCount = Math.max(...buckets);
    console.log('PriceDistributionChart - buckets:', buckets);
    console.log('PriceDistributionChart - maxCount:', maxCount);
    
    return buckets.map((count, index) => {
      const bucketStart = minPrice + index * bucketSize;
      const bucketEnd = minPrice + (index + 1) * bucketSize;
      
      // Check if this bucket overlaps with the selected range
      const isSelected = bucketEnd > selectedRange[0] && bucketStart < selectedRange[1];
      
      // Calculate height as percentage of container height
      const heightPercentage = maxCount > 0 ? (count / maxCount) * 80 : 0; // Use 80% max height
      
      console.log(`Bucket ${index}: count=${count}, height=${heightPercentage}%`);
      
      return {
        start: bucketStart,
        end: bucketEnd,
        count,
        height: heightPercentage,
        isSelected
      };
    });
  }, [offers, minPrice, maxPrice, selectedRange]);

  console.log('PriceDistributionChart - rendering with', offers.length, 'offers');

  if (offers.length === 0) {
    console.log('PriceDistributionChart - no offers, not rendering');
    return null;
  }

  return (
    <div className="mb-4">
      <div className="flex items-end justify-between h-16 space-x-1 bg-gray-50 p-2 rounded">
        {bucketData.map((bucket, index) => (
          <div key={index} className="flex-1 flex flex-col items-center justify-end h-full">
            <div
              className={`w-full transition-all duration-200 ${
                bucket.isSelected
                  ? 'bg-blue-500'
                  : 'bg-gray-300'
              }`}
              style={{ 
                height: bucket.count > 0 ? `${bucket.height}%` : '0%'
              }}
              title={`€${Math.round(bucket.start)}-€${Math.round(bucket.end)}: ${bucket.count} Angebote`}
            />
          </div>
        ))}
      </div>
    </div>
  );
};
