import { useEffect, useMemo, useState } from "react";

import { ErrorMessage } from "../components/ErrorMessage";
import { ScrollSyncedInsightTabs } from "../components/ScrollSyncedInsightTabs";
import { StateMessage } from "../components/StateMessage";
import {
  AdvancedIntelligenceResponse,
  getAdvancedIntelligence,
} from "../features/advanced/api/advancedApi";
import { ApiError } from "../lib/api/apiError";
import { formatCurrency } from "../lib/formatters";

const analysisOptions = [30, 90, 180] as const;

const insightTabs = [
  { id: "advanced-overview", label: "Overview", meta: "01" },
  { id: "advanced-report", label: "Health check", meta: "02" },
  { id: "advanced-rhythm", label: "Rhythm", meta: "03" },
  { id: "advanced-coach", label: "Coach", meta: "04" },
  { id: "advanced-recurring", label: "Recurring", meta: "05" },
  { id: "advanced-anomalies", label: "Anomalies", meta: "06" },
];

export function AdvancedPage() {
  const [analysisDays, setAnalysisDays] = useState<(typeof analysisOptions)[number]>(90);
  const [intelligence, setIntelligence] =
    useState<AdvancedIntelligenceResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let ignore = false;

    async function loadAdvancedIntelligence() {
      setIsLoading(true);
      setError(null);

      try {
        const response = await getAdvancedIntelligence(analysisDays);
        if (!ignore) {
          setIntelligence(response);
        }
      } catch (caughtError) {
        if (!ignore) {
          setError(toAdvancedErrorMessage(caughtError));
        }
      } finally {
        if (!ignore) {
          setIsLoading(false);
        }
      }
    }

    void loadAdvancedIntelligence();

    return () => {
      ignore = true;
    };
  }, [analysisDays, reloadKey]);

  const recentHeatmapDays = useMemo(
    () => intelligence?.calendar_heatmap.days.slice(-90) ?? [],
    [intelligence],
  );

  return (
    <section className="page-surface" aria-labelledby="advanced-title">
      <div className="page-heading">
        <div>
          <p>Advanced intelligence</p>
          <h1 id="advanced-title">Habit lab</h1>
        </div>

        <div className="segmented-control" aria-label="Analysis range">
          {analysisOptions.map((days) => (
            <button
              className={analysisDays === days ? "active" : ""}
              key={days}
              onClick={() => setAnalysisDays(days)}
              type="button"
            >
              {days}d
            </button>
          ))}
        </div>
      </div>

      <ErrorMessage
        actionLabel="Try again"
        message={error}
        onAction={() => setReloadKey((value) => value + 1)}
        title="Advanced intelligence unavailable"
      />

      {isLoading ? (
        <StateMessage
          description="Reviewing recurring expenses, high-spend days, anomalies, and coach actions."
          title="Loading habit lab"
          variant="loading"
        />
      ) : null}

      {intelligence ? (
        <>
          <ScrollSyncedInsightTabs
            ariaLabel="Advanced insight sections"
            tabs={insightTabs}
          />

          <div
            className="metric-grid advanced-metric-grid scroll-sync-section"
            id="advanced-overview"
          >
            <article className="metric-panel">
              <span>Weekly spend</span>
              <strong>{formatCurrency(intelligence.weekly_report.total_spend)}</strong>
            </article>
            <article className="metric-panel">
              <span>Change vs last week</span>
              <strong>{formatSignedPercent(intelligence.weekly_report.spend_change_percentage)}</strong>
            </article>
            <article className="metric-panel">
              <span>Recurring risk</span>
              <strong>
                {formatCurrency(intelligence.weekly_report.recurring_monthly_risk)}
              </strong>
            </article>
            <article className="metric-panel">
              <span>High-spend days</span>
              <strong>{intelligence.weekly_report.high_spend_days}</strong>
            </article>
          </div>

          <section
            className="dashboard-panel advanced-report-panel scroll-sync-section"
            id="advanced-report"
          >
            <div className="panel-heading">
              <div>
                <p>Weekly report</p>
                <h2>Financial health check</h2>
              </div>
              {intelligence.weekly_report.top_category ? (
                <span className="confidence-pill">
                  {intelligence.weekly_report.top_category}
                </span>
              ) : null}
            </div>
            <p>{intelligence.weekly_report.summary}</p>
            <strong>{intelligence.weekly_report.recommended_focus}</strong>
          </section>

          <div className="advanced-grid">
            <section
              className="dashboard-panel scroll-sync-section"
              id="advanced-rhythm"
              aria-labelledby="heatmap-heading"
            >
              <div className="panel-heading">
                <div>
                  <p>Calendar heatmap</p>
                  <h2 id="heatmap-heading">Spending rhythm</h2>
                </div>
                <span className="confidence-pill">
                  Peak {formatCurrency(intelligence.calendar_heatmap.max_daily_amount)}
                </span>
              </div>
              <div className="heatmap-grid" aria-label="Daily spending heatmap">
                {recentHeatmapDays.map((day) => (
                  <span
                    aria-label={`${formatDisplayDate(day.day)}: ${formatCurrency(
                      day.total_amount,
                    )}, ${day.transaction_count} transactions`}
                    className={`heatmap-day ${day.intensity}`}
                    key={day.day}
                    title={`${formatDisplayDate(day.day)} - ${formatCurrency(
                      day.total_amount,
                    )}`}
                  />
                ))}
              </div>
              <div className="heatmap-legend" aria-label="Heatmap intensity legend">
                <span>Lower</span>
                <i className="heatmap-day low" />
                <i className="heatmap-day medium" />
                <i className="heatmap-day high" />
                <span>Higher</span>
              </div>
            </section>

            <section
              className="dashboard-panel scroll-sync-section"
              id="advanced-coach"
              aria-labelledby="coach-heading"
            >
              <div className="panel-heading">
                <div>
                  <p>Habit coach</p>
                  <h2 id="coach-heading">Next best actions</h2>
                </div>
              </div>
              <ul className="advanced-card-list">
                {intelligence.coach_recommendations.map((recommendation) => (
                  <li className="coach-card" key={`${recommendation.title}-${recommendation.action}`}>
                    <div>
                      <span className={`priority-pill ${recommendation.priority}`}>
                        {recommendation.priority}
                      </span>
                      <strong>{recommendation.title}</strong>
                      <p>{recommendation.message}</p>
                      <small>{recommendation.action}</small>
                    </div>
                    <aside>{formatCurrency(recommendation.estimated_monthly_impact)}</aside>
                  </li>
                ))}
              </ul>
            </section>
          </div>

          <div className="advanced-grid">
            <section
              className="dashboard-panel scroll-sync-section"
              id="advanced-recurring"
              aria-labelledby="recurring-heading"
            >
              <div className="panel-heading">
                <div>
                  <p>Recurring candidates</p>
                  <h2 id="recurring-heading">Possible habit costs</h2>
                </div>
              </div>
              <ul className="advanced-card-list">
                {intelligence.recurring_expenses.candidates.map((candidate) => (
                  <li
                    className="recurring-card"
                    key={`${candidate.category}-${candidate.description ?? "none"}`}
                  >
                    <div>
                      <span className={`priority-pill ${candidate.confidence}`}>
                        {candidate.confidence}
                      </span>
                      <strong>{candidate.description || candidate.category}</strong>
                      <p>
                        {candidate.occurrence_count} repeats, average{" "}
                        {formatCurrency(candidate.average_amount)}
                        {candidate.average_days_between
                          ? ` every ${Number(candidate.average_days_between).toFixed(1)} days`
                          : ""}
                      </p>
                      <small>{candidate.recommendation}</small>
                    </div>
                    <aside>{formatCurrency(candidate.projected_monthly_amount)}</aside>
                  </li>
                ))}
                {intelligence.recurring_expenses.candidates.length === 0 ? (
                  <li className="empty-list-item">
                    <StateMessage
                      description="No repeated expense candidate was strong enough in this range."
                      title="No recurring risks"
                    />
                  </li>
                ) : null}
              </ul>
            </section>

            <section
              className="dashboard-panel scroll-sync-section"
              id="advanced-anomalies"
              aria-labelledby="anomaly-heading"
            >
              <div className="panel-heading">
                <div>
                  <p>Anomaly signals</p>
                  <h2 id="anomaly-heading">Unusual spending</h2>
                </div>
              </div>
              <ul className="advanced-card-list">
                {intelligence.anomalies.map((anomaly) => (
                  <li
                    className={`anomaly-card ${anomaly.severity}`}
                    key={`${anomaly.anomaly_type}-${anomaly.detected_at}-${anomaly.amount}`}
                  >
                    <div>
                      <span>{anomaly.severity}</span>
                      <strong>{anomaly.title}</strong>
                      <p>{anomaly.description}</p>
                      <small>{formatDisplayDate(anomaly.detected_at)}</small>
                    </div>
                    <aside>{formatCurrency(anomaly.amount)}</aside>
                  </li>
                ))}
                {intelligence.anomalies.length === 0 ? (
                  <li className="empty-list-item">
                    <StateMessage
                      description="No unusual spending signals were found in this range."
                      title="No anomalies"
                    />
                  </li>
                ) : null}
              </ul>
            </section>
          </div>
        </>
      ) : null}
    </section>
  );
}

function formatSignedPercent(value: string): string {
  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) {
    return "0%";
  }

  const sign = numericValue > 0 ? "+" : "";
  return `${sign}${numericValue.toFixed(0)}%`;
}

function formatDisplayDate(value: string): string {
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
  }).format(new Date(value));
}

function toAdvancedErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  return "Unable to load advanced intelligence. Check your connection and try again.";
}
