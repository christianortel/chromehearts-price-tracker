import Link from "next/link";

import { ConfidenceBadge } from "@/components/confidence-badge";
import type { ProductListItem } from "@/lib/types";

function formatMoney(value: string | null | undefined) {
  if (!value) {
    return "N/A";
  }
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(
    Number(value),
  );
}

export function ProductGrid({ products }: { products: ProductListItem[] }) {
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      {products.map((product) => (
        <Link key={product.id} href={`/products/${product.id}`} className="panel group p-5">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">{product.category.replaceAll("_", " ")}</p>
              <h3 className="mt-3 text-xl font-semibold text-parchment group-hover:text-bronze">{product.canonical_name}</h3>
            </div>
            <ConfidenceBadge value={product.latest_metric?.confidence_score} />
          </div>
          <div className="mt-6 grid grid-cols-2 gap-3 text-sm">
            <div className="rounded-2xl border border-white/10 bg-black/20 p-3">
              <p className="text-parchment/45">Retail</p>
              <p className="mt-2 text-lg">{formatMoney(product.latest_metric?.retail_best_known)}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-black/20 p-3">
              <p className="text-parchment/45">Ask median</p>
              <p className="mt-2 text-lg">{formatMoney(product.latest_metric?.ask_median)}</p>
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}

