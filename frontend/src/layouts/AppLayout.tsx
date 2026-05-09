import { useEffect, useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { getCurrentUser, User } from "../features/auth/api/authApi";
import { ApiError } from "../lib/api/apiError";
import { clearAccessToken } from "../lib/auth/tokenStorage";

const navigationItems = [
  { label: "Dashboard", to: "/dashboard" },
  { label: "Expenses", to: "/expenses" },
  { label: "Goals", to: "/goals" },
  { label: "Insights", to: "/insights" },
  { label: "Simulator", to: "/simulator" },
];

export function AppLayout() {
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [profileError, setProfileError] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false;

    async function loadCurrentUser() {
      try {
        const user = await getCurrentUser();
        if (!ignore) {
          setCurrentUser(user);
          setProfileError(null);
        }
      } catch (caughtError) {
        if (caughtError instanceof ApiError && caughtError.status === 401) {
          clearAccessToken();
          navigate("/auth/login", { replace: true });
          return;
        }

        if (!ignore) {
          setProfileError("Profile unavailable");
        }
      }
    }

    void loadCurrentUser();

    return () => {
      ignore = true;
    };
  }, [navigate]);

  function handleLogout() {
    clearAccessToken();
    navigate("/auth/login", { replace: true });
  }

  return (
    <div className="app-shell">
      <aside className="app-sidebar" aria-label="Primary navigation">
        <div className="app-brand">
          <span>MS</span>
          <div>
            <strong>Micro-Savings</strong>
            <small>Habit Analyzer</small>
          </div>
        </div>

        <nav className="app-nav">
          {navigationItems.map((item) => (
            <NavLink
              className={({ isActive }) =>
                isActive ? "app-nav-link active" : "app-nav-link"
              }
              key={item.to}
              to={item.to}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="app-main">
        <header className="app-topbar">
          <div>
            <p>Workspace</p>
            <strong>Personal finance behavior</strong>
          </div>
          <div className="topbar-actions">
            <div className="user-summary" aria-label="Current user">
              <span>{getInitials(currentUser)}</span>
              <div>
                <strong>{currentUser?.full_name || currentUser?.email || "Loading user"}</strong>
                <small>{profileError || currentUser?.email || "Checking session"}</small>
              </div>
            </div>
            <button className="secondary-button" onClick={handleLogout} type="button">
              Log out
            </button>
          </div>
        </header>

        <main className="app-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

function getInitials(user: User | null): string {
  const displayName = user?.full_name || user?.email;
  if (!displayName) {
    return "--";
  }

  return displayName
    .split(/[\s@.]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join("");
}
