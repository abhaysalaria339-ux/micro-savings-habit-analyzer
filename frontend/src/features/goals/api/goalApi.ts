import { apiRequest } from "../../../lib/api/httpClient";

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

export type CreateGoalPayload = {
  name: string;
  target_amount: string;
  current_amount?: string;
  target_date?: string;
};

export type GoalProgressPayload = {
  current_amount: string;
};

export function createGoal(payload: CreateGoalPayload): Promise<Goal> {
  return apiRequest<Goal>("/goals", {
    method: "POST",
    body: payload,
  });
}

export function listGoals(isCompleted?: boolean): Promise<Goal[]> {
  const searchParams = new URLSearchParams();

  if (isCompleted !== undefined) {
    searchParams.set("is_completed", String(isCompleted));
  }

  const query = searchParams.toString();
  return apiRequest<Goal[]>(query ? `/goals?${query}` : "/goals");
}

export function updateGoalProgress(
  goalId: string,
  payload: GoalProgressPayload,
): Promise<Goal> {
  return apiRequest<Goal>(`/goals/${goalId}/progress`, {
    method: "PATCH",
    body: payload,
  });
}
