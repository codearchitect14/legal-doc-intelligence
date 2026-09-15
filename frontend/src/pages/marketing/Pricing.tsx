import { Check } from "lucide-react";
import { Link } from "react-router-dom";

import { Button } from "../../components/Button";
import { Card } from "../../components/Card";

const TIERS = [
  {
    name: "Solo",
    price: "$99",
    period: "/ month",
    description: "For solo practitioners handling a steady caseload.",
    features: ["Up to 10 active cases", "1 user seat", "Email support"],
  },
  {
    name: "Firm",
    price: "$349",
    period: "/ month",
    description: "For small and mid-sized firms with a case team.",
    features: ["Up to 75 active cases", "Up to 10 user seats", "Priority support", "Firm-wide usage reporting"],
    highlighted: true,
  },
  {
    name: "Enterprise",
    price: "Contact us",
    period: "",
    description: "For firms needing custom volume or deployment terms.",
    features: ["Unlimited cases", "Unlimited seats", "Dedicated onboarding"],
  },
];

export function Pricing() {
  return (
    <div className="mx-auto max-w-5xl px-6 py-16">
      <h1 className="text-center text-3xl font-bold text-slate-900">Simple, Transparent Pricing</h1>
      <p className="mx-auto mt-4 max-w-xl text-center text-slate-600">
        Published tiers — no quote request required to see what this costs.
      </p>

      <div className="mt-12 grid gap-6 sm:grid-cols-3">
        {TIERS.map((tier) => (
          <Card
            key={tier.name}
            className={tier.highlighted ? "border-brand-600 ring-1 ring-brand-600" : ""}
          >
            <h3 className="font-semibold text-slate-900">{tier.name}</h3>
            <p className="mt-2 text-sm text-slate-500">{tier.description}</p>
            <p className="mt-4 text-3xl font-bold text-slate-900">
              {tier.price}
              <span className="text-base font-normal text-slate-500">{tier.period}</span>
            </p>
            <ul className="mt-4 space-y-2 text-sm text-slate-600">
              {tier.features.map((feature) => (
                <li key={feature} className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-success-500" aria-hidden />
                  {feature}
                </li>
              ))}
            </ul>
            <Link to="/demo" className="mt-6 block">
              <Button
                variant={tier.highlighted ? "primary" : "secondary"}
                className="w-full justify-center"
              >
                Request a Demo
              </Button>
            </Link>
          </Card>
        ))}
      </div>
    </div>
  );
}
