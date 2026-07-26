import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Loader2, ArrowRight, Plus } from "lucide-react";

import { AppLayout } from "../../layouts/AppLayout";
import { StatCard } from "../../components/ui/StatCard";
import { Button } from "../../components/ui/Button";
import { dashboardService } from "../../services/DashboardService";
import type { DashboardSummary } from "../../types/Dashboard";

function formatScore(score: number | null) {
  if (score === null) return "—";
  return `${Math.round(score)}`;
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data = await dashboardService.getSummary();
        if (!cancelled) setSummary(data);
      } catch (err) {
        if (!cancelled) setError("Couldn't load your dashboard. Try refreshing the page.");
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  if (isLoading) {
    return (
      <AppLayout>
        <div className="flex h-64 items-center justify-center">
          <Loader2 className="h-5 w-5 animate-spin text-text-muted" />
        </div>
      </AppLayout>
    );
  }

  if (error) {
    return (
      <AppLayout>
        <div className="rounded-lg border border-danger bg-danger-soft px-4 py-3 text-sm text-danger">
          {error}
        </div>
      </AppLayout>
    );
  }

  if (!summary) return null;

  const hasInterviews = summary.recent_interviews.length > 0;

  return (
    <AppLayout>
      <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }}>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-text-primary">Dashboard</h1>
            <p className="mt-1 text-sm text-text-secondary">Your interview practice at a glance.</p>
          </div>
          <Link to="/interview">
            <Button>
              <Plus className="h-4 w-4" />
              New interview
            </Button>
          </Link>
        </div>

        <div className="mt-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
          <StatCard label="Total interviews" value={summary.total_interviews} />
          <StatCard label="Completed" value={summary.completed_interviews} />
          <StatCard label="Average score" value={formatScore(summary.average_score)} accent />
          <StatCard label="Best score" value={formatScore(summary.best_score)} accent />
        </div>

        <div className="mt-10">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-medium text-text-primary">Recent interviews</h2>
            <Link
              to="/history"
              className="flex items-center gap-1 text-sm text-text-secondary hover:text-text-primary"
            >
              View all
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>

          {!hasInterviews ? (
            <div className="mt-4 rounded-lg border border-dashed border-border py-12 text-center">
              <p className="text-sm text-text-secondary">No interviews yet.</p>
              <Link to="/interview" className="mt-2 inline-block text-sm text-accent hover:text-accent-hover">
                Start your first one
              </Link>
            </div>
          ) : (
            <div className="mt-4 divide-y divide-border-subtle overflow-hidden rounded-lg border border-border">
              {summary.recent_interviews.map((interview) => (
                <Link
                  key={interview.id}
                  to={`/report/${interview.id}`}
                  className="flex items-center justify-between gap-4 bg-surface px-5 py-4 transition-colors duration-150 hover:bg-surface-raised"
                >
                  <div>
                    <p className="text-sm font-medium text-text-primary">{interview.role_applied}</p>
                    <p className="mt-0.5 text-xs text-text-muted">
                      {interview.difficulty} · {formatDate(interview.started_at)}
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="rounded-full border border-border-subtle px-2.5 py-1 text-xs capitalize text-text-secondary">
                      {interview.status}
                    </span>
                    <span className="w-10 text-right text-sm font-medium text-text-primary">
                      {formatScore(interview.overall_score)}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </motion.div>
    </AppLayout>
  );
}