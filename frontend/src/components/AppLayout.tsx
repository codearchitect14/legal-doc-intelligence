import { FolderKanban, LogOut, Scale, Settings } from "lucide-react";
import { Link, NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../lib/auth";

const NAV_ITEMS = [
  { to: "/app", label: "Cases", icon: FolderKanban, end: true },
  { to: "/app/settings", label: "Settings", icon: Settings, end: false },
];

export function AppLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="flex w-60 flex-col border-r border-slate-200 bg-white">
        <div className="flex items-center gap-2 px-5 py-5 font-bold text-slate-900">
          <Scale className="h-5 w-5 text-brand-600" aria-hidden />
          Legal Doc Intel
        </div>
        <nav className="flex-1 space-y-1 px-3">
          {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium ${
                  isActive ? "bg-brand-50 text-brand-700" : "text-slate-600 hover:bg-slate-100"
                }`
              }
            >
              <Icon className="h-4 w-4" aria-hidden />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-3">
          <Link to="/" className="text-sm text-slate-400 hover:text-slate-600">
            ← Marketing site
          </Link>
          <div className="flex items-center gap-4 text-sm">
            <span className="text-slate-600">{user?.email}</span>
            <button
              onClick={logout}
              className="flex items-center gap-1.5 font-medium text-slate-500 hover:text-slate-900"
            >
              <LogOut className="h-4 w-4" aria-hidden />
              Log out
            </button>
          </div>
        </header>
        <main className="flex-1 p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
