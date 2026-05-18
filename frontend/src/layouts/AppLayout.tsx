import { MouseEvent, useEffect, useState } from "react";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";

import { getCurrentUser, User } from "../features/auth/api/authApi";
import { ApiError } from "../lib/api/apiError";
import { clearAccessToken } from "../lib/auth/tokenStorage";
import {
  workspaceSectionChangeEvent,
  workspaceSectionConfig,
} from "../pages/workspaceConfig";

type ThemeMode = "light" | "dark";

const navigationItems = workspaceSectionConfig.map((section) => ({
  label: section.label,
  sectionId: section.id,
  to: `/dashboard#${section.id}`,
}));

const routeSectionByPath = new Map([
  ["/dashboard", "workspace-dashboard"],
  ["/expenses", "workspace-expenses"],
  ["/goals", "workspace-goals"],
  ["/budgets", "workspace-budgets"],
  ["/insights", "workspace-insights"],
  ["/advanced", "workspace-advanced"],
  ["/simulator", "workspace-simulator"],
  ["/more", "workspace-more"],
]);

export function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [activeWorkspaceSection, setActiveWorkspaceSection] = useState(() =>
    getInitialWorkspaceSection(),
  );
  const [themeMode, setThemeMode] = useState<ThemeMode>(() => getInitialThemeMode());
  const routeActiveSection =
    routeSectionByPath.get(location.pathname) || "workspace-dashboard";
  const displayedActiveSection =
    location.pathname === "/dashboard" ? activeWorkspaceSection : routeActiveSection;

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

  useEffect(() => {
    document.documentElement.dataset.theme = themeMode;
    window.localStorage.setItem("theme-mode", themeMode);
  }, [themeMode]);

  useEffect(() => {
    function handleWorkspaceSectionChange(event: Event) {
      const sectionId = (event as CustomEvent<string>).detail;
      if (sectionId) {
        setActiveWorkspaceSection(sectionId);
      }
    }

    window.addEventListener(workspaceSectionChangeEvent, handleWorkspaceSectionChange);

    return () => {
      window.removeEventListener(
        workspaceSectionChangeEvent,
        handleWorkspaceSectionChange,
      );
    };
  }, []);

  function handleLogout() {
    clearAccessToken();
    navigate("/auth/login", { replace: true });
  }

  function handleWorkspaceNavigation(
    event: MouseEvent<HTMLAnchorElement>,
    sectionId: string,
  ) {
    setActiveWorkspaceSection(sectionId);

    if (location.pathname !== "/dashboard") {
      return;
    }

    const section = document.getElementById(sectionId);
    if (!section) {
      return;
    }

    event.preventDefault();
    window.history.replaceState(null, "", `/dashboard#${sectionId}`);
    section.scrollIntoView({
      behavior: prefersReducedMotion() ? "auto" : "smooth",
      block: "start",
    });
  }

  function toggleThemeMode() {
    setThemeMode((currentTheme) => (currentTheme === "dark" ? "light" : "dark"));
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
            <Link
              aria-current={
                displayedActiveSection === item.sectionId ? "page" : undefined
              }
              className={
                displayedActiveSection === item.sectionId
                  ? "app-nav-link active"
                  : "app-nav-link"
              }
              key={item.sectionId}
              onClick={(event) => handleWorkspaceNavigation(event, item.sectionId)}
              to={item.to}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <p className="app-credit">
          Developed by <span>Abhay Salaria</span>
        </p>
      </aside>

      <div className="app-main">
        <header className="app-topbar">
          <div>
            <p>Workspace</p>
            <strong>Personal finance behavior</strong>
          </div>
          <div className="topbar-actions">
            <button
              aria-label={`Switch to ${themeMode === "dark" ? "light" : "dark"} mode`}
              className="theme-toggle-button"
              onClick={toggleThemeMode}
              type="button"
            >
              <span aria-hidden="true">{themeMode === "dark" ? "L" : "D"}</span>
              <strong>{themeMode === "dark" ? "Light" : "Dark"}</strong>
            </button>
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

function getInitialWorkspaceSection(): string {
  return window.location.hash.slice(1) || "workspace-dashboard";
}

function getInitialThemeMode(): ThemeMode {
  const savedTheme = window.localStorage.getItem("theme-mode");
  if (savedTheme === "dark" || savedTheme === "light") {
    return savedTheme;
  }

  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function prefersReducedMotion(): boolean {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
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
