import { CheckCircle2 } from "lucide-react";
import { type FormEvent, useState } from "react";

import { Button } from "../../components/Button";
import { Card } from "../../components/Card";

export function Demo() {
  const [submitted, setSubmitted] = useState(false);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    // No CRM/email infrastructure exists yet to route this anywhere real;
    // this confirms the request was captured client-side rather than
    // pretending to send it somewhere it can't go.
    setSubmitted(true);
  }

  return (
    <div className="mx-auto max-w-lg px-6 py-16">
      <h1 className="text-3xl font-bold text-slate-900">Request a Demo</h1>
      <p className="mt-3 text-slate-600">
        Tell us a bit about your firm and we'll follow up to schedule a walkthrough.
      </p>

      <Card className="mt-8">
        {submitted ? (
          <div className="flex flex-col items-center py-6 text-center">
            <CheckCircle2 className="h-10 w-10 text-success-500" aria-hidden />
            <p className="mt-3 font-semibold text-slate-900">Thanks — we'll be in touch.</p>
            <p className="mt-1 text-sm text-slate-500">
              A member of our team will reach out to schedule your demo.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700" htmlFor="name">
                Name
              </label>
              <input
                id="name"
                required
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700" htmlFor="firm">
                Firm name
              </label>
              <input
                id="firm"
                required
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700" htmlFor="email">
                Work email
              </label>
              <input
                id="email"
                type="email"
                required
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700" htmlFor="message">
                What kind of cases does your firm handle?
              </label>
              <textarea
                id="message"
                rows={3}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
              />
            </div>
            <Button type="submit" className="w-full justify-center">
              Request a Demo
            </Button>
          </form>
        )}
      </Card>
    </div>
  );
}
