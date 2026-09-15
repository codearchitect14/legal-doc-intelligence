import { Card } from "../../components/Card";
import { useAuth } from "../../lib/auth";

export function Settings() {
  const { user } = useAuth();

  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-900">Settings</h1>

      <Card className="mt-6 max-w-md">
        <h2 className="font-semibold text-slate-900">Your Account</h2>
        <dl className="mt-3 space-y-2 text-sm">
          <div className="flex justify-between">
            <dt className="text-slate-500">Email</dt>
            <dd className="text-slate-900">{user?.email}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-slate-500">Role</dt>
            <dd className="capitalize text-slate-900">{user?.role.replace(/_/g, " ")}</dd>
          </div>
        </dl>
      </Card>
    </div>
  );
}
