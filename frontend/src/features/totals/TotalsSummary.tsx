import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card } from "../../components/Card";
import type { Schemas } from "../../lib/apiClient";

export function TotalsSummary({ totals }: { totals: Schemas["CaseTotalsOut"] | null }) {
  if (!totals) {
    return <p className="text-sm text-slate-500">Run analysis to see damages totals.</p>;
  }

  const data = [
    { name: "Billed", amount: Number(totals.total_billed) },
    { name: "Wage Loss", amount: Number(totals.total_wages) },
  ];

  return (
    <div className="grid gap-6 sm:grid-cols-2">
      <div className="space-y-3">
        <Card>
          <p className="text-sm text-slate-500">Total Billed</p>
          <p className="mt-1 text-2xl font-bold text-slate-900">
            ${Number(totals.total_billed).toLocaleString()}
          </p>
        </Card>
        <Card>
          <p className="text-sm text-slate-500">Total Wage Loss</p>
          <p className="mt-1 text-2xl font-bold text-slate-900">
            ${Number(totals.total_wages).toLocaleString()}
          </p>
        </Card>
      </div>
      <ResponsiveContainer width="100%" height={180}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
          <YAxis stroke="#94a3b8" fontSize={12} />
          <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
          <Bar dataKey="amount" fill="#4f46e5" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
