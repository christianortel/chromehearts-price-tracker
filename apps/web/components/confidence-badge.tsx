const SCALE = [
  { threshold: 0.85, label: "High", color: "bg-moss/20 text-moss" },
  { threshold: 0.65, label: "Medium", color: "bg-bronze/20 text-bronze" },
  { threshold: 0, label: "Low", color: "bg-ember/20 text-ember" },
];

export function ConfidenceBadge({ value }: { value: string | null | undefined }) {
  const numeric = value ? Number(value) : 0;
  const match = SCALE.find((entry) => numeric >= entry.threshold) ?? SCALE[SCALE.length - 1];
  return (
    <span className={`rounded-full px-3 py-1 text-xs font-medium ${match.color}`}>
      {match.label} confidence
    </span>
  );
}

