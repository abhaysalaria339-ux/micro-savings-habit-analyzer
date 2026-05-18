import { apiRequest } from "../../../lib/api/httpClient";

export type RecurringExpenseCandidate = {
  category: string;
  description: string | null;
  occurrence_count: number;
  average_amount: string;
  total_amount: string;
  average_days_between: string | null;
  projected_monthly_amount: string;
  confidence: "low" | "medium" | "high";
  next_expected_at: string | null;
  recommendation: string;
};

export type RecurringExpenseResponse = {
  start_date: string;
  end_date: string;
  candidates: RecurringExpenseCandidate[];
};

export type CalendarHeatmapDay = {
  day: string;
  total_amount: string;
  transaction_count: number;
  intensity: "none" | "low" | "medium" | "high";
};

export type CalendarHeatmapResponse = {
  start_date: string;
  end_date: string;
  max_daily_amount: string;
  days: CalendarHeatmapDay[];
};

export type WeeklyFinancialHealthReport = {
  start_date: string;
  end_date: string;
  total_spend: string;
  previous_total_spend: string;
  spend_change_percentage: string;
  top_category: string | null;
  top_category_amount: string;
  recurring_monthly_risk: string;
  high_spend_days: number;
  summary: string;
  recommended_focus: string;
};

export type SpendingAnomaly = {
  anomaly_type: "large_transaction" | "category_spike" | "high_spend_day";
  severity: "info" | "warning" | "critical";
  title: string;
  description: string;
  detected_at: string;
  amount: string;
  category: string | null;
};

export type HabitCoachRecommendation = {
  priority: "low" | "medium" | "high";
  title: string;
  message: string;
  action: string;
  estimated_monthly_impact: string;
};

export type AdvancedIntelligenceResponse = {
  analysis_days: number;
  recurring_expenses: RecurringExpenseResponse;
  calendar_heatmap: CalendarHeatmapResponse;
  weekly_report: WeeklyFinancialHealthReport;
  anomalies: SpendingAnomaly[];
  coach_recommendations: HabitCoachRecommendation[];
};

export function getAdvancedIntelligence(
  analysisDays = 90,
): Promise<AdvancedIntelligenceResponse> {
  return apiRequest<AdvancedIntelligenceResponse>(
    `/advanced/intelligence?analysis_days=${analysisDays}`,
  );
}
