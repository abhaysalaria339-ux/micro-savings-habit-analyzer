import { FormEvent, useEffect, useMemo, useState } from "react";

import { ErrorMessage } from "../components/ErrorMessage";
import { StateMessage } from "../components/StateMessage";
import {
  Budget,
  deleteBudget,
  listBudgets,
  saveBudget,
} from "../features/budgets/api/budgetApi";
import { ApiError } from "../lib/api/apiError";
import { formatCurrency } from "../lib/formatters";

export function BudgetsPage() {
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [category, setCategory] = useState("");
  const [monthlyLimit, setMonthlyLimit] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  const totalLimit = useMemo(
    () => budgets.reduce((total, budget) => total + Number(budget.monthly_limit), 0),
    [budgets],
  );
  const totalSpent = useMemo(
    () => budgets.reduce((total, budget) => total + Number(budget.spent_amount), 0),
    [budgets],
  );

  useEffect(() => {
    let ignore = false;

    async function loadBudgets() {
      setIsLoading(true);
      setError(null);

      try {
        const response = await listBudgets();
        if (!ignore) {
          setBudgets(response);
        }
      } catch (caughtError) {
        if (!ignore) {
          setError(toBudgetErrorMessage(caughtError));
        }
      } finally {
        if (!ignore) {
          setIsLoading(false);
        }
      }
    }

    void loadBudgets();

    return () => {
      ignore = true;
    };
  }, [reloadKey]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSuccessMessage(null);

    if (!category.trim() || !monthlyLimit.trim()) {
      setError("Category and monthly limit are required.");
      return;
    }

    setIsSaving(true);

    try {
      const savedBudget = await saveBudget({
        category: category.trim(),
        monthly_limit: monthlyLimit.trim(),
      });
      setBudgets((currentBudgets) => [
        savedBudget,
        ...currentBudgets.filter((budget) => budget.id !== savedBudget.id),
      ]);
      setCategory("");
      setMonthlyLimit("");
      setSuccessMessage(`${savedBudget.category} budget saved.`);
    } catch (caughtError) {
      setError(toBudgetErrorMessage(caughtError));
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDelete(budget: Budget) {
    const shouldDelete = window.confirm(`Delete ${budget.category} budget?`);
    if (!shouldDelete) {
      return;
    }

    setError(null);
    setSuccessMessage(null);

    try {
      await deleteBudget(budget.id);
      setBudgets((currentBudgets) =>
        currentBudgets.filter((currentBudget) => currentBudget.id !== budget.id),
      );
    } catch (caughtError) {
      setError(toBudgetErrorMessage(caughtError));
    }
  }

  return (
    <section className="page-surface" aria-labelledby="budgets-title">
      <div className="page-heading">
        <div>
          <p>Guardrails</p>
          <h1 id="budgets-title">Budgets</h1>
        </div>
      </div>

      <div className="metric-grid budget-metric-grid">
        <article className="metric-panel">
          <span>Monthly limit</span>
          <strong>{formatCurrency(totalLimit)}</strong>
        </article>
        <article className="metric-panel">
          <span>Tracked spend</span>
          <strong>{formatCurrency(totalSpent)}</strong>
        </article>
        <article className="metric-panel">
          <span>Remaining</span>
          <strong>{formatCurrency(Math.max(totalLimit - totalSpent, 0))}</strong>
        </article>
        <article className="metric-panel">
          <span>Active budgets</span>
          <strong>{budgets.length}</strong>
        </article>
      </div>

      <div className="budgets-layout">
        <section className="form-panel" aria-labelledby="budget-form-title">
          <div className="panel-heading">
            <div>
              <p>Monthly cap</p>
              <h2 id="budget-form-title">Set budget</h2>
            </div>
          </div>

          <form className="budget-form" onSubmit={handleSubmit}>
            <label>
              Category
              <input
                maxLength={80}
                onChange={(event) => setCategory(event.target.value)}
                placeholder="Food, transport, shopping"
                required
                type="text"
                value={category}
              />
            </label>

            <label>
              Monthly limit
              <input
                inputMode="decimal"
                min="1"
                onChange={(event) => setMonthlyLimit(event.target.value)}
                placeholder="5000.00"
                required
                step="0.01"
                type="number"
                value={monthlyLimit}
              />
            </label>

            <ErrorMessage message={error} title="Budget not saved" />

            {successMessage ? (
              <p className="form-message success" role="status">
                {successMessage}
              </p>
            ) : null}

            <button className="primary-button" disabled={isSaving} type="submit">
              {isSaving ? "Saving budget..." : "Save budget"}
            </button>
          </form>
        </section>

        <section className="dashboard-panel" aria-labelledby="budget-list-title">
          <div className="panel-heading">
            <div>
              <p>Usage</p>
              <h2 id="budget-list-title">Budget guardrails</h2>
            </div>
          </div>

          <ErrorMessage
            actionLabel="Reload"
            message={error}
            onAction={() => setReloadKey((value) => value + 1)}
            title="Budgets unavailable"
          />

          {isLoading ? (
            <StateMessage
              description="Loading category limits and current month spend."
              title="Loading budgets"
              variant="loading"
            />
          ) : null}

          {!isLoading && budgets.length === 0 ? (
            <StateMessage
              description="Create category budgets to compare spending with monthly limits."
              title="No budgets yet"
            />
          ) : null}

          <ul className="budget-list">
            {budgets.map((budget) => (
              <li className={`budget-item ${budget.status}`} key={budget.id}>
                <div className="budget-item-header">
                  <div>
                    <span>{budget.status}</span>
                    <strong>{budget.category}</strong>
                  </div>
                  <button
                    className="ghost-button"
                    onClick={() => void handleDelete(budget)}
                    type="button"
                  >
                    Delete
                  </button>
                </div>
                <div className="budget-progress-track" aria-hidden="true">
                  <span style={{ width: `${Math.min(Number(budget.usage_percentage), 100)}%` }} />
                </div>
                <div className="budget-amount-row">
                  <span>{formatCurrency(budget.spent_amount)} spent</span>
                  <span>{formatCurrency(budget.monthly_limit)} limit</span>
                </div>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </section>
  );
}

function toBudgetErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  return "Unable to load budgets. Check your connection and try again.";
}
