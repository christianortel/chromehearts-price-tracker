import type { Observation, ProductBrowseSort } from "@/lib/types";

export type BrowseState = {
  query: string;
  categories: string[];
  sourceTypes: string[];
  marketSides: Array<Observation["market_side"]>;
  minConfidence: string;
  sort: ProductBrowseSort;
  offset: number;
};

export const DEFAULT_BROWSE_SORT: ProductBrowseSort = "updated_desc";
export const DEFAULT_BROWSE_CONFIDENCE = "0";
export const DEFAULT_BROWSE_STATE: BrowseState = {
  query: "",
  categories: [],
  sourceTypes: [],
  marketSides: [],
  minConfidence: DEFAULT_BROWSE_CONFIDENCE,
  sort: DEFAULT_BROWSE_SORT,
  offset: 0,
};

const validSorts = new Set<ProductBrowseSort>([
  "updated_desc",
  "premium_desc",
  "freshness_desc",
  "confidence_desc",
  "name_asc",
]);

const validConfidenceValues = new Set(["0", "0.6", "0.75", "0.85"]);
const validMarketSides = new Set<Observation["market_side"]>(["retail", "ask", "sold"]);

function uniqueValues(values: string[]) {
  return [...new Set(values.filter((value) => value.trim().length > 0))];
}

function firstValue(value: string | string[] | undefined) {
  return typeof value === "string" ? value : Array.isArray(value) ? value[0] : undefined;
}

function arrayValues(value: string | string[] | undefined) {
  if (typeof value === "string") {
    return [value];
  }
  return Array.isArray(value) ? value : [];
}

function parseOffset(value: string | undefined) {
  const numericValue = Number(value ?? "");
  return Number.isFinite(numericValue) && numericValue > 0 ? Math.floor(numericValue) : 0;
}

function parseSort(value: string | undefined): ProductBrowseSort {
  if (value && validSorts.has(value as ProductBrowseSort)) {
    return value as ProductBrowseSort;
  }
  return DEFAULT_BROWSE_SORT;
}

function parseConfidence(value: string | undefined) {
  if (value && validConfidenceValues.has(value)) {
    return value;
  }
  return DEFAULT_BROWSE_CONFIDENCE;
}

function parseMarketSides(values: string[]) {
  return uniqueValues(values).filter((value): value is Observation["market_side"] =>
    validMarketSides.has(value as Observation["market_side"]),
  );
}

export function buildBrowseStateFromRecord(
  params: Record<string, string | string[] | undefined>,
): BrowseState {
  return {
    ...DEFAULT_BROWSE_STATE,
    query: firstValue(params.q)?.trim() ?? "",
    categories: uniqueValues(arrayValues(params.categories)),
    sourceTypes: uniqueValues(arrayValues(params.source_types)),
    marketSides: parseMarketSides(arrayValues(params.market_sides)),
    minConfidence: parseConfidence(firstValue(params.min_confidence)),
    sort: parseSort(firstValue(params.sort)),
    offset: parseOffset(firstValue(params.offset)),
  };
}

export function buildBrowseStateFromSearchParams(searchParams: URLSearchParams): BrowseState {
  return {
    ...DEFAULT_BROWSE_STATE,
    query: searchParams.get("q")?.trim() ?? "",
    categories: uniqueValues(searchParams.getAll("categories")),
    sourceTypes: uniqueValues(searchParams.getAll("source_types")),
    marketSides: parseMarketSides(searchParams.getAll("market_sides")),
    minConfidence: parseConfidence(searchParams.get("min_confidence") ?? undefined),
    sort: parseSort(searchParams.get("sort") ?? undefined),
    offset: parseOffset(searchParams.get("offset") ?? undefined),
  };
}

export function buildBrowseQueryString(state: BrowseState) {
  const params = new URLSearchParams();
  if (state.query.trim()) {
    params.set("q", state.query.trim());
  }
  for (const category of state.categories) {
    params.append("categories", category);
  }
  for (const sourceType of state.sourceTypes) {
    params.append("source_types", sourceType);
  }
  for (const marketSide of state.marketSides) {
    params.append("market_sides", marketSide);
  }
  if (state.minConfidence !== DEFAULT_BROWSE_CONFIDENCE) {
    params.set("min_confidence", state.minConfidence);
  }
  if (state.sort !== DEFAULT_BROWSE_SORT) {
    params.set("sort", state.sort);
  }
  if (state.offset > 0) {
    params.set("offset", String(state.offset));
  }
  return params.toString();
}

export function buildBrowseHref(pathname: string, state: BrowseState) {
  const queryString = buildBrowseQueryString(state);
  return queryString ? `${pathname}?${queryString}` : pathname;
}
