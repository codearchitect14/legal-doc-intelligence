# Sample Case Data

The demonstration case folder at `data/sample_case_folder/` is assembled from genuinely real, publicly available documents (Phase 7, per `PROJECT_PLAN_v2.md` Section 11). Every file's exact provenance is documented below - no ambiguity about what's an original download versus real text placed into a PDF we generated.

| File | Source | Retrieved | How it was obtained |
|---|---|---|---|
| `irs_form_w2_blank.pdf` | [irs.gov/pub/irs-pdf/fw2.pdf](https://www.irs.gov/pub/irs-pdf/fw2.pdf) | 2026-09-15 | Original PDF, downloaded directly - unmodified |
| `scotus_opinion_loper_bright.pdf` | [supremecourt.gov - *Loper Bright Enterprises v. Raimondo*, No. 22-451](https://www.supremecourt.gov/opinions/23pdf/22-451_7m58.pdf) | 2026-09-15 | Original PDF, downloaded directly - unmodified |
| `sec_exhibit_employment_agreement.pdf` | [SEC EDGAR - Exhibit 10.1, CIK 0000006885](https://www.sec.gov/Archives/edgar/data/6885/000000688511000152/ex10_1.pdf) | 2026-09-15 | Original PDF, downloaded directly - unmodified |
| `mtsamples_orthopedic_consult.pdf` | [mtsamples.com - Orthopedic Consult](https://www.mtsamples.com/site/pages/sample.asp?Type=49-Orthopedic&Sample=1502-Orthopedic+Consult) | 2026-09-15 | mtsamples publishes real (already anonymized) sample reports as a web page, not a downloadable file. The report's full text was copied verbatim and placed into a PDF generated for this project - the text is real, the PDF container is ours |

**Deferred for a future pass, not silently substituted:** CORD/SROIE/FUNSD (large ML benchmark datasets on Kaggle/HuggingFace, needing dataset-download tooling this pass didn't set up), DOL wage forms, and additional mtsamples variety. The four files above are enough to exercise every document category the pipeline classifies (medical record, filing, contract, wage-adjacent form) without those.

No figures were overlaid onto the IRS form - it's used blank, as a real example of the document type. No real client data is used anywhere in this folder; every source is a public filing, a public court opinion, a public government form, or an already-anonymized public sample report.
