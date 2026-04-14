import { AppShell } from "@/components/app-shell";
import { ConfidenceBadge } from "@/components/confidence-badge";
import { EvidenceTable } from "@/components/evidence-table";
import { MetricStrip } from "@/components/metric-strip";
import { PriceHistoryChart } from "@/components/price-history-chart";
import { getProduct } from "@/lib/api";

export default async function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const product = await getProduct(id);
  const metric = product.latest_metric;

  return (
    <AppShell
      eyebrow={product.category.replaceAll("_", " ")}
      title={product.canonical_name}
      description="Retail, ask, and sold evidence are intentionally separated here so the premium signal remains honest."
    >
      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-6">
          <MetricStrip
            metrics={{
              retail: metric?.retail_best_known,
              ask: metric?.ask_median,
              sold: metric?.sold_median_30d,
              premium: metric?.premium_vs_retail_pct,
            }}
          />
          <PriceHistoryChart
            points={[
              { label: "Retail", retail: Number(metric?.retail_best_known ?? 0) },
              { label: "Ask", ask: Number(metric?.ask_median ?? 0) },
              { label: "Sold", sold: metric?.sold_median_30d ? Number(metric.sold_median_30d) : undefined },
            ]}
          />
          <EvidenceTable observations={product.observations} />
        </div>
        <aside className="space-y-6">
          <div className="panel p-5">
            <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Trust and freshness</p>
            <div className="mt-4 flex flex-wrap gap-2">
              <ConfidenceBadge value={metric?.confidence_score} />
              <span className="rounded-full bg-white/10 px-3 py-1 text-xs">Freshness {metric?.freshness_score ?? "N/A"}</span>
            </div>
            <p className="mt-4 text-sm text-parchment/65">{product.notes}</p>
          </div>
          <div className="panel p-5">
            <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Alias map</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {product.aliases.map((alias) => (
                <span key={alias} className="rounded-full border border-white/10 px-3 py-1 text-sm">
                  {alias}
                </span>
              ))}
            </div>
          </div>
        </aside>
      </div>
    </AppShell>
  );
}
