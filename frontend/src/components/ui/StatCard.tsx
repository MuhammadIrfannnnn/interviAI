interface StatCardProps {
  label: string;
  value: string | number;
  accent?: boolean;
}

export function StatCard({ label, value, accent }: StatCardProps) {
  return (
    <div className="rounded-lg border border-border bg-surface p-5">
      <p className="text-xs uppercase tracking-wide text-text-muted">{label}</p>
      <p className={`mt-2 text-2xl font-semibold ${accent ? "text-accent" : "text-text-primary"}`}>
        {value}
      </p>
    </div>
  );
}