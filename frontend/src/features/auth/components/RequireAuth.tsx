import { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";

import { getAccessToken } from "../../../lib/auth/tokenStorage";

type RequireAuthProps = {
  children: ReactNode;
};

export function RequireAuth({ children }: RequireAuthProps) {
  const location = useLocation();
  const accessToken = getAccessToken();

  if (!accessToken) {
    return <Navigate to="/auth/login" replace state={{ from: location }} />;
  }

  return children;
}
