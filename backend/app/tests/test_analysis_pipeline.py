import pymupdf as fitz


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
    # insert_text() silently drops text that overflows the page width for a
    # single unwrapped line, so longer test strings need insert_textbox()'s
    # wrapping instead.
    doc = fitz.open()
    page = doc.new_page()
    page.insert_textbox(page.rect + (36, 36, -36, -36), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def _upload(client, token, case_id, filename, text):
    response = client.post(
        f"/cases/{case_id}/documents",
        files={"files": (filename, _build_text_pdf(text), "application/pdf")},
        headers=_auth_headers(token),
    )
    assert response.status_code == 201, response.text
    return response.json()[0]["id"]


def test_analyze_produces_chronology_totals_and_conflict_flag(client):
    _register_firm(client, "Firm A", "admin-a2@example.com", "password123")
    token = _login(client, "admin-a2@example.com", "password123")

    case_response = client.post(
        "/cases", json={"title": "Billing case"}, headers=_auth_headers(token)
    )
    case_id = case_response.json()["id"]

    _upload(
        client,
        token,
        case_id,
        "bill1.pdf",
        "Invoice from Acme Billing Services, dated January 5, 2024. Itemized charges "
        "and payment terms enclosed. Amount due: $1,250.00.",
    )
    _upload(
        client,
        token,
        case_id,
        "bill2.pdf",
        "Invoice from Acme Billing Services, dated January 5, 2024. Itemized charges "
        "and payment terms enclosed. Amount due: $900.00.",
    )

    analyze_response = client.post(f"/cases/{case_id}/analyze", headers=_auth_headers(token))
    assert analyze_response.status_code == 200, analyze_response.text
    result = analyze_response.json()

    assert len(result["chronology"]) >= 2
    assert all(e["event_date"] == "2024-01-05" for e in result["chronology"])

    assert float(result["totals"]["total_billed"]) == 2150.0

    assert any(
        flag["flag_type"] == "conflicting_amounts_same_date" for flag in result["inconsistencies"]
    )

    chronology_get = client.get(f"/cases/{case_id}/chronology", headers=_auth_headers(token))
    assert chronology_get.status_code == 200
    assert len(chronology_get.json()) == len(result["chronology"])

    totals_get = client.get(f"/cases/{case_id}/totals", headers=_auth_headers(token))
    assert totals_get.status_code == 200
    assert float(totals_get.json()["total_billed"]) == 2150.0

    inconsistencies_get = client.get(
        f"/cases/{case_id}/inconsistencies", headers=_auth_headers(token)
    )
    assert inconsistencies_get.status_code == 200
    assert len(inconsistencies_get.json()) == len(result["inconsistencies"])


def test_totals_404_before_analyze_runs(client):
    _register_firm(client, "Firm B", "admin-b2@example.com", "password123")
    token = _login(client, "admin-b2@example.com", "password123")
    case_response = client.post(
        "/cases", json={"title": "Fresh case"}, headers=_auth_headers(token)
    )
    case_id = case_response.json()["id"]

    response = client.get(f"/cases/{case_id}/totals", headers=_auth_headers(token))
    assert response.status_code == 404


def test_firm_cannot_read_another_firms_analysis(client):
    _register_firm(client, "Firm C", "admin-c2@example.com", "password123")
    _register_firm(client, "Firm D", "admin-d2@example.com", "password123")
    token_c = _login(client, "admin-c2@example.com", "password123")
    token_d = _login(client, "admin-d2@example.com", "password123")

    case_response = client.post(
        "/cases", json={"title": "Firm C case"}, headers=_auth_headers(token_c)
    )
    case_id = case_response.json()["id"]
    _upload(client, token_c, case_id, "bill.pdf", "Invoice dated January 5, 2024. Amount due: $500.00.")
    client.post(f"/cases/{case_id}/analyze", headers=_auth_headers(token_c))

    for path in ("chronology", "totals", "inconsistencies"):
        response = client.get(f"/cases/{case_id}/{path}", headers=_auth_headers(token_d))
        assert response.status_code == 404

    analyze_as_d = client.post(f"/cases/{case_id}/analyze", headers=_auth_headers(token_d))
    assert analyze_as_d.status_code == 404
