import { Scale } from "lucide-react";
import { Link, NavLink, Outlet } from "react-router-dom";

import { Button } from "./Button";

const NAV_LINKS = [
  { to: "/product", label: "Product" },
  { to: "/solutions", label: "Solutions" },
  { to: "/security", label: "Security" },
  { to: "/pricing", label: "Pricing" },
];

export function PublicLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link to="/" className="flex items-center gap-2 font-bold text-slate-900">
            <Scale className="h-6 w-6 text-brand-600" aria-hidden />
            Legal Doc Intelligence
          </Link>
          <nav className="hidden items-center gap-6 text-sm font-medium text-slate-600 md:flex">
            {NAV_LINKS.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  isActive ? "text-brand-700" : "hover:text-slate-900"
                }
              >
                {link.label}
              </NavLink>
            ))}
          </nav>
          <div className="flex items-center gap-3">
            <Link to="/demo" className="hidden text-sm font-medium text-slate-600 hover:text-slate-900 sm:block">
              Request a Demo
            </Link>
            <Link to="/login">
              <Button variant="secondary">Log In</Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1">
        <Outlet />
      </main>

      <footer className="border-t border-slate-200 bg-slate-50">
        <div className="mx-auto max-w-6xl px-6 py-10 text-sm text-slate-500">
          <div className="flex flex-col justify-between gap-6 sm:flex-row">
            <p>© {new Date().getFullYear()} Legal Doc Intelligence. All rights reserved.</p>
            <div className="flex gap-6">
              {NAV_LINKS.map((link) => (
                <Link key={link.to} to={link.to} className="hover:text-slate-900">
                  {link.label}
                </Link>
              ))}
              <Link to="/demo" className="hover:text-slate-900">
                Contact
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
