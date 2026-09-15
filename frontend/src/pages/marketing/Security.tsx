import { KeyRound, Lock, ShieldCheck } from "lucide-react";

import { Card } from "../../components/Card";

// Every claim on this page describes a guarantee actually implemented and
// tested in the codebase (see backend/app/tests/test_firm_isolation.py and
// the auth/RBAC layer) - no forward-looking or invented claims.
const GUARANTEES = [
  {
    icon: Lock,
    title: "Firm-level data isolation at the query layer",
    description:
      "Every case, document, and derived record carries a firm identifier, and every database query is filtered by it - not only checked at the API boundary. This is proven by an automated test suite that verifies one firm's token can never read another firm's data, run on every change before it can merge.",
  },
  {
    icon: KeyRound,
    title: "Modern authentication",
    description:
      "Passwords are hashed with bcrypt, never stored in plain text. Sessions use short-lived JSON Web Token access tokens paired with longer-lived refresh tokens, both signed with a secret held only in server-side configuration.",
  },
  {
    icon: ShieldCheck,
    title: "Role-based access control",
    description:
      "Firm administrator, lawyer, and paralegal roles restrict which actions each user can perform within a firm account.",
  },
];

export function Security() {
  return (
    <div className="mx-auto max-w-4xl px-6 py-16">
      <h1 className="text-3xl font-bold text-slate-900">Security and Trust</h1>
      <p className="mt-4 text-slate-600">
        Legal buyers evaluate trust before they evaluate features. Here is exactly what is built,
        described plainly.
      </p>

      <div className="mt-10 space-y-6">
        {GUARANTEES.map(({ icon: Icon, title, description }) => (
          <Card key={title} className="flex gap-4">
            <Icon className="h-6 w-6 shrink-0 text-brand-600" aria-hidden />
            <div>
              <h3 className="font-semibold text-slate-900">{title}</h3>
              <p className="mt-1 text-sm text-slate-600">{description}</p>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
