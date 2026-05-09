import { useEffect, useMemo, useState } from "react";

import { ApiError } from "../lib/api/apiError";
import { ErrorMessage } from "../components/ErrorMessage";
import { StateMessage } from "../components/StateMessage";
import { formatCurrency } from "../lib/formatters";
import {
  DashboardResponse,
  getDashboard,
  SpendingTrendPoint,
} from "../features/dashboard/api/dashboardApi";

export function DashboardPage() {
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let ignore = false;

    async function loadDashboard() {
      setIsLoading(true);
      setError(null);

      try {
        const response = await getDashboard();
        if (!ignore) {
          setDashboard(response);
        }
      } catch (caughtError) {
        if (!ignore) {
          setError(toDashboardErrorMessage(caughtError));
        }
      } finally {
        if (!ignore) {
          setIsLoading(false);
        }
      }
    }

    void loadDashboard();

    return () => {
      ignore = true;
    };
  }, [reloadKey]);

  const summaryItems = useMemo(() => {
    if (!dashboard) {
      return [
        { label: "Monthly spend", value: "--" },
        { label: "Savings opportunities", value: "--" },
        { label: "Behavior score", value: "--" },
        { label: "Active goals", value: "--" },
      ];
    }

    return [
      {
        label: "Monthly spend",
        value: formatCurrency(dashboard.spending_summary.total_amount),
      },
      {
        label: "Savings opportunities",
        value: formatCurrency(sumSavings(dashboard.savings_opportunities)),
      },
      {
        label: "Behavior score",
        value: `${dashboard.behavior_score.score}`,
      },
      {
        label: "Active goals",
        value: `${dashboard.goals.filter((goal) => !goal.is_completed).length}`,
      },
    ];
  }, [dashboard]);

  return (
    <section className="dashboard-page" aria-labelledby="dashboard-title">
      <div className="page-heading">
        <div>
          <p>Overview</p>
          <h1 id="dashboard-title">Dashboard</h1>
        </div>
      </div>

      <ErrorMessage
        actionLabel="Try again"
        message={error}
        onAction={() => setReloadKey((value) => value + 1)}
        title="Dashboard unavailable"
      />

      {isLoading ? (
        <StateMessage
          description="Refreshing spending totals, behavior score, alerts, and savings opportunities."
          title="Loading dashboard"
          variant="loading"
        />
      ) : null}

      <div className="metric-grid">
        {summaryItems.map((item) => (
          <article className="metric-panel" key={item.label}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
          </article>
        ))}
      </div>

      <div className="dashboard-grid">
        <section className="dashboard-panel" aria-labelledby="trend-title">
          <div className="panel-heading">
            <div>
              <p>Trend</p>
              <h2 id="trend-title">Spending trends</h2>
            </div>
          </div>
          <TrendBars points={dashboard?.spending_trends.points ?? []} />
        </section>

        <section className="dashboard-panel" aria-labelledby="behavior-title">
          <div className="panel-heading">
            <div>
              <p>Score</p>
              <h2 id="behavior-title">Behavior</h2>
            </div>
          </div>
          <div className="behavior-score">
            <strong>{dashboard?.behavior_score.classification ?? "--"}</strong>
            <span>{dashboard ? `${dashboard.behavior_score.score}/100` : "--"}</span>
          </div>
          <ul className="status-list compact">
            {(dashboard?.behavior_score.factors ?? []).slice(0, 3).map((factor) => (
              <li key={factor.name}>{factor.message}</li>
            ))}
          </ul>
        </section>
      </div>

      <div className="dashboard-grid lower">
        <section className="dashboard-panel" aria-labelledby="opportunities-title">
          <div className="panel-heading">
            <div>
              <p>Actions</p>
              <h2 id="opportunities-title">Savings opportunities</h2>
            </div>
          </div>
          <ul className="insight-list">
            {(dashboard?.savings_opportunities ?? []).slice(0, 4).map((insight) => (
              <li key={`${insight.insight_type}-${insight.title}`}>
                <strong>{insight.title}</strong>
                <p>{insight.action}</p>
                <span>{formatCurrency(insight.estimated_monthly_savings)} monthly</span>
              </li>
            ))}
            {dashboard && dashboard.savings_opportunities.length === 0 ? (
              <li>
                <strong>No savings opportunities yet</strong>
                <p>Add more expenses to generate stronger behavioral signals.</p>
              </li>
            ) : null}
          </ul>
        </section>

        <section className="dashboard-panel" aria-labelledby="alerts-title">
          <div className="panel-heading">
            <div>
              <p>Nudges</p>
              <h2 id="alerts-title">Alerts</h2>
            </div>
          </div>
          <ul className="status-list compact">
            {(dashboard?.alerts ?? []).slice(0, 4).map((alert) => (
              <li key={`${alert.alert_type}-${alert.title}`}>
                {alert.title}
              </li>
            ))}
            {dashboard && dashboard.alerts.length === 0 ? (
              <li>No alerts for the selected period.</li>
            ) : null}
          </ul>
        </section>
      </div>
    </section>
  );
}

function TrendBars({ points }: { points: SpendingTrendPoint[] }) {
  const maxAmount = Math.max(...points.map((point) => Number(point.total_amount)), 1);
  const visiblePoints = points.slice(-8);

  if (visiblePoints.length === 0) {
    return (
      <StateMessage
        description="Add daily expenses and the trend chart will show how your spending changes over time."
        title="No trend data yet"
      />
    );
  }

  return (
    <div className="trend-bars" aria-label="Spending trend chart">
      {visiblePoints.map((point) => {
        const height = Math.max(12, (Number(point.total_amount) / maxAmount) * 100);
        return (
          <div className="trend-bar-item" key={point.period_start}>
            <span style={{ height: `${height}%` }} />
            <small>{formatShortDate(point.period_start)}</small>
          </div>
        );
      })}
    </div>
  );
}

function sumSavings(insights: DashboardResponse["savings_opportunities"]): string {
  return insights
    .reduce((total, insight) => total + Number(insight.estimated_monthly_savings), 0)
    .toFixed(2);
}

function formatShortDate(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
  }).format(new Date(value));
}

function toDashboardErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  return "Unable to load dashboard. Check your connection and try again.";
}
