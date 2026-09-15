import { Scale } from "lucide-react";
import { type FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { Button } from "../../components/Button";
import { Card } from "../../components/Card";
import { ApiError } from "../../lib/apiClient";
import { useAuth } from "../../lib/auth";

export function Register() {
  const { registerFirm } = useAuth();
  const navigate = useNavigate();
  const [firmName, setFirmName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await registerFirm({ firm_name: firmName, admin_email: email, admin_password: password });
      navigate("/app", { replace: true });
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
        <h1 className="mt-4 text-xl font-semibold text-slate-900">Register your firm</h1>
        <p className="mt-1 text-sm text-slate-500">
          Creates a firm account and its first administrator.
        </p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700" htmlFor="firmName">
              Firm name
            </label>
            <input
              id="firmName"
              required
              value={firmName}
              onChange={(e) => setFirmName(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700" htmlFor="email">
              Admin email
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
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>
          {error && <p className="text-sm text-danger-500">{error}</p>}
          <Button type="submit" disabled={submitting} className="w-full justify-center">
            {submitting ? "Creating firm…" : "Create Firm"}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-500">
          Already have an account?{" "}
          <Link to="/login" className="font-medium text-brand-700 hover:underline">
            Log in
          </Link>
        </p>
      </Card>
    </div>
  );
}
