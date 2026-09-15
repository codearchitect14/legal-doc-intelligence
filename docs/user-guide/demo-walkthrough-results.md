# Demo Walkthrough Results

Run at: 2026-09-15T14:57:55.389744+00:00
Base URL: http://localhost:8020

## 1. Firm registration and login
- Registered firm and admin user `demo-walkthrough-0b95a46f@example.com`, status 201
- Logged in, access token acquired

## 2. Case creation
- Created case `cd360476-69c7-40d3-a466-bd7eada6c79c`

## 3. Document upload (real files from data/sample_case_folder/)
- Uploaded 4 real documents in 0.04s:
  - `irs_form_w2_blank.pdf` (2100 KB)
  - `mtsamples_orthopedic_consult.pdf` (3 KB)
  - `scotus_opinion_loper_bright.pdf` (622 KB)
  - `sec_exhibit_employment_agreement.pdf` (68 KB)

## 4. Waiting for background processing (OCR, classification, extraction)
- Processing settled after 13.50s
  - `617897a1...` -> category=`uncertain`, ocr_status=`not_required`
  - `e9c4b14f...` -> category=`uncertain`, ocr_status=`not_required`
  - `e230dff6...` -> category=`filing`, ocr_status=`not_required`
  - `efb6b096...` -> category=`contract`, ocr_status=`not_required`

## 5. Analysis (chronology, totals, inconsistencies)
- Analysis completed in 0.46s
- Chronology events: 293
- Total billed: $0.00
- Total wage loss: $0.00
- Inconsistencies flagged: 0

### Observations from this run (real documents behave differently than short test fixtures)
- 2/4 document(s) classified as `uncertain` - this project's fixed category prototypes (medical record, bill, wage record, correspondence, contract, filing) don't cleanly cover every real document shape (e.g. a lengthy government form or a 100+ page appellate opinion). This is exactly the case Section 10.1's planned LLM-escalation hook is meant for; that escalation isn't built yet, so these stay `uncertain` rather than being guessed at.
- 293 chronology events from only 4 documents is disproportionately high - long real-world legal/government documents are dense with date-like text (citation years, statutory references, form instructions) that reads as a case-relevant date to the current date extractor. Short synthetic test fixtures don't surface this; real documents do. Worth a future pass narrowing date extraction to category-appropriate contexts.

## 6. Draft generation
- `chronology_summary`: status=`complete` in 0.07s
  - Content length: 8305 characters
- `demand_letter`: status=`template_fallback` in 0.08s
  - Content length: 8306 characters

Note: `status="complete"` covers both a successful real LLM call and a case where no narrative was needed at all (a clean chronology_summary) - the API doesn't currently distinguish the two. Only `status="template_fallback"` unambiguously means the LLM path was attempted and both providers were unavailable or the token budget was spent.

## Summary
- Total wall-clock time, upload through both drafts: 16.63s
- This number reflects one run on one development machine, recorded here for internal tracking, not published as a marketing claim (PROJECT_PLAN_v2.md Section 13.3 requires real measurement behind any such claim, and a single local run isn't a representative production number).
