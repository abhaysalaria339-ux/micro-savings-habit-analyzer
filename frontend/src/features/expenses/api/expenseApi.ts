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

export type ExpenseImportRowResult = {
  row_number: number;
  status: "imported" | "failed" | "skipped_duplicate" | "skipped_credit";
  error: string | null;
  expense: Expense | null;
};

export type ExpenseImportResponse = {
  imported_count: number;
  failed_count: number;
  skipped_count: number;
  results: ExpenseImportRowResult[];
};

export type ExpenseDuplicateCheckResponse = {
  has_duplicates: boolean;
  matches: Expense[];
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

export function checkExpenseDuplicate(
  payload: CreateExpensePayload,
): Promise<ExpenseDuplicateCheckResponse> {
  return apiRequest<ExpenseDuplicateCheckResponse>("/expenses/duplicate-check", {
    method: "POST",
    body: payload,
  });
}

export function importExpensesFromCsv(
  csvContent: string,
): Promise<ExpenseImportResponse> {
  return apiRequest<ExpenseImportResponse>("/expenses/import", {
    method: "POST",
    body: {
      csv_content: csvContent,
    },
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
