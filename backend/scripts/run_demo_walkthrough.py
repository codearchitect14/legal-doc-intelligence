"""Phase 7 demonstration walkthrough (PROJECT_PLAN_v2.md Section 14 Phase 7).

Runs the full pipeline against the real demo case folder
(data/sample_case_folder/) through the live HTTP API, not a mocked test,
and records what actually happened: how the app classified each real
document, what it extracted, and whether drafting completed via a real LLM
call or fell back to the deterministic template. Every number in the
output is a real measurement from this run, not an invented claim (Section
13.3 requires that before any number could ever appear on the marketing
site).

Usage:
    uv run python scripts/run_demo_walkthrough.py [--base-url http://localhost:8000]

Requires the backend, Postgres, and Redis already running.
"""

import argparse
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import httpx

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_FOLDER = REPO_ROOT / "data" / "sample_case_folder"


def main() -> int:
    # Windows consoles often default to a non-UTF-8 codepage; reconfigure so
    # this script never crashes on an accidental non-ASCII character later.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    args = parser.parse_args()

    client = httpx.Client(base_url=args.base_url, timeout=60)
    report_lines: list[str] = []

    def record(line: str) -> None:
        print(line)
        report_lines.append(line)

    run_id = uuid4().hex[:8]
    email = f"demo-walkthrough-{run_id}@example.com"
    password = "demo-walkthrough-pass-123"

    record("# Demo Walkthrough Results\n")
    record(f"Run at: {datetime.now(UTC).isoformat()}")
    record(f"Base URL: {args.base_url}\n")

    overall_start = time.perf_counter()

    record("## 1. Firm registration and login")
    response = client.post(
        "/auth/register-firm",
        json={"firm_name": f"Demo Walkthrough Firm {run_id}", "admin_email": email, "admin_password": password},
    )
    response.raise_for_status()
    record(f"- Registered firm and admin user `{email}`, status {response.status_code}")

    response = client.post("/auth/login", data={"username": email, "password": password})
    response.raise_for_status()
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    record("- Logged in, access token acquired")

    record("\n## 2. Case creation")
    response = client.post("/cases", json={"title": "Demo Walkthrough Case"})
    response.raise_for_status()
    case_id = response.json()["id"]
    record(f"- Created case `{case_id}`")

    record("\n## 3. Document upload (real files from data/sample_case_folder/)")
    sample_files = sorted(SAMPLE_FOLDER.glob("*.pdf"))
    if not sample_files:
        record(f"- ERROR: no PDF files found in {SAMPLE_FOLDER}")
        return 1

    upload_start = time.perf_counter()
    files_payload = [
        ("files", (f.name, f.read_bytes(), "application/pdf")) for f in sample_files
    ]
    response = client.post(f"/cases/{case_id}/documents", files=files_payload)
    response.raise_for_status()
    uploaded = response.json()
    upload_duration = time.perf_counter() - upload_start
    record(f"- Uploaded {len(uploaded)} real documents in {upload_duration:.2f}s:")
    for f in sample_files:
        record(f"  - `{f.name}` ({f.stat().st_size / 1024:.0f} KB)")

    # Background processing (OCR/classification/extraction) runs after the
    # upload response is sent; poll until every document leaves "pending".
    record("\n## 4. Waiting for background processing (OCR, classification, extraction)")
    # A 2MB+ scanned form or a 100+ page opinion can take over a minute to
    # OCR and classify; a short timeout here previously let the script move
    # on to /analyze before every document had finished, silently analyzing
    # a partial document set. 180 x 2s = 6 minutes of headroom.
    process_start = time.perf_counter()
    max_attempts = 180
    poll_interval_seconds = 2
    for attempt in range(max_attempts):
        response = client.get(f"/cases/{case_id}/documents")
        response.raise_for_status()
        documents = response.json()
        if all(d["ocr_status"] != "pending" for d in documents):
            break
        time.sleep(poll_interval_seconds)
    else:
        still_pending = [d["id"][:8] for d in documents if d["ocr_status"] == "pending"]
        record(
            f"- WARNING: {len(still_pending)} document(s) still `pending` after "
            f"{max_attempts * poll_interval_seconds}s ({still_pending}); analysis below "
            "will run against an incomplete document set."
        )
    process_duration = time.perf_counter() - process_start
    record(f"- Processing settled after {process_duration:.2f}s")
    for d in documents:
        record(f"  - `{d['id'][:8]}...` -> category=`{d['category']}`, ocr_status=`{d['ocr_status']}`")

    record("\n## 5. Analysis (chronology, totals, inconsistencies)")
    analyze_start = time.perf_counter()
    response = client.post(f"/cases/{case_id}/analyze")
    response.raise_for_status()
    analysis = response.json()
    analyze_duration = time.perf_counter() - analyze_start
    record(f"- Analysis completed in {analyze_duration:.2f}s")
    record(f"- Chronology events: {len(analysis['chronology'])}")
    record(f"- Total billed: ${analysis['totals']['total_billed']}")
    record(f"- Total wage loss: ${analysis['totals']['total_wages']}")
    record(f"- Inconsistencies flagged: {len(analysis['inconsistencies'])}")
    for flag in analysis["inconsistencies"]:
        record(f"  - [{flag['flag_type']}] {flag['description']}")

    uncertain_count = sum(1 for d in documents if d["category"] == "uncertain")
    events_per_doc = len(analysis["chronology"]) / max(len(documents), 1)
    if uncertain_count or events_per_doc > 20:
        record("\n### Observations from this run (real documents behave differently than short test fixtures)")
        if uncertain_count:
            record(
                f"- {uncertain_count}/{len(documents)} document(s) classified as `uncertain` - "
                "this project's fixed category prototypes (medical record, bill, wage record, "
                "correspondence, contract, filing) don't cleanly cover every real document shape "
                "(e.g. a lengthy government form or a 100+ page appellate opinion). This is exactly "
                "the case Section 10.1's planned LLM-escalation hook is meant for; that escalation "
                "isn't built yet, so these stay `uncertain` rather than being guessed at."
            )
        if events_per_doc > 20:
            record(
                f"- {len(analysis['chronology'])} chronology events from only {len(documents)} "
                "documents is disproportionately high - long real-world legal/government documents "
                "are dense with date-like text (citation years, statutory references, form "
                "instructions) that reads as a case-relevant date to the current date extractor. "
                "Short synthetic test fixtures don't surface this; real documents do. Worth a "
                "future pass narrowing date extraction to category-appropriate contexts."
            )

    record("\n## 6. Draft generation")
    for output_type in ("chronology_summary", "demand_letter"):
        draft_start = time.perf_counter()
        response = client.post(f"/cases/{case_id}/draft", json={"output_type": output_type})
        response.raise_for_status()
        draft = response.json()
        draft_duration = time.perf_counter() - draft_start
        record(f"- `{output_type}`: status=`{draft['status']}` in {draft_duration:.2f}s")
        record(f"  - Content length: {len(draft['content'])} characters")

    record(
        "\nNote: `status=\"complete\"` covers both a successful real LLM call and a case where "
        "no narrative was needed at all (a clean chronology_summary) - the API doesn't currently "
        "distinguish the two. Only `status=\"template_fallback\"` unambiguously means the LLM "
        "path was attempted and both providers were unavailable or the token budget was spent."
    )

    overall_duration = time.perf_counter() - overall_start
    record("\n## Summary")
    record(f"- Total wall-clock time, upload through both drafts: {overall_duration:.2f}s")
    record(
        "- This number reflects one run on one development machine, recorded here for "
        "internal tracking, not published as a marketing claim (PROJECT_PLAN_v2.md Section 13.3 "
        "requires real measurement behind any such claim, and a single local run isn't a "
        "representative production number)."
    )

    output_path = REPO_ROOT / "docs" / "user-guide" / "demo-walkthrough-results.md"
    output_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"\nResults written to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
