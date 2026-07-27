import api from "./api";
import type { ResumeResponse } from "../types/resume";

export const resumeService = {
  async getResume(): Promise<ResumeResponse> {
    const { data } = await api.get<ResumeResponse>("/resume/");
    return data;
  },

  // NOTE: form field name assumed as "file" (common FastAPI UploadFile
  // convention) — flag if the backend expects something else, e.g. "resume".
  // Uploading again replaces the existing resume server-side —
  // there's no separate delete endpoint.
  async uploadResume(file: File): Promise<ResumeResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const { data } = await api.post<ResumeResponse>("/resume/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  },
};