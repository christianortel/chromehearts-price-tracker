function formatMoney(value: string | null | undefined) {
  if (!value) {
    return "N/A";
  }
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(Number(value));
}

export function MetricStrip({
  metrics,
}: {
  metrics: {
    retail: string | null | undefined;
    ask: string | null | undefined;
    sold: string | null | undefined;
    premium: string | null | undefined;
  };
}) {
  const items = [
    { label: "Best-known retail", value: formatMoney(metrics.retail) },
    { label: "Current ask median", value: formatMoney(metrics.ask) },
    { label: "Sold median 30d", value: formatMoney(metrics.sold) },
    { label: "Premium vs retail", value: metrics.premium ? `${Number(metrics.premium).toFixed(1)}%` : "N/A" },
  ];

  return (
    <div className="grid gap-3 md:grid-cols-4">
      {items.map((item) => (
        <div key={item.label} className="panel p-4">
          <p className="text-xs uppercase tracking-[0.3em] text-parchment/45">{item.label}</p>
          <p className="mt-3 text-2xl font-semibold text-parchment">{item.value}</p>
        </div>
      ))}
    </div>
  );
}

