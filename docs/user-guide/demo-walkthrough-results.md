# Demo Walkthrough Results

Run at: 2026-09-15T18:12:01.688309+00:00
Base URL: http://localhost:8000

## 1. Firm registration and login
- Registered firm and admin user `demo-walkthrough-b2250534@example.com`, status 201
- Logged in, access token acquired

## 2. Case creation
- Created case `938e5ee7-5e9e-4ecd-b4ae-2f291f0fc633`

## 3. Document upload (real files from data/sample_case_folder/)
- Uploaded 4 real documents in 0.23s:
  - `irs_form_w2_blank.pdf` (2100 KB)
  - `mtsamples_orthopedic_consult.pdf` (3 KB)
  - `scotus_opinion_loper_bright.pdf` (622 KB)
  - `sec_exhibit_employment_agreement.pdf` (68 KB)

## 4. Waiting for background processing (OCR, classification, extraction)
- Processing settled after 16.89s
  - `f3a05832...` -> category=`uncertain`, ocr_status=`not_required`
  - `6406e021...` -> category=`uncertain`, ocr_status=`not_required`
  - `8e2dc2bc...` -> category=`filing`, ocr_status=`not_required`
  - `48793a7c...` -> category=`contract`, ocr_status=`not_required`

## 5. Analysis (chronology, totals, inconsistencies)
- Analysis completed in 0.29s
- Chronology events: 293
- Total billed: $0.00
- Total wage loss: $0.00
- Inconsistencies flagged: 0

### Observations from this run (real documents behave differently than short test fixtures)
- 2/4 document(s) classified as `uncertain` - this project's fixed category prototypes (medical record, bill, wage record, correspondence, contract, filing) don't cleanly cover every real document shape (e.g. a lengthy government form or a 100+ page appellate opinion). This is exactly the case Section 10.1's planned LLM-escalation hook is meant for; that escalation isn't built yet, so these stay `uncertain` rather than being guessed at.
- 293 chronology events from only 4 documents is disproportionately high - long real-world legal/government documents are dense with date-like text (citation years, statutory references, form instructions) that reads as a case-relevant date to the current date extractor. Short synthetic test fixtures don't surface this; real documents do. Worth a future pass narrowing date extraction to category-appropriate contexts.

## 6. Draft generation
- `chronology_summary`: status=`complete` in 0.02s
  - Content length: 8305 characters
- `demand_letter`: status=`complete` in 3.03s
  - Content length: 3038 characters

Note: `status="complete"` covers both a successful real LLM call and a case where no narrative was needed at all (a clean chronology_summary) - the API doesn't currently distinguish the two. Only `status="template_fallback"` unambiguously means the LLM path was attempted and both providers were unavailable or the token budget was spent.

## Summary
- Total wall-clock time, upload through both drafts: 20.90s
- This number reflects one run on one development machine, recorded here for internal tracking, not published as a marketing claim (PROJECT_PLAN_v2.md Section 13.3 requires real measurement behind any such claim, and a single local run isn't a representative production number).
