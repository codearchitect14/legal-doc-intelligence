import pymupdf as fitz
from sqlalchemy import select

from app.models.embedding_chunk import EmbeddingChunk


def _register_firm(client, firm_name: str, email: str, password: str) -> None:
    response = client.post(
        "/auth/register-firm",
        json={"firm_name": firm_name, "admin_email": email, "admin_password": password},
    )
    assert response.status_code == 201, response.text


def _login(client, email: str, password: str) -> str:
    response = client.post("/auth/login", data={"username": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _build_text_pdf(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    # insert_text() silently drops text that overflows the page width for a
    # single unwrapped line, so longer test strings need insert_textbox()'s
    # wrapping instead.
    page.insert_textbox(page.rect + (36, 36, -36, -36), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_upload_pdf_is_extracted_classified_and_embedded(client, db_session):
    _register_firm(client, "Firm A", "admin-a@example.com", "password123")
    token = _login(client, "admin-a@example.com", "password123")

    case_response = client.post(
        "/cases", json={"title": "Medical case"}, headers=_auth_headers(token)
    )
    assert case_response.status_code == 201, case_response.text
    case_id = case_response.json()["id"]

    pdf_bytes = _build_text_pdf(
        "Doctor's clinical notes: patient diagnosis, treatment history, and hospital discharge summary."
    )
    upload_response = client.post(
        f"/cases/{case_id}/documents",
        files={"files": ("clinical_notes.pdf", pdf_bytes, "application/pdf")},
        headers=_auth_headers(token),
    )
    assert upload_response.status_code == 201, upload_response.text
    documents = upload_response.json()
    assert len(documents) == 1
    document_id = documents[0]["id"]
    # The upload response is serialized before the background task runs
    # (FastAPI sends the response, then executes BackgroundTasks), so it
    # still shows the pre-processing "pending" state here.
    assert documents[0]["ocr_status"] == "pending"

    # By the time client.post() returns, the TestClient has driven the
    # background task to completion, so a follow-up GET sees final state.
    get_response = client.get(
        f"/cases/{case_id}/documents/{document_id}", headers=_auth_headers(token)
    )
    assert get_response.status_code == 200
    assert get_response.json()["ocr_status"] == "not_required"
    assert get_response.json()["category"] == "medical_record"

    chunks = db_session.execute(
        select(EmbeddingChunk).where(EmbeddingChunk.document_id == document_id)
    ).scalars().all()
    assert len(chunks) >= 1
    assert len(chunks[0].embedding) == 384


def test_rejects_unsupported_file_type(client):
    _register_firm(client, "Firm B", "admin-b@example.com", "password123")
    token = _login(client, "admin-b@example.com", "password123")

    case_response = client.post(
        "/cases", json={"title": "Case"}, headers=_auth_headers(token)
    )
    case_id = case_response.json()["id"]

    response = client.post(
        f"/cases/{case_id}/documents",
        files={"files": ("malware.exe", b"not a real document", "application/octet-stream")},
        headers=_auth_headers(token),
    )
    assert response.status_code == 415


def test_firm_cannot_upload_to_or_list_another_firms_case(client):
    _register_firm(client, "Firm C", "admin-c@example.com", "password123")
    _register_firm(client, "Firm D", "admin-d@example.com", "password123")
    token_c = _login(client, "admin-c@example.com", "password123")
    token_d = _login(client, "admin-d@example.com", "password123")

    case_response = client.post(
        "/cases", json={"title": "Firm C case"}, headers=_auth_headers(token_c)
    )
    case_id = case_response.json()["id"]

    pdf_bytes = _build_text_pdf("A short letter between two parties dated last week.")
    upload_as_d = client.post(
        f"/cases/{case_id}/documents",
        files={"files": ("letter.pdf", pdf_bytes, "application/pdf")},
        headers=_auth_headers(token_d),
    )
    assert upload_as_d.status_code == 404

    list_as_d = client.get(f"/cases/{case_id}/documents", headers=_auth_headers(token_d))
    assert list_as_d.status_code == 404


def test_document_file_and_fields_are_readable_and_firm_scoped(client):
    _register_firm(client, "Firm E", "admin-e@example.com", "password123")
    _register_firm(client, "Firm F", "admin-f@example.com", "password123")
    token_e = _login(client, "admin-e@example.com", "password123")
    token_f = _login(client, "admin-f@example.com", "password123")

    case_response = client.post(
        "/cases", json={"title": "Bill case"}, headers=_auth_headers(token_e)
    )
    case_id = case_response.json()["id"]

    pdf_bytes = _build_text_pdf(
        "Invoice from Acme Billing Services, dated January 5, 2024. Amount due: $500.00."
    )
    upload_response = client.post(
        f"/cases/{case_id}/documents",
        files={"files": ("bill.pdf", pdf_bytes, "application/pdf")},
        headers=_auth_headers(token_e),
    )
    document_id = upload_response.json()[0]["id"]

    file_response = client.get(
        f"/cases/{case_id}/documents/{document_id}/file", headers=_auth_headers(token_e)
    )
    assert file_response.status_code == 200
    assert file_response.content.startswith(b"%PDF")

    fields_response = client.get(
        f"/cases/{case_id}/documents/{document_id}/fields", headers=_auth_headers(token_e)
    )
    assert fields_response.status_code == 200
    assert any(f["field_name"] == "date" for f in fields_response.json())

    file_as_f = client.get(
        f"/cases/{case_id}/documents/{document_id}/file", headers=_auth_headers(token_f)
    )
    assert file_as_f.status_code == 404

    fields_as_f = client.get(
        f"/cases/{case_id}/documents/{document_id}/fields", headers=_auth_headers(token_f)
    )
    assert fields_as_f.status_code == 404
