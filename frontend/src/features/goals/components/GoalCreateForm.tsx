import { FormEvent, useMemo, useState } from "react";

import { ErrorMessage } from "../../../components/ErrorMessage";
import { ApiError } from "../../../lib/api/apiError";
import { createGoal, Goal } from "../api/goalApi";

type GoalCreateFormProps = {
  onCreated?: (goal: Goal) => void;
};

export function GoalCreateForm({ onCreated }: GoalCreateFormProps) {
  const [name, setName] = useState("");
  const [targetAmount, setTargetAmount] = useState("");
  const [currentAmount, setCurrentAmount] = useState("0.00");
  const [targetDate, setTargetDate] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const canSubmit = useMemo(
    () => name.trim() !== "" && targetAmount.trim() !== "",
    [name, targetAmount],
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSuccessMessage(null);

    if (!canSubmit) {
      setError("Goal name and target amount are required.");
      return;
    }

    setIsSubmitting(true);

    try {
      const goal = await createGoal({
        name: name.trim(),
        target_amount: targetAmount.trim(),
        current_amount: currentAmount.trim() || "0.00",
        target_date: targetDate || undefined,
      });
      onCreated?.(goal);
      setSuccessMessage(`${goal.name} goal created.`);
      resetForm();
    } catch (caughtError) {
      setError(toGoalErrorMessage(caughtError));
    } finally {
      setIsSubmitting(false);
    }
  }

  function resetForm() {
    setName("");
    setTargetAmount("");
    setCurrentAmount("0.00");
    setTargetDate("");
  }

  return (
    <section className="form-panel" aria-labelledby="goal-form-title">
      <div className="panel-heading">
        <div>
          <p>Savings target</p>
          <h2 id="goal-form-title">Create goal</h2>
        </div>
      </div>

      <form className="goal-form" onSubmit={handleSubmit}>
        <label className="full-width-field">
          Goal name
          <input
            maxLength={120}
            onChange={(event) => setName(event.target.value)}
            placeholder="Emergency fund"
            required
            type="text"
            value={name}
          />
        </label>

        <label>
          Target amount
          <input
            inputMode="decimal"
            min="0.01"
            onChange={(event) => setTargetAmount(event.target.value)}
            placeholder="1000.00"
            required
            step="0.01"
            type="number"
            value={targetAmount}
          />
        </label>

        <label>
          Current amount
          <input
            inputMode="decimal"
            min="0"
            onChange={(event) => setCurrentAmount(event.target.value)}
            step="0.01"
            type="number"
            value={currentAmount}
          />
        </label>

        <label className="full-width-field">
          Target date
          <input
            onChange={(event) => setTargetDate(event.target.value)}
            type="date"
            value={targetDate}
          />
        </label>

        <ErrorMessage message={error} title="Goal not saved" />

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
          {isSubmitting ? "Creating goal..." : "Create goal"}
        </button>
      </form>
    </section>
  );
}

function toGoalErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  return "Unable to create goal. Check your connection and try again.";
}
