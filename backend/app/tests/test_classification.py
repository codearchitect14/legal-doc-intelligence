from app.services.classification import classify


def test_clinical_notes_classify_as_medical_record():
    text = "Doctor's clinical notes: patient diagnosis, treatment history, and hospital discharge summary."
    category, confidence = classify(text)
    assert category == "medical_record"
    assert confidence > 0


def test_explanation_of_benefits_classifies_as_bill_not_wage_record():
    # A real Explanation of Benefits document (data/sample_case_folder/
    # cms_sample_eob.pdf) was misclassified as wage_record on semantic
    # similarity alone (0.523 vs 0.507 for bill - a near-tie, not a clear
    # miss) despite containing none of a pay stub's actual vocabulary
    # (no "hourly rate", "gross pay", "hours worked") and several
    # unambiguous billing phrases. This is representative real-EOB
    # language, not the literal file, to keep the test self-contained.
    text = (
        "EXPLANATION OF BENEFITS (EOB) - THIS IS NOT A BILL. "
        "Statement Date: 03/20/2022. Provider charges are listed below. "
        "Amount billed: $375.00. Plan paid: $118.12. Patient responsibility: $35.00. "
        "This is a summary of the benefits provided under your health plan."
    )
    category, _ = classify(text)
    assert category == "bill"


def test_wage_statement_still_classifies_as_wage_record():
    # Guards against the keyword boost above overcorrecting: a real pay
    # stub's own vocabulary must still win comfortably.
    text = (
        "WAGE STATEMENT. Employer: Acme Corp. Pay period ending 04/01/2026. "
        "Hourly rate: $22.50. Hours worked: 80. Gross pay: $1,800.00. "
        "Net pay: $1,420.33 after deductions."
    )
    category, _ = classify(text)
    assert category == "wage_record"
