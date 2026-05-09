import { ReactNode } from "react";
import { Navigate } from "react-router-dom";

import { getAccessToken } from "../../../lib/auth/tokenStorage";

type RedirectIfAuthenticatedProps = {
  children: ReactNode;
};

export function RedirectIfAuthenticated({ children }: RedirectIfAuthenticatedProps) {
  const accessToken = getAccessToken();

  if (accessToken) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}
