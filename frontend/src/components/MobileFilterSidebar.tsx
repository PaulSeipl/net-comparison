
import React from 'react';
import { FilterState, NormalizedOffer } from '@/types/api';
import { FilterSidebar } from '@/components/FilterSidebar';
import { SortingControls } from '@/components/SortingControls';
import { SortOption } from '@/types/api';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { Filter, SlidersHorizontal } from 'lucide-react';
import { useIsMobile } from '@/hooks/use-mobile';

interface MobileFilterSidebarProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  offers: NormalizedOffer[];
  resultCount: number;
  sortOption?: SortOption;
  onSortChange?: (option: SortOption) => void;
  searchData?: any;
  filteredOffers?: NormalizedOffer[];
  priceRangeModified: boolean;
  onPriceRangeModified: (modified: boolean) => void;
}

export const MobileFilterSidebar: React.FC<MobileFilterSidebarProps> = ({
  filters,
  onFiltersChange,
  offers,
  resultCount,
  sortOption = 'best_value',
  onSortChange,
  searchData,
  filteredOffers = [],
  priceRangeModified,
  onPriceRangeModified,
}) => {
  const isMobile = useIsMobile();
  const [isOpen, setIsOpen] = React.useState(false);

  if (!isMobile) {
    return (
      <div className="lg:w-64 flex-shrink-0">
        <FilterSidebar
          filters={filters}
          onFiltersChange={onFiltersChange}
          offers={offers}
          priceRangeModified={priceRangeModified}
          onPriceRangeModified={onPriceRangeModified}
        />
      </div>
    );
  }

  return (
    <div className="sticky top-0 z-40 bg-white border-b shadow-sm">
      <Sheet open={isOpen} onOpenChange={setIsOpen}>
        <div className="flex items-center justify-between p-4">
          <div className="text-sm text-gray-600">
            {resultCount} {resultCount === 1 ? 'Angebot' : 'Angebote'} gefunden
          </div>
          <SheetTrigger asChild>
            <Button 
              variant="outline" 
              size="sm" 
              className="flex items-center gap-2"
            >
              <SlidersHorizontal className="w-4 h-4" />
              Filter
            </Button>
          </SheetTrigger>
        </div>
        
        <SheetContent side="left" className="w-80 p-0">
          <SheetHeader className="p-4 border-b">
            <SheetTitle className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-blue-600" />
              Filter & Sortierung
            </SheetTitle>
          </SheetHeader>
          <div className="p-4 overflow-y-auto h-full space-y-4">
            {/* Sorting controls in mobile sidebar */}
            {onSortChange && searchData && (
              <div className="border-b pb-4">
                <SortingControls
                  sortOption={sortOption}
                  onSortChange={onSortChange}
                  resultCount={resultCount}
                  searchData={searchData}
                  offers={filteredOffers}
                />
              </div>
            )}
            
            <FilterSidebar
              filters={filters}
              onFiltersChange={onFiltersChange}
              offers={offers}
              priceRangeModified={priceRangeModified}
              onPriceRangeModified={onPriceRangeModified}
            />
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
};
