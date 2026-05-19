import { useEffect, useMemo, useState } from "react";
import type { CSSProperties } from "react";

import { ApiError } from "../lib/api/apiError";
import { ErrorMessage } from "../components/ErrorMessage";
import { StateMessage } from "../components/StateMessage";
import { subscribeToExpenseDataChanged } from "../lib/expenseEvents";
import { formatCurrency } from "../lib/formatters";
import {
  DashboardResponse,
  getDashboard,
  HabitTimelineEvent,
  SpendingTrendPoint,
} from "../features/dashboard/api/dashboardApi";

const trendChartTypeOptions = ["bar", "line", "area"] as const;
type TrendChartType = (typeof trendChartTypeOptions)[number];

const trendChartTypeLabels: Record<TrendChartType, string> = {
  area: "Area",
  bar: "Bar",
  line: "Line",
};

const trendChartPreferenceKey = "dashboard-trend-chart-type";

export function DashboardPage() {
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);
  const [trendChartType, setTrendChartType] = useState<TrendChartType>(
    getInitialTrendChartType,
  );

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

  useEffect(() => {
    window.localStorage.setItem(trendChartPreferenceKey, trendChartType);
  }, [trendChartType]);

  useEffect(() => {
    return subscribeToExpenseDataChanged(() => {
      setReloadKey((value) => value + 1);
    });
  }, []);

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
        label: "Leak risk",
        value: `${dashboard.money_leak_score.score}/100`,
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
            <label className="chart-type-control" htmlFor="trend-chart-type">
              <span>Chart</span>
              <select
                id="trend-chart-type"
                onChange={(event) =>
                  setTrendChartType(toTrendChartType(event.target.value))
                }
                value={trendChartType}
              >
                {trendChartTypeOptions.map((option) => (
                  <option key={option} value={option}>
                    {trendChartTypeLabels[option]}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <TrendChart
            chartType={trendChartType}
            points={dashboard?.spending_trends.points ?? []}
          />
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

      <section
        className={`dashboard-panel money-leak-score-panel ${dashboard?.money_leak_score.risk_level ?? "low"}`}
        aria-labelledby="money-leak-score-title"
      >
        <div className="panel-heading">
          <div>
            <p>Leak score</p>
            <h2 id="money-leak-score-title">Invisible money leak risk</h2>
          </div>
          <span className="risk-pill">
            {dashboard?.money_leak_score.risk_level ?? "low"} risk
          </span>
        </div>

        {dashboard ? (
          <div className="money-leak-score-grid">
            <div className="money-leak-score-hero">
              <span>Risk score</span>
              <strong>{dashboard.money_leak_score.score}/100</strong>
              <small>
                {formatCurrency(dashboard.money_leak_score.projected_monthly_leak)} projected
                monthly leak
              </small>
            </div>

            <div className="money-leak-score-copy">
              <p>{dashboard.money_leak_score.summary}</p>
              <strong>{dashboard.money_leak_score.recommended_action}</strong>
            </div>

            <ul className="money-leak-evidence-list">
              {dashboard.money_leak_score.evidence.slice(0, 3).map((item) => (
                <li key={item.name}>
                  <span>{item.impact > 0 ? `+${item.impact}` : item.impact}</span>
                  <p>{item.message}</p>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <StateMessage
            description="Add repeated expenses to calculate leak risk."
            title="No money leak score yet"
          />
        )}
      </section>

      <section className="dashboard-panel habit-timeline-panel" aria-labelledby="habit-timeline-title">
        <div className="panel-heading">
          <div>
            <p>Behavior story</p>
            <h2 id="habit-timeline-title">Habit timeline</h2>
          </div>
        </div>

        <HabitTimeline events={dashboard?.habit_timeline?.events ?? []} />
      </section>

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

function HabitTimeline({ events }: { events: HabitTimelineEvent[] }) {
  if (events.length === 0) {
    return (
      <StateMessage
        description="Add more expenses and the timeline will turn spending behavior into clear habit moments."
        title="No timeline events yet"
      />
    );
  }

  return (
    <ol className="habit-timeline-list">
      {events.slice(0, 5).map((event) => (
        <li key={`${event.event_type}-${event.happened_at}-${event.title}`}>
          <span className={`timeline-dot ${event.severity}`} aria-hidden="true" />
          <div>
            <time dateTime={event.happened_at}>{formatShortDate(event.happened_at)}</time>
            <strong>{event.title}</strong>
            <p>{event.description}</p>
            <small>{event.action}</small>
          </div>
          {event.amount ? (
            <span className="timeline-amount">{formatCurrency(event.amount)}</span>
          ) : null}
        </li>
      ))}
    </ol>
  );
}

function TrendChart({
  chartType,
  points,
}: {
  chartType: TrendChartType;
  points: SpendingTrendPoint[];
}) {
  const visiblePoints = points.slice(-8);
  const maxAmount = Math.max(
    ...visiblePoints.map((point) => Number(point.total_amount)),
    1,
  );
  const averageAmount =
    visiblePoints.reduce((total, point) => total + Number(point.total_amount), 0) /
    Math.max(visiblePoints.length, 1);

  if (visiblePoints.length === 0) {
    return (
      <StateMessage
        description="Add daily expenses and the trend chart will show how your spending changes over time."
        title="No trend data yet"
      />
    );
  }

  if (chartType === "line" || chartType === "area") {
    return (
      <TrendLineChart
        averageAmount={averageAmount}
        chartType={chartType}
        maxAmount={maxAmount}
        points={visiblePoints}
      />
    );
  }

  return (
    <div
      className="trend-bars trend-chart"
      aria-label="Spending trend bar chart"
      style={{ "--trend-point-count": visiblePoints.length } as CSSProperties}
    >
      {visiblePoints.map((point) => {
        const amount = Number(point.total_amount);
        const height = Math.max(12, (amount / maxAmount) * 100);
        const palette = getTrendPalette(amount, averageAmount);
        return (
          <div
            aria-label={`${formatShortDate(point.period_start)} ${formatCurrency(point.total_amount)}`}
            className="trend-bar-item"
            key={point.period_start}
            style={
              {
                "--chart-point-color": palette.color,
                "--chart-point-glow": palette.glow,
              } as CSSProperties
            }
          >
            <span style={{ height: `${height}%` }} />
            <small>{formatShortDate(point.period_start)}</small>
          </div>
        );
      })}
    </div>
  );
}

function TrendLineChart({
  averageAmount,
  chartType,
  maxAmount,
  points,
}: {
  averageAmount: number;
  chartType: Extract<TrendChartType, "area" | "line">;
  maxAmount: number;
  points: SpendingTrendPoint[];
}) {
  const chartWidth = 360;
  const chartHeight = 190;
  const chartLeft = 18;
  const chartRight = chartWidth - 18;
  const chartTop = 18;
  const chartBottom = 150;
  const chartRange = chartBottom - chartTop;
  const step = points.length > 1 ? (chartRight - chartLeft) / (points.length - 1) : 0;

  const renderedPoints = points.map((point, index) => {
    const amount = Number(point.total_amount);
    const palette = getTrendPalette(amount, averageAmount);
    const x = points.length === 1 ? chartWidth / 2 : chartLeft + step * index;
    const y = chartBottom - (amount / maxAmount) * chartRange;

    return {
      amount,
      color: palette.color,
      glow: palette.glow,
      key: point.period_start,
      label: formatShortDate(point.period_start),
      x,
      y,
    };
  });

  const linePath = renderedPoints
    .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`)
    .join(" ");
  const areaPath =
    renderedPoints.length > 1
      ? `${linePath} L ${renderedPoints[renderedPoints.length - 1].x} ${chartBottom} L ${renderedPoints[0].x} ${chartBottom} Z`
      : "";

  return (
    <div
      className={`trend-line-chart trend-chart ${chartType}`}
      aria-label={`Spending trend ${chartType} chart`}
    >
      <svg
        aria-hidden="true"
        className="trend-svg"
        focusable="false"
        preserveAspectRatio="none"
        viewBox={`0 0 ${chartWidth} ${chartHeight}`}
      >
        <line className="trend-grid-line" x1="18" x2="342" y1="150" y2="150" />
        <line className="trend-grid-line soft" x1="18" x2="342" y1="84" y2="84" />
        {chartType === "area" && areaPath ? (
          <path className="trend-area-fill" d={areaPath} />
        ) : null}
        <path className="trend-line-path" d={linePath} />
        {renderedPoints.map((point) => (
          <circle
            className="trend-point"
            cx={point.x}
            cy={point.y}
            fill={point.color}
            key={point.key}
            r="4.5"
          />
        ))}
      </svg>
      <div
        className="trend-line-labels"
        style={{ "--trend-point-count": points.length } as CSSProperties}
      >
        {renderedPoints.map((point) => (
          <span key={point.key}>
            <small>{point.label}</small>
            <strong>{formatCurrency(point.amount)}</strong>
          </span>
        ))}
      </div>
    </div>
  );
}

function getTrendPalette(amount: number, averageAmount: number): {
  color: string;
  glow: string;
} {
  if (amount <= averageAmount * 0.75) {
    return { color: "#34c759", glow: "#49fa76ff" };
  }

  if (amount <= averageAmount * 1.15) {
    return { color: "#ffcc00", glow: "#fdd948ff" };
  }

  if (amount <= averageAmount * 1.5) {
    return { color: "#ff9500", glow: "#feae3dff" };
  }

  return { color: "#ff3b30", glow: "#fb8983ff" };
}

function toTrendChartType(value: string): TrendChartType {
  return trendChartTypeOptions.includes(value as TrendChartType)
    ? (value as TrendChartType)
    : "bar";
}

function getInitialTrendChartType(): TrendChartType {
  return toTrendChartType(window.localStorage.getItem(trendChartPreferenceKey) ?? "bar");
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
