
export interface Address {
  street: string;
  house_number: string;
  zip: number;
  city: string;
  country_code: string;
}

export interface NetworkRequestData {
  address: Address;
}

export interface PriceDetails {
  monthly_cost: number;
  monthly_cost_with_discount?: number | null;
  monthly_savings?: number | null;
  monthly_cost_after_promotion?: number | null;
  total_savings?: number | null;
  setup_fee?: number | null;
  discount_percentage?: number | null;
}

export type ConnectionType = "DSL" | "Cable" | "Fiber" | "Mobile";

export type Provider = "WebWunder" | "ByteMe" | "Ping Perfect" | "VerbynDich" | "Servus Speed";

export interface NormalizedOffer {
  provider: Provider;
  offer_id: string;
  name: string;
  speed: number;
  connection_type: ConnectionType;
  price_details: PriceDetails;
  contract_duration: number;
  installation_service: boolean | null;
  max_age?: number | null;
  tv_service?: string | null;
  promotion_length?: number | null;
  data_limit?: number | null;
  fetched_at: string;
}

export interface FilterState {
  priceRange: [number, number];
  speedRequirement: number;
  contractDuration: number[];
  connectionTypes: ConnectionType[];
  providers: string[];
  installationService: boolean | null;
}

export type SortOption = "best_value" | "lowest_price" | "fastest_speed" | "shortest_contract";
