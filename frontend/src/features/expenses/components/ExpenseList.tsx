import { FormEvent, useEffect, useMemo, useState } from "react";

import { ErrorMessage } from "../../../components/ErrorMessage";
import { ApiError } from "../../../lib/api/apiError";
import { formatCurrency } from "../../../lib/formatters";
import { StateMessage } from "../../../components/StateMessage";
import {
  deleteExpense,
  Expense,
  listExpenses,
  updateExpense,
} from "../api/expenseApi";

type ExpenseListProps = {
  refreshKey: number;
};

type EditFormState = {
  amount: string;
  category: string;
  description: string;
  spentAt: string;
};

const pageSize = 10;

export function ExpenseList({ refreshKey }: ExpenseListProps) {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const [categoryFilter, setCategoryFilter] = useState("");
  const [startDateFilter, setStartDateFilter] = useState("");
  const [endDateFilter, setEndDateFilter] = useState("");
  const [editingExpenseId, setEditingExpenseId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<EditFormState | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  const currentPage = useMemo(() => Math.floor(offset / pageSize) + 1, [offset]);
  const totalPages = useMemo(
    () => Math.max(1, Math.ceil(total / pageSize)),
    [total],
  );

  useEffect(() => {
    let ignore = false;

    async function loadExpenses() {
      setIsLoading(true);
      setError(null);

      try {
        const response = await listExpenses({
          category: categoryFilter.trim() || undefined,
          startDate: startDateFilter ? startOfDayIso(startDateFilter) : undefined,
          endDate: endDateFilter ? endOfDayIso(endDateFilter) : undefined,
          limit: pageSize,
          offset,
        });

        if (!ignore) {
          setExpenses(response.items);
          setTotal(response.total);
          setHasMore(response.has_more);
        }
      } catch (caughtError) {
        if (!ignore) {
          setError(toExpenseErrorMessage(caughtError));
        }
      } finally {
        if (!ignore) {
          setIsLoading(false);
        }
      }
    }

    void loadExpenses();

    return () => {
      ignore = true;
    };
  }, [categoryFilter, endDateFilter, offset, refreshKey, reloadKey, startDateFilter]);

  function handleFilterSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setOffset(0);
  }

  function clearFilters() {
    setCategoryFilter("");
    setStartDateFilter("");
    setEndDateFilter("");
    setOffset(0);
  }

  function startEditing(expense: Expense) {
    setEditingExpenseId(expense.id);
    setEditForm({
      amount: expense.amount,
      category: expense.category,
      description: expense.description ?? "",
      spentAt: toDateTimeLocalValue(new Date(expense.spent_at)),
    });
    setError(null);
  }

  async function saveEdit(expenseId: string) {
    if (!editForm) {
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      await updateExpense(expenseId, {
        amount: editForm.amount.trim(),
        category: editForm.category.trim(),
        description: editForm.description.trim() || undefined,
        spent_at: new Date(editForm.spentAt).toISOString(),
      });
      setEditingExpenseId(null);
      setEditForm(null);
      await reloadCurrentPage();
    } catch (caughtError) {
      setError(toExpenseErrorMessage(caughtError));
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDelete(expenseId: string) {
    const shouldDelete = window.confirm("Delete this expense?");
    if (!shouldDelete) {
      return;
    }

    setError(null);

    try {
      await deleteExpense(expenseId);
      const nextOffset =
        expenses.length === 1 && offset > 0 ? Math.max(0, offset - pageSize) : offset;
      setOffset(nextOffset);
      await reloadCurrentPage(nextOffset);
    } catch (caughtError) {
      setError(toExpenseErrorMessage(caughtError));
    }
  }

  async function reloadCurrentPage(nextOffset = offset) {
    const response = await listExpenses({
      category: categoryFilter.trim() || undefined,
      startDate: startDateFilter ? startOfDayIso(startDateFilter) : undefined,
      endDate: endDateFilter ? endOfDayIso(endDateFilter) : undefined,
      limit: pageSize,
      offset: nextOffset,
    });
    setExpenses(response.items);
    setTotal(response.total);
    setHasMore(response.has_more);
  }

  return (
    <section className="dashboard-panel expense-list-panel" aria-labelledby="expense-list-title">
      <div className="panel-heading">
        <div>
          <p>History</p>
          <h2 id="expense-list-title">Recent expenses</h2>
        </div>
        <span className="total-pill">{total} total</span>
      </div>

      <form className="expense-filter-form" onSubmit={handleFilterSubmit}>
        <label>
          Category
          <input
            maxLength={80}
            onChange={(event) => setCategoryFilter(event.target.value)}
            placeholder="Coffee"
            type="text"
            value={categoryFilter}
          />
        </label>

        <label>
          Start
          <input
            onChange={(event) => setStartDateFilter(event.target.value)}
            type="date"
            value={startDateFilter}
          />
        </label>

        <label>
          End
          <input
            onChange={(event) => setEndDateFilter(event.target.value)}
            type="date"
            value={endDateFilter}
          />
        </label>

        <div className="filter-actions">
          <button className="secondary-button" type="submit">
            Apply
          </button>
          <button className="ghost-button" onClick={clearFilters} type="button">
            Clear
          </button>
        </div>
      </form>

      <ErrorMessage
        actionLabel="Reload"
        message={error}
        onAction={() => setReloadKey((value) => value + 1)}
        title="Expense history unavailable"
      />

      {isLoading ? (
        <StateMessage
          description="Fetching your latest expense history and filters."
          title="Loading expenses"
          variant="loading"
        />
      ) : null}

      {!isLoading && expenses.length === 0 ? (
        <StateMessage
          description="Try clearing filters or add a new expense to start building behavior insights."
          title="No expenses found"
        />
      ) : null}

      <div className="expense-list">
        {expenses.map((expense) => (
          <article className="expense-item" key={expense.id}>
            {editingExpenseId === expense.id && editForm ? (
              <div className="expense-edit-grid">
                <label>
                  Amount
                  <input
                    min="0.01"
                    onChange={(event) =>
                      setEditForm({ ...editForm, amount: event.target.value })
                    }
                    step="0.01"
                    type="number"
                    value={editForm.amount}
                  />
                </label>
                <label>
                  Category
                  <input
                    maxLength={80}
                    onChange={(event) =>
                      setEditForm({ ...editForm, category: event.target.value })
                    }
                    type="text"
                    value={editForm.category}
                  />
                </label>
                <label>
                  Spent at
                  <input
                    onChange={(event) =>
                      setEditForm({ ...editForm, spentAt: event.target.value })
                    }
                    type="datetime-local"
                    value={editForm.spentAt}
                  />
                </label>
                <label className="full-width-field">
                  Description
                  <textarea
                    maxLength={255}
                    onChange={(event) =>
                      setEditForm({ ...editForm, description: event.target.value })
                    }
                    rows={2}
                    value={editForm.description}
                  />
                </label>
                <div className="row-actions full-width-field">
                  <button
                    className="primary-button"
                    disabled={isSaving}
                    onClick={() => void saveEdit(expense.id)}
                    type="button"
                  >
                    {isSaving ? "Saving..." : "Save"}
                  </button>
                  <button
                    className="secondary-button"
                    onClick={() => {
                      setEditingExpenseId(null);
                      setEditForm(null);
                    }}
                    type="button"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <>
                <div>
                  <span className="expense-category">{expense.category}</span>
                  <h3>{formatCurrency(expense.amount)}</h3>
                  <p>{expense.description || "No description"}</p>
                </div>
                <div className="expense-meta">
                  <time dateTime={expense.spent_at}>{formatDate(expense.spent_at)}</time>
                  <div className="row-actions">
                    <button
                      className="secondary-button"
                      onClick={() => startEditing(expense)}
                      type="button"
                    >
                      Edit
                    </button>
                    <button
                      className="danger-button"
                      onClick={() => void handleDelete(expense.id)}
                      type="button"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </>
            )}
          </article>
        ))}
      </div>

      <div className="pagination-row">
        <button
          className="secondary-button"
          disabled={offset === 0}
          onClick={() => setOffset(Math.max(0, offset - pageSize))}
          type="button"
        >
          Previous
        </button>
        <span>
          Page {currentPage} of {totalPages}
        </span>
        <button
          className="secondary-button"
          disabled={!hasMore}
          onClick={() => setOffset(offset + pageSize)}
          type="button"
        >
          Next
        </button>
      </div>
    </section>
  );
}

function startOfDayIso(dateValue: string): string {
  return new Date(`${dateValue}T00:00:00`).toISOString();
}

function endOfDayIso(dateValue: string): string {
  return new Date(`${dateValue}T23:59:59`).toISOString();
}

function toDateTimeLocalValue(date: Date): string {
  const offsetMs = date.getTimezoneOffset() * 60_000;
  return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16);
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function toExpenseErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  return "Unable to load expenses. Check your connection and try again.";
}
