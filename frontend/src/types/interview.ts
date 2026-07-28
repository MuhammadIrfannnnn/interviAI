// Confirmed against real /interview/start and /interview/message responses.
export interface StartInterviewPayload {
  role_applied: string;
  difficulty: string;
}

export interface StartInterviewResponse {
  message: string;
  session_id: number;
  first_question: string;
}

export interface InterviewMessagePayload {
  session_id: number;
  answer: string;
}

// NOTE: next_question being null/absent is assumed to signal the interview
// has ended — not yet confirmed against a real "final answer" response.
// When that happens, the page falls back to GET /interview/{session_id}
// for the closing message and full report.
export interface InterviewMessageResponse {
  session_id: number;
  evaluation: MessageEvaluation;
  next_question: string | null;
}

export interface CompetencyReport {
  competency: string;
  level: string;
  summary: string;
}

export interface InterviewReport {
  overall_score: number;
  technical_score: number;
  communication_score: number;
  confidence_score: number;
  problem_solving_score: number;
  recommendation: string;
  overall_feedback: string;
  strengths: string[];
  weaknesses: string[];
  highlights: string[];
  concerns: string[];
  technical_evidence: string[];
  learning_roadmap: string[];
  competency_reports: CompetencyReport[];
}

export interface MessageEvaluation {
  technical_score: number;
  communication_score: number;
  confidence_score: number;
  correctness: string;
  strengths: string[];
  weaknesses: string[];
  feedback: string;
  // Present on the live /interview/message response, not persisted on
  // historical messages returned by GET /interview/{session_id}.
  follow_up_strategy?: string;
}

export interface InterviewMessage {
  id: number;
  speaker: "AI" | "candidate";
  message: string;
  created_at: string;
  evaluation: MessageEvaluation | null;
}

export interface InterviewHistoryItem {
  session_id: number;
  role_applied: string;
  difficulty: string;
  status: string;
  overall_score: number | null;
  started_at: string;
  ended_at: string | null;
}

export interface InterviewSession {
  id: number;
  role_applied: string;
  difficulty: string;
  status: string;
  started_at: string;
  ended_at: string | null;
  overall_score: number;
}

export interface InterviewDetails {
  session: InterviewSession;
  messages: InterviewMessage[];
  report: InterviewReport | null;
}