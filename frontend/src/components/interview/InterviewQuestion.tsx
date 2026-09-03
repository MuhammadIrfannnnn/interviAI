import { motion } from "framer-motion";
import { Play, VolumeX } from "lucide-react";

interface InterviewQuestionProps {
  question: string;
  /** If true, show a "Play question" button because autoplay was blocked. */
  isAutoplayBlocked?: boolean;
  /** Callback to retry playback (must be called from a user gesture). */
  onPlayClick?: () => void;
  /** If TTS failed entirely. */
  ttsError?: string | null;
}

export function InterviewQuestion({
  question,
  isAutoplayBlocked,
  onPlayClick,
  ttsError,
}: InterviewQuestionProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="mx-auto w-full max-w-2xl rounded-lg border border-border bg-surface px-5 py-4 sm:px-6 sm:py-5"
    >
      {/* Header */}
      <div className="mb-2 flex items-center gap-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-accent">
          AI Interviewer
        </span>
      </div>

      {/* Question text */}
      <p className="text-sm leading-relaxed text-text-primary sm:text-base">
        {question}
      </p>

      {/* Autoplay blocked — show manual play button */}
      {isAutoplayBlocked && onPlayClick && (
        <button
          onClick={onPlayClick}
          className="mt-3 inline-flex items-center gap-1.5 rounded-md border border-accent-muted bg-accent-soft px-3 py-1.5 text-xs font-medium text-accent transition-colors hover:bg-accent/10"
          aria-label="Play question"
        >
          <Play className="h-3.5 w-3.5" />
          Play question
        </button>
      )}

      {/* TTS failed notice */}
      {ttsError && (
        <div className="mt-3 flex items-center gap-1.5 text-xs text-text-muted">
          <VolumeX className="h-3.5 w-3.5" />
          {ttsError}
        </div>
      )}
    </motion.div>
  );
}
