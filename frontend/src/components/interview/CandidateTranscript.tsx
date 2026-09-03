import { Loader2, Send, RotateCcw } from "lucide-react";
import { motion } from "framer-motion";

interface CandidateTranscriptProps {
  /** The transcribed text, or null while still transcribing. */
  transcript: string | null;
  /** Whether STT is currently in progress. */
  isTranscribing: boolean;
  /** Whether the answer is being sent to the backend. */
  isSending: boolean;
  /** Send the transcript as the candidate answer. */
  onSend: () => void;
  /** Discard the transcript and re-record. */
  onRerecord: () => void;
}

export function CandidateTranscript({
  transcript,
  isTranscribing,
  isSending,
  onSend,
  onRerecord,
}: CandidateTranscriptProps) {
  if (isTranscribing) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="mx-auto flex w-full max-w-2xl items-center justify-center gap-2 rounded-lg border border-border bg-surface px-5 py-4 text-sm text-text-secondary"
      >
        <Loader2 className="h-4 w-4 animate-spin text-accent" />
        Transcribing your answer...
      </motion.div>
    );
  }

  if (!transcript) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="mx-auto w-full max-w-2xl rounded-lg border border-accent-muted bg-accent-soft px-5 py-4"
    >
      <p className="mb-3 text-sm leading-relaxed text-text-primary">{transcript}</p>

      <div className="flex items-center gap-2">
        <button
          onClick={onSend}
          disabled={isSending}
          className="inline-flex items-center gap-1.5 rounded-md bg-accent px-3 py-1.5 text-xs font-medium text-bg transition-colors hover:bg-accent-hover disabled:opacity-50"
          aria-label="Send answer"
        >
          {isSending ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Send className="h-3.5 w-3.5" />
          )}
          Send answer
        </button>

        <button
          onClick={onRerecord}
          disabled={isSending}
          className="inline-flex items-center gap-1.5 rounded-md border border-border bg-surface px-3 py-1.5 text-xs font-medium text-text-secondary transition-colors hover:text-text-primary disabled:opacity-50"
          aria-label="Re-record answer"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          Re-record
        </button>
      </div>
    </motion.div>
  );
}
