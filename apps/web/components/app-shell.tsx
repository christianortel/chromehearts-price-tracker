import Link from "next/link";
import type { ReactNode } from "react";

export function AppShell({
  children,
  eyebrow,
  title,
  description,
}: {
  children: ReactNode;
  eyebrow?: string;
  title: string;
  description?: string;
}) {
  return (
    <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-4 pb-16 pt-6 sm:px-6 lg:px-8">
      <header className="mb-8 flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-5">
        <div>
          <p className="text-xs uppercase tracking-[0.45em] text-bronze/80">Chrome Hearts Price Intelligence</p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight text-parchment sm:text-5xl">{title}</h1>
          {description ? <p className="mt-3 max-w-3xl text-sm text-parchment/70 sm:text-base">{description}</p> : null}
        </div>
        <nav className="flex flex-wrap gap-2 text-sm text-parchment/70">
          <Link className="rounded-full border border-white/10 px-4 py-2 hover:border-bronze/60 hover:text-parchment" href="/">
            Home
          </Link>
          <Link className="rounded-full border border-white/10 px-4 py-2 hover:border-bronze/60 hover:text-parchment" href="/browse">
            Browse
          </Link>
          <Link className="rounded-full border border-white/10 px-4 py-2 hover:border-bronze/60 hover:text-parchment" href="/submit">
            Submit
          </Link>
          <Link className="rounded-full border border-white/10 px-4 py-2 hover:border-bronze/60 hover:text-parchment" href="/admin">
            Admin
          </Link>
        </nav>
      </header>
      {eyebrow ? <p className="mb-4 text-xs uppercase tracking-[0.4em] text-parchment/40">{eyebrow}</p> : null}
      <main className="flex-1">{children}</main>
    </div>
  );
}
