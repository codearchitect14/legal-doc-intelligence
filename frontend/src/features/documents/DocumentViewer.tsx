import { Download, ExternalLink, FileText } from "lucide-react";
import { useEffect, useState } from "react";

import { Badge, statusTone } from "../../components/Badge";
import { Spinner } from "../../components/Spinner";
import { documentsApi, type Schemas } from "../../lib/apiClient";

export function DocumentViewer({
  caseId,
  document,
}: {
  caseId: string;
  document: Schemas["DocumentOut"];
}) {
  const [file, setFile] = useState<{ url: string; contentType: string } | null>(null);
  const [fields, setFields] = useState<Schemas["ExtractedFieldOut"][]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let currentUrl: string | null = null;
    setLoading(true);
    Promise.all([
      documentsApi.fetchFile(caseId, document.id),
      documentsApi.fields(caseId, document.id),
    ])
      .then(([fetchedFile, fetchedFields]) => {
        currentUrl = fetchedFile.url;
        setFile(fetchedFile);
        setFields(fetchedFields);
      })
      .finally(() => setLoading(false));

    return () => {
      if (currentUrl) URL.revokeObjectURL(currentUrl);
    };
  }, [caseId, document.id]);

  if (loading) return <Spinner label="Loading document…" />;

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,3fr)_minmax(220px,1fr)]">
      <div className="overflow-hidden rounded-card border border-slate-200 bg-white shadow-sm">
        <div className="flex items-center justify-between gap-3 border-b border-slate-200 bg-slate-50 px-4 py-3">
          <div className="flex min-w-0 items-center gap-2">
            <FileText className="h-4 w-4 shrink-0 text-slate-400" aria-hidden />
            <span className="truncate text-sm font-medium text-slate-800">{document.filename}</span>
            {document.category && (
              <Badge tone={statusTone(document.category)}>{document.category}</Badge>
            )}
          </div>
          <div className="flex shrink-0 items-center gap-3">
            <a
              href={file?.url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 text-sm font-medium text-brand-700 hover:underline"
              title="Open full size in a new tab"
            >
              <ExternalLink className="h-3.5 w-3.5" aria-hidden />
              <span className="hidden sm:inline">Open full size</span>
            </a>
            <a
              href={file?.url}
              download={document.filename}
              className="inline-flex items-center gap-1 text-sm font-medium text-brand-700 hover:underline"
              title="Download original file"
            >
              <Download className="h-3.5 w-3.5" aria-hidden />
              <span className="hidden sm:inline">Download</span>
            </a>
          </div>
        </div>
        <div className="bg-slate-100 p-2">
          {file?.contentType === "application/pdf" ? (
            // A multi-page real document (a 100+ page opinion, a full-page
            // scanned form) is unreadable squeezed into a small fixed-height
            // box next to the fields panel - this needs to be the dominant
            // element on the page, sized to the viewport, not a thumbnail.
            <iframe
              title={document.filename}
              src={file.url}
              className="h-[80vh] w-full rounded border border-slate-200 bg-white"
            />
          ) : file?.contentType.startsWith("image/") ? (
            <img
              src={file.url}
              alt={document.filename}
              className="max-h-[80vh] w-full rounded border border-slate-200 bg-white object-contain"
            />
          ) : (
            <div className="flex h-[80vh] items-center justify-center rounded border border-slate-200 bg-white text-sm text-slate-500">
              <a href={file?.url} download={document.filename} className="font-medium text-brand-700 hover:underline">
                Download original file
              </a>
            </div>
          )}
        </div>
      </div>

      <div>
        <h3 className="text-sm font-semibold text-slate-900">Extracted Fields</h3>
        {fields.length === 0 ? (
          <p className="mt-2 text-sm text-slate-500">No fields extracted for this document.</p>
        ) : (
          <ul className="mt-3 space-y-2">
            {fields.map((field) => (
              <li
                key={field.id}
                className="flex justify-between gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm"
              >
                <span className="font-medium capitalize text-slate-700">
                  {field.field_name.replace(/_/g, " ")}
                </span>
                <span className="text-right text-slate-600">
                  {field.field_name.endsWith("_amount") ? `$${field.field_value}` : field.field_value}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
