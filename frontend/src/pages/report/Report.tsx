import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Loader2,
  Download,
  ThumbsUp,
  ThumbsDown,
  Sparkles,
  AlertTriangle,
  Map as MapIcon,
} from "lucide-react";

import { AppLayout } from "../../layouts/AppLayout";
import { Button } from "../../components/ui/Button";
import { StatCard } from "../../components/ui/StatCard";
import { interviewService } from "../../services/interviewService";
import type { InterviewDetails } from "../../types/interview";

function formatScore(score: number) {
  return score.toFixed(1);
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function recommendationTone(recommendation: string) {
  const lower = recommendation.toLowerCase();
  if (lower.includes("strong hire") || lower.includes("hire")) {
    return "border-accent-muted bg-accent-soft text-accent";
  }
  if (lower.includes("no hire")) {
    return "border-danger bg-danger-soft text-danger";
  }
  return "border-border-subtle bg-surface-raised text-text-secondary";
}

export default function Report() {
  const { id } = useParams<{ id: string }>();
  const sessionId = Number(id);

  const [details, setDetails] = useState<InterviewDetails | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isExporting, setIsExporting] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data = await interviewService.getDetails(sessionId);
        if (!cancelled) setDetails(data);
      } catch {
        if (!cancelled) setError("Couldn't load this interview report.");
      }
    }

    if (!Number.isNaN(sessionId)) load();
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const blob = await interviewService.exportReport(sessionId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `interview-report-${sessionId}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      setError("Couldn't export the report. Try again.");
    } finally {
      setIsExporting(false);
    }
  };

  if (error) {
    return (
      <AppLayout>
        <div className="rounded-md border border-danger bg-danger-soft px-4 py-3 text-sm text-danger">
          {error}
        </div>
      </AppLayout>
    );
  }

  if (!details) {
    return (
      <AppLayout>
        <div className="flex h-64 items-center justify-center">
          <Loader2 className="h-5 w-5 animate-spin text-text-muted" />
        </div>
      </AppLayout>
    );
  }

  const { session, messages, report } = details;

  return (
    <AppLayout>
      <motion.div
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="mx-auto max-w-3xl"
      >
        {/* Header */}
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-xl font-semibold text-text-primary">{session.role_applied}</h1>
            <p className="mt-1 text-sm text-text-secondary">
              {session.difficulty} · {formatDate(session.started_at)}
              {session.ended_at && ` – ${formatDate(session.ended_at)}`}
            </p>
          </div>
          {report && (
            <Button onClick={handleExport} isLoading={isExporting} variant="ghost">
              <Download className="h-4 w-4" />
              Export PDF
            </Button>
          )}
        </div>

        {!report ? (
          <div className="mt-8 rounded-lg border border-dashed border-border py-12 text-center">
            <p className="text-sm text-text-secondary">
              This interview is still in progress — a report generates once it's completed.
            </p>
          </div>
        ) : (
          <>
            {/* Score breakdown */}
            <div className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-5">
              <StatCard label="Overall" value={formatScore(report.overall_score)} accent />
              <StatCard label="Technical" value={formatScore(report.technical_score)} />
              <StatCard label="Communication" value={formatScore(report.communication_score)} />
              <StatCard label="Confidence" value={formatScore(report.confidence_score)} />
              <StatCard label="Problem solving" value={formatScore(report.problem_solving_score)} />
            </div>

            {/* Recommendation */}
            <div
              className={`mt-6 inline-flex items-center rounded-full border px-3 py-1 text-sm font-medium ${recommendationTone(
                report.recommendation
              )}`}
            >
              {report.recommendation}
            </div>

            {/* Overall feedback */}
            <div className="mt-6 rounded-lg border border-border bg-surface p-5">
              <p className="text-sm leading-relaxed text-text-secondary">{report.overall_feedback}</p>
            </div>

            {/* Strengths / weaknesses */}
            <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="rounded-lg border border-border bg-surface p-5">
                <div className="flex items-center gap-1.5 text-xs uppercase tracking-wide text-text-muted">
                  <ThumbsUp className="h-3.5 w-3.5" />
                  Strengths
                </div>
                <ul className="mt-3 flex flex-col gap-2">
                  {report.strengths.map((s) => (
                    <li key={s} className="text-sm leading-relaxed text-text-secondary">
                      {s}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="rounded-lg border border-border bg-surface p-5">
                <div className="flex items-center gap-1.5 text-xs uppercase tracking-wide text-text-muted">
                  <ThumbsDown className="h-3.5 w-3.5" />
                  Weaknesses
                </div>
                <ul className="mt-3 flex flex-col gap-2">
                  {report.weaknesses.map((w) => (
                    <li key={w} className="text-sm leading-relaxed text-text-secondary">
                      {w}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Concerns */}
            {report.concerns.length > 0 && (
              <div className="mt-6 rounded-lg border border-border bg-surface p-5">
                <div className="flex items-center gap-1.5 text-xs uppercase tracking-wide text-text-muted">
                  <AlertTriangle className="h-3.5 w-3.5" />
                  Concerns
                </div>
                <ul className="mt-3 flex flex-col gap-2">
                  {report.concerns.map((c) => (
                    <li key={c} className="text-sm leading-relaxed text-text-secondary">
                      {c}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Competency breakdown */}
            <div className="mt-6">
              <p className="text-sm font-medium text-text-primary">Competencies</p>
              <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
                {report.competency_reports.map((c) => (
                  <div key={c.competency} className="rounded-lg border border-border bg-surface p-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium capitalize text-text-primary">
                        {c.competency.replace(/_/g, " ")}
                      </span>
                      <span className="rounded-full border border-accent-muted bg-accent-soft px-2 py-0.5 text-xs text-accent">
                        {c.level}
                      </span>
                    </div>
                    <p className="mt-2 text-sm leading-relaxed text-text-secondary">{c.summary}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Learning roadmap */}
            {report.learning_roadmap.length > 0 && (
              <div className="mt-6 rounded-lg border border-border bg-surface p-5">
                <div className="flex items-center gap-1.5 text-xs uppercase tracking-wide text-text-muted">
                  <MapIcon className="h-3.5 w-3.5" />
                  Learning roadmap
                </div>
                <ol className="mt-3 flex flex-col gap-2">
                  {report.learning_roadmap.map((item, i) => (
                    <li key={item} className="flex gap-2.5 text-sm leading-relaxed text-text-secondary">
                      <span className="font-mono text-xs text-text-muted">{i + 1}.</span>
                      {item}
                    </li>
                  ))}
                </ol>
              </div>
            )}
          </>
        )}

        {/* Conversation timeline */}
        <div className="mt-10">
          <div className="flex items-center gap-1.5 text-sm font-medium text-text-primary">
            <Sparkles className="h-4 w-4 text-accent" />
            Conversation
          </div>

          <div className="mt-4 flex flex-col gap-3">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex ${msg.speaker === "AI" ? "justify-start" : "justify-end"}`}>
                <div className="flex max-w-lg flex-col gap-2">
                  <div
                    className={`rounded-lg border px-4 py-3 text-sm leading-relaxed ${
                      msg.speaker === "AI"
                        ? "border-border bg-surface-raised text-text-primary"
                        : "border-accent-muted bg-accent-soft text-text-primary"
                    }`}
                  >
                    {msg.message}
                  </div>

                  {msg.evaluation && (
                    <div className="rounded-lg border border-border-subtle bg-surface px-4 py-3">
                      <div className="flex flex-wrap gap-3 text-xs text-text-muted">
                        <span>Technical {msg.evaluation.technical_score}</span>
                        <span>Communication {msg.evaluation.communication_score}</span>
                        <span>Confidence {msg.evaluation.confidence_score}</span>
                        <span className="text-text-secondary">{msg.evaluation.correctness}</span>
                      </div>
                      <p className="mt-2 text-xs leading-relaxed text-text-secondary">
                        {msg.evaluation.feedback}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    </AppLayout>
  );
}
