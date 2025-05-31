
interface AddressSuggestion {
  street: string;
  houseNumber?: string;
  zip: number;
  city: string;
  fullAddress: string;
}

class AddressService {
  private baseUrl = 'https://api.zippopotam.us/de';

  async searchAddresses(query: string): Promise<AddressSuggestion[]> {
    if (query.length < 3) return [];

    try {
      // Extract ZIP code if present
      const zipMatch = query.match(/\b(\d{5})\b/);
      
      if (zipMatch) {
        const zip = zipMatch[1];
        const response = await fetch(`${this.baseUrl}/${zip}`);
        
        if (response.ok) {
          const data = await response.json();
          return data.places.map((place: any) => ({
            street: '',
            zip: parseInt(zip),
            city: place['place name'],
            fullAddress: `${zip} ${place['place name']}`
          }));
        }
      }

      // For demo purposes, return mock suggestions based on common German cities
      const mockSuggestions = this.getMockSuggestions(query);
      return mockSuggestions;
    } catch (error) {
      console.error('Address search error:', error);
      return this.getMockSuggestions(query);
    }
  }

  private getMockSuggestions(query: string): AddressSuggestion[] {
    const commonAddresses = [
      { street: 'Musterstraße', zip: 80333, city: 'München' },
      { street: 'Hauptstraße', zip: 10115, city: 'Berlin' },
      { street: 'Bahnhofstraße', zip: 20095, city: 'Hamburg' },
      { street: 'Königsallee', zip: 40212, city: 'Düsseldorf' },
      { street: 'Marienplatz', zip: 80331, city: 'München' },
      { street: 'Alexanderplatz', zip: 10178, city: 'Berlin' },
      { street: 'Reeperbahn', zip: 20359, city: 'Hamburg' },
      { street: 'Zeil', zip: 60313, city: 'Frankfurt am Main' },
    ];

    return commonAddresses
      .filter(addr => 
        addr.street.toLowerCase().includes(query.toLowerCase()) ||
        addr.city.toLowerCase().includes(query.toLowerCase()) ||
        addr.zip.toString().includes(query)
      )
      .map(addr => ({
        street: addr.street,
        zip: addr.zip,
        city: addr.city,
        fullAddress: `${addr.street}, ${addr.zip} ${addr.city}`
      }))
      .slice(0, 5);
  }

  validateGermanZip(zip: string): boolean {
    return /^\d{5}$/.test(zip);
  }

  validateHouseNumber(houseNumber: string): boolean {
    return /^[1-9]\d*[a-zA-Z]?(-[1-9]\d*[a-zA-Z]?)?$/.test(houseNumber);
  }
}

export const addressService = new AddressService();
export type { AddressSuggestion };
