import { apiRequest } from "../../../lib/api/httpClient";

export type SavingsInsightsResponse = {
  start_date: string;
  end_date: string;
  period: "weekly" | "monthly";
  total_estimated_monthly_savings: string;
  insights: SavingsInsight[];
};

export type SavingsInsight = {
  insight_type: "micro_expense" | "repeated_spending" | "category_concentration";
  title: string;
  message: string;
  action: string;
  estimated_monthly_savings: string;
};

export type SpendingAlertsResponse = {
  start_date: string;
  end_date: string;
  alerts: SpendingAlert[];
};

export type SpendingAlert = {
  alert_type: "micro_expense" | "repeated_spending" | "weekend_spending" | "behavior_score";
  severity: "info" | "warning" | "critical";
  title: string;
  message: string;
  nudge: string;
  estimated_monthly_impact: string;
};

export function getSavingsInsights(
  period: "weekly" | "monthly",
): Promise<SavingsInsightsResponse> {
  return apiRequest<SavingsInsightsResponse>(`/insights/savings?period=${period}`);
}

export function getSpendingAlerts(): Promise<SpendingAlertsResponse> {
  return apiRequest<SpendingAlertsResponse>("/alerts");
}
