import type { ReactNode } from "react";

type Tone = "success" | "warning" | "danger" | "info" | "neutral";

const toneClasses: Record<Tone, string> = {
  success: "bg-success-50 text-success-700",
  warning: "bg-warning-50 text-warning-700",
  danger: "bg-danger-50 text-danger-700",
  info: "bg-info-50 text-info-700",
  neutral: "bg-slate-100 text-slate-700",
};

export function Badge({ tone = "neutral", children }: { tone?: Tone; children: ReactNode }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${toneClasses[tone]}`}
    >
      {children}
    </span>
  );
}

export function statusTone(status: string): Tone {
  const map: Record<string, Tone> = {
    completed: "success",
    complete: "success",
    not_required: "success",
    pending: "warning",
    template_fallback: "warning",
    failed: "danger",
    intake: "info",
  };
  return map[status] ?? "neutral";
}

// Raw backend enum values (ocr_status, draft status, etc.) are internal
// vocabulary, not something a first-time user should have to decode -
// "not_required" reads as an error to someone who doesn't know it means
// "processing finished, OCR wasn't needed for this file."
export function statusLabel(status: string): string {
  const map: Record<string, string> = {
    pending: "Processing…",
    not_required: "Ready",
    completed: "Ready",
    complete: "Ready",
    failed: "Failed",
    template_fallback: "Ready (template)",
    intake: "Intake",
  };
  return map[status] ?? status;
}
