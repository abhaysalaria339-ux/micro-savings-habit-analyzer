import { FormEvent, useMemo, useState } from "react";

import {
  SavingsSimulationResult,
  simulateSavings,
} from "../features/simulator/api/simulatorApi";
import { ErrorMessage } from "../components/ErrorMessage";
import { StateMessage } from "../components/StateMessage";
import { ApiError } from "../lib/api/apiError";

const reductionPresets = ["5", "10", "15", "25"];

export function SimulatorPage() {
  const [currentMonthlyAmount, setCurrentMonthlyAmount] = useState("");
  const [reductionPercentage, setReductionPercentage] = useState("10");
  const [result, setResult] = useState<SavingsSimulationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const canSubmit = useMemo(
    () =>
      currentMonthlyAmount.trim() !== "" &&
      reductionPercentage.trim() !== "" &&
      Number(currentMonthlyAmount) > 0 &&
      Number(reductionPercentage) >= 0 &&
      Number(reductionPercentage) <= 100,
    [currentMonthlyAmount, reductionPercentage],
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (!canSubmit) {
      setError("Enter a monthly amount above 0 and a reduction between 0 and 100.");
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await simulateSavings({
        current_monthly_amount: currentMonthlyAmount.trim(),
        reduction_percentage: reductionPercentage.trim(),
      });
      setResult(response);
    } catch (caughtError) {
      setError(toSimulatorErrorMessage(caughtError));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="page-surface" aria-labelledby="simulator-title">
      <div className="page-heading">
        <div>
          <p>What-if planning</p>
          <h1 id="simulator-title">Savings simulator</h1>
        </div>
      </div>

      <div className="simulator-layout">
        <section className="form-panel" aria-labelledby="simulation-form-title">
          <div className="panel-heading">
            <div>
              <p>Scenario</p>
              <h2 id="simulation-form-title">Model a reduction</h2>
            </div>
          </div>

          <form className="simulator-form" onSubmit={handleSubmit}>
            <label>
              Current monthly amount
              <input
                inputMode="decimal"
                min="0.01"
                onChange={(event) => setCurrentMonthlyAmount(event.target.value)}
                placeholder="300.00"
                required
                step="0.01"
                type="number"
                value={currentMonthlyAmount}
              />
            </label>

            <label>
              Reduction percentage
              <input
                inputMode="decimal"
                max="100"
                min="0"
                onChange={(event) => setReductionPercentage(event.target.value)}
                required
                step="0.01"
                type="number"
                value={reductionPercentage}
              />
            </label>

            <div className="preset-row" aria-label="Reduction presets">
              {reductionPresets.map((preset) => (
                <button
                  className={
                    reductionPercentage === preset
                      ? "preset-button active"
                      : "preset-button"
                  }
                  key={preset}
                  onClick={() => setReductionPercentage(preset)}
                  type="button"
                >
                  {preset}%
                </button>
              ))}
            </div>

            <ErrorMessage message={error} title="Simulation unavailable" />

            <button
              className="primary-button"
              disabled={isSubmitting || !canSubmit}
              type="submit"
            >
              {isSubmitting ? "Calculating..." : "Calculate savings"}
            </button>
          </form>
        </section>

        <section
          className="dashboard-panel simulator-result-panel"
          aria-labelledby="simulation-result-title"
        >
          <div className="panel-heading">
            <div>
              <p>Projection</p>
              <h2 id="simulation-result-title">Savings result</h2>
            </div>
          </div>

          {result ? (
            <>
              <div className="simulation-hero">
                <span>Yearly savings</span>
                <strong>{formatCurrency(result.projected_yearly_savings)}</strong>
              </div>

              <div className="simulation-result-grid">
                <article>
                  <span>Monthly savings</span>
                  <strong>{formatCurrency(result.projected_monthly_savings)}</strong>
                </article>
                <article>
                  <span>Reduced monthly amount</span>
                  <strong>{formatCurrency(result.reduced_monthly_amount)}</strong>
                </article>
                <article>
                  <span>Reduction</span>
                  <strong>{Number(result.reduction_percentage).toFixed(0)}%</strong>
                </article>
              </div>
            </>
          ) : (
            <StateMessage
              description="Enter a monthly spending amount and choose a reduction percentage to see projected savings."
              title="No simulation yet"
            />
          )}
        </section>
      </div>
    </section>
  );
}

function formatCurrency(amount: string): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(Number(amount));
}

function toSimulatorErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  return "Unable to run simulation. Check your connection and try again.";
}
