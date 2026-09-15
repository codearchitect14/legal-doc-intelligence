// Abstract, brand-colored illustrations for the marketing site
// (PROJECT_PLAN_v2.md Section 13.3: no licensed stock photography available
// for this build, and the plan itself names abstract illustration of the
// workflow - documents, timelines, checkmarks - as the more credible
// fallback for a technical product).

export function WorkflowIllustration({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 480 200" className={className} role="img" aria-label="Upload, analyze, and draft workflow">
      <defs>
        <linearGradient id="wf-bg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#eef2ff" />
          <stop offset="1" stopColor="#e0e7ff" />
        </linearGradient>
      </defs>
      <rect width="480" height="200" rx="16" fill="url(#wf-bg)" />
      {[
        { x: 40, label: "Upload" },
        { x: 200, label: "Analyze" },
        { x: 360, label: "Draft" },
      ].map((step, i) => (
        <g key={step.label}>
          <rect x={step.x} y="70" width="80" height="60" rx="12" fill="#ffffff" stroke="#4f46e5" strokeWidth="2" />
          {i === 0 && (
            <path d="M80 90 v20 M72 100 l8 -10 l8 10" stroke="#4338ca" strokeWidth="3" fill="none" strokeLinecap="round" strokeLinejoin="round" />
          )}
          {i === 1 && (
            <>
              <circle cx="240" cy="100" r="14" fill="none" stroke="#4338ca" strokeWidth="3" />
              <path d="M250 110 l8 8" stroke="#4338ca" strokeWidth="3" strokeLinecap="round" />
            </>
          )}
          {i === 2 && (
            <path d="M388 88 h24 M388 100 h24 M388 112 h16" stroke="#4338ca" strokeWidth="3" strokeLinecap="round" />
          )}
          <text x={step.x + 40} y="150" textAnchor="middle" fontSize="13" fontWeight="600" fill="#312e81">
            {step.label}
          </text>
        </g>
      ))}
      <path d="M120 100 H200 M280 100 H360" stroke="#818cf8" strokeWidth="3" strokeDasharray="6 6" markerEnd="url(#wf-arrow)" />
      <defs>
        <marker id="wf-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 z" fill="#818cf8" />
        </marker>
      </defs>
    </svg>
  );
}

export function TimelineIllustration({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 320 160" className={className} role="img" aria-label="Chronological case timeline">
      <line x1="30" y1="80" x2="290" y2="80" stroke="#c7d2fe" strokeWidth="3" />
      {[30, 110, 190, 270].map((x, i) => (
        <g key={x}>
          <circle cx={x} cy="80" r="8" fill={i === 2 ? "#f59e0b" : "#4f46e5"} />
          <rect x={x - 24} y={i % 2 === 0 ? 20 : 110} width="48" height="30" rx="6" fill="#ffffff" stroke="#a5b4fc" />
        </g>
      ))}
    </svg>
  );
}

export function DocumentStackIllustration({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 200 160" className={className} role="img" aria-label="Classified document set">
      <rect x="40" y="30" width="100" height="120" rx="8" fill="#e0e7ff" stroke="#a5b4fc" strokeWidth="2" />
      <rect x="55" y="15" width="100" height="120" rx="8" fill="#ffffff" stroke="#6366f1" strokeWidth="2" />
      <line x1="70" y1="45" x2="140" y2="45" stroke="#4f46e5" strokeWidth="3" strokeLinecap="round" />
      <line x1="70" y1="60" x2="140" y2="60" stroke="#818cf8" strokeWidth="3" strokeLinecap="round" />
      <line x1="70" y1="75" x2="120" y2="75" stroke="#818cf8" strokeWidth="3" strokeLinecap="round" />
      <circle cx="130" cy="105" r="16" fill="#22c55e" />
      <path d="M123 105 l5 5 l10 -10" stroke="#ffffff" strokeWidth="2.5" fill="none" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function ShieldIllustration({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 160 160" className={className} role="img" aria-label="Security and firm data isolation">
      <path d="M80 15 L135 35 V80 C135 115 110 140 80 150 C50 140 25 115 25 80 V35 Z" fill="#eef2ff" stroke="#4338ca" strokeWidth="3" />
      <path d="M58 82 L73 97 L104 62" stroke="#4338ca" strokeWidth="6" fill="none" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function CalculatorIllustration({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 160 160" className={className} role="img" aria-label="Deterministic damages calculation">
      <rect x="35" y="20" width="90" height="120" rx="10" fill="#ffffff" stroke="#6366f1" strokeWidth="3" />
      <rect x="47" y="34" width="66" height="24" rx="4" fill="#e0e7ff" />
      {[0, 1, 2].map((row) =>
        [0, 1, 2].map((col) => (
          <circle key={`${row}-${col}`} cx={58 + col * 22} cy={82 + row * 20} r="6" fill="#a5b4fc" />
        )),
      )}
    </svg>
  );
}
