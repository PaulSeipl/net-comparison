
import React from 'react';
import { SortOption, NormalizedOffer, NetworkRequestData } from '@/types/api';
import { ShareButton } from '@/components/ShareButton';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent } from '@/components/ui/card';

interface SortingControlsProps {
  sortOption: SortOption;
  onSortChange: (option: SortOption) => void;
  resultCount: number;
  searchData: NetworkRequestData | null;
  offers: NormalizedOffer[];
}

export const SortingControls: React.FC<SortingControlsProps> = ({
  sortOption,
  onSortChange,
  resultCount,
  searchData,
  offers,
}) => {
  const sortOptions = [
    { value: 'best_value' as SortOption, label: 'Bestes Preis-Leistungs-Verhältnis' },
    { value: 'lowest_price' as SortOption, label: 'Niedrigster Preis' },
    { value: 'fastest_speed' as SortOption, label: 'Höchste Geschwindigkeit' },
    { value: 'shortest_contract' as SortOption, label: 'Kürzeste Vertragslaufzeit' },
  ];

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">
              {resultCount} {resultCount === 1 ? 'Angebot' : 'Angebote'} gefunden
            </span>
            
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-700">Sortieren nach:</span>
              <Select value={sortOption} onValueChange={onSortChange}>
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {sortOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          
          {searchData && offers.length > 0 && (
            <ShareButton searchData={searchData} offers={offers} />
          )}
        </div>
      </CardContent>
    </Card>
  );
};
