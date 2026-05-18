import { env } from "../../../config/env";
import { apiRequest } from "../../../lib/api/httpClient";
import { getAccessToken } from "../../../lib/auth/tokenStorage";

export type UserSettings = {
  currency: string;
  monthly_income: string | null;
  savings_target_percentage: string;
  email_notifications_enabled: boolean;
  sms_notifications_enabled: boolean;
  phone_number: string | null;
};

export type NotificationItem = {
  id: string;
  notification_type: string;
  severity: "info" | "warning" | "critical";
  channel: "in_app" | "email" | "sms";
  delivery_status: "pending" | "sent" | "failed";
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
};

export type NotificationListResponse = {
  items: NotificationItem[];
  unread_count: number;
};

export type ForecastResponse = {
  month_end_projection: string;
  current_month_spend: string;
  daily_average: string;
  projected_savings_gap: string;
  confidence: string;
  summary: string;
};

export type SubscriptionResponse = {
  candidates: Array<{
    category: string;
    description: string | null;
    occurrence_count: number;
    average_amount: string;
    estimated_monthly_cost: string;
    confidence: string;
  }>;
};

export function getSettings(): Promise<UserSettings> {
  return apiRequest<UserSettings>("/settings");
}

export function updateSettings(payload: UserSettings): Promise<UserSettings> {
  return apiRequest<UserSettings>("/settings", {
    method: "PUT",
    body: {
      ...payload,
      monthly_income: payload.monthly_income || null,
      phone_number: payload.phone_number || null,
    },
  });
}

export function getNotifications(): Promise<NotificationListResponse> {
  return apiRequest<NotificationListResponse>("/notifications");
}

export function syncNotifications(): Promise<void> {
  return apiRequest<void>("/notifications/sync", { method: "POST" });
}

export function markNotificationsRead(): Promise<void> {
  return apiRequest<void>("/notifications/read-all", { method: "POST" });
}

export function getForecast(): Promise<ForecastResponse> {
  return apiRequest<ForecastResponse>("/forecast/month-end");
}

export function getSubscriptions(): Promise<SubscriptionResponse> {
  return apiRequest<SubscriptionResponse>("/subscriptions");
}

export function seedDemoData(): Promise<void> {
  return apiRequest<void>("/demo/seed", { method: "POST" });
}

export function resetDemoData(): Promise<void> {
  return apiRequest<void>("/demo/reset", { method: "DELETE" });
}

export function updateProfile(fullName: string): Promise<void> {
  return apiRequest<void>("/account/profile", {
    method: "PATCH",
    body: { full_name: fullName },
  });
}

export function changePassword(
  currentPassword: string,
  newPassword: string,
): Promise<void> {
  return apiRequest<void>("/account/password", {
    method: "PATCH",
    body: { current_password: currentPassword, new_password: newPassword },
  });
}

export function deleteAccount(): Promise<void> {
  return apiRequest<void>("/account", { method: "DELETE" });
}

export async function downloadBackup(): Promise<void> {
  const payload = await apiRequest<unknown>("/backup/export");
  const blob = new Blob([JSON.stringify(payload, null, 2)], {
    type: "application/json",
  });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "micro-savings-backup.json";
  link.click();
  window.URL.revokeObjectURL(url);
}

export async function importPdfStatement(file: File): Promise<void> {
  const base64 = await fileToBase64(file);
  await apiRequest("/expenses/import/pdf", {
    method: "POST",
    body: { pdf_base64: base64 },
  });
}

export async function importBackup(file: File): Promise<void> {
  const payload = JSON.parse(await file.text());
  await apiRequest("/backup/import", {
    method: "POST",
    body: { payload, skip_duplicates: true },
  });
}

function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const value = String(reader.result ?? "");
      resolve(value.includes(",") ? value.split(",")[1] : value);
    };
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });
}

export async function authenticatedFetch(path: string): Promise<Response> {
  const headers = new Headers();
  const token = getAccessToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  return fetch(`${env.apiBaseUrl}${path}`, { headers });
}
