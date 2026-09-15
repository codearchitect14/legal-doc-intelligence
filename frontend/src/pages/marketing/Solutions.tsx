import { Card } from "../../components/Card";

export function Solutions() {
  return (
    <div className="mx-auto max-w-5xl px-6 py-16">
      <h1 className="text-3xl font-bold text-slate-900">Built for the Firms Enterprise Platforms Ignore</h1>
      <p className="mt-4 max-w-2xl text-slate-600">
        Large legal AI platforms are sized, priced, and sold for enterprise firms with a
        procurement process. Mid-sized firms and solo practitioners are left with either that
        expense or plain document chat with no analytical output. Legal Doc Intelligence is built
        for what's in between.
      </p>

      <div className="mt-10 grid gap-6 sm:grid-cols-2">
        <Card>
          <h3 className="font-semibold text-slate-900">Speed of setup</h3>
          <p className="mt-2 text-sm text-slate-600">
            Register a firm, invite your team, and process your first case the same day — no
            sales-led onboarding cycle required.
          </p>
        </Card>
        <Card>
          <h3 className="font-semibold text-slate-900">Transparent pricing</h3>
          <p className="mt-2 text-sm text-slate-600">
            Published tiers, not a quote you have to request. See{" "}
            <a href="/pricing" className="font-medium text-brand-700 hover:underline">
              Pricing
            </a>
            .
          </p>
        </Card>
        <Card>
          <h3 className="font-semibold text-slate-900">Analytical output, not just chat</h3>
          <p className="mt-2 text-sm text-slate-600">
            A chronology, a damages estimate, and flagged inconsistencies — work product, not a
            search box over your documents.
          </p>
        </Card>
        <Card>
          <h3 className="font-semibold text-slate-900">Right-sized for a case team</h3>
          <p className="mt-2 text-sm text-slate-600">
            Built around how a paralegal and a lawyer actually work a case, not a broad platform
            with modules your firm will never use.
          </p>
        </Card>
      </div>
    </div>
  );
}
