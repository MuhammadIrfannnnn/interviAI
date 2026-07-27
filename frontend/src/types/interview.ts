// NOTE: StartInterviewPayload / InterviewMessagePayload / InterviewTurnResponse
// below are still placeholders pending /docs confirmation for /interview/start
// and /interview/message. Everything else in this file (session, messages,
// report shapes) is confirmed against the real GET /interview/{session_id}
// response.

export interface StartInterviewPayload {
  role_applied: string;
  difficulty: string;
}

export interface InterviewMessagePayload {
  session_id: number;
  answer: string;
}

export interface InterviewQuestion {
  question: string;
  // Backend may include topic/competency metadata alongside the question —
  // add fields here once confirmed.
}

export interface AnswerEvaluation {
  score: number;
  feedback: string;
}

// Response shape for both /interview/start and /interview/message —
// per the doc, every answer returns either the next question or, if the
// interview is ending, the final report.
export interface InterviewTurnResponse {
  session_id: number;
  status: "active" | "completed";
  question: InterviewQuestion | null;
  evaluation: AnswerEvaluation | null;
  report: InterviewReport | null;
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