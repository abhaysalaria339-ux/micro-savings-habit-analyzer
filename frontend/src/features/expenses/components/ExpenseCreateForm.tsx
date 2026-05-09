import { FormEvent, useMemo, useState } from "react";

import { ErrorMessage } from "../../../components/ErrorMessage";
import { ApiError } from "../../../lib/api/apiError";
import { formatCurrency } from "../../../lib/formatters";
import { createExpense, Expense } from "../api/expenseApi";

type ExpenseCreateFormProps = {
  onCreated?: (expense: Expense) => void;
};

type QuickExpensePreset = {
  label: string;
  amount: string;
  category: string;
  description: string;
};

const quickExpensePresets: QuickExpensePreset[] = [
  {
    label: "Coffee",
    amount: "80.00",
    category: "Coffee",
    description: "Quick coffee stop",
  },
  {
    label: "Snack",
    amount: "50.00",
    category: "Snacks",
    description: "Small snack purchase",
  },
  {
    label: "Ride",
    amount: "120.00",
    category: "Transport",
    description: "Short ride",
  },
];

export function ExpenseCreateForm({ onCreated }: ExpenseCreateFormProps) {
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("");
  const [description, setDescription] = useState("");
  const [spentAt, setSpentAt] = useState(toDateTimeLocalValue(new Date()));
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const canSubmit = useMemo(
    () => amount.trim() !== "" && category.trim() !== "" && spentAt !== "",
    [amount, category, spentAt],
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSuccessMessage(null);

    if (!canSubmit) {
      setError("Amount, category, and spent date are required.");
      return;
    }

    setIsSubmitting(true);

    try {
      const expense = await createExpense({
        amount: amount.trim(),
        category: category.trim(),
        description: description.trim() || undefined,
        spent_at: new Date(spentAt).toISOString(),
      });
      onCreated?.(expense);
      setSuccessMessage(`${expense.category} expense added.`);
      resetForm();
    } catch (caughtError) {
      setError(toExpenseErrorMessage(caughtError));
    } finally {
      setIsSubmitting(false);
    }
  }

  function applyPreset(preset: QuickExpensePreset) {
    setAmount(preset.amount);
    setCategory(preset.category);
    setDescription(preset.description);
    setSpentAt(toDateTimeLocalValue(new Date()));
    setError(null);
    setSuccessMessage(null);
  }

  function resetForm() {
    setAmount("");
    setCategory("");
    setDescription("");
    setSpentAt(toDateTimeLocalValue(new Date()));
  }

  return (
    <section className="form-panel" aria-labelledby="expense-form-title">
      <div className="panel-heading">
        <div>
          <p>Manual entry</p>
          <h2 id="expense-form-title">Add expense</h2>
        </div>
      </div>

      <div className="quick-add-row" aria-label="Quick add expenses">
        {quickExpensePresets.map((preset) => (
          <button
            className="quick-add-button"
            key={preset.label}
            onClick={() => applyPreset(preset)}
            type="button"
          >
            <span>{preset.label}</span>
            <strong>{formatCurrency(preset.amount)}</strong>
          </button>
        ))}
      </div>

      <form className="expense-form" onSubmit={handleSubmit}>
        <label>
          Amount
          <input
            inputMode="decimal"
            min="0.01"
            name="amount"
            onChange={(event) => setAmount(event.target.value)}
            placeholder="120.00"
            required
            step="0.01"
            type="number"
            value={amount}
          />
        </label>

        <label>
          Category
          <input
            maxLength={80}
            name="category"
            onChange={(event) => setCategory(event.target.value)}
            placeholder="Coffee, snacks, transport"
            required
            type="text"
            value={category}
          />
        </label>

        <label>
          Spent at
          <input
            name="spentAt"
            onChange={(event) => setSpentAt(event.target.value)}
            required
            type="datetime-local"
            value={spentAt}
          />
        </label>

        <label className="full-width-field">
          Description
          <textarea
            maxLength={255}
            name="description"
            onChange={(event) => setDescription(event.target.value)}
            placeholder="Optional note"
            rows={3}
            value={description}
          />
        </label>

        <ErrorMessage message={error} title="Expense not saved" />

        {successMessage ? (
          <p className="form-message success" role="status">
            {successMessage}
          </p>
        ) : null}

        <button
          className="primary-button full-width-field"
          disabled={isSubmitting || !canSubmit}
          type="submit"
        >
          {isSubmitting ? "Adding expense..." : "Add expense"}
        </button>
      </form>
    </section>
  );
}

function toDateTimeLocalValue(date: Date): string {
  const offsetMs = date.getTimezoneOffset() * 60_000;
  return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16);
}

function toExpenseErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  return "Unable to add expense. Check your connection and try again.";
}
