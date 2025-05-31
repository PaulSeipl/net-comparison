
import React, { useState, useEffect, useRef } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { addressService, AddressSuggestion } from '@/services/addressService';
import { MapPin, Loader2 } from 'lucide-react';

interface AddressAutocompleteProps {
  onAddressSelect: (address: {
    street: string;
    houseNumber: string;
    zip: string;
    city: string;
  }) => void;
  initialValue?: string;
  error?: string;
}

export const AddressAutocomplete: React.FC<AddressAutocompleteProps> = ({
  onAddressSelect,
  initialValue = '',
  error
}) => {
  const [query, setQuery] = useState(initialValue);
  const [suggestions, setSuggestions] = useState<AddressSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const searchAddresses = async () => {
      if (query.length < 3) {
        setSuggestions([]);
        setShowSuggestions(false);
        return;
      }

      setLoading(true);
      try {
        const results = await addressService.searchAddresses(query);
        setSuggestions(results);
        setShowSuggestions(true);
        setSelectedIndex(-1);
      } catch (error) {
        console.error('Address search failed:', error);
        setSuggestions([]);
      } finally {
        setLoading(false);
      }
    };

    const timeoutId = setTimeout(searchAddresses, 300);
    return () => clearTimeout(timeoutId);
  }, [query]);

  const handleSelectSuggestion = (suggestion: AddressSuggestion) => {
    const address = {
      street: suggestion.street,
      houseNumber: suggestion.houseNumber || '',
      zip: suggestion.zip.toString(),
      city: suggestion.city
    };
    
    setQuery(suggestion.fullAddress);
    setShowSuggestions(false);
    onAddressSelect(address);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestions || suggestions.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev > 0 ? prev - 1 : suggestions.length - 1
        );
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
          handleSelectSuggestion(suggestions[selectedIndex]);
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        setSelectedIndex(-1);
        break;
    }
  };

  return (
    <div className="relative">
      <Label htmlFor="address">Adresse *</Label>
      <div className="relative">
        <Input
          ref={inputRef}
          id="address"
          name="address"
          type="text"
          placeholder="Straße, PLZ oder Ort eingeben..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
          className={error ? 'border-red-500 pr-10' : 'pr-10'}
          autoComplete="off"
        />
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
          ) : (
            <MapPin className="w-4 h-4 text-gray-400" />
          )}
        </div>
      </div>
      
      {error && <p className="text-red-500 text-sm mt-1">{error}</p>}

      {showSuggestions && suggestions.length > 0 && (
        <div
          ref={suggestionsRef}
          className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-auto"
        >
          {suggestions.map((suggestion, index) => (
            <div
              key={`${suggestion.zip}-${suggestion.city}-${index}`}
              className={`px-4 py-2 cursor-pointer hover:bg-gray-50 flex items-center space-x-2 ${
                index === selectedIndex ? 'bg-blue-50 border-l-2 border-blue-500' : ''
              }`}
              onClick={() => handleSelectSuggestion(suggestion)}
            >
              <MapPin className="w-4 h-4 text-gray-400 flex-shrink-0" />
              <span className="text-sm text-gray-900">{suggestion.fullAddress}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
