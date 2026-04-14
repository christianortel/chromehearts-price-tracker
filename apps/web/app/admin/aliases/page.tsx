import Link from "next/link";

import { addAliasAction, deleteAliasAction } from "@/app/admin/actions";
import { AppShell } from "@/components/app-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getProductAliases, getProducts, searchProducts } from "@/lib/api";

export default async function AdminAliasesPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const params = await searchParams;
  const query = params.q?.trim() ?? "";
  const adminToken = process.env.ADMIN_TOKEN;
  const products = query.length > 1 ? (await searchProducts(query)).items : (await getProducts()).slice(0, 12);
  const productsWithAliases = await Promise.all(
    products.map(async (product) => ({
      product,
      aliases: await getProductAliases(product.id, adminToken),
    })),
  );

  return (
    <AppShell
      eyebrow="Admin alias management"
      title="Manage canonical naming and alias coverage"
      description="Keep matching safe by adding high-signal aliases deliberately and removing bad ones quickly when they create false matches."
    >
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <form className="flex flex-1 gap-3" method="GET">
          <Input defaultValue={query} name="q" placeholder="Search products for alias management" />
          <Button type="submit">Search</Button>
        </form>
        <Link className="text-sm text-bronze hover:text-parchment" href="/admin">
          Back to admin
        </Link>
      </div>

      <div className="grid gap-4">
        {productsWithAliases.map(({ product, aliases }) => (
          <div key={product.id} className="panel p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">{product.category.replaceAll("_", " ")}</p>
                <h2 className="mt-2 text-2xl font-semibold">{product.canonical_name}</h2>
              </div>
              <span className="rounded-full bg-white/10 px-3 py-1 text-xs text-parchment/70">#{product.id}</span>
            </div>

            <div className="mt-5 flex flex-wrap gap-2">
              {aliases.map((alias) => (
                <form action={deleteAliasAction} className="flex items-center gap-2 rounded-full border border-white/10 bg-black/20 px-3 py-2" key={alias.id}>
                  <input name="aliasId" type="hidden" value={alias.id} />
                  <span className="text-sm">{alias.alias_text}</span>
                  <button className="text-xs text-ember hover:text-parchment" type="submit">
                    Remove
                  </button>
                </form>
              ))}
              {aliases.length === 0 ? <p className="text-sm text-parchment/55">No aliases added yet.</p> : null}
            </div>

            <form action={addAliasAction} className="mt-5 grid gap-3 md:grid-cols-[1fr_180px_auto]">
              <input name="productId" type="hidden" value={product.id} />
              <Input name="aliasText" placeholder="Add alias text" required />
              <select className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-parchment" defaultValue="manual" name="aliasType">
                <option value="manual">manual</option>
                <option value="abbreviation">abbreviation</option>
                <option value="community">community</option>
                <option value="source_specific">source_specific</option>
              </select>
              <Button type="submit">Add alias</Button>
            </form>
          </div>
        ))}
      </div>
    </AppShell>
  );
}

