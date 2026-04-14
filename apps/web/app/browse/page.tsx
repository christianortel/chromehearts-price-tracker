import { AppShell } from "@/components/app-shell";
import { BrowseExplorer } from "@/components/browse-explorer";
import { buildBrowseStateFromRecord } from "@/lib/browse-state";

export default async function BrowsePage({
  searchParams,
}: {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
}) {
  const initialState = buildBrowseStateFromRecord((await searchParams) ?? {});

  return (
    <AppShell
      eyebrow="Browse and search"
      title="Browse collector-facing product intelligence"
      description="Filter by category, inspect recent updates, and compare best-known retail against ask and sold evidence without collapsing signal types."
    >
      <BrowseExplorer initialState={initialState} />
    </AppShell>
  );
}
