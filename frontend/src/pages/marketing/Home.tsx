import { CheckCircle2, FileSearch, Scale as ScaleIcon } from "lucide-react";
import { Link } from "react-router-dom";

import { Button } from "../../components/Button";
import { Card } from "../../components/Card";
import { ShieldIllustration, WorkflowIllustration } from "../../components/illustrations";

export function Home() {
  return (
    <div>
      <section className="mx-auto max-w-6xl px-6 py-20 text-center">
        <h1 className="mx-auto max-w-3xl text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl">
          Turn a folder of case documents into a chronology, a damages estimate, and a first
          draft - automatically.
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-600">
          Legal Doc Intelligence classifies, cross-checks, and organizes medical records, bills,
          wage reports, and correspondence, then produces a structured case record a lawyer or
          paralegal currently builds by hand.
        </p>
        <div className="mt-8 flex items-center justify-center gap-4">
          <Link to="/demo">
            <Button className="px-6 py-3 text-base">Request a Demo</Button>
          </Link>
          <Link to="/login">
            <Button variant="secondary" className="px-6 py-3 text-base">
              Log In
            </Button>
          </Link>
        </div>
      </section>

      <section className="mx-auto max-w-5xl px-6 pb-16">
        <WorkflowIllustration className="w-full" />
      </section>

      <section className="bg-slate-50 py-16">
        <div className="mx-auto grid max-w-6xl gap-6 px-6 sm:grid-cols-3">
          <Card>
            <FileSearch className="h-6 w-6 text-brand-600" aria-hidden />
            <h3 className="mt-3 font-semibold text-slate-900">Beyond search and chat</h3>
            <p className="mt-2 text-sm text-slate-600">
              Damage calculation, deadline extraction, and inconsistency detection - analytical
              output, not just document Q&amp;A.
            </p>
          </Card>
          <Card>
            <ScaleIcon className="h-6 w-6 text-brand-600" aria-hidden />
            <h3 className="mt-3 font-semibold text-slate-900">Built for mid-sized firms</h3>
            <p className="mt-2 text-sm text-slate-600">
              Fast to set up, transparently priced - an alternative to enterprise platforms sized
              for firms that don't have a procurement department.
            </p>
          </Card>
          <Card>
            <CheckCircle2 className="h-6 w-6 text-brand-600" aria-hidden />
            <h3 className="mt-3 font-semibold text-slate-900">A model call only at the end</h3>
            <p className="mt-2 text-sm text-slate-600">
              Deterministic extraction and rules do the work first; a language model is used once
              per case, only to write the connecting narrative.
            </p>
          </Card>
        </div>
      </section>

      <section className="mx-auto max-w-5xl px-6 py-16">
        <div className="flex flex-col items-center gap-8 sm:flex-row">
          <ShieldIllustration className="h-40 w-40 shrink-0" />
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Firm data stays firm data</h2>
            <p className="mt-3 text-slate-600">
              Every case, document, and derived record is scoped to a firm at the database query
              layer - not only checked at the API boundary - so one firm can never see another
              firm's data, even from a coding mistake.{" "}
              <Link to="/security" className="font-medium text-brand-700 hover:underline">
                Read about our security model →
              </Link>
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
