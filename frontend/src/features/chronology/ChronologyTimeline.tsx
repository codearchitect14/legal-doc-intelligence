import type { Schemas } from "../../lib/apiClient";

// event.description from the backend is "{category}: {raw extracted text}"
// (e.g. "uncertain: 1/7/26") - internal debugging shorthand, not something
// a user should have to decode. Split it back apart and present it as two
// clearly labeled columns instead.
function splitDescription(description: string): { category: string; text: string } {
  const separatorIndex = description.indexOf(": ");
  if (separatorIndex === -1) return { category: "document", text: description };
  return {
    category: description.slice(0, separatorIndex),
    text: description.slice(separatorIndex + 2),
  };
}

export function ChronologyTimeline({ events }: { events: Schemas["TimelineEventOut"][] }) {
  if (events.length === 0) {
    return <p className="text-sm text-slate-500">No dated events extracted yet.</p>;
  }

  return (
    <div>
      <p className="mb-3 text-sm text-slate-500">
        {events.length} date{events.length === 1 ? "" : "s"} found across the case's documents,
        earliest first. Long or unclassified documents can surface incidental numbers that look
        like dates but aren't meaningful case events.
      </p>
      <ul className="divide-y divide-slate-200 rounded-card border border-slate-200 bg-white">
        {events.map((event) => {
          const { category, text } = splitDescription(event.description);
          return (
            <li key={event.id} className="flex items-center gap-4 px-4 py-2 text-sm">
              <span className="w-28 shrink-0 font-medium text-slate-700">{event.event_date}</span>
              <span className="text-slate-500">
                Found in a document classified as <strong className="text-slate-700">{category}</strong>
                {" "}
                (raw text: "{text}")
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
