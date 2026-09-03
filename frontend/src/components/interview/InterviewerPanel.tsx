import { motion } from "framer-motion";
import { Bot } from "lucide-react";

export type InterviewerState = "idle" | "speaking" | "listening" | "thinking";

interface InterviewerPanelProps {
  state: InterviewerState;
}

/** Ring colour / animation per interviewer state. */
const ringConfig: Record<InterviewerState, { className: string; animate: boolean }> = {
  idle: { className: "border-border", animate: false },
  speaking: { className: "border-accent", animate: true },
  listening: { className: "border-border", animate: false },
  thinking: { className: "border-accent-muted", animate: true },
};

export function InterviewerPanel({ state }: InterviewerPanelProps) {
  const cfg = ringConfig[state];

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative">
        {/* Animated outer ring */}
        {cfg.animate && state === "speaking" ? (
          <motion.div
            className={`absolute -inset-3 rounded-full border-2 ${cfg.className}`}
            animate={{ scale: [1, 1.06, 1], opacity: [0.6, 1, 0.6] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          />
        ) : null}

        {cfg.animate && state === "thinking" ? (
          <motion.div
            className={`absolute -inset-3 rounded-full border-2 ${cfg.className}`}
            animate={{ opacity: [0.4, 1, 0.4] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
          />
        ) : null}

        {/* Static ring (always present for non-animated states) */}
        {!cfg.animate && (
          <div className={`absolute -inset-3 rounded-full border-2 ${cfg.className}`} />
        )}

        {/* Avatar circle */}
        <div className="relative flex h-28 w-28 items-center justify-center rounded-full bg-surface-raised sm:h-36 sm:w-36">
          <Bot className="h-12 w-12 text-text-secondary sm:h-14 sm:w-14" />
        </div>
      </div>

      {/* Status label */}
      <span className="text-xs font-medium uppercase tracking-wider text-text-muted">
        {state === "speaking" && "Speaking"}
        {state === "thinking" && "Thinking"}
        {state === "listening" && "Listening"}
        {state === "idle" && "AI Interviewer"}
      </span>
    </div>
  );
}
