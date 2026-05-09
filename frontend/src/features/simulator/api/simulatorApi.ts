import { apiRequest } from "../../../lib/api/httpClient";

export type SavingsSimulationPayload = {
  current_monthly_amount: string;
  reduction_percentage: string;
};

export type SavingsSimulationResult = {
  current_monthly_amount: string;
  reduction_percentage: string;
  reduced_monthly_amount: string;
  projected_monthly_savings: string;
  projected_yearly_savings: string;
};

export function simulateSavings(
  payload: SavingsSimulationPayload,
): Promise<SavingsSimulationResult> {
  return apiRequest<SavingsSimulationResult>("/simulator/savings", {
    method: "POST",
    body: payload,
  });
}
