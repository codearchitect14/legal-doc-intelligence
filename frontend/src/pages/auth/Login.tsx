import { Scale } from "lucide-react";
import { type FormEvent, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { Button } from "../../components/Button";
import { Card } from "../../components/Card";
import { ApiError } from "../../lib/apiClient";
import { useAuth } from "../../lib/auth";

export function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(email, password);
      const redirectTo = (location.state as { from?: string } | null)?.from ?? "/app";
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-6">
      <Card className="w-full max-w-sm">
        <div className="flex items-center gap-2 font-bold text-slate-900">
          <Scale className="h-6 w-6 text-brand-600" aria-hidden />
          Legal Doc Intelligence
        </div>
        <h1 className="mt-4 text-xl font-semibold text-slate-900">Log in</h1>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>
          {error && <p className="text-sm text-danger-500">{error}</p>}
          <Button type="submit" disabled={submitting} className="w-full justify-center">
            {submitting ? "Logging in…" : "Log In"}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-500">
          New firm?{" "}
          <Link to="/register" className="font-medium text-brand-700 hover:underline">
            Register your firm
          </Link>
        </p>
      </Card>
    </div>
  );
}
