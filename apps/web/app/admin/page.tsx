import { AppShell } from "@/components/app-shell";
import { AdminDashboard } from "@/components/admin-dashboard";
import { getAdminProductSearch, getAdminScrapeRuns, getAdminSourceHealth, getAdminSubmissions, getSources, getUnmatchedObservations } from "@/lib/api";

function readString(value: string | string[] | undefined) {
  return typeof value === "string" ? value : Array.isArray(value) ? value[0] : undefined;
}

export default async function AdminPage({
  searchParams,
}: {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
}) {
  const adminToken = process.env.ADMIN_TOKEN;
  const params = (await searchParams) ?? {};
  const submissionSearchQuery = readString(params.submissionQuery)?.trim() || "";
  const submissionSearchId = Number(readString(params.submissionId) ?? "") || null;
  const observationSearchQuery = readString(params.observationQuery)?.trim() || "";
  const observationSearchId = Number(readString(params.observationId) ?? "") || null;

  const [unmatched, submissions, sources, sourceHealth, scrapeRuns] = await Promise.all([
    getUnmatchedObservations(adminToken),
    getAdminSubmissions(adminToken),
    getSources(),
    getAdminSourceHealth(adminToken),
    getAdminScrapeRuns(adminToken),
  ]);
  const [submissionSearchResults, observationSearchResults] = await Promise.all([
    submissionSearchQuery ? getAdminProductSearch(submissionSearchQuery, adminToken) : Promise.resolve([]),
    observationSearchQuery ? getAdminProductSearch(observationSearchQuery, adminToken) : Promise.resolve([]),
  ]);

  return (
    <AppShell
      eyebrow="Admin operations"
      title="Keep noisy data honest"
      description="Review unmatched observations, moderate submissions, and keep source health visible without overstating confidence."
    >
      <AdminDashboard
        unmatched={unmatched}
        submissions={submissions}
        sources={sources}
        sourceHealth={sourceHealth}
        scrapeRuns={scrapeRuns}
        submissionSearchId={submissionSearchId}
        submissionSearchQuery={submissionSearchQuery}
        submissionSearchResults={submissionSearchResults}
        observationSearchId={observationSearchId}
        observationSearchQuery={observationSearchQuery}
        observationSearchResults={observationSearchResults}
      />
    </AppShell>
  );
}
