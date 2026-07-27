import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Loader2, Inbox } from "lucide-react";

import { AppLayout } from "../../layouts/AppLayout";
import { interviewService } from "../../services/interviewService";
import type { InterviewHistoryItem } from "../../types/interview";

type Filter = "all" | "active" | "completed";

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatScore(score: number | null) {
  return score === null ? "—" : `${Math.round(score)}`;
}

export default function History() {
  const [interviews, setInterviews] = useState<InterviewHistoryItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<Filter>("all");

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data = await interviewService.getHistory();
        if (!cancelled) setInterviews(data);
      } catch {
        if (!cancelled) setError("Couldn't load your interview history. Try refreshing the page.");
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const filtered = useMemo(() => {
    if (!interviews) return [];
    if (filter === "all") return interviews;
    return interviews.filter((i) => i.status.toLowerCase() === filter);
  }, [interviews, filter]);

  const filters: { key: Filter; label: string }[] = [
    { key: "all", label: "All" },
    { key: "active", label: "Active" },
    { key: "completed", label: "Completed" },
  ];

  return (
    <AppLayout>
      <motion.div
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
      >
        <h1 className="text-xl font-semibold text-text-primary">Interview history</h1>
        <p className="mt-1 text-sm text-text-secondary">Every session you've started, in one place.</p>

        <div className="mt-6 flex gap-1.5">
          {filters.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => setFilter(key)}
              className={`h-8 rounded-md px-3 text-sm transition-colors duration-150 ${
                filter === key
                  ? "bg-surface-raised text-text-primary"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        <div className="mt-5">
          {error && (
            <div className="rounded-md border border-danger bg-danger-soft px-4 py-3 text-sm text-danger">
              {error}
            </div>
          )}

          {!error && interviews === null && (
            <div className="flex h-48 items-center justify-center">
              <Loader2 className="h-5 w-5 animate-spin text-text-muted" />
            </div>
          )}

          {!error && interviews !== null && filtered.length === 0 && (
            <div className="flex flex-col items-center rounded-lg border border-dashed border-border py-16 text-center">
              <Inbox className="h-6 w-6 text-text-muted" />
              <p className="mt-3 text-sm text-text-secondary">
                {interviews.length === 0 ? "No interviews yet." : `No ${filter} interviews.`}
              </p>
              {interviews.length === 0 && (
                <Link to="/interview" className="mt-2 text-sm text-accent hover:text-accent-hover">
                  Start your first one
                </Link>
              )}
            </div>
          )}

          {!error && filtered.length > 0 && (
            <div className="divide-y divide-border-subtle overflow-hidden rounded-lg border border-border">
              {filtered.map((interview) => (
                <Link
                  key={interview.session_id}
                  to={`/report/${interview.session_id}`}
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
