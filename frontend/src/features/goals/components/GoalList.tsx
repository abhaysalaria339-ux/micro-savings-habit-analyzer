import { FormEvent, useEffect, useState } from "react";

import { ErrorMessage } from "../../../components/ErrorMessage";
import { ApiError } from "../../../lib/api/apiError";
import { StateMessage } from "../../../components/StateMessage";
import { Goal, listGoals, updateGoalProgress } from "../api/goalApi";

type GoalListProps = {
  refreshKey: number;
};

export function GoalList({ refreshKey }: GoalListProps) {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [completionFilter, setCompletionFilter] = useState<"all" | "active" | "done">(
    "all",
  );
  const [progressInputs, setProgressInputs] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [savingGoalId, setSavingGoalId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let ignore = false;

    async function loadGoals() {
      setIsLoading(true);
      setError(null);

      try {
        const response = await listGoals(resolveCompletionFilter(completionFilter));
        if (!ignore) {
          setGoals(response);
          setProgressInputs(
            Object.fromEntries(
              response.map((goal) => [goal.id, goal.current_amount]),
            ),
          );
        }
      } catch (caughtError) {
        if (!ignore) {
          setError(toGoalErrorMessage(caughtError));
        }
      } finally {
        if (!ignore) {
          setIsLoading(false);
        }
      }
    }

    void loadGoals();

    return () => {
      ignore = true;
    };
  }, [completionFilter, refreshKey, reloadKey]);

  async function handleProgressSubmit(
    event: FormEvent<HTMLFormElement>,
    goal: Goal,
  ) {
    event.preventDefault();
    setSavingGoalId(goal.id);
    setError(null);

    try {
      const updatedGoal = await updateGoalProgress(goal.id, {
        current_amount: progressInputs[goal.id] || goal.current_amount,
      });
      setGoals((currentGoals) =>
        currentGoals.map((currentGoal) =>
          currentGoal.id === updatedGoal.id ? updatedGoal : currentGoal,
        ),
      );
      setProgressInputs((currentInputs) => ({
        ...currentInputs,
        [updatedGoal.id]: updatedGoal.current_amount,
      }));
    } catch (caughtError) {
      setError(toGoalErrorMessage(caughtError));
    } finally {
      setSavingGoalId(null);
    }
  }

  return (
    <section className="dashboard-panel goal-list-panel" aria-labelledby="goal-list-title">
      <div className="panel-heading">
        <div>
          <p>Progress</p>
          <h2 id="goal-list-title">Savings goals</h2>
        </div>
      </div>

      <div className="segmented-control" aria-label="Goal completion filter">
        <button
          className={completionFilter === "all" ? "active" : ""}
          onClick={() => setCompletionFilter("all")}
          type="button"
        >
          All
        </button>
        <button
          className={completionFilter === "active" ? "active" : ""}
          onClick={() => setCompletionFilter("active")}
          type="button"
        >
          Active
        </button>
        <button
          className={completionFilter === "done" ? "active" : ""}
          onClick={() => setCompletionFilter("done")}
          type="button"
        >
          Done
        </button>
      </div>

      <ErrorMessage
        actionLabel="Reload"
        message={error}
        onAction={() => setReloadKey((value) => value + 1)}
        title="Goals unavailable"
      />

      {isLoading ? (
        <StateMessage
          description="Checking your savings targets and progress."
          title="Loading goals"
          variant="loading"
        />
      ) : null}

      {!isLoading && goals.length === 0 ? (
        <StateMessage
          description="Create a savings goal or switch filters to review completed goals."
          title="No goals found"
        />
      ) : null}

      <div className="goal-list">
        {goals.map((goal) => (
          <article className="goal-item" key={goal.id}>
            <div className="goal-item-header">
              <div>
                <span className={goal.is_completed ? "goal-pill done" : "goal-pill"}>
                  {goal.is_completed ? "Completed" : "Active"}
                </span>
                <h3>{goal.name}</h3>
              </div>
              <strong>{formatPercent(goal.progress_percentage)}</strong>
            </div>

            <div
              className="goal-progress-track"
              aria-label={`${goal.name} progress`}
              aria-valuemax={100}
              aria-valuemin={0}
              aria-valuenow={Number(goal.progress_percentage)}
              role="progressbar"
            >
              <span style={{ width: `${Number(goal.progress_percentage)}%` }} />
            </div>

            <div className="goal-amount-row">
              <span>{formatCurrency(goal.current_amount)}</span>
              <span>{formatCurrency(goal.target_amount)}</span>
            </div>

            {goal.target_date ? (
              <p className="muted-copy">Target date: {formatDate(goal.target_date)}</p>
            ) : null}

            <form
              className="goal-progress-form"
              onSubmit={(event) => void handleProgressSubmit(event, goal)}
            >
              <label>
                Current amount
                <input
                  min="0"
                  onChange={(event) =>
                    setProgressInputs((currentInputs) => ({
                      ...currentInputs,
                      [goal.id]: event.target.value,
                    }))
                  }
                  step="0.01"
                  type="number"
                  value={progressInputs[goal.id] ?? goal.current_amount}
                />
              </label>
              <button
                className="secondary-button"
                disabled={savingGoalId === goal.id}
                type="submit"
              >
                {savingGoalId === goal.id ? "Saving..." : "Update"}
              </button>
            </form>
          </article>
        ))}
      </div>
    </section>
  );
}

function resolveCompletionFilter(filter: "all" | "active" | "done"): boolean | undefined {
  if (filter === "active") {
    return false;
  }

  if (filter === "done") {
    return true;
  }

  return undefined;
}

function formatCurrency(amount: string): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(Number(amount));
}

function formatPercent(value: string): string {
  return `${Number(value).toFixed(0)}%`;
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
  }).format(new Date(`${value}T00:00:00`));
}

function toGoalErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  return "Unable to load goals. Check your connection and try again.";
}
