export type RetailerId =
  "walmart" | "target" | "homedepot" | "lowes" | "bestbuy";
export type Product = {
  id: string;
  name: string;
  brand: string;
  model_number: string;
  upc: string;
  gtin: string;
  image_url: string;
  provenance: "demo" | "live";
};
export type Retailer = {
  id: RetailerId;
  name: string;
  website: string;
  status: string;
  store_prices: boolean;
  inventory_quantity: boolean;
  live_verified: boolean;
};
export type Status = {
  mode: "demo" | "live";
  demo_zips: string[];
  zip_count: number;
  cache_seconds: number;
  retailers: Retailer[];
  monitoring: string;
};
export type Offer = {
  id: string;
  product: Product;
  retailer_id: RetailerId;
  retailer_name: string;
  store: {
    id: string;
    name: string;
    address: string;
    city: string;
    state: string;
    zip_code: string;
  };
  price: string | null;
  regular_price: string | null;
  discount: number | null;
  currency: string;
  inventory_status: string;
  inventory_quantity: number | null;
  observed_at: string;
  distance: number;
  product_url: string | null;
  confidence: number;
  match_reason: string;
  provenance: string;
  cached: boolean;
};
export type SearchResult = {
  query: string;
  location: { city: string; state: string; zip_code: string };
  radius: number;
  mode: string;
  offers: Offer[];
  providers: { retailer_id: string; status: string; message: string }[];
};
export type Observation = {
  id: number;
  price: number | null;
  regular_price: number | null;
  observed_at: string;
  retailer_id: RetailerId;
  store_id: string;
  store_name: string;
  zip_code: string;
  inventory_status: string;
  provenance: string;
};
export type Watch = {
  id: number;
  product: Product;
  target_price: number;
  zip_code: string;
  radius: number;
  retailers: RetailerId[];
  last_attempted_at: string | null;
  last_successful_at: string | null;
  check_status: string;
  provenance: string;
};
export type Alert = {
  id: number;
  message: string;
  created_at: string;
  read: boolean;
  provenance: string;
};
