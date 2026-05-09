import { env } from "../../config/env";
import { getAccessToken } from "../auth/tokenStorage";
import { ApiError } from "./apiError";

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
};

export async function apiRequest<TResponse>(
  path: string,
  options: RequestOptions = {},
): Promise<TResponse> {
  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");

  if (options.body !== undefined) {
    headers.set("Content-Type", "application/json");
  }

  const accessToken = getAccessToken();
  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  const response = await fetch(`${env.apiBaseUrl}${path}`, {
    ...options,
    headers,
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });

  if (!response.ok) {
    throw await toApiError(response);
  }

  if (response.status === 204) {
    return undefined as TResponse;
  }

  return response.json() as Promise<TResponse>;
}

async function toApiError(response: Response): Promise<ApiError> {
  const fallbackMessage = "Request failed.";

  try {
    const payload = await response.json();
    return new ApiError(
      payload?.error?.message ?? fallbackMessage,
      response.status,
      payload?.error?.details,
    );
  } catch {
    return new ApiError(fallbackMessage, response.status);
  }
}
