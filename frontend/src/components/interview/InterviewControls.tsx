import { Mic, PhoneOff, Square } from "lucide-react";
import { motion } from "framer-motion";

interface InterviewControlsProps {
  /** Current voice state of the interview. */
  voiceState: string;
  /** Whether the browser supports MediaRecorder. */
  micSupported: boolean;
  /** Whether voice mode is currently active (vs typed mode). */
  voiceMode: boolean;
  /** Toggle between voice and typed mode. */
  onToggleVoiceMode: () => void;
  /** Called when the candidate clicks the mic button. */
  onMicClick: () => void;
  /** Called when the candidate ends the interview. */
  onEndInterview: () => void;
}

export function InterviewControls({
  voiceState,
  micSupported,
  voiceMode,
  onToggleVoiceMode,
  onMicClick,
  onEndInterview,
}: InterviewControlsProps) {
  const isRecording = voiceState === "recording";
  const canRecord = voiceState === "ready" && voiceMode && micSupported;

  return (
    <div className="flex flex-col items-center gap-4">
      {/* Voice / Type toggle */}
      {micSupported && (
        <div className="flex items-center gap-1 rounded-full border border-border bg-surface px-1 py-1">
          <button
            onClick={() => { if (voiceMode) onToggleVoiceMode(); }}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              voiceMode
                ? "bg-accent-soft text-accent"
                : "text-text-muted hover:text-text-secondary"
            }`}
            disabled={voiceState === "recording" || voiceState === "transcribing" || voiceState === "processing"}
          >
            <span className="flex items-center gap-1">
              <Mic className="h-3 w-3" /> Voice
            </span>
          </button>
          <button
            onClick={() => { if (!voiceMode) onToggleVoiceMode(); }}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              !voiceMode
                ? "bg-accent-soft text-accent"
                : "text-text-muted hover:text-text-secondary"
            }`}
            disabled={voiceState === "recording" || voiceState === "transcribing" || voiceState === "processing"}
          >
            Type
          </button>
        </div>
      )}

      {/* Control buttons */}
      <div className="flex items-center gap-3">
        {/* Microphone button (only in voice mode) */}
        {voiceMode && micSupported && (
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={onMicClick}
            disabled={!canRecord && !isRecording}
            aria-label={isRecording ? "Stop recording" : "Start recording"}
            className={`relative flex h-14 w-14 items-center justify-center rounded-full border-2 transition-colors
              ${isRecording
                ? "border-danger bg-danger/10 text-danger"
                : canRecord
                  ? "border-accent bg-accent-soft text-accent hover:bg-accent/10"
                  : "border-border bg-surface text-text-muted opacity-50"
              }`}
          >
            {isRecording ? (
              <Square className="h-5 w-5" />
            ) : (
              <Mic className="h-5 w-5" />
            )}

            {/* Recording pulse ring */}
            {isRecording && (
              <motion.div
                className="absolute inset-0 rounded-full border-2 border-danger"
                animate={{ scale: [1, 1.15, 1], opacity: [0.6, 0, 0.6] }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
              />
            )}
          </motion.button>
        )}

        {/* End interview */}
        <motion.button
          whileTap={{ scale: 0.95 }}
          onClick={onEndInterview}
          aria-label="End interview"
          className="flex h-14 w-14 items-center justify-center rounded-full border-2 border-danger bg-danger/10 text-danger transition-colors hover:bg-danger/20"
        >
          <PhoneOff className="h-5 w-5" />
        </motion.button>
      </div>
    </div>
  );
}
