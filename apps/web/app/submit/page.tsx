import { AppShell } from "@/components/app-shell";
import { SubmissionForm } from "@/components/submission-form";

export default function SubmitPage() {
  return (
    <AppShell
      eyebrow="Community retail reports"
      title="Submit a retail sighting"
      description="Receipt-backed submissions increase trust, but all community data is still treated as evidence that can be reviewed, approved, or rejected."
    >
      <SubmissionForm />
    </AppShell>
  );
}

