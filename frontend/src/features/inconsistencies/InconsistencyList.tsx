import { AlertTriangle, CheckCircle2 } from "lucide-react";

import { Badge } from "../../components/Badge";
import { EmptyState } from "../../components/EmptyState";
import type { Schemas } from "../../lib/apiClient";

export function InconsistencyList({ flags }: { flags: Schemas["InconsistencyFlagOut"][] }) {
  if (flags.length === 0) {
    return (
      <EmptyState
        icon={CheckCircle2}
        title="No inconsistencies flagged"
        description="Rule-based checks found nothing to flag for this case."
      />
    );
  }

  return (
    <ul className="space-y-3">
      {flags.map((flag) => (
        <li key={flag.id} className="flex items-start gap-3 rounded-card border border-warning-50 bg-warning-50 p-4">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-warning-500" aria-hidden />
          <div>
            <Badge tone="warning">{flag.flag_type.replace(/_/g, " ")}</Badge>
            <p className="mt-1 text-sm text-slate-700">{flag.description}</p>
          </div>
        </li>
      ))}
    </ul>
  );
}
