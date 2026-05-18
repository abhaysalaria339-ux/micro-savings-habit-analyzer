import { ChangeEvent, FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { ErrorMessage } from "../components/ErrorMessage";
import { StateMessage } from "../components/StateMessage";
import {
  changePassword,
  deleteAccount,
  downloadBackup,
  ForecastResponse,
  getForecast,
  getNotifications,
  getSettings,
  getSubscriptions,
  importBackup,
  importPdfStatement,
  markNotificationsRead,
  NotificationListResponse,
  resetDemoData,
  seedDemoData,
  SubscriptionResponse,
  syncNotifications,
  updateProfile,
  updateSettings,
  UserSettings,
} from "../features/more/api/moreApi";
import { clearAccessToken } from "../lib/auth/tokenStorage";
import { formatCurrency } from "../lib/formatters";

const defaultSettings: UserSettings = {
  currency: "INR",
  monthly_income: "",
  savings_target_percentage: "20.00",
  email_notifications_enabled: false,
  sms_notifications_enabled: false,
  phone_number: "",
};

export function MorePage() {
  const navigate = useNavigate();
  const [settings, setSettings] = useState<UserSettings>(defaultSettings);
  const [notifications, setNotifications] = useState<NotificationListResponse | null>(null);
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [subscriptions, setSubscriptions] = useState<SubscriptionResponse | null>(null);
  const [profileName, setProfileName] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false;

    async function loadMoreData() {
      setIsLoading(true);
      setError(null);
      try {
        const [settingsResponse, notificationResponse, forecastResponse, subscriptionResponse] =
          await Promise.all([
            getSettings(),
            getNotifications(),
            getForecast(),
            getSubscriptions(),
          ]);
        if (!ignore) {
          setSettings({
            ...settingsResponse,
            monthly_income: settingsResponse.monthly_income ?? "",
            phone_number: settingsResponse.phone_number ?? "",
          });
          setNotifications(notificationResponse);
          setForecast(forecastResponse);
          setSubscriptions(subscriptionResponse);
        }
      } catch {
        if (!ignore) {
          setError("Unable to load advanced tools. Check your connection and try again.");
        }
      } finally {
        if (!ignore) {
          setIsLoading(false);
        }
      }
    }

    void loadMoreData();

    return () => {
      ignore = true;
    };
  }, []);

  async function handleSettingsSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await runAction("Settings saved.", async () => {
      const response = await updateSettings(settings);
      setSettings({
        ...response,
        monthly_income: response.monthly_income ?? "",
        phone_number: response.phone_number ?? "",
      });
    });
  }

  async function handleProfileSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await runAction("Profile updated.", () => updateProfile(profileName));
  }

  async function handlePasswordSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await runAction("Password changed.", async () => {
      await changePassword(currentPassword, newPassword);
      setCurrentPassword("");
      setNewPassword("");
    });
  }

  async function handlePdfImport(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    await runAction("PDF statement imported.", () => importPdfStatement(file));
  }

  async function handleBackupImport(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    await runAction("Backup imported.", () => importBackup(file));
  }

  async function runAction(successMessage: string, action: () => Promise<unknown>) {
    setError(null);
    setStatus(null);

    try {
      await action();
      setStatus(successMessage);
    } catch {
      setError("Action failed. Please verify the input and try again.");
    }
  }

  async function handleDeleteAccount() {
    const shouldDelete = window.confirm("Delete your account and all data?");
    if (!shouldDelete) {
      return;
    }

    await runAction("Account deleted.", async () => {
      await deleteAccount();
      clearAccessToken();
      navigate("/auth/login", { replace: true });
    });
  }

  return (
    <section className="page-surface" aria-labelledby="more-title">
      <div className="page-heading">
        <div>
          <p>Controls</p>
          <h1 id="more-title">More</h1>
        </div>
      </div>

      <ErrorMessage message={error} title="Action unavailable" />
      {status ? (
        <p className="form-message success" role="status">
          {status}
        </p>
      ) : null}

      {isLoading ? (
        <StateMessage
          description="Loading settings, notifications, forecasts, and account tools."
          title="Loading tools"
          variant="loading"
        />
      ) : null}

      <div className="more-grid">
        <section className="dashboard-panel">
          <div className="panel-heading">
            <div>
              <p>Settings</p>
              <h2>Personalization</h2>
            </div>
          </div>
          <form className="compact-form" onSubmit={handleSettingsSubmit}>
            <label>
              Monthly income
              <input
                inputMode="decimal"
                onChange={(event) =>
                  setSettings({ ...settings, monthly_income: event.target.value })
                }
                placeholder="50000.00"
                type="number"
                value={settings.monthly_income ?? ""}
              />
            </label>
            <label>
              Savings target %
              <input
                max="100"
                min="0"
                onChange={(event) =>
                  setSettings({
                    ...settings,
                    savings_target_percentage: event.target.value,
                  })
                }
                type="number"
                value={settings.savings_target_percentage}
              />
            </label>
            <label>
              Phone number
              <input
                onChange={(event) =>
                  setSettings({ ...settings, phone_number: event.target.value })
                }
                placeholder="+91..."
                type="tel"
                value={settings.phone_number ?? ""}
              />
            </label>
            <label className="toggle-row">
              <input
                checked={settings.email_notifications_enabled}
                onChange={(event) =>
                  setSettings({
                    ...settings,
                    email_notifications_enabled: event.target.checked,
                  })
                }
                type="checkbox"
              />
              Email notifications
            </label>
            <label className="toggle-row">
              <input
                checked={settings.sms_notifications_enabled}
                onChange={(event) =>
                  setSettings({
                    ...settings,
                    sms_notifications_enabled: event.target.checked,
                  })
                }
                type="checkbox"
              />
              SMS notifications
            </label>
            <button className="primary-button" type="submit">
              Save settings
            </button>
          </form>
        </section>

        <section className="dashboard-panel">
          <div className="panel-heading">
            <div>
              <p>Forecast</p>
              <h2>Month-end projection</h2>
            </div>
            <span className="confidence-pill">{forecast?.confidence ?? "low"}</span>
          </div>
          <div className="more-stat">
            <strong>{formatCurrency(forecast?.month_end_projection ?? "0")}</strong>
            <p>{forecast?.summary ?? "Add expenses to generate a projection."}</p>
            <small>Savings gap {formatCurrency(forecast?.projected_savings_gap ?? "0")}</small>
          </div>
        </section>

        <section className="dashboard-panel">
          <div className="panel-heading">
            <div>
              <p>Notifications</p>
              <h2>Alert center</h2>
            </div>
            <span className="confidence-pill">{notifications?.unread_count ?? 0} unread</span>
          </div>
          <div className="button-row">
            <button
              className="secondary-button"
              onClick={() => void runAction("Notifications synced.", syncNotifications)}
              type="button"
            >
              Sync alerts
            </button>
            <button
              className="secondary-button"
              onClick={() => void runAction("Notifications marked read.", markNotificationsRead)}
              type="button"
            >
              Mark read
            </button>
          </div>
          <ul className="compact-list">
            {(notifications?.items ?? []).slice(0, 5).map((notification) => (
              <li key={notification.id}>
                <strong>{notification.title}</strong>
                <p>{notification.message}</p>
              </li>
            ))}
          </ul>
        </section>

        <section className="dashboard-panel">
          <div className="panel-heading">
            <div>
              <p>Subscriptions</p>
              <h2>Recurring bills</h2>
            </div>
          </div>
          <ul className="compact-list">
            {(subscriptions?.candidates ?? []).map((candidate) => (
              <li key={`${candidate.category}-${candidate.description ?? "none"}`}>
                <strong>{candidate.description || candidate.category}</strong>
                <p>
                  {formatCurrency(candidate.estimated_monthly_cost)} monthly ·{" "}
                  {candidate.confidence}
                </p>
              </li>
            ))}
          </ul>
        </section>

        <section className="dashboard-panel">
          <div className="panel-heading">
            <div>
              <p>Import</p>
              <h2>PDF and backup</h2>
            </div>
          </div>
          <label className="file-picker">
            <span>Import bank PDF</span>
            <input accept="application/pdf" onChange={handlePdfImport} type="file" />
          </label>
          <label className="file-picker">
            <span>Import backup JSON</span>
            <input accept="application/json" onChange={handleBackupImport} type="file" />
          </label>
          <button
            className="secondary-button"
            onClick={() => void runAction("Backup downloaded.", downloadBackup)}
            type="button"
          >
            Export backup
          </button>
        </section>

        <section className="dashboard-panel">
          <div className="panel-heading">
            <div>
              <p>Demo</p>
              <h2>Demo data tools</h2>
            </div>
          </div>
          <div className="button-row">
            <button
              className="secondary-button"
              onClick={() => void runAction("Demo data seeded.", seedDemoData)}
              type="button"
            >
              Seed data
            </button>
            <button
              className="danger-button"
              onClick={() => void runAction("Demo data reset.", resetDemoData)}
              type="button"
            >
              Reset data
            </button>
          </div>
        </section>

        <section className="dashboard-panel">
          <div className="panel-heading">
            <div>
              <p>Account</p>
              <h2>Profile and security</h2>
            </div>
          </div>
          <form className="compact-form" onSubmit={handleProfileSubmit}>
            <label>
              Full name
              <input
                onChange={(event) => setProfileName(event.target.value)}
                placeholder="Your name"
                type="text"
                value={profileName}
              />
            </label>
            <button className="secondary-button" type="submit">
              Update profile
            </button>
          </form>
          <form className="compact-form" onSubmit={handlePasswordSubmit}>
            <label>
              Current password
              <input
                onChange={(event) => setCurrentPassword(event.target.value)}
                type="password"
                value={currentPassword}
              />
            </label>
            <label>
              New password
              <input
                onChange={(event) => setNewPassword(event.target.value)}
                type="password"
                value={newPassword}
              />
            </label>
            <button className="secondary-button" type="submit">
              Change password
            </button>
          </form>
          <button className="danger-button" onClick={() => void handleDeleteAccount()} type="button">
            Delete account
          </button>
        </section>
      </div>
    </section>
  );
}
