import type {
  AdminAssetPreview,
  AdminObservationDetail,
  DuplicateObservationGroup,
  ProductDetail,
  ProductListItem,
  ScrapeRun,
  ScrapeRunDetail,
  Source,
  SourceHealth,
  SubmissionAssetUpload,
  Submission,
  UnmatchedObservation,
} from "@/lib/types";

const baseMetric = {
  id: 1,
  product_id: 1,
  snapshot_date: "2026-04-13",
  retail_low: "425.00",
  retail_high: "465.00",
  retail_best_known: "425.00",
  ask_median: "795.00",
  ask_low: "740.00",
  ask_high: "895.00",
  sold_median_30d: null,
  sold_median_90d: null,
  sample_size_asks: 14,
  sample_size_solds: 0,
  premium_vs_retail_pct: "87.0588",
  premium_vs_retail_abs: "370.00",
  freshness_score: "0.944",
  confidence_score: "0.832",
  generated_at: "2026-04-13T00:00:00Z",
};

export const mockProducts: ProductListItem[] = [
  {
    id: 1,
    canonical_name: "Chrome Hearts Cross Patch Trucker Hat Black",
    slug: "chrome-hearts-cross-patch-trucker-hat-black",
    category: "trucker_hat",
    subcategory: "hat",
    material: "cotton/poly mesh",
    updated_at: "2026-04-13T00:00:00Z",
    latest_metric: baseMetric,
  },
  {
    id: 2,
    canonical_name: "Chrome Hearts Forever Ring",
    slug: "chrome-hearts-forever-ring",
    category: "ring",
    subcategory: "silver ring",
    material: "sterling silver",
    updated_at: "2026-04-12T00:00:00Z",
    latest_metric: {
      ...baseMetric,
      id: 2,
      product_id: 2,
      retail_best_known: "495.00",
      ask_median: "890.00",
      premium_vs_retail_abs: "395.00",
      premium_vs_retail_pct: "79.7979",
    },
  },
  {
    id: 3,
    canonical_name: "Chrome Hearts Cross Patch Zip Up Hoodie Black",
    slug: "chrome-hearts-cross-patch-zip-up-hoodie-black",
    category: "zip_up",
    subcategory: "zip hoodie",
    material: "cotton fleece",
    updated_at: "2026-04-11T00:00:00Z",
    latest_metric: {
      ...baseMetric,
      id: 3,
      product_id: 3,
      retail_best_known: "885.00",
      ask_median: "1495.00",
      premium_vs_retail_abs: "610.00",
      premium_vs_retail_pct: "68.9266",
    },
  },
];

export const mockProductBrowseSignals: Record<
  number,
  {
    sourceTypes: string[];
    marketSides: Array<"retail" | "ask" | "sold">;
  }
> = {
  1: {
    sourceTypes: ["community_retail", "marketplace"],
    marketSides: ["retail", "ask"],
  },
  2: {
    sourceTypes: ["community_retail", "curated_reseller"],
    marketSides: ["retail", "ask"],
  },
  3: {
    sourceTypes: ["marketplace"],
    marketSides: ["ask"],
  },
};

export const mockProductDetail: ProductDetail = {
  ...mockProducts[0],
  notes: "Seeded sample detail used when the API is unavailable in local web-only mode.",
  created_at: "2026-04-01T00:00:00Z",
  aliases: ["CH Cross Patch Trucker Hat Black"],
  observations: [
    {
      id: 101,
      product_id: 1,
      raw_title: "Chrome Hearts Cross Patch Trucker Hat Black",
      normalized_title: "chrome hearts cross patch trucker hat black",
      source_id: 1,
      source_item_id: "seed-retail-1",
      source_url: "seed://retail/1",
      source_type_snapshot: "community_retail",
      market_side: "retail",
      seller_or_store: "Chrome Hearts Miami",
      location_text: "Miami, US",
      condition: null,
      size_text: null,
      currency: "USD",
      price_amount: "425.00",
      shipping_amount: null,
      tax_included: false,
      observed_at: "2026-04-05T00:00:00Z",
      last_seen_at: "2026-04-05T00:00:00Z",
      status: "active",
      proof_type: "receipt",
      proof_asset_url: null,
      extraction_confidence: "0.990",
      match_confidence: "0.980",
      price_confidence: "0.980",
      raw_payload_json: {},
    },
    {
      id: 102,
      product_id: 1,
      raw_title: "Chrome Hearts Cross Patch Trucker Hat Black",
      normalized_title: "chrome hearts cross patch trucker hat black",
      source_id: 2,
      source_item_id: "seed-ask-1",
      source_url: "seed://ask/1",
      source_type_snapshot: "marketplace",
      market_side: "ask",
      seller_or_store: "Sample eBay Seller",
      location_text: "US",
      condition: "Pre-Owned",
      size_text: null,
      currency: "USD",
      price_amount: "795.00",
      shipping_amount: "18.00",
      tax_included: null,
      observed_at: "2026-04-11T00:00:00Z",
      last_seen_at: "2026-04-11T00:00:00Z",
      status: "active",
      proof_type: "listing",
      proof_asset_url: null,
      extraction_confidence: "0.820",
      match_confidence: "0.970",
      price_confidence: "0.620",
      raw_payload_json: {},
    },
  ],
};

export const mockSources: Source[] = [
  {
    id: 1,
    name: "ebay",
    source_type: "marketplace",
    base_url: "https://www.ebay.com",
    crawl_method: "static_html",
    enabled: true,
    policy_status: "fixture_validated",
    notes: "Marketplace asks.",
    created_at: "2026-04-01T00:00:00Z",
    updated_at: "2026-04-13T00:00:00Z",
  },
  {
    id: 2,
    name: "rinkan",
    source_type: "curated_reseller",
    base_url: "https://rinkan-online.com",
    crawl_method: "static_html",
    enabled: true,
    policy_status: "fixture_validated",
    notes: "Curated reseller asks.",
    created_at: "2026-04-01T00:00:00Z",
    updated_at: "2026-04-13T00:00:00Z",
  },
  {
    id: 3,
    name: "reddit",
    source_type: "community_retail",
    base_url: "https://www.reddit.com",
    crawl_method: "manual_entry",
    enabled: false,
    policy_status: "stubbed",
    notes: "Community retail adapter intentionally stubbed pending compliant access review.",
    created_at: "2026-04-01T00:00:00Z",
    updated_at: "2026-04-13T00:00:00Z",
  },
];

export const mockSourceHealth: SourceHealth[] = [
  {
    source_id: 1,
    source_name: "ebay",
    source_type: "marketplace",
    crawl_method: "static_html",
    policy_status: "fixture_validated",
    enabled: true,
    last_status: "success",
    last_finished_at: "2026-04-13T02:15:00Z",
    recent_error_count: 0,
    success_rate: 1,
  },
  {
    source_id: 2,
    source_name: "rinkan",
    source_type: "curated_reseller",
    crawl_method: "static_html",
    policy_status: "fixture_validated",
    enabled: true,
    last_status: "success",
    last_finished_at: "2026-04-13T01:40:00Z",
    recent_error_count: 0,
    success_rate: 0.9,
  },
  {
    source_id: 3,
    source_name: "reddit",
    source_type: "community_retail",
    crawl_method: "manual_entry",
    policy_status: "stubbed",
    enabled: false,
    last_status: "stubbed",
    last_finished_at: "2026-04-13T01:38:00Z",
    recent_error_count: 1,
    success_rate: 0,
  },
];

export const mockScrapeRuns: ScrapeRun[] = [
  {
    id: 1201,
    source_id: 1,
    source_name: "ebay",
    started_at: "2026-04-13T02:12:00Z",
    finished_at: "2026-04-13T02:15:00Z",
    status: "success",
    discovered_count: 24,
    parsed_count: 24,
    inserted_count: 24,
    error_count: 0,
    notes: "query=chrome hearts; discovered=24; inserted=24",
  },
  {
    id: 1200,
    source_id: 3,
    source_name: "reddit",
    started_at: "2026-04-13T01:37:00Z",
    finished_at: "2026-04-13T01:38:00Z",
    status: "stubbed",
    discovered_count: 0,
    parsed_count: 0,
    inserted_count: 0,
    error_count: 1,
    notes: "query=chrome hearts; adapter not implemented",
  },
];

export const mockScrapeRunDetails: Record<string, ScrapeRunDetail> = {
  "1200": {
    ...mockScrapeRuns[1],
    errors: [
      {
        id: 8001,
        scrape_run_id: 1200,
        source_id: 3,
        source_name: "reddit",
        item_reference: null,
        error_type: "not_implemented",
        error_message: "Reddit adapter is intentionally disabled pending compliant access approval.",
        html_snapshot_path: "scrape-errors/ebay/run-4001-snapshot.html",
        screenshot_path: null,
        created_at: "2026-04-13T01:38:00Z",
      },
    ],
  },
  "1201": {
    ...mockScrapeRuns[0],
    errors: [],
  },
};

export const mockAssetPreviews: Record<string, AdminAssetPreview> = {
  "scrape-errors/ebay/run-4001-snapshot.html": {
    asset_path: "scrape-errors/ebay/run-4001-snapshot.html",
    content_type: "text/html",
    kind: "text",
    file_name: "run-4001-snapshot.html",
    byte_size: 128,
    truncated: false,
    text_content: "<html><body><li class=\"s-item\"><span class=\"s-item__price\">not-a-price</span></li></body></html>",
    base64_content: null,
  },
  "submission-proofs/2026/04/mock-proof.jpg": {
    asset_path: "submission-proofs/2026/04/mock-proof.jpg",
    content_type: "image/jpeg",
    kind: "image",
    file_name: "mock-proof.jpg",
    byte_size: 128,
    truncated: false,
    text_content: null,
    base64_content: "/9j/4AAQSkZJRgABAQAAAQABAAD/",
  },
};

export const mockSubmissionAssetUpload: SubmissionAssetUpload = {
  asset_path: "submission-proofs/2026/04/mock-proof.jpg",
  content_type: "image/jpeg",
  file_name: "mock-proof.jpg",
  byte_size: 128,
};

export const mockDuplicateGroups: DuplicateObservationGroup[] = [
  {
    duplicate_group_key: "seed-duplicate-group-1",
    duplicate_count: 2,
    latest_observed_at: "2026-04-13T02:15:00Z",
    suggested_keep_observation_id: 3001,
    suggested_keep_reason: "listing-backed evidence, already matched to a canonical product, marketplace listing",
    observations: [
      {
        ...mockProductDetail.observations[1],
        id: 3001,
        source_item_id: "dup-1",
        source_url: "seed://duplicates/1",
        observed_at: "2026-04-13T02:15:00Z",
        last_seen_at: "2026-04-13T02:15:00Z",
        source_name: "ebay",
        product_name: "Chrome Hearts Cross Patch Trucker Hat Black",
      },
      {
        ...mockProductDetail.observations[1],
        id: 3002,
        source_item_id: "dup-2",
        source_url: "seed://duplicates/2",
        observed_at: "2026-04-13T02:12:00Z",
        last_seen_at: "2026-04-13T02:12:00Z",
        source_name: "ebay",
        product_name: "Chrome Hearts Cross Patch Trucker Hat Black",
      },
    ],
  },
];

export const mockUnmatched: UnmatchedObservation[] = [
  {
    ...mockProductDetail.observations[1],
    id: 501,
    product_id: null,
    source_name: "ebay",
    raw_title: "Chrome Hearts CH trucker cap cross patch black OS",
    normalized_title: "chrome hearts chrome hearts trucker hat cross patch black os",
    match_confidence: "0.610",
    top_candidates: [
      { product_id: 1, product_name: "Chrome Hearts Cross Patch Trucker Hat Black", score: 0.94, reason: "alias similarity, category hint" },
      { product_id: 3, product_name: "Chrome Hearts Cross Patch Zip Up Hoodie Black", score: 0.72, reason: "canonical similarity" },
    ],
  },
];

export const mockAliases = [
  {
    id: 1,
    product_id: 1,
    alias_text: "CH Cross Patch Trucker Hat Black",
    alias_type: "abbreviation",
    source_name: "seed",
    created_at: "2026-04-01T00:00:00Z",
  },
  {
    id: 2,
    product_id: 2,
    alias_text: "CH Forever Ring",
    alias_type: "abbreviation",
    source_name: "seed",
    created_at: "2026-04-01T00:00:00Z",
  },
];

export const mockSubmissions: Submission[] = [
  {
    id: 900,
    submission_type: "retail_report",
    item_name: "Chrome Hearts Forever Ring",
    price: "495.00",
    currency: "USD",
    store: "Chrome Hearts NYC",
    city: "New York",
    country: "US",
    date_seen: "2026-03-01",
    notes: "Receipt-backed local sample.",
    receipt_asset_url: "submission-proofs/2026/04/mock-proof.jpg",
    status: "pending",
    created_at: "2026-04-10T00:00:00Z",
    top_candidates: [
      { product_id: 2, product_name: "Chrome Hearts Forever Ring", score: 0.98, reason: "canonical title similarity" },
      { product_id: 1, product_name: "Chrome Hearts Cross Patch Trucker Hat Black", score: 0.41, reason: "weak catalog overlap" },
    ],
  },
];

export const mockObservationDetails: Record<string, AdminObservationDetail> = {
  "501": {
    ...mockUnmatched[0],
    source_name: "ebay",
    product_name: null,
    variant_key: null,
    duplicate_group_key: "ebay-ch-trucker-425",
    first_seen_at: "2026-04-11T00:00:00Z",
    created_at: "2026-04-11T00:00:00Z",
    updated_at: "2026-04-13T00:00:00Z",
    retail_report: null,
    match_reviews: [
      {
        id: 7101,
        proposed_product_id: 1,
        proposed_product_name: "Chrome Hearts Cross Patch Trucker Hat Black",
        reviewer_decision: "needs_review",
        reviewer_notes: "Alias overlap looks strong, but title still abbreviates multiple tokens.",
        reviewed_at: "2026-04-13T00:30:00Z",
      },
    ],
  },
  "3001": {
    ...mockDuplicateGroups[0].observations[0],
    source_name: "ebay",
    product_name: "Chrome Hearts Cross Patch Trucker Hat Black",
    variant_key: null,
    duplicate_group_key: mockDuplicateGroups[0].duplicate_group_key,
    first_seen_at: "2026-04-13T02:15:00Z",
    created_at: "2026-04-13T02:15:00Z",
    updated_at: "2026-04-13T02:15:00Z",
    top_candidates: [
      { product_id: 1, product_name: "Chrome Hearts Cross Patch Trucker Hat Black", score: 0.97, reason: "canonical similarity, category hint" },
      { product_id: 3, product_name: "Chrome Hearts Cross Patch Zip Up Hoodie Black", score: 0.51, reason: "weak canonical overlap" },
    ],
    retail_report: null,
    match_reviews: [
      {
        id: 7102,
        proposed_product_id: 1,
        proposed_product_name: "Chrome Hearts Cross Patch Trucker Hat Black",
        reviewer_decision: "matched",
        reviewer_notes: "Matched during duplicate review triage.",
        reviewed_at: "2026-04-13T02:16:00Z",
      },
    ],
  },
};
