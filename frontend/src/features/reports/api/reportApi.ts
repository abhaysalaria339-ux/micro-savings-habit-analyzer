import { env } from "../../../config/env";
import { getAccessToken } from "../../../lib/auth/tokenStorage";

export async function downloadMonthlyReport(): Promise<void> {
  const headers = new Headers();
  const accessToken = getAccessToken();
  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  const response = await fetch(`${env.apiBaseUrl}/reports/monthly.csv`, {
    headers,
  });
  if (!response.ok) {
    throw new Error("Unable to download monthly report.");
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `micro-savings-report-${new Date().toISOString().slice(0, 7)}.csv`;
  link.click();
  window.URL.revokeObjectURL(url);
}
