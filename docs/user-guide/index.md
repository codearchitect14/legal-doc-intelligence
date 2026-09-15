# User Guide

This walks through using Legal Doc Intelligence as a lawyer or paralegal, end to end. It describes what's actually built as of Phase 6 - every screen and action named here exists in the running app.

## 1. Register your firm

Visit `/register` on the running frontend and provide your firm's name, an admin email, and a password. This creates your firm and its first user with the **Firm Administrator** role. There is no separate sign-up approval step for this MVP - the account is usable immediately.

## 2. Log in

Visit `/login` with the email and password from registration. You're taken to the case dashboard at `/app`.

## 3. Create a case

From the dashboard, click **New Case** and give it a title (e.g. the client or matter name). Your new case appears in the case list with a status badge.

## 4. Upload documents

Open the case and go to the **Documents** tab. Click **Upload Documents** and select one or more files, or a `.zip` archive of files - supported types are PDF, DOCX, and common image formats (PNG, JPG, TIFF, BMP).

Behind the scenes, each document is:

- OCR'd automatically if it's a scan with no extractable text layer (native digital files skip this)
- Classified into a category (medical record, bill, wage record, correspondence, contract, or filing)
- Scanned for dates, amounts, and other structured fields relevant to its category

This happens in the background - the document list shows each file's status and detected category once processing finishes (usually a few seconds per document).

## 5. View a document alongside its extracted fields

Click any document in the list. The original file is shown next to the fields the system extracted from it, so you can verify accuracy directly against the source rather than trusting the extraction blindly.

## 6. Run analysis

Once your documents are uploaded and processed, click **Run Analysis** at the top of the case. This builds three things from everything extracted so far:

- **Chronology** - every dated event across all documents, merged into one ordered timeline
- **Damages** - billed amounts and wage loss figures, summed deterministically (not by a language model doing arithmetic)
- **Inconsistencies** - rule-based flags, such as conflicting billed amounts for the same date, or a suspiciously large gap between medical records

You can re-run analysis at any point after uploading more documents; it recomputes from scratch rather than accumulating duplicates.

## 7. Generate a draft

In the **Draft** tab, choose an output type:

- **Chronology Summary** - a plain case summary. If nothing was flagged as inconsistent, this is assembled entirely from a template at zero model cost. If something needs explaining in prose, it escalates to a single language-model call.
- **Demand Letter** - always uses a language model once, to write the narrative connecting the chronology and totals together. If both configured providers (Groq and Gemini) are unavailable, or the case's token budget has been used up, you still get a complete draft - it falls back to the same template, clearly labeled, rather than leaving you with nothing.

## 8. Edit and export

The generated draft is shown in an editable text area. Make any changes and click **Save Edits** - they persist immediately. When you're satisfied, click **Export .docx** to download the draft as a Word document.

## 9. Settings

The **Settings** page shows your firm name and your own account's email and role.

## A note on data isolation

Every case, document, and derived result you see is scoped to your firm. This isn't just a UI convention - it's enforced at the database query layer on the backend, and proven by an automated test suite that verifies one firm's login can never read another firm's data, run on every change before it can be merged.

## Seeing it run on real documents

[Demo Walkthrough Results](demo-walkthrough-results.md) is a recorded run of every step above against a case folder of real, publicly sourced documents (a court opinion, an SEC filing exhibit, an IRS form, and a real medical transcription sample) - including what the system actually classified and extracted, and an honest note about where real documents behaved differently than the short test fixtures used elsewhere in this project.
