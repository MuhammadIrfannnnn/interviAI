import api from "./api";
import type {
  StartInterviewPayload,
  StartInterviewResponse,
  InterviewMessagePayload,
  InterviewMessageResponse,
  InterviewHistoryItem,
  InterviewDetails,
} from "../types/interview";

export const interviewService = {
  async start(payload: StartInterviewPayload): Promise<StartInterviewResponse> {
    const { data } = await api.post<StartInterviewResponse>("/interview/start", payload);
    return data;
  },

  async sendMessage(payload: InterviewMessagePayload): Promise<InterviewMessageResponse> {
    const { data } = await api.post<InterviewMessageResponse>("/interview/message", payload);
    return data;
  },

  async getHistory(): Promise<InterviewHistoryItem[]> {
    const { data } = await api.get<{ interviews: InterviewHistoryItem[] }>("/interview/history");
    return data.interviews;
  },

  async getDetails(sessionId: number): Promise<InterviewDetails> {
    const { data } = await api.get<InterviewDetails>(`/interview/${sessionId}`);
    return data;
  },

  // Returns a PDF — handled as a blob so the browser can trigger a download
  // rather than trying to parse it as JSON.
  async exportReport(sessionId: number): Promise<Blob> {
    const { data } = await api.get(`/interview/${sessionId}/export`, {
      responseType: "blob",
    });
    return data;
  },
};