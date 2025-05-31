
import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { NetworkRequestData } from '@/types/api';
import { validateSearchForm, ValidationErrors } from '@/utils/validation';
import { useSessionState } from '@/hooks/useSessionState';
import { Search, MapPin } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface SearchFormProps {
  onSearch: (data: NetworkRequestData) => void;
}

export const SearchForm: React.FC<SearchFormProps> = ({ onSearch }) => {
  const { lastSearch, saveSearch, clearSearch } = useSessionState();
  const { toast } = useToast();
  
  const [formData, setFormData] = useState({
    street: '',
    houseNumber: '',
    zip: '',
    city: '',
  });

  const [errors, setErrors] = useState<ValidationErrors>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  // Load last search on mount
  useEffect(() => {
    if (lastSearch) {
      setFormData({
        street: lastSearch.address.street,
        houseNumber: lastSearch.address.house_number,
        zip: lastSearch.address.zip.toString(),
        city: lastSearch.address.city,
      });
    }
  }, [lastSearch]);

  const validateField = (field: keyof typeof formData, value: string) => {
    const tempData = { ...formData, [field]: value };
    const fieldErrors = validateSearchForm(tempData);
    
    setErrors(prev => ({
      ...prev,
      [field]: fieldErrors[field as keyof ValidationErrors]
    }));
  };

  const handleFieldChange = (field: keyof typeof formData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    validateField(field, value);
    setTouched(prev => ({ ...prev, [field]: true }));
  };

  const validateForm = (): boolean => {
    const formErrors = validateSearchForm(formData);
    setErrors(formErrors);
    
    setTouched({
      street: true,
      houseNumber: true,
      zip: true,
      city: true,
    });
    
    return Object.keys(formErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validateForm()) {
      const searchData: NetworkRequestData = {
        address: {
          street: formData.street,
          house_number: formData.houseNumber,
          zip: parseInt(formData.zip),
          city: formData.city,
          country_code: 'DE',
        },
      };

      saveSearch(searchData);
      onSearch(searchData);
      
      toast({
        title: "Suche gestartet",
        description: "Angebote werden von allen Anbietern abgerufen.",
      });
    }
  };

  return (
    <Card className="max-w-4xl mx-auto shadow-lg">
      <CardHeader className="text-center pb-4">
        <CardTitle className="text-2xl font-bold text-gray-900 flex items-center justify-center gap-2">
          <Search className="w-6 h-6 text-blue-600" />
          Internetanbieter finden
        </CardTitle>
        <p className="text-gray-600">
          Geben Sie Ihre Adresse ein. Anschlussart und Installation können Sie anschließend filtern.
        </p>
      </CardHeader>
      
      <CardContent className="p-6">
        <form onSubmit={handleSubmit} className="space-y-6" autoComplete="on">
          {/* Address Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 mb-3">
              <MapPin className="w-5 h-5 text-blue-600" />
              <h3 className="text-lg font-semibold text-gray-900">Ihre Adresse</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="md:col-span-2">
                <Label htmlFor="street" className="text-sm font-medium">Straße *</Label>
                <Input
                  id="street"
                  name="street"
                  type="text"
                  placeholder="z.B. Musterstraße"
                  value={formData.street}
                  onChange={(e) => handleFieldChange('street', e.target.value)}
                  className={touched.street && errors.street ? 'border-red-500' : ''}
                  autoComplete="address-line1"
                />
                {touched.street && errors.street && (
                  <p className="text-red-500 text-sm mt-1">{errors.street}</p>
                )}
              </div>

              <div>
                <Label htmlFor="houseNumber" className="text-sm font-medium">Nr. *</Label>
                <Input
                  id="houseNumber"
                  name="houseNumber"
                  type="text"
                  placeholder="5"
                  value={formData.houseNumber}
                  onChange={(e) => handleFieldChange('houseNumber', e.target.value)}
                  className={touched.houseNumber && errors.houseNumber ? 'border-red-500' : ''}
                  autoComplete="address-line2"
                />
                {touched.houseNumber && errors.houseNumber && (
                  <p className="text-red-500 text-sm mt-1">{errors.houseNumber}</p>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="zip" className="text-sm font-medium">PLZ *</Label>
                <Input
                  id="zip"
                  name="zip"
                  type="text"
                  placeholder="80333"
                  maxLength={5}
                  value={formData.zip}
                  onChange={(e) => handleFieldChange('zip', e.target.value.replace(/\D/g, ''))}
                  className={touched.zip && errors.zip ? 'border-red-500' : ''}
                  autoComplete="postal-code"
                />
                {touched.zip && errors.zip && (
                  <p className="text-red-500 text-sm mt-1">{errors.zip}</p>
                )}
              </div>

              <div>
                <Label htmlFor="city" className="text-sm font-medium">Stadt *</Label>
                <Input
                  id="city"
                  name="city"
                  type="text"
                  placeholder="München"
                  value={formData.city}
                  onChange={(e) => handleFieldChange('city', e.target.value)}
                  className={touched.city && errors.city ? 'border-red-500' : ''}
                  autoComplete="address-level2"
                />
                {touched.city && errors.city && (
                  <p className="text-red-500 text-sm mt-1">{errors.city}</p>
                )}
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="border-t pt-6 space-y-3">
            <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white text-lg py-6 font-semibold">
              <Search className="w-5 h-5 mr-2" />
              Angebote vergleichen
            </Button>
            
            {lastSearch && (
              <div className="flex gap-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    if (lastSearch) {
                      setFormData({
                        street: lastSearch.address.street,
                        houseNumber: lastSearch.address.house_number,
                        zip: lastSearch.address.zip.toString(),
                        city: lastSearch.address.city,
                      });
                      toast({
                        title: "Letzte Suche wiederhergestellt",
                        description: "Ihre letzten Suchkriterien wurden geladen.",
                      });
                    }
                  }}
                  className="flex-1"
                >
                  Letzte Suche wiederholen
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={clearSearch}
                  className="flex-1"
                >
                  Suchverlauf löschen
                </Button>
              </div>
            )}
          </div>
        </form>
      </CardContent>
    </Card>
  );
};
