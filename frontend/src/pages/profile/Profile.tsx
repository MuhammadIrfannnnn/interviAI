import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { AxiosError } from "axios";
import { Loader2, FileText, LogOut, Mail } from "lucide-react";

import { AppLayout } from "../../layouts/AppLayout";
import { Button } from "../../components/ui/Button";
import { StatCard } from "../../components/ui/StatCard";
import { useAuth } from "../../hooks/useAuth";
import { resumeService } from "../../services/resumeService";
import { dashboardService } from "../../services/DashboardService";
import type { ResumeResponse } from "../../types/resume";
import type { DashboardSummary } from "../../types/Dashboard";

function initials(name?: string, email?: string) {
  if (name) {
    return name
      .split(" ")
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase())
      .join("");
  }
  return email?.[0]?.toUpperCase() ?? "?";
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function Profile() {
  const { user, logout } = useAuth();
  const [resume, setResume] = useState<ResumeResponse | null>(null);
  const [hasResume, setHasResume] = useState<boolean | null>(null);
  const [stats, setStats] = useState<DashboardSummary | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadResume() {
      try {
        const data = await resumeService.getResume();
        if (!cancelled) {
          setResume(data);
          setHasResume(true);
        }
      } catch (err) {
        if (cancelled) return;
        if (err instanceof AxiosError && err.response?.status === 404) {
          setHasResume(false);
        }
      }
    }

    async function loadStats() {
      try {
        const data = await dashboardService.getSummary();
        if (!cancelled) setStats(data);
      } catch {
        // Non-critical for this page — fail silently, stats section just won't render.
      }
    }

    loadResume();
    loadStats();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <AppLayout>
      <motion.div
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="mx-auto max-w-2xl"
      >
        <h1 className="text-xl font-semibold text-text-primary">Profile</h1>

        {/* Identity card */}
        <div className="mt-6 flex items-center gap-4 rounded-lg border border-border bg-surface p-5">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-accent-soft text-lg font-medium text-accent">
            {initials(user?.full_name, user?.email)}
          </div>
          <div>
            <p className="text-base font-medium text-text-primary">{user?.full_name ?? user?.email ?? "—"}</p>
            <div className="mt-1 flex items-center gap-1.5 text-sm text-text-secondary">
              <Mail className="h-3.5 w-3.5" />
              {user?.email}
            </div>
          </div>
        </div>

        {/* Practice stats */}
        {stats && (
          <div className="mt-6">
            <p className="text-sm font-medium text-text-primary">Practice stats</p>
            <div className="mt-3 grid grid-cols-3 gap-3">
              <StatCard label="Total interviews" value={stats.total_interviews} />
              <StatCard label="Completed" value={stats.completed_interviews} />
              <StatCard label="Best score" value={stats.best_score.toFixed(1)} accent />
            </div>
          </div>
        )}

        {/* Resume summary */}
        <div className="mt-6">
          <p className="text-sm font-medium text-text-primary">Resume</p>

          {hasResume === null && (
            <div className="mt-3 flex h-16 items-center justify-center rounded-lg border border-border bg-surface">
              <Loader2 className="h-4 w-4 animate-spin text-text-muted" />
            </div>
          )}

          {hasResume === false && (
            <div className="mt-3 flex items-center justify-between rounded-lg border border-dashed border-border bg-surface px-5 py-4">
              <p className="text-sm text-text-secondary">No resume uploaded yet.</p>
              <Link to="/resume">
                <Button variant="ghost">Upload</Button>
              </Link>
            </div>
          )}

          {hasResume && resume && (
            <div className="mt-3 flex items-center justify-between rounded-lg border border-border bg-surface px-5 py-4">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-md bg-surface-raised">
                  <FileText className="h-4 w-4 text-text-secondary" />
                </div>
                <div>
                  <p className="text-sm font-medium text-text-primary">{resume.resume.file_name}</p>
                  <p className="text-xs text-text-muted">
                    Uploaded {formatDate(resume.resume.uploaded_at)}
                  </p>
                </div>
              </div>
              <Link to="/resume">
                <Button variant="ghost">Manage</Button>
              </Link>
            </div>
          )}
        </div>

        {/* Sign out */}
        <div className="mt-10 border-t border-border-subtle pt-6">
          <Button variant="ghost" onClick={logout}>
            <LogOut className="h-4 w-4" />
            Sign out
          </Button>
        </div>
      </motion.div>
    </AppLayout>
  );
}
