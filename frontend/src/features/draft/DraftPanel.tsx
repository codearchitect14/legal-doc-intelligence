import { Download, Save } from "lucide-react";
import { useEffect, useState } from "react";

import { Badge, statusTone } from "../../components/Badge";
import { Button } from "../../components/Button";
import { Spinner } from "../../components/Spinner";
import { ApiError, draftApi, type Schemas } from "../../lib/apiClient";

const OUTPUT_TYPE_LABELS: Record<string, string> = {
  chronology_summary: "Chronology Summary",
  demand_letter: "Demand Letter",
};

export function DraftPanel({ caseId }: { caseId: string }) {
  const [drafts, setDrafts] = useState<Schemas["DraftOutputOut"][]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [content, setContent] = useState("");
  const [generating, setGenerating] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selected = drafts.find((d) => d.id === selectedId) ?? null;

  async function loadDrafts(preferId?: string) {
    const list = await draftApi.list(caseId);
    setDrafts(list);
    const next = preferId ?? list[list.length - 1]?.id ?? null;
    setSelectedId(next);
    setContent(list.find((d) => d.id === next)?.content ?? "");
  }

  useEffect(() => {
    loadDrafts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseId]);

  useEffect(() => {
    setContent(selected?.content ?? "");
  }, [selected]);

  async function handleGenerate(outputType: string) {
    setGenerating(outputType);
    setError(null);
    try {
      const draft = await draftApi.create(caseId, outputType);
      await loadDrafts(draft.id);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not generate the draft.");
    } finally {
      setGenerating(null);
    }
  }

  async function handleSave() {
    if (!selected) return;
    setSaving(true);
    try {
      const updated = await draftApi.update(caseId, selected.id, content);
      setDrafts((prev) => prev.map((d) => (d.id === updated.id ? updated : d)));
    } finally {
      setSaving(false);
    }
  }

  async function handleExport() {
    if (!selected) return;
    const url = await draftApi.fetchExportUrl(caseId, selected.id);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${selected.output_type}-${selected.id}.docx`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div>
      <div className="flex flex-wrap gap-3">
        {Object.entries(OUTPUT_TYPE_LABELS).map(([type, label]) => (
          <Button
            key={type}
            variant="secondary"
            disabled={generating !== null}
            onClick={() => handleGenerate(type)}
          >
            {generating === type ? "Generating…" : `Generate ${label}`}
          </Button>
        ))}
      </div>
      {error && <p className="mt-2 text-sm text-danger-500">{error}</p>}

      {drafts.length > 0 && (
        <div className="mt-6 flex gap-2 border-b border-slate-200">
          {drafts.map((draft) => (
            <button
              key={draft.id}
              onClick={() => setSelectedId(draft.id)}
              className={`border-b-2 px-3 py-2 text-sm font-medium ${
                selectedId === draft.id
                  ? "border-brand-600 text-brand-700"
                  : "border-transparent text-slate-500 hover:text-slate-800"
              }`}
            >
              {OUTPUT_TYPE_LABELS[draft.output_type] ?? draft.output_type}
            </button>
          ))}
        </div>
      )}

      {selected && (
        <div className="mt-4">
          <div className="mb-2 flex items-center justify-between">
            <Badge tone={statusTone(selected.status)}>{selected.status.replace(/_/g, " ")}</Badge>
            <div className="flex gap-2">
              <Button variant="secondary" onClick={handleSave} disabled={saving}>
                <Save className="h-4 w-4" aria-hidden />
                {saving ? "Saving…" : "Save Edits"}
              </Button>
              <Button variant="secondary" onClick={handleExport}>
                <Download className="h-4 w-4" aria-hidden />
                Export .docx
              </Button>
            </div>
          </div>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={16}
            className="w-full rounded-card border border-slate-300 p-4 font-mono text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
        </div>
      )}

      {drafts.length === 0 && !generating && (
        <p className="mt-4 text-sm text-slate-500">No drafts yet — generate one above.</p>
      )}
      {generating && drafts.length === 0 && <Spinner label="Generating draft…" />}
    </div>
  );
}
