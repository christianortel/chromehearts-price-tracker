"use client";

import { useQuery } from "@tanstack/react-query";
import { useDeferredValue, useEffect, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

import { ProductGrid } from "@/components/product-grid";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getBrowseCatalog } from "@/lib/api";
import {
  buildBrowseHref,
  buildBrowseQueryString,
  buildBrowseStateFromSearchParams,
  DEFAULT_BROWSE_STATE,
  type BrowseState,
} from "@/lib/browse-state";
import type { ProductBrowseSort } from "@/lib/types";

const categoryOptions = [
  { value: "trucker_hat", label: "trucker hats" },
  { value: "hoodie", label: "hoodies" },
  { value: "zip_up", label: "zip-ups" },
  { value: "long_sleeve", label: "long sleeves" },
  { value: "ring", label: "rings" },
  { value: "bracelet", label: "bracelets" },
];

const sourceTypeOptions = [
  { value: "community_retail", label: "community retail" },
  { value: "curated_reseller", label: "curated resellers" },
  { value: "marketplace", label: "marketplaces" },
  { value: "sold_comp", label: "sold comps" },
  { value: "import", label: "imports" },
];

const marketSideOptions = [
  { value: "retail", label: "retail evidence" },
  { value: "ask", label: "ask evidence" },
  { value: "sold", label: "sold evidence" },
];

const confidenceOptions = [
  { value: "0", label: "Any confidence" },
  { value: "0.6", label: "0.60+" },
  { value: "0.75", label: "0.75+" },
  { value: "0.85", label: "0.85+" },
];

const sortOptions: Array<{ value: ProductBrowseSort; label: string }> = [
  { value: "updated_desc", label: "Recently updated" },
  { value: "premium_desc", label: "Highest premium" },
  { value: "freshness_desc", label: "Freshest data" },
  { value: "confidence_desc", label: "Highest confidence" },
  { value: "name_asc", label: "Name" },
];

const quickViewPresets: Array<{ label: string; description: string; state: BrowseState }> = [
  {
    label: "Recent retail",
    description: "Recent community-backed retail sightings.",
    state: {
      ...DEFAULT_BROWSE_STATE,
      sourceTypes: ["community_retail"],
      marketSides: ["retail"],
    },
  },
  {
    label: "Curated asks",
    description: "Dealer asks with stronger asking-price trust.",
    state: {
      ...DEFAULT_BROWSE_STATE,
      sourceTypes: ["curated_reseller"],
      marketSides: ["ask"],
      sort: "confidence_desc",
    },
  },
  {
    label: "Marketplace asks",
    description: "Noisier marketplace asks sorted by premium.",
    state: {
      ...DEFAULT_BROWSE_STATE,
      sourceTypes: ["marketplace"],
      marketSides: ["ask"],
      sort: "premium_desc",
    },
  },
  {
    label: "High premium",
    description: "Products currently showing the largest premium vs retail.",
    state: {
      ...DEFAULT_BROWSE_STATE,
      sort: "premium_desc",
    },
  },
];

function toggleValue(values: string[], value: string) {
  return values.includes(value) ? values.filter((entry) => entry !== value) : [...values, value];
}

function getFacetCount(items: Array<{ key: string; count: number }>, key: string) {
  return items.find((item) => item.key === key)?.count ?? 0;
}

export function BrowseExplorer({ initialState }: { initialState: BrowseState }) {
  const pageSize = 12;
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [query, setQuery] = useState(initialState.query);
  const [categories, setCategories] = useState<string[]>(initialState.categories);
  const [sourceTypes, setSourceTypes] = useState<string[]>(initialState.sourceTypes);
  const [marketSides, setMarketSides] = useState<string[]>(initialState.marketSides);
  const [minConfidence, setMinConfidence] = useState(initialState.minConfidence);
  const [sort, setSort] = useState<ProductBrowseSort>(initialState.sort);
  const [offset, setOffset] = useState(initialState.offset);
  const [shareStatus, setShareStatus] = useState<"idle" | "copied" | "failed">("idle");
  const deferredQuery = useDeferredValue(query);
  const currentBrowseState: BrowseState = {
    query,
    categories,
    sourceTypes,
    marketSides: marketSides as Array<"retail" | "ask" | "sold">,
    minConfidence,
    sort,
    offset,
  };
  const currentBrowseQuery = buildBrowseQueryString(currentBrowseState);
  const shareHref = buildBrowseHref(pathname, currentBrowseState);

  function applyBrowseState(nextState: BrowseState) {
    setQuery(nextState.query);
    setCategories(nextState.categories);
    setSourceTypes(nextState.sourceTypes);
    setMarketSides(nextState.marketSides);
    setMinConfidence(nextState.minConfidence);
    setSort(nextState.sort);
    setOffset(nextState.offset);
  }

  useEffect(() => {
    const parsedState = buildBrowseStateFromSearchParams(searchParams);
    const parsedStateQuery = buildBrowseQueryString(parsedState);

    if (currentBrowseQuery === parsedStateQuery) {
      return;
    }

    setQuery(parsedState.query);
    setCategories(parsedState.categories);
    setSourceTypes(parsedState.sourceTypes);
    setMarketSides(parsedState.marketSides);
    setMinConfidence(parsedState.minConfidence);
    setSort(parsedState.sort);
    setOffset(parsedState.offset);
  }, [searchParams, currentBrowseQuery]);

  useEffect(() => {
    const currentQuery = searchParams.toString();

    if (currentBrowseQuery === currentQuery) {
      return;
    }

    router.replace(currentBrowseQuery ? `${pathname}?${currentBrowseQuery}` : pathname, { scroll: false });
  }, [router, pathname, searchParams, currentBrowseQuery]);

  useEffect(() => {
    setShareStatus("idle");
  }, [shareHref]);

  async function handleCopyLink() {
    try {
      if (typeof window === "undefined" || !navigator.clipboard) {
        throw new Error("Clipboard unavailable");
      }
      const shareUrl = new URL(shareHref, window.location.origin).toString();
      await navigator.clipboard.writeText(shareUrl);
      setShareStatus("copied");
    } catch {
      setShareStatus("failed");
    }
  }

  const productsQuery = useQuery({
    queryKey: ["browse-products", deferredQuery, categories, sourceTypes, marketSides, minConfidence, sort, offset],
    queryFn: () =>
      getBrowseCatalog({
        q: deferredQuery.trim() || undefined,
        categories,
        sourceTypes,
        marketSides: marketSides as Array<"retail" | "ask" | "sold">,
        minConfidence: minConfidence === "0" ? null : Number(minConfidence),
        sort,
        limit: pageSize,
        offset,
      }),
  });

  const browseResult = productsQuery.data;
  const items = browseResult?.items ?? [];
  const total = browseResult?.total ?? 0;
  const activeFilterCount =
    categories.length +
    sourceTypes.length +
    marketSides.length +
    (deferredQuery.trim() ? 1 : 0) +
    (minConfidence === "0" ? 0 : 1) +
    (sort === "updated_desc" ? 0 : 1);
  const startIndex = total === 0 ? 0 : offset + 1;
  const endIndex = total === 0 ? 0 : offset + items.length;

  return (
    <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
      <aside className="panel p-5">
        <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Filters</p>
        <div className="mt-5 space-y-4 text-sm text-parchment/75">
          <Input
            placeholder="Search product or alias"
            value={query}
            onChange={(event) => {
              setQuery(event.target.value);
              setOffset(0);
            }}
          />

          <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="text-parchment/45">Categories</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {categoryOptions.map((category) => (
                <button
                  key={category.value}
                  type="button"
                  onClick={() => {
                    setCategories((current) => toggleValue(current, category.value));
                    setOffset(0);
                  }}
                  className={`rounded-full border px-3 py-1 text-xs transition ${
                    categories.includes(category.value)
                      ? "border-bronze bg-bronze/15 text-parchment"
                      : "border-white/10 text-parchment/75 hover:border-white/20"
                  }`}
                >
                  {category.label} ({getFacetCount(browseResult?.facets.categories ?? [], category.value)})
                </button>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="text-parchment/45">Source classes</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {sourceTypeOptions.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => {
                    setSourceTypes((current) => toggleValue(current, option.value));
                    setOffset(0);
                  }}
                  className={`rounded-full border px-3 py-1 text-xs transition ${
                    sourceTypes.includes(option.value)
                      ? "border-bronze bg-bronze/15 text-parchment"
                      : "border-white/10 text-parchment/75 hover:border-white/20"
                  }`}
                >
                  {option.label} ({getFacetCount(browseResult?.facets.source_types ?? [], option.value)})
                </button>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="text-parchment/45">Evidence types</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {marketSideOptions.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => {
                    setMarketSides((current) => toggleValue(current, option.value));
                    setOffset(0);
                  }}
                  className={`rounded-full border px-3 py-1 text-xs transition ${
                    marketSides.includes(option.value)
                      ? "border-bronze bg-bronze/15 text-parchment"
                      : "border-white/10 text-parchment/75 hover:border-white/20"
                  }`}
                >
                  {option.label} ({getFacetCount(browseResult?.facets.market_sides ?? [], option.value)})
                </button>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="text-parchment/45">Metric confidence</p>
            <select
              value={minConfidence}
              onChange={(event) => {
                setMinConfidence(event.target.value);
                setOffset(0);
              }}
              className="mt-3 w-full rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-sm text-parchment outline-none"
            >
              {confidenceOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="text-parchment/45">Sort</p>
            <select
              value={sort}
              onChange={(event) => {
                setSort(event.target.value as ProductBrowseSort);
                setOffset(0);
              }}
              className="mt-3 w-full rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-sm text-parchment outline-none"
            >
              {sortOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="text-parchment/45">Confidence posture</p>
            <p className="mt-2 text-xs text-parchment/60">
              Retail, ask, and sold evidence stay separate. Filters narrow the evidence surface without inventing one blended market price.
            </p>
          </div>

          <button
            type="button"
            onClick={() => applyBrowseState(DEFAULT_BROWSE_STATE)}
            className="w-full rounded-xl border border-white/10 px-4 py-2 text-left text-sm text-parchment/75 transition hover:border-white/20 hover:text-parchment"
          >
            Reset filters
          </button>
        </div>
      </aside>

      <section className="space-y-4">
        <div className="panel p-5">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Catalog discovery</p>
              <h2 className="mt-2 text-2xl font-semibold text-parchment">Browse collector-facing product intelligence</h2>
              <p className="mt-2 max-w-3xl text-sm text-parchment/65">
                Filter by category, evidence source class, market side, and confidence without blurring retail, ask, and sold observations together.
              </p>
            </div>
            <div className="flex flex-col gap-3">
              <div className="rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-right">
                <p className="text-xs uppercase tracking-[0.25em] text-parchment/45">Matching products</p>
                <p className="mt-2 text-2xl font-semibold text-parchment">{total}</p>
                <p className="mt-1 text-xs text-parchment/55">{activeFilterCount} active filters</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-black/20 px-4 py-3">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="text-xs uppercase tracking-[0.25em] text-parchment/45">Share this view</p>
                    <p className="mt-2 max-w-sm text-xs text-parchment/60">
                      Copy the current filter state or jump into one of the curated quick views below.
                    </p>
                  </div>
                  <Button type="button" onClick={handleCopyLink} className="rounded-xl px-4 py-2">
                    Copy share link
                  </Button>
                </div>
                <p className="mt-3 truncate rounded-xl border border-white/10 bg-black/30 px-3 py-2 font-mono text-[11px] text-parchment/60">
                  {shareHref}
                </p>
                <p className="mt-2 text-xs text-parchment/55">
                  {shareStatus === "copied"
                    ? "Link copied for sharing."
                    : shareStatus === "failed"
                      ? "Clipboard access is unavailable in this environment, but the URL still reflects the current view."
                      : "The URL updates automatically as filters change."}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="panel p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Quick views</p>
          <p className="mt-2 text-sm text-parchment/60">
            Curated browse presets for the most common collector workflows.
          </p>
          <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            {quickViewPresets.map((preset) => (
              <button
                key={preset.label}
                type="button"
                onClick={() => applyBrowseState(preset.state)}
                className="rounded-2xl border border-white/10 bg-black/20 p-4 text-left transition hover:border-white/20"
              >
                <p className="text-sm font-semibold text-parchment">{preset.label}</p>
                <p className="mt-2 text-xs text-parchment/60">{preset.description}</p>
              </button>
            ))}
          </div>
        </div>

        {productsQuery.isLoading ? <div className="panel p-6 text-sm text-parchment/60">Loading filtered product catalog...</div> : null}

        {!productsQuery.isLoading && items.length === 0 ? (
          <div className="panel p-6 text-sm text-parchment/60">
            No products matched the current filters. Try widening the category, source, or confidence posture.
          </div>
        ) : null}

        {!productsQuery.isLoading && items.length > 0 ? (
          <div className="flex flex-wrap items-center justify-between gap-3 text-sm text-parchment/60">
            <p>
              Showing {startIndex}-{endIndex} of {total} matching products
            </p>
            <div className="flex gap-2">
              <button
                type="button"
                disabled={offset === 0}
                onClick={() => setOffset((current) => Math.max(0, current - pageSize))}
                className="rounded-xl border border-white/10 px-4 py-2 transition disabled:cursor-not-allowed disabled:opacity-40"
              >
                Previous
              </button>
              <button
                type="button"
                disabled={!browseResult?.has_next_page}
                onClick={() => setOffset((current) => current + pageSize)}
                className="rounded-xl border border-white/10 px-4 py-2 transition disabled:cursor-not-allowed disabled:opacity-40"
              >
                Next
              </button>
            </div>
          </div>
        ) : null}

        {items.length > 0 ? <ProductGrid products={items} /> : null}
      </section>
    </div>
  );
}
