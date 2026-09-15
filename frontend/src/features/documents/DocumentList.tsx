import { FileText } from "lucide-react";

import { Badge, statusTone } from "../../components/Badge";
import type { Schemas } from "../../lib/apiClient";

export function DocumentList({
  documents,
  selectedId,
  onSelect,
}: {
  documents: Schemas["DocumentOut"][];
  selectedId: string | null;
  onSelect: (documentId: string) => void;
}) {
  if (documents.length === 0) {
    return <p className="text-sm text-slate-500">No documents uploaded yet.</p>;
  }

  return (
    <ul className="divide-y divide-slate-200 rounded-card border border-slate-200 bg-white">
      {documents.map((doc) => (
        <li key={doc.id}>
          <button
            onClick={() => onSelect(doc.id)}
            className={`flex w-full items-center justify-between gap-3 px-4 py-3 text-left text-sm hover:bg-slate-50 ${
              selectedId === doc.id ? "bg-brand-50" : ""
            }`}
          >
            <span className="flex items-center gap-2 truncate">
              <FileText className="h-4 w-4 shrink-0 text-slate-400" aria-hidden />
              <span className="truncate">{doc.category ?? "Uncategorized"}</span>
            </span>
            <Badge tone={statusTone(doc.ocr_status)}>{doc.ocr_status}</Badge>
          </button>
        </li>
      ))}
    </ul>
  );
}
