import { FolderX, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { Button } from "../../components/Button";
import { EmptyState } from "../../components/EmptyState";
import { Spinner } from "../../components/Spinner";
import { ChronologyTimeline } from "../../features/chronology/ChronologyTimeline";
import { DocumentList } from "../../features/documents/DocumentList";
import { DocumentUpload } from "../../features/documents/DocumentUpload";
import { DocumentViewer } from "../../features/documents/DocumentViewer";
import { DraftPanel } from "../../features/draft/DraftPanel";
import { InconsistencyList } from "../../features/inconsistencies/InconsistencyList";
import { TotalsSummary } from "../../features/totals/TotalsSummary";
import { ApiError, analysisApi, casesApi, documentsApi, type Schemas } from "../../lib/apiClient";

const TABS = ["Documents", "Chronology", "Damages", "Inconsistencies", "Draft"] as const;
type Tab = (typeof TABS)[number];

export function CaseDetail() {
  const { caseId } = useParams<{ caseId: string }>();
  const [caseData, setCaseData] = useState<Schemas["CaseOut"] | null>(null);
  const [documents, setDocuments] = useState<Schemas["DocumentOut"][]>([]);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const selectedDoc = documents.find((d) => d.id === selectedDocId) ?? null;
  const [chronology, setChronology] = useState<Schemas["TimelineEventOut"][]>([]);
  const [totals, setTotals] = useState<Schemas["CaseTotalsOut"] | null>(null);
  const [inconsistencies, setInconsistencies] = useState<Schemas["InconsistencyFlagOut"][]>([]);
  const [tab, setTab] = useState<Tab>("Documents");
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);

  function reloadDocuments() {
    if (!caseId) return;
    documentsApi.list(caseId).then(setDocuments);
  }

  // Upload finishing and background processing (OCR/classification/
  // extraction) finishing are two different moments - the upload response
  // returns immediately while processing keeps running server-side. Without
  // this, a document stays stuck showing "Uncategorized / pending" on
  // screen until the user manually reloads the whole page, even though
  // processing may have already finished.
  useEffect(() => {
    const stillProcessing = documents.some((d) => d.ocr_status === "pending");
    if (!stillProcessing) return;
    const timer = setInterval(reloadDocuments, 2000);
    return () => clearInterval(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [documents]);

  function reloadAnalysis() {
    if (!caseId) return;
    analysisApi.chronology(caseId).then(setChronology);
    analysisApi.totals(caseId).then(setTotals).catch(() => setTotals(null));
    analysisApi.inconsistencies(caseId).then(setInconsistencies);
  }

  useEffect(() => {
    if (!caseId) return;
    // A case can 404 here if the ID belongs to another firm, was deleted,
    // or was mistyped - the loading spinner must not spin forever in any
    // of those cases (this used to be exactly what happened).
    casesApi
      .get(caseId)
      .then((data) => {
        setCaseData(data);
        reloadDocuments();
        reloadAnalysis();
      })
      .catch(() => setNotFound(true));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseId]);

  async function handleAnalyze() {
    if (!caseId) return;
    setAnalyzing(true);
    setAnalyzeError(null);
    try {
      await analysisApi.analyze(caseId);
      reloadAnalysis();
      // Analysis results land on the Chronology/Damages/Inconsistencies
      // tabs, not the Documents tab the user is usually on when they click
      // this. Without switching tabs, a fast, successful run looks
      // identical to the button doing nothing at all.
      setTab("Chronology");
    } catch (err) {
      setAnalyzeError(
        err instanceof ApiError ? err.message : "Analysis failed. Please try again.",
      );
    } finally {
      setAnalyzing(false);
    }
  }

  if (notFound) {
    return (
      <EmptyState
        icon={FolderX}
        title="Case not found"
        description="This case doesn't exist, or you don't have access to it."
        action={
          <Link to="/app" className="text-sm font-medium text-brand-700 hover:underline">
            ← Back to your cases
          </Link>
        }
      />
    );
  }

  if (!caseId || !caseData) return <Spinner label="Loading case…" />;

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">{caseData.title}</h1>
        <Button variant="secondary" onClick={handleAnalyze} disabled={analyzing}>
          <RefreshCw className={`h-4 w-4 ${analyzing ? "animate-spin" : ""}`} aria-hidden />
          {analyzing ? "Analyzing…" : "Run Analysis"}
        </Button>
      </div>
      {analyzeError && <p className="mt-2 text-sm text-danger-500">{analyzeError}</p>}

      <div className="mt-6 flex gap-1 border-b border-slate-200">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium ${
              tab === t
                ? "border-b-2 border-brand-600 text-brand-700"
                : "text-slate-500 hover:text-slate-800"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="mt-6">
        {tab === "Documents" && (
          <div className="space-y-6">
            <DocumentUpload caseId={caseId} onUploaded={reloadDocuments} />
            <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
              <DocumentList
                documents={documents}
                selectedId={selectedDocId}
                onSelect={setSelectedDocId}
              />
              {selectedDoc ? (
                <DocumentViewer caseId={caseId} document={selectedDoc} />
              ) : (
                <p className="text-sm text-slate-500">Select a document to view it.</p>
              )}
            </div>
          </div>
        )}

        {tab === "Chronology" && <ChronologyTimeline events={chronology} />}
        {tab === "Damages" && <TotalsSummary totals={totals} />}
        {tab === "Inconsistencies" && <InconsistencyList flags={inconsistencies} />}
        {tab === "Draft" && <DraftPanel caseId={caseId} />}
      </div>
    </div>
  );
}
