import api from "./api";
import type { DashboardSummary } from "../types/Dashboard";

// Path confirmed: /api/v1/interview/dashboard
export const dashboardService = {
  async getSummary(): Promise<DashboardSummary> {
    const { data } = await api.get<DashboardSummary>("/interview/dashboard");
    return data;
  },
};