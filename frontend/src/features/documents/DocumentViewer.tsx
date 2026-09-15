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
    <div className="grid gap-6 lg:grid-cols-2">
      <div className="rounded-card border border-slate-200 bg-slate-50 p-2">
        {file?.contentType === "application/pdf" ? (
          <iframe title="Original document" src={file.url} className="h-[500px] w-full rounded" />
        ) : file?.contentType.startsWith("image/") ? (
          <img src={file.url} alt="Original document" className="max-h-[500px] w-full rounded object-contain" />
        ) : (
          <div className="flex h-[500px] items-center justify-center text-sm text-slate-500">
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
                className="flex justify-between rounded-lg border border-slate-200 px-3 py-2 text-sm"
              >
                <span className="font-medium capitalize text-slate-700">
                  {field.field_name.replace(/_/g, " ")}
                </span>
                <span className="text-slate-600">{field.field_value}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
