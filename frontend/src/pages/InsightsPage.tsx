import { useEffect, useState } from "react";

import { ApiError } from "../lib/api/apiError";
import { ErrorMessage } from "../components/ErrorMessage";
import { StateMessage } from "../components/StateMessage";
import { formatCurrency } from "../lib/formatters";
import {
  getSavingsInsights,
  getSpendingAlerts,
  SavingsInsightsResponse,
  SpendingAlertsResponse,
} from "../features/insights/api/insightApi";
import {
  getSpendingProfile,
  MLSpendingProfileResponse,
} from "../features/ml/api/mlApi";
import { downloadMonthlyReport } from "../features/reports/api/reportApi";

type InsightPeriod = "weekly" | "monthly";

export function InsightsPage() {
  const [period, setPeriod] = useState<InsightPeriod>("monthly");
  const [insights, setInsights] = useState<SavingsInsightsResponse | null>(null);
  const [alerts, setAlerts] = useState<SpendingAlertsResponse | null>(null);
  const [spendingProfile, setSpendingProfile] =
    useState<MLSpendingProfileResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);
  const [isDownloadingReport, setIsDownloadingReport] = useState(false);

  useEffect(() => {
    let ignore = false;

    async function loadInsights() {
      setIsLoading(true);
      setError(null);

      try {
        const [insightResponse, alertResponse, profileResponse] = await Promise.all([
          getSavingsInsights(period),
          getSpendingAlerts(),
          getSpendingProfile(),
        ]);

        if (!ignore) {
          setInsights(insightResponse);
          setAlerts(alertResponse);
          setSpendingProfile(profileResponse);
        }
      } catch (caughtError) {
        if (!ignore) {
          setError(toInsightErrorMessage(caughtError));
        }
      } finally {
        if (!ignore) {
          setIsLoading(false);
        }
      }
    }

    void loadInsights();

    return () => {
      ignore = true;
    };
  }, [period, reloadKey]);

  return (
    <section className="page-surface" aria-labelledby="insights-title">
      <div className="page-heading">
        <div>
          <p>Analysis</p>
          <h1 id="insights-title">Insights</h1>
        </div>

        <div className="segmented-control" aria-label="Insight period">
          <button
            className={period === "weekly" ? "active" : ""}
            onClick={() => setPeriod("weekly")}
            type="button"
          >
            Weekly
          </button>
          <button
            className={period === "monthly" ? "active" : ""}
            onClick={() => setPeriod("monthly")}
            type="button"
          >
            Monthly
          </button>
        </div>
        <button
          className="secondary-button"
          disabled={isDownloadingReport}
          onClick={() => void handleReportDownload()}
          type="button"
        >
          {isDownloadingReport ? "Exporting..." : "Export CSV"}
        </button>
      </div>

      <ErrorMessage
        actionLabel="Try again"
        message={error}
        onAction={() => setReloadKey((value) => value + 1)}
        title="Insights unavailable"
      />

      {isLoading ? (
        <StateMessage
          description="Analyzing alerts, savings opportunities, and monthly impact."
          title="Loading insights"
          variant="loading"
        />
      ) : null}

      <div className="insights-layout">
        <section className="dashboard-panel savings-summary-panel">
          <div className="panel-heading">
            <div>
              <p>Potential</p>
              <h2>Estimated savings</h2>
            </div>
          </div>
          <strong>
            {formatCurrency(insights?.total_estimated_monthly_savings ?? "0")}
          </strong>
          <span>estimated monthly savings</span>
        </section>

        <section className="dashboard-panel" aria-labelledby="alerts-heading">
          <div className="panel-heading">
            <div>
              <p>Nudges</p>
              <h2 id="alerts-heading">Smart alerts</h2>
            </div>
          </div>
          <ul className="alert-list">
            {(alerts?.alerts ?? []).map((alert) => (
              <li className={`alert-card ${alert.severity}`} key={`${alert.alert_type}-${alert.title}`}>
                <span>{alert.severity}</span>
                <strong>{alert.title}</strong>
                <p>{alert.nudge}</p>
                <small>{formatCurrency(alert.estimated_monthly_impact)} monthly impact</small>
              </li>
            ))}
            {alerts && alerts.alerts.length === 0 ? (
              <li className="empty-list-item">
                <StateMessage
                  description="No urgent nudges are available for the current spending period."
                  title="No spending alerts"
                />
              </li>
            ) : null}
          </ul>
        </section>
      </div>

      <section className="dashboard-panel ml-profile-panel" aria-labelledby="ml-profile-heading">
        <div className="panel-heading">
          <div>
            <p>ML profile</p>
            <h2 id="ml-profile-heading">Spending behavior cluster</h2>
          </div>
          {spendingProfile ? (
            <span className="confidence-pill">
              {formatPercent(spendingProfile.confidence)} confidence
            </span>
          ) : null}
        </div>

        {spendingProfile ? (
          <div className="ml-profile-grid">
            <div className="ml-profile-summary">
              <span>{spendingProfile.profile_label}</span>
              <p>{spendingProfile.summary}</p>
              <small>
                Based on {spendingProfile.transaction_count} expenses from the last{" "}
                {spendingProfile.analysis_days} days.
              </small>
            </div>

            <div className="ml-signal-grid" aria-label="Profile signals">
              <article>
                <span>Micro-expense ratio</span>
                <strong>{formatPercent(spendingProfile.features.micro_expense_ratio)}</strong>
              </article>
              <article>
                <span>Weekend spend</span>
                <strong>{formatPercent(spendingProfile.features.weekend_spend_ratio)}</strong>
              </article>
              <article>
                <span>Food and snacks</span>
                <strong>
                  {formatPercent(spendingProfile.features.food_and_snack_spend_ratio)}
                </strong>
              </article>
            </div>

            <div>
              <h3>Why this profile</h3>
              <ul className="ml-profile-list">
                {spendingProfile.reasons.map((reason) => (
                  <li key={reason}>{reason}</li>
                ))}
              </ul>
            </div>

            <div>
              <h3>Next actions</h3>
              <ul className="ml-profile-list">
                {spendingProfile.recommendations.map((recommendation) => (
                  <li key={recommendation}>{recommendation}</li>
                ))}
              </ul>
            </div>
          </div>
        ) : (
          <StateMessage
            description="Add more expenses to generate a spending behavior cluster."
            title="No ML profile yet"
          />
        )}
      </section>

      <section className="dashboard-panel insights-panel" aria-labelledby="recommendations-heading">
        <div className="panel-heading">
          <div>
            <p>Recommendations</p>
            <h2 id="recommendations-heading">Savings insights</h2>
          </div>
        </div>
        <ul className="recommendation-list">
          {(insights?.insights ?? []).map((insight) => (
            <li key={`${insight.insight_type}-${insight.title}`}>
              <div>
                <span>{formatInsightType(insight.insight_type)}</span>
                <strong>{insight.title}</strong>
                <p>{insight.message}</p>
              </div>
              <aside>
                <strong>{formatCurrency(insight.estimated_monthly_savings)}</strong>
                <p>{insight.action}</p>
              </aside>
            </li>
          ))}
          {insights && insights.insights.length === 0 ? (
            <li className="empty-list-item">
              <StateMessage
                description="Add more expenses to generate personalized savings recommendations."
                title="No recommendations yet"
              />
            </li>
          ) : null}
        </ul>
      </section>
    </section>
  );

  async function handleReportDownload() {
    setIsDownloadingReport(true);
    setError(null);

    try {
      await downloadMonthlyReport();
    } catch {
      setError("Unable to download the monthly report. Try again.");
    } finally {
      setIsDownloadingReport(false);
    }
  }
}

function formatInsightType(type: string): string {
  return type
    .split("_")
    .map((part) => part[0].toUpperCase() + part.slice(1))
    .join(" ");
}

function formatPercent(value: string): string {
  return `${(Number(value) * 100).toFixed(0)}%`;
}

function toInsightErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  return "Unable to load insights. Check your connection and try again.";
}
