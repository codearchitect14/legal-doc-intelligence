import { ExternalLink } from "lucide-react";
import { useEffect, useState } from "react";

import { Spinner } from "../../components/Spinner";
import { documentsApi, type Schemas } from "../../lib/apiClient";

export function DocumentViewer({ caseId, documentId }: { caseId: string; documentId: string }) {
  const [file, setFile] = useState<{ url: string; contentType: string } | null>(null);
  const [fields, setFields] = useState<Schemas["ExtractedFieldOut"][]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let currentUrl: string | null = null;
    setLoading(true);
    Promise.all([documentsApi.fetchFile(caseId, documentId), documentsApi.fields(caseId, documentId)])
      .then(([fetchedFile, fetchedFields]) => {
        currentUrl = fetchedFile.url;
        setFile(fetchedFile);
        setFields(fetchedFields);
      })
      .finally(() => setLoading(false));

    return () => {
      if (currentUrl) URL.revokeObjectURL(currentUrl);
    };
  }, [caseId, documentId]);

  if (loading) return <Spinner label="Loading document…" />;

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,3fr)_minmax(220px,1fr)]">
      <div className="rounded-card border border-slate-200 bg-slate-50 p-2">
        <div className="mb-2 flex items-center justify-end">
          <a
            href={file?.url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 text-sm font-medium text-brand-700 hover:underline"
          >
            <ExternalLink className="h-3.5 w-3.5" aria-hidden />
            Open full size in a new tab
          </a>
        </div>
        {file?.contentType === "application/pdf" ? (
          // A multi-page real document (a 100+ page opinion, a full-page
          // scanned form) is unreadable squeezed into a small fixed-height
          // box next to the fields panel - this needs to be the dominant
          // element on the page, sized to the viewport, not a thumbnail.
          <iframe
            title="Original document"
            src={file.url}
            className="h-[85vh] w-full rounded bg-white"
          />
        ) : file?.contentType.startsWith("image/") ? (
          <img
            src={file.url}
            alt="Original document"
            className="max-h-[85vh] w-full rounded object-contain"
          />
        ) : (
          <div className="flex h-[85vh] items-center justify-center text-sm text-slate-500">
            <a href={file?.url} download className="font-medium text-brand-700 hover:underline">
              Download original file
            </a>
          </div>
        )}
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
                <span className="text-right text-slate-600">{field.field_value}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
