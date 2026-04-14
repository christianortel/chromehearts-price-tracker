import { ConfidenceBadge } from "@/components/confidence-badge";
import type { Observation } from "@/lib/types";

function formatMoney(value: string) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(
    Number(value),
  );
}

export function EvidenceTable({ observations }: { observations: Observation[] }) {
  return (
    <div className="panel overflow-hidden">
      <div className="border-b border-white/10 px-5 py-4">
        <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Evidence</p>
        <h3 className="mt-2 text-xl font-semibold">Observation timeline</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="bg-white/5 text-left text-parchment/55">
            <tr>
              <th className="px-5 py-3">Type</th>
              <th className="px-5 py-3">Price</th>
              <th className="px-5 py-3">Source</th>
              <th className="px-5 py-3">Seen</th>
              <th className="px-5 py-3">Confidence</th>
            </tr>
          </thead>
          <tbody>
            {observations.map((observation) => (
              <tr key={observation.id} className="border-t border-white/5">
                <td className="px-5 py-4 capitalize">{observation.market_side}</td>
                <td className="px-5 py-4">{formatMoney(observation.price_amount)}</td>
                <td className="px-5 py-4">
                  <a className="text-bronze hover:text-parchment" href={observation.source_url} target="_blank" rel="noreferrer">
                    {observation.seller_or_store ?? observation.source_type_snapshot}
                  </a>
                </td>
                <td className="px-5 py-4">{new Date(observation.observed_at).toLocaleDateString()}</td>
                <td className="px-5 py-4">
                  <ConfidenceBadge value={observation.price_confidence} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

