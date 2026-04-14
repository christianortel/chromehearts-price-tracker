import Link from "next/link";

import { AppShell } from "@/components/app-shell";
import { getAdminObservationDetail } from "@/lib/api";

function formatDate(value: string | null) {
  if (!value) {
    return "Never";
  }
  return new Date(value).toLocaleString();
}

function isLocalAssetPath(value: string) {
  return !/^https?:\/\//i.test(value);
}

function isHttpUrl(value: string) {
  return /^https?:\/\//i.test(value);
}

export default async function AdminObservationDetailPage({
  params,
}: {
  params: Promise<{ observationId: string }>;
}) {
  const { observationId } = await params;
  const adminToken = process.env.ADMIN_TOKEN;
  const observation = await getAdminObservationDetail(observationId, adminToken);

  return (
    <AppShell
      eyebrow="Admin observation detail"
      title={`Inspect observation #${observation.id}`}
      description="Review source metadata, raw payload, proof context, and prior match decisions without collapsing noisy evidence into a single opaque record."
    >
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-2 text-xs text-parchment/55">
          <span className="rounded-full bg-white/10 px-3 py-1 uppercase tracking-[0.2em]">{observation.market_side}</span>
          <span className="rounded-full bg-white/10 px-3 py-1 uppercase tracking-[0.2em]">{observation.status}</span>
          <span className="rounded-full bg-white/10 px-3 py-1 uppercase tracking-[0.2em]">
            {observation.source_name}
          </span>
        </div>
        <Link className="text-sm text-bronze hover:text-parchment" href="/admin">
          Back to admin
        </Link>
      </div>

      <section className="grid gap-4 md:grid-cols-4">
        <div className="panel p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Observed</p>
          <p className="mt-3 text-sm text-parchment/75">{formatDate(observation.observed_at)}</p>
        </div>
        <div className="panel p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Price</p>
          <p className="mt-3 text-sm text-parchment/75">
            {observation.price_amount} {observation.currency}
          </p>
        </div>
        <div className="panel p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Product</p>
          <p className="mt-3 text-sm text-parchment/75">{observation.product_name ?? "Unmatched"}</p>
        </div>
        <div className="panel p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Duplicate group</p>
          <p className="mt-3 break-all text-sm text-parchment/75">{observation.duplicate_group_key ?? "None"}</p>
        </div>
      </section>

      <section className="mt-6 grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="panel p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Observation metadata</p>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Title</p>
              <p className="mt-2 text-sm text-parchment/75">{observation.raw_title}</p>
              <p className="mt-2 text-xs text-parchment/50">{observation.normalized_title}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Source record</p>
              <p className="mt-2 break-all text-sm text-parchment/75">{observation.source_item_id}</p>
              <p className="mt-2 break-all text-xs text-parchment/50">{observation.source_url}</p>
              {isHttpUrl(observation.source_url) ? (
                <a
                  className="mt-2 inline-flex text-xs text-bronze hover:text-parchment"
                  href={observation.source_url}
                  rel="noreferrer"
                  target="_blank"
                >
                  Open source URL
                </a>
              ) : null}
            </div>
            <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Seller / location</p>
              <p className="mt-2 text-sm text-parchment/75">{observation.seller_or_store ?? "Not captured"}</p>
              <p className="mt-2 text-xs text-parchment/50">{observation.location_text ?? "No location captured"}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Condition / size</p>
              <p className="mt-2 text-sm text-parchment/75">{observation.condition ?? "Not captured"}</p>
              <p className="mt-2 text-xs text-parchment/50">{observation.size_text ?? "No size captured"}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Confidence</p>
              <p className="mt-2 text-sm text-parchment/75">
                extraction {observation.extraction_confidence} | match {observation.match_confidence} | price{" "}
                {observation.price_confidence}
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Lifecycle</p>
              <p className="mt-2 text-sm text-parchment/75">first seen {formatDate(observation.first_seen_at)}</p>
              <p className="mt-2 text-xs text-parchment/50">last seen {formatDate(observation.last_seen_at)}</p>
              <p className="mt-2 text-xs text-parchment/50">updated {formatDate(observation.updated_at)}</p>
            </div>
          </div>
        </div>

        <div className="panel p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Proof and review context</p>
          <div className="mt-4 space-y-4">
            <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Proof</p>
              <p className="mt-2 text-sm text-parchment/75">{observation.proof_type ?? "No proof type recorded"}</p>
              {observation.proof_asset_url ? (
                isLocalAssetPath(observation.proof_asset_url) ? (
                  <Link
                    className="mt-2 inline-flex text-sm text-bronze hover:text-parchment"
                    href={`/admin/assets/view?path=${encodeURIComponent(observation.proof_asset_url)}&label=${encodeURIComponent("Observation proof")}`}
                  >
                    Inspect stored proof
                  </Link>
                ) : (
                  <a
                    className="mt-2 inline-flex text-sm text-bronze hover:text-parchment"
                    href={observation.proof_asset_url}
                    rel="noreferrer"
                    target="_blank"
                  >
                    Open proof URL
                  </a>
                )
              ) : (
                <p className="mt-2 text-xs text-parchment/50">No proof asset recorded.</p>
              )}
            </div>

            <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Retail report</p>
              {observation.retail_report ? (
                <>
                  <p className="mt-2 text-sm text-parchment/75">
                    {observation.retail_report.store_name ?? "Unknown store"} | {observation.retail_report.moderator_status}
                  </p>
                  <p className="mt-2 text-xs text-parchment/50">
                    {observation.retail_report.city ?? "Unknown city"}, {observation.retail_report.country ?? "Unknown country"}
                  </p>
                  <p className="mt-2 text-xs text-parchment/50">
                    receipt submitted {observation.retail_report.receipt_submitted ? "yes" : "no"}
                  </p>
                  {observation.retail_report.moderator_notes ? (
                    <p className="mt-2 text-xs text-parchment/50">{observation.retail_report.moderator_notes}</p>
                  ) : null}
                </>
              ) : (
                <p className="mt-2 text-sm text-parchment/60">No retail report is attached to this observation.</p>
              )}
            </div>

            <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Suggested candidates</p>
              {observation.top_candidates.length === 0 ? (
                <p className="mt-2 text-sm text-parchment/60">No ranked candidates were generated.</p>
              ) : (
                <div className="mt-3 space-y-2">
                  {observation.top_candidates.map((candidate) => (
                    <p key={`${observation.id}-${candidate.product_id}`} className="text-sm text-parchment/75">
                      {candidate.product_name ?? `#${candidate.product_id}`} | score {candidate.score.toFixed(3)} | {candidate.reason}
                    </p>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="mt-6 grid gap-4 lg:grid-cols-[0.8fr_1.2fr]">
        <div className="panel p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Match review history</p>
          {observation.match_reviews.length === 0 ? (
            <p className="mt-4 text-sm text-parchment/60">No match reviews have been recorded yet.</p>
          ) : (
            <div className="mt-4 space-y-3">
              {observation.match_reviews.map((review) => (
                <div key={review.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
                  <p className="text-sm text-parchment/75">
                    {review.reviewer_decision} | {review.proposed_product_name ?? "No proposed product"}
                  </p>
                  <p className="mt-2 text-xs text-parchment/50">{formatDate(review.reviewed_at)}</p>
                  {review.reviewer_notes ? <p className="mt-2 text-xs text-parchment/60">{review.reviewer_notes}</p> : null}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="panel p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Raw payload</p>
          <pre className="mt-4 overflow-x-auto rounded-2xl border border-white/10 bg-black/30 p-4 text-xs text-parchment/75">
            {JSON.stringify(observation.raw_payload_json, null, 2)}
          </pre>
        </div>
      </section>
    </AppShell>
  );
}
