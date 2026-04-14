export type MetricSnapshot = {
  id: number;
  product_id: number;
  snapshot_date: string;
  retail_low: string | null;
  retail_high: string | null;
  retail_best_known: string | null;
  ask_median: string | null;
  ask_low: string | null;
  ask_high: string | null;
  sold_median_30d: string | null;
  sold_median_90d: string | null;
  sample_size_asks: number;
  sample_size_solds: number;
  premium_vs_retail_pct: string | null;
  premium_vs_retail_abs: string | null;
  freshness_score: string | null;
  confidence_score: string | null;
  generated_at: string;
};

export type Observation = {
  id: number;
  product_id: number | null;
  raw_title: string;
  normalized_title: string;
  source_id: number;
  source_item_id: string;
  source_url: string;
  source_type_snapshot: string;
  market_side: "retail" | "ask" | "sold";
  seller_or_store: string | null;
  location_text: string | null;
  condition: string | null;
  size_text: string | null;
  currency: string;
  price_amount: string;
  shipping_amount: string | null;
  tax_included: boolean | null;
  observed_at: string;
  last_seen_at: string;
  status: string;
  proof_type: string | null;
  proof_asset_url: string | null;
  extraction_confidence: string;
  match_confidence: string;
  price_confidence: string;
  raw_payload_json: Record<string, unknown>;
};

export type ProductListItem = {
  id: number;
  canonical_name: string;
  slug: string;
  category: string;
  subcategory: string | null;
  material: string | null;
  updated_at: string;
  latest_metric: MetricSnapshot | null;
};

export type ProductBrowseSort =
  | "updated_desc"
  | "premium_desc"
  | "freshness_desc"
  | "confidence_desc"
  | "name_asc";

export type ProductBrowseFilters = {
  q?: string;
  categories?: string[];
  sourceTypes?: string[];
  marketSides?: Array<Observation["market_side"]>;
  minConfidence?: number | null;
  sort?: ProductBrowseSort;
  limit?: number;
  offset?: number;
};

export type ProductFacetCount = {
  key: string;
  label: string;
  count: number;
};

export type ProductBrowseFacets = {
  categories: ProductFacetCount[];
  source_types: ProductFacetCount[];
  market_sides: ProductFacetCount[];
};

export type ProductBrowseResult = {
  total: number;
  limit: number;
  offset: number;
  has_next_page: boolean;
  items: ProductListItem[];
  facets: ProductBrowseFacets;
};

export type ProductDetail = ProductListItem & {
  notes: string | null;
  created_at: string;
  observations: Observation[];
  aliases: string[];
};

export type Source = {
  id: number;
  name: string;
  source_type: string;
  base_url: string | null;
  crawl_method: string;
  enabled: boolean;
  policy_status: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type SourceHealth = {
  source_id: number;
  source_name: string;
  source_type: string;
  crawl_method: string;
  policy_status: string;
  enabled: boolean;
  last_status: string | null;
  last_finished_at: string | null;
  recent_error_count: number;
  success_rate: number | null;
};

export type ScrapeRun = {
  id: number;
  source_id: number;
  source_name: string | null;
  started_at: string;
  finished_at: string | null;
  status: string;
  discovered_count: number;
  parsed_count: number;
  inserted_count: number;
  error_count: number;
  notes: string | null;
};

export type ScrapeError = {
  id: number;
  scrape_run_id: number;
  source_id: number;
  source_name: string | null;
  item_reference: string | null;
  error_type: string;
  error_message: string;
  html_snapshot_path: string | null;
  screenshot_path: string | null;
  created_at: string;
};

export type ScrapeRunDetail = ScrapeRun & {
  errors: ScrapeError[];
};

export type AdminAssetPreview = {
  asset_path: string;
  content_type: string;
  kind: string;
  file_name: string;
  byte_size: number;
  truncated: boolean;
  text_content: string | null;
  base64_content: string | null;
};

export type AdminObservationMatchReview = {
  id: number;
  proposed_product_id: number | null;
  proposed_product_name: string | null;
  reviewer_decision: string;
  reviewer_notes: string | null;
  reviewed_at: string | null;
};

export type AdminObservationRetailReport = {
  id: number;
  store_name: string | null;
  city: string | null;
  country: string | null;
  receipt_submitted: boolean;
  moderator_status: string;
  moderator_notes: string | null;
  created_at: string;
  updated_at: string;
};

export type AdminObservationDetail = Observation & {
  source_name: string;
  product_name: string | null;
  variant_key: string | null;
  duplicate_group_key: string | null;
  first_seen_at: string;
  created_at: string;
  updated_at: string;
  top_candidates: MatchCandidate[];
  retail_report: AdminObservationRetailReport | null;
  match_reviews: AdminObservationMatchReview[];
};

export type DuplicateObservation = Observation & {
  source_name: string;
  product_name: string | null;
};

export type DuplicateObservationGroup = {
  duplicate_group_key: string;
  duplicate_count: number;
  latest_observed_at: string;
  suggested_keep_observation_id: number | null;
  suggested_keep_reason: string | null;
  observations: DuplicateObservation[];
};

export type Submission = {
  id: number;
  submission_type: string;
  item_name: string;
  price: string;
  currency: string;
  store: string | null;
  city: string | null;
  country: string | null;
  date_seen: string | null;
  notes: string | null;
  receipt_asset_url: string | null;
  status: string;
  created_at: string;
  top_candidates: MatchCandidate[];
};

export type SubmissionAssetUpload = {
  asset_path: string;
  content_type: string;
  file_name: string;
  byte_size: number;
};

export type UnmatchedObservation = Observation & {
  source_name: string;
  top_candidates: MatchCandidate[];
};

export type MatchCandidate = {
  product_id: number;
  product_name: string | null;
  score: number;
  reason: string;
};

export type ProductAlias = {
  id: number;
  product_id: number;
  alias_text: string;
  alias_type: string;
  source_name: string | null;
  created_at: string;
};
