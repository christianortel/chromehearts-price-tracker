import Image from "next/image";
import Link from "next/link";

import { AppShell } from "@/components/app-shell";
import { getAdminAssetPreview } from "@/lib/api";

export default async function AdminAssetViewPage({
  searchParams,
}: {
  searchParams: Promise<{ path?: string; label?: string }>;
}) {
  const params = await searchParams;
  const assetPath = params.path?.trim();
  const label = params.label?.trim() || "Artifact preview";

  if (!assetPath) {
    return (
      <AppShell
        eyebrow="Admin asset preview"
        title="Missing artifact path"
        description="Provide an artifact path to inspect a stored scrape snapshot or screenshot."
      >
        <Link className="text-sm text-bronze hover:text-parchment" href="/admin">
          Back to admin
        </Link>
      </AppShell>
    );
  }

  const adminToken = process.env.ADMIN_TOKEN;
  const preview = await getAdminAssetPreview(assetPath, adminToken);

  return (
    <AppShell
      eyebrow="Admin asset preview"
      title={label}
      description="Stored preview data is shown in a protected admin view so parse-failure artifacts can be inspected without exposing arbitrary paths publicly."
    >
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-2 text-xs text-parchment/55">
          <span className="rounded-full bg-white/10 px-3 py-1 uppercase tracking-[0.2em]">
            {preview.kind}
          </span>
          <span className="rounded-full bg-white/10 px-3 py-1 uppercase tracking-[0.2em]">
            {preview.content_type}
          </span>
          <span className="rounded-full bg-white/10 px-3 py-1 uppercase tracking-[0.2em]">
            bytes {preview.byte_size}
          </span>
          {preview.truncated ? (
            <span className="rounded-full bg-ember/15 px-3 py-1 uppercase tracking-[0.2em] text-ember">
              truncated
            </span>
          ) : null}
        </div>
        <Link className="text-sm text-bronze hover:text-parchment" href="/admin">
          Back to admin
        </Link>
      </div>

      <section className="panel p-5">
        <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Artifact path</p>
        <p className="mt-3 break-all font-mono text-xs text-parchment/60">{preview.asset_path}</p>
      </section>

      <section className="panel mt-6 p-5">
        <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">Preview</p>
        {preview.kind === "image" && preview.base64_content ? (
          <Image
            alt={preview.file_name}
            className="mt-4 max-h-[70vh] rounded-2xl border border-white/10 object-contain"
            height={900}
            src={`data:${preview.content_type};base64,${preview.base64_content}`}
            unoptimized
            width={1200}
          />
        ) : null}
        {preview.kind === "text" ? (
          <pre className="mt-4 overflow-x-auto rounded-2xl border border-white/10 bg-black/30 p-4 text-xs text-parchment/75">
            {preview.text_content ?? ""}
          </pre>
        ) : null}
        {preview.kind === "binary" ? (
          <p className="mt-4 text-sm text-parchment/60">
            Binary preview is not rendered inline. The file metadata is available above.
          </p>
        ) : null}
      </section>
    </AppShell>
  );
}
