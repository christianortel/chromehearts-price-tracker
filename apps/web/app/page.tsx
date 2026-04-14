import Link from "next/link";

import { AppShell } from "@/components/app-shell";
import { MetricStrip } from "@/components/metric-strip";
import { ProductGrid } from "@/components/product-grid";
import { getProducts } from "@/lib/api";

export default async function HomePage() {
  const products = await getProducts();
  const featured = products.slice(0, 3);
  const premium = [...products].sort(
    (a, b) => Number(b.latest_metric?.premium_vs_retail_pct ?? 0) - Number(a.latest_metric?.premium_vs_retail_pct ?? 0),
  );

  return (
    <AppShell
      eyebrow="Observation-first collector intelligence"
      title="Fragmented prices, made legible."
      description="Track best-known retail sightings, curated dealer asks, marketplace noise, and sold comps without pretending any one number is the truth."
    >
      <section className="grid gap-6 lg:grid-cols-[1.4fr_0.8fr]">
        <div className="panel overflow-hidden p-8">
          <p className="text-xs uppercase tracking-[0.4em] text-bronze/80">Live product intelligence</p>
          <h2 className="mt-4 max-w-2xl font-[var(--font-display)] text-5xl leading-none text-parchment sm:text-6xl">
            Evidence over hype. Confidence over guesswork.
          </h2>
          <p className="mt-5 max-w-2xl text-base text-parchment/70">
            Chrome Hearts pricing is noisy. This MVP separates retail, ask, and sold evidence so collectors can see markup, freshness, and trust at a glance.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link className="rounded-full bg-bronze px-5 py-3 text-sm font-semibold text-ink hover:bg-parchment" href="/browse">
              Browse products
            </Link>
            <Link className="rounded-full border border-white/15 px-5 py-3 text-sm font-semibold text-parchment hover:border-bronze/60" href="/submit">
              Submit a retail sighting
            </Link>
          </div>
        </div>
        <MetricStrip
          metrics={{
            retail: featured[0]?.latest_metric?.retail_best_known,
            ask: featured[0]?.latest_metric?.ask_median,
            sold: featured[0]?.latest_metric?.sold_median_30d,
            premium: featured[0]?.latest_metric?.premium_vs_retail_pct,
          }}
        />
      </section>

      <section className="mt-10 grid gap-6 lg:grid-cols-2">
        <div className="panel p-6">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Latest retail updates</p>
          <div className="mt-5 space-y-4">
            {featured.map((product) => (
              <div key={product.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
                <p className="text-sm text-parchment/55">{product.category.replaceAll("_", " ")}</p>
                <p className="mt-2 text-lg font-semibold">{product.canonical_name}</p>
                <p className="mt-2 text-sm text-parchment/70">
                  Best-known retail: ${Number(product.latest_metric?.retail_best_known ?? 0).toFixed(0)}
                </p>
              </div>
            ))}
          </div>
        </div>
        <div className="panel p-6">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Highest current premiums</p>
          <div className="mt-5 space-y-4">
            {premium.slice(0, 3).map((product) => (
              <div key={product.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
                <p className="text-lg font-semibold">{product.canonical_name}</p>
                <p className="mt-2 text-sm text-parchment/70">
                  Premium vs retail: {Number(product.latest_metric?.premium_vs_retail_pct ?? 0).toFixed(1)}%
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mt-10">
        <div className="mb-5 flex items-end justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Recently updated products</p>
            <h2 className="mt-2 text-3xl font-semibold">Collector-facing browse feed</h2>
          </div>
          <Link className="text-sm text-bronze hover:text-parchment" href="/browse">
            See full browse view
          </Link>
        </div>
        <ProductGrid products={products.slice(0, 6)} />
      </section>
    </AppShell>
  );
}

