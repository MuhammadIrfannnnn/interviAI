import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { AxiosError } from "axios";
import {
  Loader2,
  FileWarning,
  Sparkles,
  Send,
  CheckCircle2,
  PartyPopper,
} from "lucide-react";

import { AppLayout } from "../../layouts/AppLayout";
import { Button } from "../../components/ui/Button";
import { resumeService } from "../../services/resumeService";
import { interviewService } from "../../services/interviewService";
import type { MessageEvaluation } from "../../types/interview";

type Phase = "checking-resume" | "no-resume" | "setup" | "starting" | "chat" | "sending" | "completed" | "error";

const DIFFICULTIES = ["Easy", "Medium", "Hard"];

interface ChatMessage {
  id: string;
  speaker: "AI" | "candidate";
  text: string;
  evaluation?: MessageEvaluation;
}

export default function Interview() {
  const navigate = useNavigate();
  const [phase, setPhase] = useState<Phase>("checking-resume");
  const [roleApplied, setRoleApplied] = useState("");
  const [difficulty, setDifficulty] = useState("Easy");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [sessionId, setSessionId] = useState<number | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [answer, setAnswer] = useState("");

  const scrollRef = useRef<HTMLDivElement>(null);

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
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, phase]);

  const handleStart = async () => {
    if (!roleApplied.trim()) {
      setErrorMessage("Enter the role you're interviewing for.");
      return;
    }

    setErrorMessage(null);
    setPhase("starting");
    try {
      const data = await interviewService.start({ role_applied: roleApplied.trim(), difficulty });
      setSessionId(data.session_id);
      setMessages([{ id: `q-${data.session_id}-0`, speaker: "AI", text: data.first_question }]);
      setPhase("chat");
    } catch {
      setErrorMessage("Couldn't start the interview. Try again.");
      setPhase("setup");
    }
  };

  const handleSend = async () => {
    if (!answer.trim() || sessionId === null) return;

    const candidateMsg: ChatMessage = {
      id: `a-${Date.now()}`,
      speaker: "candidate",
      text: answer.trim(),
    };
    setMessages((prev) => [...prev, candidateMsg]);
    setAnswer("");
    setPhase("sending");

    try {
      const data = await interviewService.sendMessage({
        session_id: sessionId,
        answer: candidateMsg.text,
      });

      // Attach the evaluation to the answer that was just sent.
      setMessages((prev) =>
        prev.map((m) => (m.id === candidateMsg.id ? { ...m, evaluation: data.evaluation } : m))
      );

      if (data.next_question) {
        setMessages((prev) => [
          ...prev,
          { id: `q-${Date.now()}`, speaker: "AI", text: data.next_question as string },
        ]);
        setPhase("chat");
      } else {
        // No next question — treat as the interview having ended. Pull the
        // closing message and full report from the details endpoint.
        try {
          const details = await interviewService.getDetails(sessionId);
          const closing = details.messages[details.messages.length - 1];
          if (closing?.speaker === "AI") {
            setMessages((prev) => [
              ...prev,
              { id: `closing-${closing.id}`, speaker: "AI", text: closing.message },
            ]);
          }
        } catch {
          // Non-critical — completion screen still works without the closing line.
        }
        setPhase("completed");
      }
    } catch {
      setErrorMessage("Couldn't send your answer. Try again.");
      setPhase("chat");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <AppLayout>
      <motion.div
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="mx-auto max-w-2xl"
      >
        {phase === "checking-resume" && (
          <div className="flex h-64 items-center justify-center">
            <Loader2 className="h-5 w-5 animate-spin text-text-muted" />
          </div>
        )}

        {phase === "error" && (
          <div className="rounded-md border border-danger bg-danger-soft px-4 py-3 text-sm text-danger">
            {errorMessage}
          </div>
        )}

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
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-text-secondary">Role</label>
                <input
                  value={roleApplied}
                  onChange={(e) => setRoleApplied(e.target.value)}
                  placeholder="e.g. Backend developer"
                  disabled={phase === "starting"}
                  className="h-10 rounded-md border border-border bg-surface px-3 text-sm text-text-primary
                    placeholder:text-text-muted outline-none transition-colors duration-150
                    focus:border-accent focus:ring-1 focus:ring-accent disabled:opacity-50"
                />
              </div>

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

        {(phase === "chat" || phase === "sending" || phase === "completed") && (
          <div className="flex flex-col">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-text-primary">{roleApplied}</p>
                <p className="text-xs text-text-muted">{difficulty}</p>
              </div>
              {phase === "completed" && (
                <span className="flex items-center gap-1.5 rounded-full border border-accent-muted bg-accent-soft px-2.5 py-1 text-xs text-accent">
                  <PartyPopper className="h-3.5 w-3.5" />
                  Complete
                </span>
              )}
            </div>

            {errorMessage && (
              <div className="mt-3 rounded-md border border-danger bg-danger-soft px-4 py-2.5 text-sm text-danger">
                {errorMessage}
              </div>
            )}

            <div className="mt-4 flex max-h-[55vh] flex-col gap-3 overflow-y-auto pr-1">
              <AnimatePresence initial={false}>
                {messages.map((msg) => (
                  <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.25 }}
                    className={`flex ${msg.speaker === "AI" ? "justify-start" : "justify-end"}`}
                  >
                    <div className="flex max-w-md flex-col gap-1.5">
                      <div
                        className={`rounded-lg border px-4 py-3 text-sm leading-relaxed ${
                          msg.speaker === "AI"
                            ? "border-border bg-surface-raised text-text-primary"
                            : "border-accent-muted bg-accent-soft text-text-primary"
                        }`}
                      >
                        {msg.text}
                      </div>

                      {msg.evaluation && (
                        <div className="flex items-center gap-1.5 self-end text-xs text-text-muted">
                          <CheckCircle2 className="h-3 w-3 text-accent" />
                          Evaluated — technical {msg.evaluation.technical_score}
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}

                {phase === "sending" && (
                  <motion.div
                    key="thinking"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex justify-start"
                  >
                    <div className="flex items-center gap-1.5 rounded-lg border border-border bg-surface-raised px-4 py-3">
                      <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-text-muted" />
                      <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-text-muted [animation-delay:150ms]" />
                      <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-text-muted [animation-delay:300ms]" />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
              <div ref={scrollRef} />
            </div>

            {phase === "completed" ? (
              <div className="mt-6 flex justify-center">
                <Button onClick={() => sessionId && navigate(`/report/${sessionId}`)}>
                  View full report
                </Button>
              </div>
            ) : (
              <div className="mt-4 flex items-end gap-2">
                <textarea
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  onKeyDown={handleKeyDown}
                  disabled={phase === "sending"}
                  placeholder="Type your answer… (Enter to send, Shift+Enter for a new line)"
                  rows={2}
                  className="h-16 flex-1 resize-none rounded-md border border-border bg-surface px-3 py-2.5 text-sm text-text-primary
                    placeholder:text-text-muted outline-none transition-colors duration-150
                    focus:border-accent focus:ring-1 focus:ring-accent disabled:opacity-50"
                />
                <Button
                  onClick={handleSend}
                  disabled={!answer.trim()}
                  isLoading={phase === "sending"}
                  className="h-16 w-16 shrink-0"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            )}
          </div>
        )}
      </motion.div>
    </AppLayout>
  );
}