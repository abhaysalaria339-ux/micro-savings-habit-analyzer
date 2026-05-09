import { apiRequest } from "../../../lib/api/httpClient";

export type AuthToken = {
  access_token: string;
  token_type: string;
};

export type User = {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type RegisterPayload = LoginPayload & {
  full_name?: string;
};

export function loginUser(payload: LoginPayload): Promise<AuthToken> {
  return apiRequest<AuthToken>("/auth/login", {
    method: "POST",
    body: payload,
  });
}

export function registerUser(payload: RegisterPayload): Promise<User> {
  return apiRequest<User>("/auth/register", {
    method: "POST",
    body: payload,
  });
}

export function getCurrentUser(): Promise<User> {
  return apiRequest<User>("/auth/me");
}
