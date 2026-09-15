import type { Schemas } from "../../lib/apiClient";

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
        {events.map((event) => (
          <li key={event.id} className="flex items-center gap-4 px-4 py-2 text-sm">
            <span className="w-28 shrink-0 font-medium text-slate-700">{event.event_date}</span>
            <span className="text-slate-500">{event.description}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
