import {
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { Schemas } from "../../lib/apiClient";

export function ChronologyTimeline({ events }: { events: Schemas["TimelineEventOut"][] }) {
  if (events.length === 0) {
    return <p className="text-sm text-slate-500">No dated events extracted yet.</p>;
  }

  const points = events.map((event, index) => ({
    time: new Date(event.event_date).getTime(),
    // Spread points across a couple of vertical lanes purely so labels
    // don't all collide on one line; the Y axis carries no other meaning.
    lane: index % 3,
    description: event.description,
    date: event.event_date,
  }));

  return (
    <div>
      <ResponsiveContainer width="100%" height={180}>
        <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis
            dataKey="time"
            type="number"
            domain={["dataMin", "dataMax"]}
            tickFormatter={(value) => new Date(value).toLocaleDateString()}
            stroke="#94a3b8"
            fontSize={12}
          />
          <YAxis dataKey="lane" type="number" hide domain={[-1, 3]} />
          <Tooltip
            formatter={(_value, _name, item) => [item.payload.description, item.payload.date]}
            labelFormatter={() => ""}
          />
          <Scatter data={points} fill="#4f46e5" />
        </ScatterChart>
      </ResponsiveContainer>

      <ul className="mt-4 space-y-2">
        {events.map((event) => (
          <li key={event.id} className="flex gap-3 text-sm">
            <span className="w-24 shrink-0 font-medium text-slate-500">{event.event_date}</span>
            <span className="text-slate-700">{event.description}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
