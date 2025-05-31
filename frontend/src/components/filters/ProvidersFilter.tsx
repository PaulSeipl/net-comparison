
import React from 'react';
import { NormalizedOffer } from '@/types/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Building2 } from 'lucide-react';

interface ProvidersFilterProps {
  providers: string[];
  onProviderChange: (provider: string, checked: boolean) => void;
  offers: NormalizedOffer[];
}

export const ProvidersFilter: React.FC<ProvidersFilterProps> = ({
  providers,
  onProviderChange,
  offers,
}) => {
  // Get unique providers from offers
  const availableProviders = React.useMemo(() => {
    const providerSet = new Set(offers.map(offer => offer.provider));
    return Array.from(providerSet);
  }, [offers]);

  return (
    <Card>
      <CardHeader className="pb-2 p-4">
        <CardTitle className="text-sm flex items-center gap-2">
          <Building2 className="w-4 h-4 text-blue-600" />
          Anbieter
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 p-4 pt-0">
        {availableProviders.map((provider) => (
          <div key={provider} className="flex items-center space-x-2">
            <Checkbox
              id={`provider-${provider}`}
              checked={providers.includes(provider)}
              onCheckedChange={(checked) => onProviderChange(provider, !!checked)}
            />
            <label
              htmlFor={`provider-${provider}`}
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
            >
              {provider}
            </label>
          </div>
        ))}
      </CardContent>
    </Card>
  );
};
