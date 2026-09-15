import {
  CalculatorIllustration,
  DocumentStackIllustration,
  TimelineIllustration,
  WorkflowIllustration,
} from "../../components/illustrations";

const FEATURES = [
  {
    title: "Intake and classification",
    description:
      "Upload a folder or archive of files. Scanned pages are OCR'd automatically, and every document is classified — medical record, bill, wage record, correspondence, contract, or filing.",
    illustration: DocumentStackIllustration,
  },
  {
    title: "Chronology building",
    description:
      "Extracted dates from across every document are merged into a single ordered timeline, with source references back to the originating document.",
    illustration: TimelineIllustration,
  },
  {
    title: "Damages calculation",
    description:
      "Billed amounts and wage loss figures are summed deterministically — a spreadsheet-grade total, not a language model doing arithmetic.",
    illustration: CalculatorIllustration,
  },
  {
    title: "Draft generation",
    description:
      "A first-draft case summary or demand letter is assembled from the chronology and totals. A model is used only once per case, to write the connecting narrative.",
    illustration: WorkflowIllustration,
  },
];

export function Product() {
  return (
    <div className="mx-auto max-w-5xl px-6 py-16">
      <h1 className="text-3xl font-bold text-slate-900">Product Overview</h1>
      <p className="mt-3 max-w-2xl text-slate-600">
        Four steps take a raw case folder to a reviewable first draft.
      </p>

      <div className="mt-12 space-y-16">
        {FEATURES.map(({ title, description, illustration: Illustration }, i) => (
          <div
            key={title}
            className={`flex flex-col items-center gap-8 ${i % 2 === 1 ? "sm:flex-row-reverse" : "sm:flex-row"}`}
          >
            <Illustration className="h-40 w-full max-w-xs shrink-0" />
            <div>
              <h2 className="text-xl font-semibold text-slate-900">{title}</h2>
              <p className="mt-2 text-slate-600">{description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
