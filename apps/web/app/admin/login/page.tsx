import { AppShell } from "@/components/app-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import { loginAction } from "./actions";

export default async function AdminLoginPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string }>;
}) {
  const params = await searchParams;
  const hasError = params.error === "1";

  return (
    <AppShell
      eyebrow="Admin access"
      title="Authenticate before reviewing source data"
      description="Admin tools are protected because the web app can access privileged backend moderation endpoints on your behalf."
    >
      <form action={loginAction} className="panel mx-auto max-w-xl space-y-4 p-8">
        <p className="text-sm text-parchment/65">Enter the configured admin token to unlock moderation, source health, and review queues.</p>
        <Input name="token" type="password" placeholder="Admin token" required />
        <Button type="submit">Enter admin</Button>
        {hasError ? <p className="text-sm text-ember">The provided admin token was invalid.</p> : null}
      </form>
    </AppShell>
  );
}

