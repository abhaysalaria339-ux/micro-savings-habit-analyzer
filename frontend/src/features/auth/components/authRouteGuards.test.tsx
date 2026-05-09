import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it } from "vitest";

import { clearAccessToken, setAccessToken } from "../../../lib/auth/tokenStorage";
import { RedirectIfAuthenticated } from "./RedirectIfAuthenticated";
import { RequireAuth } from "./RequireAuth";

afterEach(() => {
  clearAccessToken();
});

describe("auth route guards", () => {
  it("redirects unauthenticated users to login", () => {
    render(
      <MemoryRouter initialEntries={["/dashboard"]}>
        <Routes>
          <Route
            path="/dashboard"
            element={
              <RequireAuth>
                <h1>Dashboard</h1>
              </RequireAuth>
            }
          />
          <Route path="/auth/login" element={<h1>Log in</h1>} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByRole("heading", { name: "Log in" })).toBeInTheDocument();
  });

  it("renders protected content for authenticated users", () => {
    setAccessToken("test-token");

    render(
      <MemoryRouter initialEntries={["/dashboard"]}>
        <Routes>
          <Route
            path="/dashboard"
            element={
              <RequireAuth>
                <h1>Dashboard</h1>
              </RequireAuth>
            }
          />
          <Route path="/auth/login" element={<h1>Log in</h1>} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
  });

  it("redirects authenticated users away from auth pages", () => {
    setAccessToken("test-token");

    render(
      <MemoryRouter initialEntries={["/auth/login"]}>
        <Routes>
          <Route
            path="/auth/login"
            element={
              <RedirectIfAuthenticated>
                <h1>Log in</h1>
              </RedirectIfAuthenticated>
            }
          />
          <Route path="/dashboard" element={<h1>Dashboard</h1>} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
  });
});
