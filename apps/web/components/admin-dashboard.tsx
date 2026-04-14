import Link from "next/link";

import {
  autoMatchObservationAction,
  matchObservationAction,
  recomputeMetricsAction,
  reviewSubmissionAction,
  runSourceAction,
  toggleSourceAction,
} from "@/app/admin/actions";
import { ConfidenceBadge } from "@/components/confidence-badge";
import { Button } from "@/components/ui/button";
import type {
  ProductListItem,
  ScrapeRun,
  Source,
  SourceHealth,
  Submission,
  UnmatchedObservation,
} from "@/lib/types";

type ProductOption = {
  productId: number;
  label: string;
  hint: string;
};

export function AdminDashboard({
  unmatched,
  submissions,
  sources,
  sourceHealth,
  scrapeRuns,
  submissionSearchId,
  submissionSearchQuery,
  submissionSearchResults,
  observationSearchId,
  observationSearchQuery,
  observationSearchResults,
}: {
  unmatched: UnmatchedObservation[];
  submissions: Submission[];
  sources: Source[];
  sourceHealth: SourceHealth[];
  scrapeRuns: ScrapeRun[];
  submissionSearchId: number | null;
  submissionSearchQuery: string;
  submissionSearchResults: ProductListItem[];
  observationSearchId: number | null;
  observationSearchQuery: string;
  observationSearchResults: ProductListItem[];
}) {
  const healthBySourceId = new Map(sourceHealth.map((item) => [item.source_id, item]));
  const healthySources = sourceHealth.filter((item) => item.last_status === "success").length;

  function formatDate(value: string | null) {
    if (!value) {
      return "Never";
    }
    return new Date(value).toLocaleString();
  }

  function isLocalAssetPath(value: string) {
    return !/^https?:\/\//i.test(value);
  }

  function mergeProductOptions(
    rankedCandidates: { product_id: number; product_name: string | null; score: number; reason: string }[],
    searchResults: ProductListItem[],
  ): ProductOption[] {
    const entries = new Map<number, ProductOption>();

    for (const candidate of rankedCandidates) {
      entries.set(candidate.product_id, {
        productId: candidate.product_id,
        label: candidate.product_name ?? `#${candidate.product_id}`,
        hint: `ranked candidate | score ${candidate.score.toFixed(3)} | ${candidate.reason}`,
      });
    }

    for (const product of searchResults) {
      entries.set(product.id, {
        productId: product.id,
        label: product.canonical_name,
        hint: `search result | ${product.category.replaceAll("_", " ")}`,
      });
    }

    return Array.from(entries.values());
  }

  return (
    <div className="grid gap-6">
      <div className="flex flex-wrap justify-end gap-3">
        <Link
          className="rounded-full border border-white/15 px-4 py-2 text-sm text-parchment/75 hover:border-bronze/60 hover:text-parchment"
          href="/admin/duplicates"
        >
          Review duplicates
        </Link>
        <Link
          className="rounded-full border border-white/15 px-4 py-2 text-sm text-parchment/75 hover:border-bronze/60 hover:text-parchment"
          href="/admin/aliases"
        >
          Manage aliases
        </Link>
        <form action={recomputeMetricsAction}>
          <Button type="submit">Recompute metrics</Button>
        </form>
      </div>

      <section className="grid gap-6 xl:grid-cols-4">
        <div className="panel p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Unmatched queue</p>
          <p className="mt-3 text-4xl font-semibold">{unmatched.length}</p>
        </div>
        <div className="panel p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Pending submissions</p>
          <p className="mt-3 text-4xl font-semibold">{submissions.filter((submission) => submission.status === "pending").length}</p>
        </div>
        <div className="panel p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Enabled sources</p>
          <p className="mt-3 text-4xl font-semibold">{sources.filter((source) => source.enabled).length}</p>
        </div>
        <div className="panel p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Healthy recent sources</p>
          <p className="mt-3 text-4xl font-semibold">{healthySources}</p>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="panel p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Source controls</p>
          <p className="mt-2 max-w-2xl text-sm text-parchment/60">
            Trigger bounded refresh runs, keep source kill switches honest, and watch policy state without overstating
            live-source reliability.
          </p>
          <div className="mt-4 space-y-3">
            {sources.map((source) => {
              const health = healthBySourceId.get(source.id);
              return (
                <div key={source.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="text-lg font-medium">{source.name}</p>
                        <span className="rounded-full bg-white/10 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-parchment/65">
                          {source.source_type}
                        </span>
                        <span className="rounded-full bg-white/10 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-parchment/65">
                          {source.crawl_method}
                        </span>
                        <span className="rounded-full bg-white/10 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-parchment/65">
                          {health?.policy_status ?? source.policy_status}
                        </span>
                      </div>
                      <p className="mt-2 text-sm text-parchment/60">{source.notes ?? "No source notes recorded yet."}</p>
                      <div className="mt-3 flex flex-wrap gap-4 text-xs text-parchment/50">
                        <span>Last run: {formatDate(health?.last_finished_at ?? null)}</span>
                        <span>Last status: {health?.last_status ?? "No runs"}</span>
                        <span>Recent errors: {health?.recent_error_count ?? 0}</span>
                        <span>
                          Success rate:{" "}
                          {health?.success_rate !== null && health?.success_rate !== undefined
                            ? `${Math.round(health.success_rate * 100)}%`
                            : "N/A"}
                        </span>
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <form action={runSourceAction}>
                        <input name="sourceId" type="hidden" value={source.id} />
                        <input name="query" type="hidden" value="chrome hearts" />
                        <Button type="submit">Run refresh</Button>
                      </form>
                      <form action={toggleSourceAction}>
                        <input name="sourceId" type="hidden" value={source.id} />
                        <input name="enabled" type="hidden" value={source.enabled ? "false" : "true"} />
                        <Button className="border-white/20 bg-white/5 hover:bg-white/10" type="submit">
                          {source.enabled ? "Disable source" : "Enable source"}
                        </Button>
                      </form>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="panel p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Recent scrape runs</p>
          <div className="mt-4 space-y-3">
            {scrapeRuns.map((run) => (
              <div key={run.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-medium">{run.source_name ?? `Source ${run.source_id}`}</p>
                    <p className="mt-2 text-sm text-parchment/60">
                      {run.status} | discovered {run.discovered_count} | parsed {run.parsed_count} | inserted{" "}
                      {run.inserted_count}
                    </p>
                    <p className="mt-2 text-xs text-parchment/45">Finished {formatDate(run.finished_at)}</p>
                    {run.notes ? <p className="mt-2 text-xs text-parchment/45">{run.notes}</p> : null}
                    <Link className="mt-3 inline-flex text-xs text-bronze hover:text-parchment" href={`/admin/scrape-runs/${run.id}`}>
                      Inspect run details
                    </Link>
                  </div>
                  <span className="rounded-full bg-white/10 px-3 py-1 text-xs uppercase tracking-[0.2em] text-parchment/70">
                    errors {run.error_count}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <div className="panel p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Low-confidence observations</p>
          <div className="mt-4 space-y-3">
            {unmatched.map((item) => {
              const productOptions = mergeProductOptions(
                item.top_candidates,
                observationSearchId === item.id ? observationSearchResults : [],
              );

              return (
                <div key={item.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm text-parchment/45">{item.source_name}</p>
                      <p className="mt-1 font-medium">{item.raw_title}</p>
                      <p className="mt-2 text-sm text-parchment/60">Observed {new Date(item.observed_at).toLocaleDateString()}</p>
                      <Link className="mt-2 inline-flex text-xs text-bronze hover:text-parchment" href={`/admin/observations/${item.id}`}>
                        Inspect observation
                      </Link>
                      <p className="mt-2 text-xs text-parchment/45">
                        Suggested candidates are ranked conservatively and still require human confirmation.
                      </p>
                    </div>
                    <ConfidenceBadge value={item.match_confidence} />
                  </div>
                  <div className="mt-4 space-y-3">
                    <form action="/admin" className="grid gap-3 md:grid-cols-[1fr_auto]">
                      <input name="observationId" type="hidden" value={item.id} />
                      <input
                        className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-parchment"
                        defaultValue={observationSearchId === item.id ? observationSearchQuery : item.raw_title}
                        name="observationQuery"
                        placeholder="Search products by name or alias"
                        type="search"
                      />
                      <Button className="border-white/20 bg-white/5 hover:bg-white/10" type="submit">
                        Search catalog
                      </Button>
                    </form>
                    {observationSearchId === item.id ? (
                      <p className="text-xs text-parchment/45">
                        Search results for &quot;{observationSearchQuery}&quot;.
                        <Link className="ml-2 text-bronze hover:text-parchment" href="/admin">
                          Clear
                        </Link>
                      </p>
                    ) : null}
                    <form action={matchObservationAction} className="grid gap-3 md:grid-cols-[1fr_auto_auto]">
                      <input name="observationId" type="hidden" value={item.id} />
                      <input name="decision" type="hidden" value="matched" />
                      <select
                        className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-parchment"
                        name="productId"
                        defaultValue={productOptions[0]?.productId ?? ""}
                      >
                        <option value="">Select a product</option>
                        {productOptions.map((option) => (
                          <option key={`${item.id}-${option.productId}`} value={option.productId}>
                            {option.label} | {option.hint}
                          </option>
                        ))}
                      </select>
                      <Button type="submit">Apply match</Button>
                      <Button className="border-white/20 bg-white/5 hover:bg-white/10" formAction={autoMatchObservationAction} type="submit">
                        Auto-match
                      </Button>
                    </form>
                    <form action={matchObservationAction}>
                      <input name="observationId" type="hidden" value={item.id} />
                      <input name="decision" type="hidden" value="rejected" />
                      <Button className="border-white/20 bg-white/5 hover:bg-white/10" type="submit">
                        Mark rejected
                      </Button>
                    </form>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="panel p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Submission review</p>
          <div className="mt-4 space-y-3">
            {submissions.map((submission) => {
              const productOptions = mergeProductOptions(
                submission.top_candidates,
                submissionSearchId === submission.id ? submissionSearchResults : [],
              );

              return (
                <div key={submission.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-medium">{submission.item_name}</p>
                      {submission.receipt_asset_url ? (
                        isLocalAssetPath(submission.receipt_asset_url) ? (
                          <Link
                            className="mt-2 inline-flex text-xs text-bronze hover:text-parchment"
                            href={`/admin/assets/view?path=${encodeURIComponent(submission.receipt_asset_url)}&label=${encodeURIComponent("Submission proof")}`}
                          >
                            Inspect uploaded proof
                          </Link>
                        ) : (
                          <a
                            className="mt-2 inline-flex text-xs text-bronze hover:text-parchment"
                            href={submission.receipt_asset_url}
                            rel="noreferrer"
                            target="_blank"
                          >
                            Open external proof
                          </a>
                        )
                      ) : null}
                      <p className="mt-2 text-sm text-parchment/60">
                        {submission.store ?? "Unknown store"} - {submission.price} {submission.currency}
                      </p>
                    </div>
                    <span className="rounded-full bg-white/10 px-3 py-1 text-xs uppercase tracking-[0.2em] text-parchment/70">
                      {submission.status}
                    </span>
                  </div>
                  {submission.status === "pending" ? (
                    <div className="mt-4 space-y-3">
                      <form action="/admin" className="grid gap-3 md:grid-cols-[1fr_auto]">
                        <input name="submissionId" type="hidden" value={submission.id} />
                        <input
                          className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-parchment"
                          defaultValue={submissionSearchId === submission.id ? submissionSearchQuery : submission.item_name}
                          name="submissionQuery"
                          placeholder="Search products by name or alias"
                          type="search"
                        />
                        <Button className="border-white/20 bg-white/5 hover:bg-white/10" type="submit">
                          Search catalog
                        </Button>
                      </form>
                      {submissionSearchId === submission.id ? (
                        <p className="text-xs text-parchment/45">
                          Search results for &quot;{submissionSearchQuery}&quot;.
                          <Link className="ml-2 text-bronze hover:text-parchment" href="/admin">
                            Clear
                          </Link>
                        </p>
                      ) : null}
                      <form action={reviewSubmissionAction} className="flex flex-wrap gap-2">
                        <input name="submissionId" type="hidden" value={submission.id} />
                        <input name="decision" type="hidden" value="approved" />
                        <select
                          className="min-w-[18rem] rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-parchment"
                          name="productId"
                          defaultValue={productOptions[0]?.productId ?? ""}
                        >
                          <option value="">Approve without product match</option>
                          {productOptions.map((option) => (
                            <option key={`${submission.id}-${option.productId}`} value={option.productId}>
                              {option.label} | {option.hint}
                            </option>
                          ))}
                        </select>
                        <Button type="submit">Approve</Button>
                      </form>
                      <form action={reviewSubmissionAction}>
                        <input name="submissionId" type="hidden" value={submission.id} />
                        <input name="decision" type="hidden" value="rejected" />
                        <Button className="border-white/20 bg-white/5 hover:bg-white/10" type="submit">
                          Reject
                        </Button>
                      </form>
                    </div>
                  ) : null}
                </div>
              );
            })}
          </div>
        </div>
      </section>
    </div>
  );
}
