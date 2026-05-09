import { apiRequest } from "../../../lib/api/httpClient";

export type Expense = {
  id: string;
  user_id: string;
  amount: string;
  category: string;
  description: string | null;
  spent_at: string;
  created_at: string;
  updated_at: string;
};

export type CreateExpensePayload = {
  amount: string;
  category: string;
  description?: string;
  spent_at: string;
};

export type UpdateExpensePayload = Partial<CreateExpensePayload>;

export type ExpenseListResponse = {
  items: Expense[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
};

export type ExpenseListParams = {
  category?: string;
  startDate?: string;
  endDate?: string;
  limit: number;
  offset: number;
};

export function createExpense(payload: CreateExpensePayload): Promise<Expense> {
  return apiRequest<Expense>("/expenses", {
    method: "POST",
    body: payload,
  });
}

export function listExpenses(params: ExpenseListParams): Promise<ExpenseListResponse> {
  const searchParams = new URLSearchParams({
    limit: String(params.limit),
    offset: String(params.offset),
  });

  if (params.category) {
    searchParams.set("category", params.category);
  }

  if (params.startDate) {
    searchParams.set("start_date", params.startDate);
  }

  if (params.endDate) {
    searchParams.set("end_date", params.endDate);
  }

  return apiRequest<ExpenseListResponse>(`/expenses?${searchParams.toString()}`);
}

export function updateExpense(
  expenseId: string,
  payload: UpdateExpensePayload,
): Promise<Expense> {
  return apiRequest<Expense>(`/expenses/${expenseId}`, {
    method: "PATCH",
    body: payload,
  });
}

export function deleteExpense(expenseId: string): Promise<void> {
  return apiRequest<void>(`/expenses/${expenseId}`, {
    method: "DELETE",
  });
}
