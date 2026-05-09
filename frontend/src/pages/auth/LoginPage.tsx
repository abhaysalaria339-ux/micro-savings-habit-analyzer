import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { loginUser } from "../../features/auth/api/authApi";
import { AuthError } from "../../features/auth/components/AuthError";
import { ApiError } from "../../lib/api/apiError";
import { setAccessToken } from "../../lib/auth/tokenStorage";

export function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const token = await loginUser({
        email: email.trim(),
        password,
      });
      setAccessToken(token.access_token);
      navigate("/dashboard", { replace: true });
    } catch (caughtError) {
      setError(toAuthErrorMessage(caughtError));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="auth-panel" aria-labelledby="login-title">
      <div className="auth-heading">
        <p>Micro-Savings Habit Analyzer</p>
        <h1 id="login-title">Log in</h1>
      </div>

      <form className="auth-form" onSubmit={handleSubmit}>
        <label>
          Email
          <input
            autoComplete="email"
            inputMode="email"
            name="email"
            onChange={(event) => setEmail(event.target.value)}
            required
            type="email"
            value={email}
          />
        </label>

        <label>
          Password
          <input
            autoComplete="current-password"
            minLength={8}
            name="password"
            onChange={(event) => setPassword(event.target.value)}
            required
            type="password"
            value={password}
          />
        </label>

        <AuthError message={error} />

        <button className="primary-button" disabled={isSubmitting} type="submit">
          {isSubmitting ? "Logging in..." : "Log in"}
        </button>
      </form>

      <p className="auth-switch">
        New here? <Link to="/auth/register">Create an account</Link>
      </p>
    </section>
  );
}

function toAuthErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  return "Unable to log in. Check your connection and try again.";
}
