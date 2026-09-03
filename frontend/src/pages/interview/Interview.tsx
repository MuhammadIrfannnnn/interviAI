import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { AxiosError } from "axios";
import {
  Loader2,
  FileWarning,
  Sparkles,
  Send,
  PartyPopper,
} from "lucide-react";

import { AppLayout } from "../../layouts/AppLayout";
import { Button } from "../../components/ui/Button";
import { RoleCombobox } from "../../components/ui/RoleCombobox";
import { InterviewerPanel, type InterviewerState } from "../../components/interview/InterviewerPanel";
import { InterviewQuestion } from "../../components/interview/InterviewQuestion";
import { InterviewControls } from "../../components/interview/InterviewControls";
import { CandidateTranscript } from "../../components/interview/CandidateTranscript";
import { AudioStatus } from "../../components/interview/AudioStatus";

import { resumeService } from "../../services/resumeService";
import { interviewService } from "../../services/interviewService";
import { audioService } from "../../services/audioService";
import { extractErrorMessage } from "../../utils/ExtractErrorMessage";
import { useAudioRecorder } from "../../hooks/useAudioRecorder";
import { useSpeech } from "../../hooks/useSpeech";
import type { MessageEvaluation } from "../../types/interview";

// ── Constants ─────────────────────────────────────────────────────────────

type Phase = "checking-resume" | "no-resume" | "setup" | "starting" | "meeting" | "completed" | "error";

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

const DIFFICULTIES = ["Easy", "Medium", "Hard"];
const MAX_ROLE_LENGTH = 100;
const MAX_ANSWER_LENGTH = 5000;

// ── Role validation (mirrors backend) ─────────────────────────────────────

const PROFESSIONAL_TITLES = new Set([
  "developer", "engineer", "architect", "administrator",
  "manager", "director", "consultant", "analyst", "executive",
  "coordinator", "strategist", "planner",
  "accountant", "auditor", "actuary", "bookkeeper",
  "doctor", "physician", "nurse", "pharmacist", "dentist",
  "surgeon", "therapist", "pathologist", "radiologist",
  "optometrist", "dietitian", "midwife",
  "lawyer", "attorney", "paralegal", "advocate", "counsel",
  "magistrate", "prosecutor",
  "teacher", "lecturer", "professor", "tutor", "educator",
  "principal", "dean",
  "designer", "illustrator", "animator", "photographer",
  "videographer", "copywriter", "journalist", "editor",
  "author", "curator", "producer", "director",
  "electrician", "plumber", "carpenter", "mechanic", "welder",
  "surveyor", "inspector", "technician",
  "biologist", "chemist", "physicist", "geologist",
  "statistician", "researcher", "scientist",
  "recruiter", "chef", "pilot", "navigator", "translator",
  "interpreter", "librarian", "phlebotomist",
]);

const PRO_SUFFIXES = ["er", "or", "ist", "ant", "ian", "ee", "man"];

function isValidRole(role: string): string | null {
  const trimmed = role.trim();
  if (!trimmed) return "Please enter a job role.";
  if (trimmed.length > MAX_ROLE_LENGTH) return `Role must be ${MAX_ROLE_LENGTH} characters or fewer.`;

  const alphaCount = [...trimmed].filter((c) => /[a-zA-Z\u00C0-\u024F]/.test(c)).length;
  if (alphaCount < 2) return "Please enter a valid professional job role.";

  let run = 1;
  for (let i = 1; i < trimmed.length; i++) {
    if (trimmed[i] === trimmed[i - 1]) {
      run++;
      if (run > 3) return "Please enter a valid professional job role.";
    } else {
      run = 1;
    }
  }

  const lower = trimmed.toLowerCase();
  for (const smash of ["asdf", "qwer", "zxcv", "wasd"]) {
    if (lower.includes(smash)) return "Please enter a valid professional job role.";
  }

  const words = trimmed.split(/\s+/);
  if (words.length >= 2) {
    const hasSubstantial = words.some(
      (w) => [...w].filter((c) => /[a-zA-Z\u00C0-\u024F]/.test(c)).length >= 4,
    );
    if (!hasSubstantial) return "Please enter a valid professional job role.";
    return null;
  }

  const word = lower;
  if (PROFESSIONAL_TITLES.has(word)) return null;
  if (word.length >= 5 && PRO_SUFFIXES.some((s) => word.endsWith(s))) return null;
  if (word.length >= 8) return null;

  return "Please enter a valid professional job role.";
}

// ── Derived helpers ───────────────────────────────────────────────────────

/** Map voiceState → InterviewerPanel state. */
function panelState(voiceState: VoiceState): InterviewerState {
  switch (voiceState) {
    case "ai-speaking": return "speaking";
    case "transcribing":
    case "processing":  return "thinking";
    case "recording":   return "listening";
    default:            return "idle";
  }
}

// ── Component ─────────────────────────────────────────────────────────────

export default function Interview() {
  const navigate = useNavigate();

  // Core interview state
  const [phase, setPhase] = useState<Phase>("checking-resume");
  const [roleApplied, setRoleApplied] = useState("");
  const [difficulty, setDifficulty] = useState("Easy");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Session / question state
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState("");
  const [lastEvaluation, setLastEvaluation] = useState<MessageEvaluation | null>(null);

  // Voice state machine
  const [voiceState, setVoiceState] = useState<VoiceState>("idle");
  const [voiceMode, setVoiceMode] = useState(true);

  // Typed answer (for typed mode fallback)
  const [typedAnswer, setTypedAnswer] = useState("");

  // Transcript from STT (for review before sending)
  const [transcript, setTranscript] = useState<string | null>(null);

  // Hooks
  const recorder = useAudioRecorder();

  // Called by useSpeech whenever AI audio finishes playing naturally —
  // this is the single place that re-enables answering after speech.
  const handlePlaybackEnd = useCallback(() => {
    setVoiceState((v) => (v === "ai-speaking" ? "ready" : v));
  }, []);

  const speech = useSpeech({ onPlaybackEnd: handlePlaybackEnd });

  // Refs for cleanup
  const sessionEndedRef = useRef(false);

  // Disable voice mode if mic is not supported or errored
  useEffect(() => {
    if (!recorder.isSupported) {
      setVoiceMode(false);
    }
  }, [recorder.isSupported]);

  // If recorder errors (permission denied, etc.), fall back to typed
  useEffect(() => {
    if (recorder.error) {
      setVoiceMode(false);
      setErrorMessage(recorder.error);
      // If we were in a voice flow, revert to ready
      if (voiceState === "recording" || voiceState === "transcribing") {
        setVoiceState("ready");
      }
    }
  }, [recorder.error]); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Resume check ──────────────────────────────────────────────────────

  useEffect(() => {
    let cancelled = false;

    async function checkResume() {
      try {
        await resumeService.getResume();
        if (!cancelled) setPhase("setup");
      } catch (err) {
        if (cancelled) return;
        if (err instanceof AxiosError && err.response?.status === 404) {
          setPhase("no-resume");
        } else {
          setErrorMessage("Couldn't check your resume status. Try refreshing.");
          setPhase("error");
        }
      }
    }

    checkResume();
    return () => { cancelled = true; };
  }, []);

  // ── TTS: speak current question ──────────────────────────────────────

  const speakQuestion = useCallback(
    async (question: string) => {
      setVoiceState("ai-speaking");
      const result = await speech.speak(question);
      if (result === "failed") {
        // TTS unavailable — the question text is still visible, so let
        // the candidate answer. The muted notice is shown by the question card.
        setVoiceState((v) => (v === "ai-speaking" ? "ready" : v));
      }
      // "played"  → handlePlaybackEnd transitions to "ready"
      // "blocked" → stay "ai-speaking" until the user plays the audio
      // "stopped" → superseded by a newer question or interview end
    },
    [speech],
  );

  // ── Interview start ───────────────────────────────────────────────────

  const handleStart = async () => {
    const roleError = isValidRole(roleApplied);
    if (roleError) { setErrorMessage(roleError); return; }

    setErrorMessage(null);
    setPhase("starting");
    try {
      const data = await interviewService.start({
        role_applied: roleApplied.trim(),
        difficulty,
      });
      setSessionId(data.session_id);
      setCurrentQuestion(data.first_question);
      setPhase("meeting");

      // Trigger TTS for the first question
      void speakQuestion(data.first_question);
    } catch (err) {
      setErrorMessage(extractErrorMessage(err, "Couldn't start the interview. Try again."));
      setPhase("setup");
    }
  };

  // ── Send answer to /interview/message ─────────────────────────────────

  const submitAnswer = useCallback(
    async (answerText: string) => {
      if (sessionId === null) return;

      setVoiceState("processing");
      setTranscript(null);
      setTypedAnswer("");

      try {
        const data = await interviewService.sendMessage({
          session_id: sessionId,
          answer: answerText,
        });

        setLastEvaluation(data.evaluation ?? null);

        if (data.next_question) {
          setCurrentQuestion(data.next_question);
          void speakQuestion(data.next_question);
        } else {
          // Interview ended
          setVoiceState("completed");
          setPhase("completed");
        }
      } catch (err) {
        setErrorMessage(extractErrorMessage(err, "Couldn't send your answer. Try again."));
        setVoiceState("ready");
      }
    },
    [sessionId, speakQuestion],
  );

  // ── Recorder: audioBlob arrived → transcribe ─────────────────────────

  useEffect(() => {
    if (!recorder.audioBlob || voiceState !== "recording") return;

    // The recorder has just stopped (onstop fired, audioBlob set).
    // We transition to transcribing after the stop, but the recording state
    // was already set to false by the recorder. Let's check isRecording.
    if (recorder.isRecording) return; // still recording, not yet stopped

    setVoiceState("transcribing");

    audioService
      .transcribe(recorder.audioBlob)
      .then(({ text }) => {
        if (!text.trim()) {
          setErrorMessage("Could not detect any speech. Please try again or type your answer.");
          setVoiceState("ready");
          return;
        }
        setTranscript(text);
        setVoiceState("review");
      })
      .catch(() => {
        setErrorMessage("Couldn't transcribe your answer. Please try again or type your answer.");
        setVoiceState("ready");
      });
  }, [recorder.audioBlob, recorder.isRecording]); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Mic click handler ────────────────────────────────────────────────

  const handleMicClick = () => {
    if (voiceState === "recording") {
      recorder.stopRecording();
      // State will transition via the audioBlob effect above
    } else if (voiceState === "ready") {
      setTranscript(null);
      recorder.startRecording();
      setVoiceState("recording");
    }
  };

  // ── Typed send handler ───────────────────────────────────────────────

  const handleTypedSend = () => {
    const trimmed = typedAnswer.trim();
    if (!trimmed || voiceState !== "ready") return;
    if (trimmed.length > MAX_ANSWER_LENGTH) {
      setErrorMessage(`Answer must be ${MAX_ANSWER_LENGTH} characters or fewer.`);
      return;
    }
    submitAnswer(trimmed);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleTypedSend();
    }
  };

  // ── Transcript review actions ────────────────────────────────────────

  const handleSendTranscript = () => {
    if (!transcript) return;
    submitAnswer(transcript);
  };

  const handleRerecord = () => {
    setTranscript(null);
    recorder.clearBlob();
    setVoiceState("ready");
  };

  // ── End interview ────────────────────────────────────────────────────

  const handleEndInterview = () => {
    if (sessionEndedRef.current) return;
    sessionEndedRef.current = true;

    speech.stopSpeaking();
    if (recorder.isRecording) recorder.stopRecording();
    setVoiceState("completed");
    setPhase("completed");
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      speech.stopSpeaking();
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Toggle voice/typed mode ──────────────────────────────────────────

  const toggleVoiceMode = () => {
    if (voiceState === "recording" || voiceState === "transcribing" || voiceState === "processing") return;
    if (voiceMode) {
      // Switching voice → typed: stop any pending AI audio so the candidate
      // can answer immediately instead of waiting for playback to finish.
      speech.stopSpeaking();
      setVoiceState("ready");
    }
    setVoiceMode((prev) => !prev);
    setTranscript(null);
    recorder.clearBlob();
  };

  // ── Render ────────────────────────────────────────────────────────────

  return (
    <AppLayout>
      <motion.div
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="mx-auto max-w-3xl"
      >
        {/* ── Checking resume ──────────────────────────────────────── */}
        {phase === "checking-resume" && (
          <div className="flex h-64 items-center justify-center">
            <Loader2 className="h-5 w-5 animate-spin text-text-muted" />
          </div>
        )}

        {/* ── Error ────────────────────────────────────────────────── */}
        {phase === "error" && (
          <div className="rounded-md border border-danger bg-danger-soft px-4 py-3 text-sm text-danger">
            {errorMessage}
          </div>
        )}

        {/* ── No resume ────────────────────────────────────────────── */}
        {phase === "no-resume" && (
          <div className="flex flex-col items-center rounded-lg border border-border bg-surface px-6 py-16 text-center">
            <FileWarning className="h-8 w-8 text-text-muted" />
            <p className="mt-4 text-sm font-medium text-text-primary">Upload your resume first</p>
            <p className="mt-1 max-w-sm text-sm text-text-secondary">
              InterviAI tailors interview questions to your background, so a resume needs to be on
              file before a session can start.
            </p>
            <Link to="/resume" className="mt-6">
              <Button>Upload resume</Button>
            </Link>
          </div>
        )}

        {/* ── Setup / Starting ─────────────────────────────────────── */}
        {(phase === "setup" || phase === "starting") && (
          <div>
            <h1 className="text-xl font-semibold text-text-primary">Set up your interview</h1>
            <p className="mt-1 text-sm text-text-secondary">
              Questions will be tailored to your resume and the role below.
            </p>

            {errorMessage && (
              <div className="mt-4 rounded-md border border-danger bg-danger-soft px-4 py-2.5 text-sm text-danger">
                {errorMessage}
              </div>
            )}

            <div className="mt-6 flex flex-col gap-4">
              <RoleCombobox
                value={roleApplied}
                onChange={setRoleApplied}
                disabled={phase === "starting"}
              />

              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-text-secondary">Difficulty</label>
                <div className="flex gap-2">
                  {DIFFICULTIES.map((level) => (
                    <button
                      key={level}
                      type="button"
                      disabled={phase === "starting"}
                      onClick={() => setDifficulty(level)}
                      className={`h-10 flex-1 rounded-md border text-sm transition-colors duration-150 disabled:opacity-50 ${
                        difficulty === level
                          ? "border-accent bg-accent-soft text-accent"
                          : "border-border text-text-secondary hover:text-text-primary"
                      }`}
                    >
                      {level}
                    </button>
                  ))}
                </div>
              </div>

              <Button onClick={handleStart} isLoading={phase === "starting"} className="mt-2 w-full">
                <Sparkles className="h-4 w-4" />
                Start interview
              </Button>
            </div>
          </div>
        )}

        {/* ── Meeting phase ────────────────────────────────────────── */}
        {phase === "meeting" && (
          <div className="flex flex-col items-center gap-6">
            {/* Role / difficulty badge */}
            <div className="flex w-full items-center justify-between">
              <div>
                <p className="text-sm font-medium text-text-primary">{roleApplied}</p>
                <p className="text-xs text-text-muted">{difficulty}</p>
              </div>
            </div>

            {/* Error banner */}
            <AnimatePresence>
              {errorMessage && (
                <motion.div
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -4 }}
                  className="w-full rounded-md border border-danger bg-danger-soft px-4 py-2.5 text-sm text-danger"
                >
                  {errorMessage}
                </motion.div>
              )}
            </AnimatePresence>

            {/* AI Interviewer panel */}
            <InterviewerPanel state={panelState(voiceState)} />

            {/* Audio status label */}
            <AudioStatus voiceState={voiceState} voiceMode={voiceMode} />

            {/* Current question card */}
            <AnimatePresence mode="wait">
              <InterviewQuestion
                key={currentQuestion}
                question={currentQuestion}
                isAutoplayBlocked={speech.isAutoplayBlocked}
                onPlayClick={speech.retryAutoplay}
                ttsError={speech.ttsError}
              />
            </AnimatePresence>

            {/* Last evaluation feedback */}
            {lastEvaluation && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="w-full max-w-2xl rounded-md border border-border bg-surface px-4 py-3"
              >
                <p className="text-xs text-text-muted">
                  <span className="font-medium text-text-secondary">Last answer</span>
                  {" — "}
                  {lastEvaluation.feedback}
                </p>
              </motion.div>
            )}

            {/* ── Voice mode: transcript review area ──────────────── */}
            {voiceMode && (
              <CandidateTranscript
                transcript={transcript}
                isTranscribing={voiceState === "transcribing"}
                isSending={voiceState === "processing"}
                onSend={handleSendTranscript}
                onRerecord={handleRerecord}
              />
            )}

            {/* ── Typed mode: textarea ────────────────────────────── */}
            {!voiceMode && voiceState === "ready" && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex w-full max-w-2xl items-end gap-2"
              >
                <textarea
                  value={typedAnswer}
                  onChange={(e) => {
                    if (e.target.value.length <= MAX_ANSWER_LENGTH) {
                      setTypedAnswer(e.target.value);
                    }
                  }}
                  onKeyDown={handleKeyDown}
                  placeholder="Type your answer... (Enter to send, Shift+Enter for new line)"
                  rows={3}
                  maxLength={MAX_ANSWER_LENGTH}
                  className="h-20 flex-1 resize-none rounded-md border border-border bg-surface px-3 py-2.5 text-sm text-text-primary
                    placeholder:text-text-muted outline-none transition-colors duration-150
                    focus:border-accent focus:ring-1 focus:ring-accent"
                />
                <Button
                  onClick={handleTypedSend}
                  disabled={!typedAnswer.trim()}
                  className="h-20 w-14 shrink-0"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </motion.div>
            )}

            {/* Processing spinner for typed mode */}
            {!voiceMode && voiceState === "processing" && (
              <div className="flex items-center gap-2 text-sm text-text-secondary">
                <Loader2 className="h-4 w-4 animate-spin text-accent" />
                Evaluating your response...
              </div>
            )}

            {/* ── Controls ─────────────────────────────────────────── */}
            <InterviewControls
              voiceState={voiceState}
              micSupported={recorder.isSupported}
              voiceMode={voiceMode}
              onToggleVoiceMode={toggleVoiceMode}
              onMicClick={handleMicClick}
              onEndInterview={handleEndInterview}
            />
          </div>
        )}

        {/* ── Completed ────────────────────────────────────────────── */}
        {phase === "completed" && (
          <div className="flex flex-col items-center gap-4 rounded-lg border border-border bg-surface px-6 py-16 text-center">
            <PartyPopper className="h-10 w-10 text-accent" />
            <h2 className="text-lg font-semibold text-text-primary">Interview complete</h2>
            <p className="max-w-sm text-sm text-text-secondary">
              Great job! Your interview has been evaluated. Check the full report for detailed
              feedback and recommendations.
            </p>
            <Button onClick={() => sessionId && navigate(`/report/${sessionId}`)}>
              View full report
            </Button>
          </div>
        )}
      </motion.div>
    </AppLayout>
  );
}
