import Link from "next/link";

import { AppShell } from "@/components/app-shell";
import { getAdminScrapeRunDetail } from "@/lib/api";

function formatDate(value: string | null) {
  if (!value) {
    return "Never";
  }
  return new Date(value).toLocaleString();
}

export default async function AdminScrapeRunDetailPage({
  params,
}: {
  params: Promise<{ runId: string }>;
}) {
  const { runId } = await params;
  const adminToken = process.env.ADMIN_TOKEN;
  const run = await getAdminScrapeRunDetail(runId, adminToken);

  return (
    <AppShell
      eyebrow="Admin scrape run detail"
      title={`Inspect ${run.source_name ?? `source ${run.source_id}`} run #${run.id}`}
      description="Use persisted scrape evidence to understand parser failures, compliance stubs, and run health without guessing from aggregate counts."
    >
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-2 text-xs text-parchment/55">
          <span className="rounded-full bg-white/10 px-3 py-1 uppercase tracking-[0.2em]">{run.status}</span>
          <span className="rounded-full bg-white/10 px-3 py-1 uppercase tracking-[0.2em]">errors {run.error_count}</span>
          <span className="rounded-full bg-white/10 px-3 py-1 uppercase tracking-[0.2em]">inserted {run.inserted_count}</span>
        </div>
        <Link className="text-sm text-bronze hover:text-parchment" href="/admin">
          Back to admin
        </Link>
      </div>

      <section className="grid gap-4 md:grid-cols-4">
        <div className="panel p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Started</p>
          <p className="mt-3 text-sm text-parchment/75">{formatDate(run.started_at)}</p>
        </div>
        <div className="panel p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Finished</p>
          <p className="mt-3 text-sm text-parchment/75">{formatDate(run.finished_at)}</p>
        </div>
        <div className="panel p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Discovered / Parsed</p>
          <p className="mt-3 text-sm text-parchment/75">
            {run.discovered_count} / {run.parsed_count}
          </p>
        </div>
        <div className="panel p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Inserted</p>
          <p className="mt-3 text-sm text-parchment/75">{run.inserted_count}</p>
        </div>
      </section>

      <section className="panel mt-6 p-5">
        <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Run notes</p>
        <p className="mt-3 text-sm text-parchment/70">{run.notes ?? "No run notes recorded."}</p>
      </section>

      <section className="mt-6 grid gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Persisted scrape errors</p>
          <p className="mt-2 text-sm text-parchment/60">
            Parse failures, policy stubs, and adapter errors remain visible here so operators can distinguish source instability from empty-result runs.
          </p>
        </div>
        {run.errors.length === 0 ? (
          <div className="panel p-5">
            <p className="text-sm text-parchment/60">No scrape errors were recorded for this run.</p>
          </div>
        ) : (
          run.errors.map((error) => (
            <div key={error.id} className="panel p-5">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="text-lg font-medium">{error.error_type}</p>
                    <span className="rounded-full bg-white/10 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-parchment/65">
                      {error.source_name ?? `source ${error.source_id}`}
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-parchment/70">{error.error_message}</p>
                </div>
                <span className="rounded-full bg-white/10 px-3 py-1 text-xs uppercase tracking-[0.2em] text-parchment/65">
                  {formatDate(error.created_at)}
                </span>
              </div>
              <div className="mt-4 grid gap-3 md:grid-cols-3">
                <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
                  <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Item reference</p>
                  <p className="mt-2 text-sm text-parchment/70">{error.item_reference ?? "Not captured"}</p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
                  <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">HTML snapshot</p>
                  {error.html_snapshot_path ? (
                    <Link
                      className="mt-2 inline-flex text-sm text-bronze hover:text-parchment"
                      href={`/admin/assets/view?path=${encodeURIComponent(error.html_snapshot_path)}&label=${encodeURIComponent("HTML snapshot")}`}
                    >
                      Open snapshot
                    </Link>
                  ) : (
                    <p className="mt-2 text-sm text-parchment/70">No stored snapshot path</p>
                  )}
                </div>
                <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
                  <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Screenshot</p>
                  {error.screenshot_path ? (
                    <Link
                      className="mt-2 inline-flex text-sm text-bronze hover:text-parchment"
                      href={`/admin/assets/view?path=${encodeURIComponent(error.screenshot_path)}&label=${encodeURIComponent("Screenshot")}`}
                    >
                      Open screenshot
                    </Link>
                  ) : (
                    <p className="mt-2 text-sm text-parchment/70">No stored screenshot path</p>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </section>
    </AppShell>
  );
}
