import {
  mockAssetPreviews,
  mockDuplicateGroups,
  mockAliases,
  mockObservationDetails,
  mockProductDetail,
  mockProductBrowseSignals,
  mockProducts,
  mockScrapeRunDetails,
  mockScrapeRuns,
  mockSubmissionAssetUpload,
  mockSourceHealth,
  mockSources,
  mockSubmissions,
  mockUnmatched,
} from "@/lib/mock-data";
import type {
  AdminAssetPreview,
  AdminObservationDetail,
  ProductBrowseFilters,
  ProductBrowseResult,
  ProductBrowseSort,
  ProductAlias,
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

const ENABLE_MOCK = process.env.NEXT_PUBLIC_ENABLE_MOCK_DATA === "true";

function getApiBaseUrl() {
  if (typeof window === "undefined") {
    return process.env.API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
  }
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
}

function buildProductBrowseQuery(filters?: ProductBrowseFilters) {
  const params = new URLSearchParams();
  if (!filters) {
    return params;
  }
  if (filters.q?.trim()) {
    params.set("q", filters.q.trim());
  }
  for (const category of filters.categories ?? []) {
    params.append("categories", category);
  }
  for (const sourceType of filters.sourceTypes ?? []) {
    params.append("source_types", sourceType);
  }
  for (const marketSide of filters.marketSides ?? []) {
    params.append("market_sides", marketSide);
  }
  if (filters.minConfidence !== undefined && filters.minConfidence !== null) {
    params.set("min_confidence", String(filters.minConfidence));
  }
  if (filters.sort) {
    params.set("sort", filters.sort);
  }
  if (filters.limit !== undefined) {
    params.set("limit", String(filters.limit));
  }
  if (filters.offset !== undefined) {
    params.set("offset", String(filters.offset));
  }
  return params;
}

function getMockAliasesForProduct(productId: number) {
  return mockAliases
    .filter((alias) => alias.product_id === productId)
    .map((alias) => alias.alias_text.toLowerCase());
}

function getMockMetricScore(product: ProductListItem, sort: ProductBrowseSort) {
  if (!product.latest_metric) {
    return -1;
  }
  if (sort === "premium_desc") {
    return Number(product.latest_metric.premium_vs_retail_pct ?? -1);
  }
  if (sort === "freshness_desc") {
    return Number(product.latest_metric.freshness_score ?? -1);
  }
  if (sort === "confidence_desc") {
    return Number(product.latest_metric.confidence_score ?? -1);
  }
  return -1;
}

function getMockSourceTypes(product: ProductListItem) {
  return mockProductBrowseSignals[product.id]?.sourceTypes ?? [];
}

function getMockMarketSides(product: ProductListItem) {
  return mockProductBrowseSignals[product.id]?.marketSides ?? [];
}

function countFacetValues(values: string[]) {
  return values.reduce<Record<string, number>>((counts, value) => {
    counts[value] = (counts[value] ?? 0) + 1;
    return counts;
  }, {});
}

function buildFacetCounts(
  options: Array<{ value: string; label: string }>,
  counts: Record<string, number>,
) {
  return options
    .map((option) => ({
      key: option.value,
      label: option.label,
      count: counts[option.value] ?? 0,
    }))
    .filter((option) => option.count > 0);
}

function getMockProducts(filters?: ProductBrowseFilters): ProductListItem[] {
  const normalizedQuery = filters?.q?.trim().toLowerCase();
  let items = [...mockProducts];

  if (normalizedQuery) {
    items = items.filter((product) => {
      const aliases = getMockAliasesForProduct(product.id);
      return [product.canonical_name, product.slug, ...aliases].some((value) => value.toLowerCase().includes(normalizedQuery));
    });
  }

  if (filters?.categories?.length) {
    items = items.filter((product) => filters.categories!.includes(product.category));
  }

  if (filters?.sourceTypes?.length) {
    items = items.filter((product) => {
      const sourceTypes = mockProductBrowseSignals[product.id]?.sourceTypes ?? [];
      return filters.sourceTypes!.some((sourceType) => sourceTypes.includes(sourceType));
    });
  }

  if (filters?.marketSides?.length) {
    items = items.filter((product) => {
      const marketSides = mockProductBrowseSignals[product.id]?.marketSides ?? [];
      return filters.marketSides!.some((marketSide) => marketSides.includes(marketSide));
    });
  }

  if (filters?.minConfidence !== undefined && filters.minConfidence !== null) {
    const minConfidence = filters.minConfidence;
    items = items.filter((product) => {
      const confidence = product.latest_metric?.confidence_score;
      return confidence !== null && confidence !== undefined && Number(confidence) >= minConfidence;
    });
  }

  const sort = filters?.sort ?? "updated_desc";
  items.sort((left, right) => {
    if (sort === "name_asc") {
      return left.canonical_name.localeCompare(right.canonical_name);
    }
    if (sort === "updated_desc") {
      return right.updated_at.localeCompare(left.updated_at) || left.canonical_name.localeCompare(right.canonical_name);
    }
    const rightScore = getMockMetricScore(right, sort);
    const leftScore = getMockMetricScore(left, sort);
    if (rightScore !== leftScore) {
      return rightScore - leftScore;
    }
    return right.updated_at.localeCompare(left.updated_at) || left.canonical_name.localeCompare(right.canonical_name);
  });

  const offset = filters?.offset ?? 0;
  const limit = filters?.limit ?? items.length;
  return items.slice(offset, offset + limit);
}

function getMockBrowseResult(filters?: ProductBrowseFilters): ProductBrowseResult {
  const limit = filters?.limit ?? 12;
  const offset = filters?.offset ?? 0;
  const currentProducts = getMockProducts({ ...filters, limit, offset });
  const totalProducts = getMockProducts({ ...filters, limit: mockProducts.length, offset: 0 });

  const categoryBaseProducts = getMockProducts({
    ...filters,
    categories: [],
    limit: mockProducts.length,
    offset: 0,
  });
  const sourceTypeBaseProducts = getMockProducts({
    ...filters,
    sourceTypes: [],
    limit: mockProducts.length,
    offset: 0,
  });
  const marketSideBaseProducts = getMockProducts({
    ...filters,
    marketSides: [],
    limit: mockProducts.length,
    offset: 0,
  });

  const categoryCounts = countFacetValues(categoryBaseProducts.map((product) => product.category));
  const sourceTypeCounts = countFacetValues(
    sourceTypeBaseProducts.flatMap((product) => getMockSourceTypes(product)),
  );
  const marketSideCounts = countFacetValues(
    marketSideBaseProducts.flatMap((product) => getMockMarketSides(product)),
  );

  return {
    total: totalProducts.length,
    limit,
    offset,
    has_next_page: offset + currentProducts.length < totalProducts.length,
    items: currentProducts,
    facets: {
      categories: buildFacetCounts(
        [
          { value: "trucker_hat", label: "trucker hats" },
          { value: "hoodie", label: "hoodies" },
          { value: "zip_up", label: "zip-ups" },
          { value: "long_sleeve", label: "long sleeves" },
          { value: "ring", label: "rings" },
          { value: "bracelet", label: "bracelets" },
        ],
        categoryCounts,
      ),
      source_types: buildFacetCounts(
        [
          { value: "community_retail", label: "community retail" },
          { value: "curated_reseller", label: "curated resellers" },
          { value: "marketplace", label: "marketplaces" },
          { value: "sold_comp", label: "sold comps" },
          { value: "import", label: "imports" },
        ],
        sourceTypeCounts,
      ),
      market_sides: buildFacetCounts(
        [
          { value: "retail", label: "retail evidence" },
          { value: "ask", label: "ask evidence" },
          { value: "sold", label: "sold evidence" },
        ],
        marketSideCounts,
      ),
    },
  };
}

async function safeFetch<T>(path: string, init?: RequestInit, fallback?: T): Promise<T> {
  if (ENABLE_MOCK && fallback !== undefined) {
    return fallback;
  }
  try {
    const response = await fetch(`${getApiBaseUrl()}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
      cache: "no-store",
    });
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }
    return (await response.json()) as T;
  } catch (error) {
    if (fallback !== undefined) {
      return fallback;
    }
    throw error;
  }
}

export async function getProducts(filters?: ProductBrowseFilters): Promise<ProductListItem[]> {
  const query = buildProductBrowseQuery(filters).toString();
  const path = query ? `/products?${query}` : "/products";
  return safeFetch(path, undefined, getMockProducts(filters));
}

export async function getBrowseCatalog(filters?: ProductBrowseFilters): Promise<ProductBrowseResult> {
  const query = buildProductBrowseQuery(filters).toString();
  const path = query ? `/products/browse?${query}` : "/products/browse";
  return safeFetch(path, undefined, getMockBrowseResult(filters));
}

export async function getProduct(productId: string): Promise<ProductDetail> {
  return safeFetch(`/products/${productId}`, undefined, mockProductDetail);
}

export async function searchProducts(query: string): Promise<{ query: string; total: number; items: ProductListItem[] }> {
  const items = getMockProducts({ q: query, sort: "name_asc" });
  return safeFetch(`/search?q=${encodeURIComponent(query)}`, undefined, {
    query,
    total: items.length,
    items,
  });
}

export async function getSources(): Promise<Source[]> {
  return safeFetch("/sources", undefined, mockSources);
}

export async function getUnmatchedObservations(adminToken?: string): Promise<UnmatchedObservation[]> {
  return safeFetch(
    "/admin/unmatched",
    {
      headers: adminToken ? { "x-admin-token": adminToken } : undefined,
    },
    mockUnmatched,
  );
}

export async function getAdminSubmissions(adminToken?: string): Promise<Submission[]> {
  return safeFetch(
    "/admin/submissions",
    {
      headers: adminToken ? { "x-admin-token": adminToken } : undefined,
    },
    mockSubmissions,
  );
}

export async function getAdminProductSearch(query: string, adminToken?: string): Promise<ProductListItem[]> {
  const normalizedQuery = query.toLowerCase();
  return safeFetch(
    `/admin/products/search?q=${encodeURIComponent(query)}`,
    {
      headers: adminToken ? { "x-admin-token": adminToken } : undefined,
    },
    mockProducts.filter((product) => {
      const aliases = mockAliases
        .filter((alias) => alias.product_id === product.id)
        .map((alias) => alias.alias_text);
      return [product.canonical_name, product.slug, ...aliases].some((value) => value.toLowerCase().includes(normalizedQuery));
    }),
  );
}

export async function getAdminSourceHealth(adminToken?: string): Promise<SourceHealth[]> {
  return safeFetch(
    "/admin/source-health",
    {
      headers: adminToken ? { "x-admin-token": adminToken } : undefined,
    },
    mockSourceHealth,
  );
}

export async function getAdminScrapeRuns(adminToken?: string): Promise<ScrapeRun[]> {
  return safeFetch(
    "/admin/scrape-runs",
    {
      headers: adminToken ? { "x-admin-token": adminToken } : undefined,
    },
    mockScrapeRuns,
  );
}

export async function getAdminDuplicateGroups(adminToken?: string): Promise<DuplicateObservationGroup[]> {
  return safeFetch(
    "/admin/duplicates",
    {
      headers: adminToken ? { "x-admin-token": adminToken } : undefined,
    },
    mockDuplicateGroups,
  );
}

export async function getAdminAssetPreview(assetPath: string, adminToken?: string): Promise<AdminAssetPreview> {
  return safeFetch(
    `/admin/assets/preview?path=${encodeURIComponent(assetPath)}`,
    {
      headers: adminToken ? { "x-admin-token": adminToken } : undefined,
    },
    mockAssetPreviews[assetPath] ?? Object.values(mockAssetPreviews)[0],
  );
}

export async function getAdminObservationDetail(observationId: string, adminToken?: string): Promise<AdminObservationDetail> {
  return safeFetch(
    `/admin/observations/${observationId}`,
    {
      headers: adminToken ? { "x-admin-token": adminToken } : undefined,
    },
    mockObservationDetails[observationId] ?? mockObservationDetails["501"],
  );
}

export async function getAdminScrapeRunDetail(runId: string, adminToken?: string): Promise<ScrapeRunDetail> {
  return safeFetch(
    `/admin/scrape-runs/${runId}`,
    {
      headers: adminToken ? { "x-admin-token": adminToken } : undefined,
    },
    mockScrapeRunDetails[runId] ?? mockScrapeRunDetails["1200"],
  );
}

export async function submitRetailReport(payload: Record<string, unknown>): Promise<Submission> {
  return safeFetch(
    "/submissions",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    mockSubmissions[0],
  );
}

export async function uploadSubmissionProof(file: File): Promise<SubmissionAssetUpload> {
  if (ENABLE_MOCK) {
    return mockSubmissionAssetUpload;
  }
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${getApiBaseUrl()}/submission-assets/upload`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) {
    throw new Error(`Upload failed with status ${response.status}`);
  }
  return (await response.json()) as SubmissionAssetUpload;
}

export async function getProductAliases(productId: number, adminToken?: string): Promise<ProductAlias[]> {
  return safeFetch(
    `/admin/products/${productId}/aliases`,
    {
      headers: adminToken ? { "x-admin-token": adminToken } : undefined,
    },
    mockAliases.filter((alias) => alias.product_id === productId),
  );
}
