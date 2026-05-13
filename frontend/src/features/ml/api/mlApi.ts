import { apiRequest } from "../../../lib/api/httpClient";

export type MLFeatureSnapshot = {
  total_spend: string;
  average_transaction_amount: string;
  average_daily_spend: string;
  micro_expense_ratio: string;
  repeated_pattern_count: number;
  unique_category_count: number;
  top_category_spend_ratio: string;
  weekend_spend_ratio: string;
  food_and_snack_spend_ratio: string;
  subscription_spend_ratio: string;
  spending_frequency_per_day: string;
  spend_trend_ratio: string;
};

export type MLSpendingProfileResponse = {
  profile_id: string;
  profile_label: string;
  confidence: string;
  summary: string;
  reasons: string[];
  recommendations: string[];
  analysis_days: number;
  transaction_count: number;
  features: MLFeatureSnapshot;
};

export function getSpendingProfile(
  analysisDays = 90,
): Promise<MLSpendingProfileResponse> {
  return apiRequest<MLSpendingProfileResponse>(
    `/ml/spending-profile?analysis_days=${analysisDays}`,
  );
}
