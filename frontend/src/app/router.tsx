import { createBrowserRouter, Navigate } from "react-router-dom";

import { RedirectIfAuthenticated } from "../features/auth/components/RedirectIfAuthenticated";
import { RequireAuth } from "../features/auth/components/RequireAuth";
import { AuthLayout } from "../layouts/AuthLayout";
import { AppLayout } from "../layouts/AppLayout";
import { DashboardPage } from "../pages/DashboardPage";
import { ExpensesPage } from "../pages/ExpensesPage";
import { GoalsPage } from "../pages/GoalsPage";
import { InsightsPage } from "../pages/InsightsPage";
import { SimulatorPage } from "../pages/SimulatorPage";
import { LoginPage } from "../pages/auth/LoginPage";
import { RegisterPage } from "../pages/auth/RegisterPage";

export const router = createBrowserRouter([
  {
    path: "/auth",
    element: (
      <RedirectIfAuthenticated>
        <AuthLayout />
      </RedirectIfAuthenticated>
    ),
    children: [
      {
        path: "login",
        element: <LoginPage />,
      },
      {
        path: "register",
        element: <RegisterPage />,
      },
    ],
  },
  {
    path: "/",
    element: (
      <RequireAuth>
        <AppLayout />
      </RequireAuth>
    ),
    children: [
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: "dashboard",
        element: <DashboardPage />,
      },
      {
        path: "expenses",
        element: <ExpensesPage />,
      },
      {
        path: "goals",
        element: <GoalsPage />,
      },
      {
        path: "insights",
        element: <InsightsPage />,
      },
      {
        path: "simulator",
        element: <SimulatorPage />,
      },
    ],
  },
]);
