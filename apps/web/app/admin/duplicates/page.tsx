import Link from "next/link";

import { resolveDuplicateGroupAction, reviewDuplicateObservationAction } from "@/app/admin/actions";
import { AppShell } from "@/components/app-shell";
import { Button } from "@/components/ui/button";
import { getAdminDuplicateGroups } from "@/lib/api";

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}

export default async function AdminDuplicatesPage() {
  const adminToken = process.env.ADMIN_TOKEN;
  const duplicateGroups = await getAdminDuplicateGroups(adminToken);

  return (
    <AppShell
      eyebrow="Admin duplicate review"
      title="Review duplicate observation groups"
      description="Duplicate grouping is heuristic evidence, not truth. Keep one credible observation active, reject obvious duplicates, and avoid silently double-counting asks or retail reports."
    >
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-2 text-xs text-parchment/55">
          <span className="rounded-full bg-white/10 px-3 py-1 uppercase tracking-[0.2em]">
            groups {duplicateGroups.length}
          </span>
        </div>
        <Link className="text-sm text-bronze hover:text-parchment" href="/admin">
          Back to admin
        </Link>
      </div>

      <div className="grid gap-5">
        {duplicateGroups.length === 0 ? (
          <div className="panel p-5">
            <p className="text-sm text-parchment/60">
              No active duplicate groups are currently queued for review.
            </p>
          </div>
        ) : (
          duplicateGroups.map((group) => (
            <div key={group.duplicate_group_key} className="panel p-5">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Duplicate group</p>
                  <p className="mt-2 font-mono text-xs text-parchment/60">{group.duplicate_group_key}</p>
                  {group.suggested_keep_observation_id ? (
                    <p className="mt-3 text-sm text-parchment/60">
                      Recommended keeper: observation #{group.suggested_keep_observation_id}
                      {group.suggested_keep_reason ? ` (${group.suggested_keep_reason})` : ""}
                    </p>
                  ) : null}
                </div>
                <div className="flex flex-wrap gap-2 text-xs text-parchment/55">
                  <span className="rounded-full bg-white/10 px-3 py-1 uppercase tracking-[0.2em]">
                    observations {group.duplicate_count}
                  </span>
                  <span className="rounded-full bg-white/10 px-3 py-1 uppercase tracking-[0.2em]">
                    latest {formatDate(group.latest_observed_at)}
                  </span>
                </div>
              </div>

              <div className="mt-5 grid gap-4">
                {group.observations.map((observation, index) => (
                  <div key={observation.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
                    <div className="flex flex-wrap items-start justify-between gap-4">
                      <div>
                        <div className="flex flex-wrap items-center gap-2">
                          <p className="font-medium">{observation.raw_title}</p>
                          {index === 0 ? (
                            <span className="rounded-full bg-bronze/15 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-bronze">
                              review first
                            </span>
                          ) : null}
                          {group.suggested_keep_observation_id === observation.id ? (
                            <span className="rounded-full bg-emerald-500/15 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-emerald-300">
                              recommended keeper
                            </span>
                          ) : null}
                        </div>
                        <p className="mt-2 text-sm text-parchment/60">
                          {observation.product_name ?? "Unmatched"} | {observation.source_name} |{" "}
                          {observation.market_side}
                        </p>
                        <div className="mt-3 flex flex-wrap gap-4 text-xs text-parchment/50">
                          <span>Observed {formatDate(observation.observed_at)}</span>
                          <span>
                            {observation.price_amount} {observation.currency}
                          </span>
                          <span>Status {observation.status}</span>
                        </div>
                        <p className="mt-3 text-xs text-parchment/45">{observation.source_url}</p>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        <Link
                          className="rounded-full border border-white/15 px-4 py-2 text-sm text-parchment/75 hover:border-bronze/60 hover:text-parchment"
                          href={`/admin/observations/${observation.id}`}
                        >
                          Inspect observation
                        </Link>
                        <form action={resolveDuplicateGroupAction}>
                          <input name="duplicateGroupKey" type="hidden" value={group.duplicate_group_key} />
                          <input name="keepObservationId" type="hidden" value={observation.id} />
                          <Button type="submit">Keep this one</Button>
                        </form>
                        <form action={reviewDuplicateObservationAction}>
                          <input name="observationId" type="hidden" value={observation.id} />
                          <input name="decision" type="hidden" value="reject" />
                          <Button className="border-white/20 bg-white/5 hover:bg-white/10" type="submit">
                            Mark duplicate
                          </Button>
                        </form>
                        <form action={reviewDuplicateObservationAction}>
                          <input name="observationId" type="hidden" value={observation.id} />
                          <input name="decision" type="hidden" value="restore" />
                          <Button className="border-white/20 bg-white/5 hover:bg-white/10" type="submit">
                            Restore
                          </Button>
                        </form>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </AppShell>
  );
}
