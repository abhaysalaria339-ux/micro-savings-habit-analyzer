import { apiRequest } from "../../../lib/api/httpClient";

export type DashboardResponse = {
  start_date: string;
  end_date: string;
  spending_summary: SpendingSummary;
  spending_trends: SpendingTrendAnalysis;
  savings_opportunities: SavingsInsight[];
  behavior_score: FinancialBehaviorScore;
  alerts: SpendingAlert[];
  money_leaks: MoneyLeakAnalysis;
  money_leak_score: MoneyLeakScore;
  habit_timeline: HabitTimelineResponse;
  goals: Goal[];
};

export type SpendingSummary = {
  start_date: string | null;
  end_date: string | null;
  total_amount: string;
  transaction_count: number;
  average_expense_amount: string;
  categories: CategorySpendingSummary[];
};

export type CategorySpendingSummary = {
  category: string;
  total_amount: string;
  transaction_count: number;
  percentage_of_total: string;
};

export type SpendingTrendAnalysis = {
  start_date: string;
  end_date: string;
  interval: "daily" | "weekly" | "monthly";
  total_amount: string;
  points: SpendingTrendPoint[];
};

export type SpendingTrendPoint = {
  period_start: string;
  total_amount: string;
  transaction_count: number;
  average_expense_amount: string;
};

export type SavingsInsight = {
  insight_type: "micro_expense" | "repeated_spending" | "category_concentration";
  title: string;
  message: string;
  action: string;
  estimated_monthly_savings: string;
};

export type FinancialBehaviorScore = {
  start_date: string;
  end_date: string;
  score: number;
  classification: "Saver" | "Neutral" | "Spender";
  total_amount: string;
  transaction_count: number;
  factors: BehaviorScoreFactor[];
};

export type BehaviorScoreFactor = {
  name: string;
  impact: number;
  message: string;
};

export type SpendingAlert = {
  alert_type:
    | "micro_expense"
    | "repeated_spending"
    | "weekend_spending"
    | "behavior_score"
    | "budget_breach";
  severity: "info" | "warning" | "critical";
  title: string;
  message: string;
  nudge: string;
  estimated_monthly_impact: string;
};

export type MoneyLeakAnalysis = {
  start_date: string;
  end_date: string;
  total_leak_amount: string;
  projected_monthly_leak: string;
  patterns: MoneyLeakPattern[];
};

export type MoneyLeakScore = {
  start_date: string;
  end_date: string;
  score: number;
  risk_level: "low" | "medium" | "high" | "critical";
  projected_monthly_leak: string;
  leak_ratio: string;
  pattern_count: number;
  top_leak_category: string | null;
  summary: string;
  recommended_action: string;
  evidence: MoneyLeakScoreEvidence[];
};

export type MoneyLeakScoreEvidence = {
  name: string;
  impact: number;
  message: string;
};

export type MoneyLeakPattern = {
  category: string;
  description: string | null;
  occurrence_count: number;
  total_amount: string;
  average_amount: string;
  projected_monthly_leak: string;
  average_days_between: string | null;
  leak_risk: "low" | "medium" | "high";
  reason: string;
};

export type HabitTimelineResponse = {
  start_date: string;
  end_date: string;
  events: HabitTimelineEvent[];
};

export type HabitTimelineEvent = {
  event_type:
    | "micro_spending"
    | "weekend_shift"
    | "category_focus"
    | "money_leak"
    | "positive_signal"
    | "spending_trend";
  severity: "info" | "positive" | "warning" | "critical";
  title: string;
  description: string;
  happened_at: string;
  amount: string | null;
  category: string | null;
  action: string;
};

export type Goal = {
  id: string;
  user_id: string;
  name: string;
  target_amount: string;
  current_amount: string;
  progress_percentage: string;
  target_date: string | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
};

export function getDashboard(): Promise<DashboardResponse> {
  return apiRequest<DashboardResponse>("/dashboard");
}
