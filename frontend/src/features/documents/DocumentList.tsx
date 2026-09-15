import { FileText, Loader2 } from "lucide-react";

import { Badge, statusLabel, statusTone } from "../../components/Badge";
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

  const processingCount = documents.filter((d) => d.ocr_status === "pending").length;

  return (
    <div>
      {processingCount > 0 && (
        <div className="mb-3 flex items-center gap-2 rounded-lg border border-warning-200 bg-warning-50 px-3 py-2 text-sm text-warning-700">
          <Loader2 className="h-4 w-4 shrink-0 animate-spin" aria-hidden />
          Processing {processingCount} document{processingCount > 1 ? "s" : ""}… this page will
          update on its own, usually within a few seconds (large scanned files can take a minute
          or more).
        </div>
      )}
      <ul className="divide-y divide-slate-200 rounded-card border border-slate-200 bg-white">
        {documents.map((doc) => (
          <li key={doc.id}>
            <button
              onClick={() => onSelect(doc.id)}
              className={`flex w-full items-center justify-between gap-3 px-4 py-3 text-left text-sm hover:bg-slate-50 ${
                selectedId === doc.id ? "bg-brand-50" : ""
              }`}
            >
              <span className="flex min-w-0 items-center gap-2">
                <FileText className="h-4 w-4 shrink-0 text-slate-400" aria-hidden />
                <span className="min-w-0">
                  <span className="block truncate font-medium text-slate-800">{doc.filename}</span>
                  <span className="block truncate text-xs text-slate-500">
                    {doc.ocr_status === "pending" ? "Processing…" : (doc.category ?? "Uncategorized")}
                  </span>
                </span>
              </span>
              <Badge tone={statusTone(doc.ocr_status)}>{statusLabel(doc.ocr_status)}</Badge>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
