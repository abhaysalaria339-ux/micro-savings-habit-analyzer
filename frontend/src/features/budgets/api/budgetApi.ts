import { apiRequest } from "../../../lib/api/httpClient";

export type Budget = {
  id: string;
  user_id: string;
  category: string;
  monthly_limit: string;
  spent_amount: string;
  remaining_amount: string;
  usage_percentage: string;
  status: "safe" | "watch" | "over";
  period_start: string;
  period_end: string;
  created_at: string;
  updated_at: string;
};

export type BudgetPayload = {
  category: string;
  monthly_limit: string;
};

export function listBudgets(): Promise<Budget[]> {
  return apiRequest<Budget[]>("/budgets");
}

export function saveBudget(payload: BudgetPayload): Promise<Budget> {
  return apiRequest<Budget>("/budgets", {
    method: "POST",
    body: payload,
  });
}

export function deleteBudget(budgetId: string): Promise<void> {
  return apiRequest<void>(`/budgets/${budgetId}`, {
    method: "DELETE",
  });
}
