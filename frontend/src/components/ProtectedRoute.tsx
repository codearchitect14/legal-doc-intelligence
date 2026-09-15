import { Navigate, Outlet } from "react-router-dom";

import { useAuth } from "../lib/auth";
import { Spinner } from "./Spinner";

export function ProtectedRoute() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Spinner label="Checking your session…" />
      </div>
    );
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return <Outlet />;
}
