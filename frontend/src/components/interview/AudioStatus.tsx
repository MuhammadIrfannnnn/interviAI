import { Loader2, Mic, Volume2, Brain } from "lucide-react";

type VoiceState =
  | "idle"
  | "ai-speaking"
  | "ready"
  | "recording"
  | "transcribing"
  | "processing"
  | "review"
  | "completed"
  | "error";

interface AudioStatusProps {
  voiceState: VoiceState;
  voiceMode: boolean;
}

const stateConfig: Record<VoiceState, { label: string; icon: React.ReactNode } | null> = {
  idle: null,
  "ai-speaking": {
    label: "AI interviewer is speaking...",
    icon: <Volume2 className="h-3.5 w-3.5 text-accent" />,
  },
  ready: {
    label: "Click the microphone to answer",
    icon: <Mic className="h-3.5 w-3.5 text-accent" />,
  },
  recording: {
    label: "Listening...",
    icon: <Mic className="h-3.5 w-3.5 text-danger" />,
  },
  transcribing: {
    label: "Transcribing your answer...",
    icon: <Loader2 className="h-3.5 w-3.5 animate-spin text-accent" />,
  },
  processing: {
    label: "Evaluating your response...",
    icon: <Brain className="h-3.5 w-3.5 text-accent" />,
  },
  review: {
    label: "Review your answer below",
    icon: <Mic className="h-3.5 w-3.5 text-accent" />,
  },
  completed: null,
  error: null,
};

export function AudioStatus({ voiceState, voiceMode }: AudioStatusProps) {
  // In typed mode, only show status for states where the label is meaningful
  if (!voiceMode && voiceState !== "ai-speaking" && voiceState !== "processing") {
    return null;
  }

  const cfg = stateConfig[voiceState];
  if (!cfg) return null;

  return (
    <div className="flex items-center justify-center gap-2 text-xs text-text-secondary">
      {cfg.icon}
      <span>{cfg.label}</span>
    </div>
  );
}
