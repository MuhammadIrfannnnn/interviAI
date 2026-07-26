// Confirmed against GET /api/v1/interview/dashboard response.

export interface RecentInterview {
  id: number;
  role_applied: string;
  difficulty: string;
  status: string;
  overall_score: number | null;
  started_at: string;
  ended_at: string | null;
}

export interface DashboardSummary {
  total_interviews: number;
  completed_interviews: number;
  average_score: number;
  best_score: number;
  recent_interviews: RecentInterview[];
}