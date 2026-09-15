import httpx
import respx

from app.llm.llm_router import GEMINI_URL_TEMPLATE, GROQ_CHAT_URL
from app.models.inconsistency_flag import InconsistencyFlag


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


def _make_analyzed_case(client, db_session, email: str, with_inconsistency: bool) -> tuple[str, str]:
    _register_firm(client, f"Firm {email}", email, "password123")
    token = _login(client, email, "password123")
    case_response = client.post(
        "/cases", json={"title": "Test case"}, headers=_auth_headers(token)
    )
    case_id = case_response.json()["id"]
    # /analyze with no documents still creates a CaseTotals row (zeroed),
    # which is all create_draft requires to proceed.
    analyze_response = client.post(f"/cases/{case_id}/analyze", headers=_auth_headers(token))
    assert analyze_response.status_code == 200, analyze_response.text

    if with_inconsistency:
        db_session.add(
            InconsistencyFlag(
                case_id=case_id, flag_type="conflicting_amounts_same_date", description="test flag"
            )
        )
        db_session.commit()

    return token, case_id


GROQ_SUCCESS = httpx.Response(
    200,
    json={
        "choices": [{"message": {"content": "Groq-written narrative."}}],
        "usage": {"prompt_tokens": 100, "completion_tokens": 50},
    },
)
GEMINI_SUCCESS = httpx.Response(
    200,
    json={
        "candidates": [{"content": {"parts": [{"text": "Gemini-written narrative."}]}}],
        "usageMetadata": {"promptTokenCount": 90, "candidatesTokenCount": 40},
    },
)


@respx.mock
def test_chronology_summary_without_inconsistencies_is_template_only(client, db_session):
    groq_mock = respx.post(GROQ_CHAT_URL)
    gemini_mock = respx.post(GEMINI_URL_TEMPLATE.format(model="gemini-1.5-flash"))

    token, case_id = _make_analyzed_case(
        client, db_session, "admin-t1@example.com", with_inconsistency=False
    )
    response = client.post(
        f"/cases/{case_id}/draft",
        json={"output_type": "chronology_summary"},
        headers=_auth_headers(token),
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["status"] == "complete"
    assert "CASE SUMMARY" in body["content"]
    assert not groq_mock.called
    assert not gemini_mock.called


@respx.mock
def test_chronology_summary_with_inconsistency_escalates_to_llm(client, db_session):
    respx.post(GROQ_CHAT_URL).mock(return_value=GROQ_SUCCESS)

    token, case_id = _make_analyzed_case(
        client, db_session, "admin-t2@example.com", with_inconsistency=True
    )
    response = client.post(
        f"/cases/{case_id}/draft",
        json={"output_type": "chronology_summary"},
        headers=_auth_headers(token),
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["status"] == "complete"
    assert body["content"] == "Groq-written narrative."

    drafts_response = client.get(f"/cases/{case_id}/drafts", headers=_auth_headers(token))
    assert len(drafts_response.json()) == 1


@respx.mock
def test_demand_letter_always_calls_llm(client, db_session):
    respx.post(GROQ_CHAT_URL).mock(return_value=GROQ_SUCCESS)

    token, case_id = _make_analyzed_case(
        client, db_session, "admin-t3@example.com", with_inconsistency=False
    )
    response = client.post(
        f"/cases/{case_id}/draft",
        json={"output_type": "demand_letter"},
        headers=_auth_headers(token),
    )
    assert response.status_code == 201, response.text
    assert response.json()["content"] == "Groq-written narrative."


@respx.mock
def test_groq_failure_falls_back_to_gemini(client, db_session):
    respx.post(GROQ_CHAT_URL).mock(return_value=httpx.Response(500))
    respx.post(GEMINI_URL_TEMPLATE.format(model="gemini-1.5-flash")).mock(
        return_value=GEMINI_SUCCESS
    )

    token, case_id = _make_analyzed_case(
        client, db_session, "admin-t4@example.com", with_inconsistency=True
    )
    response = client.post(
        f"/cases/{case_id}/draft",
        json={"output_type": "chronology_summary"},
        headers=_auth_headers(token),
    )
    assert response.status_code == 201, response.text
    assert response.json()["content"] == "Gemini-written narrative."

    from app.core.redis_client import get_redis

    assert get_redis().get("llm:groq:unavailable") is not None


@respx.mock
def test_both_providers_failing_falls_back_to_template(client, db_session):
    respx.post(GROQ_CHAT_URL).mock(return_value=httpx.Response(500))
    respx.post(GEMINI_URL_TEMPLATE.format(model="gemini-1.5-flash")).mock(
        return_value=httpx.Response(500)
    )

    token, case_id = _make_analyzed_case(
        client, db_session, "admin-t5@example.com", with_inconsistency=True
    )
    response = client.post(
        f"/cases/{case_id}/draft",
        json={"output_type": "demand_letter"},
        headers=_auth_headers(token),
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["status"] == "template_fallback"
    assert "DEMAND LETTER" in body["content"]


@respx.mock
def test_firm_cannot_read_or_create_another_firms_draft(client, db_session):
    respx.post(GROQ_CHAT_URL).mock(return_value=GROQ_SUCCESS)

    _token_a, case_id = _make_analyzed_case(
        client, db_session, "admin-t6a@example.com", with_inconsistency=False
    )
    _register_firm(client, "Firm T6B", "admin-t6b@example.com", "password123")
    token_b = _login(client, "admin-t6b@example.com", "password123")

    create_as_b = client.post(
        f"/cases/{case_id}/draft",
        json={"output_type": "chronology_summary"},
        headers=_auth_headers(token_b),
    )
    assert create_as_b.status_code == 404

    list_as_b = client.get(f"/cases/{case_id}/drafts", headers=_auth_headers(token_b))
    assert list_as_b.status_code == 404


def test_edit_draft_persists_content(client, db_session):
    token, case_id = _make_analyzed_case(
        client, db_session, "admin-t7@example.com", with_inconsistency=False
    )
    create_response = client.post(
        f"/cases/{case_id}/draft",
        json={"output_type": "chronology_summary"},
        headers=_auth_headers(token),
    )
    draft_id = create_response.json()["id"]

    edit_response = client.patch(
        f"/cases/{case_id}/drafts/{draft_id}",
        json={"content": "Edited by the lawyer."},
        headers=_auth_headers(token),
    )
    assert edit_response.status_code == 200
    assert edit_response.json()["content"] == "Edited by the lawyer."

    get_response = client.get(
        f"/cases/{case_id}/drafts/{draft_id}", headers=_auth_headers(token)
    )
    assert get_response.json()["content"] == "Edited by the lawyer."


def test_export_draft_returns_a_valid_docx(client, db_session):
    token, case_id = _make_analyzed_case(
        client, db_session, "admin-t8@example.com", with_inconsistency=False
    )
    create_response = client.post(
        f"/cases/{case_id}/draft",
        json={"output_type": "chronology_summary"},
        headers=_auth_headers(token),
    )
    draft_id = create_response.json()["id"]

    export_response = client.get(
        f"/cases/{case_id}/drafts/{draft_id}/export", headers=_auth_headers(token)
    )
    assert export_response.status_code == 200
    assert export_response.headers["content-type"] == (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    # A valid .docx is a zip archive; PK\x03\x04 is the zip local-file-header magic.
    assert export_response.content.startswith(b"PK\x03\x04")


def test_firm_cannot_edit_or_export_another_firms_draft(client, db_session):
    token_a, case_id = _make_analyzed_case(
        client, db_session, "admin-t9a@example.com", with_inconsistency=False
    )
    create_response = client.post(
        f"/cases/{case_id}/draft",
        json={"output_type": "chronology_summary"},
        headers=_auth_headers(token_a),
    )
    draft_id = create_response.json()["id"]

    _register_firm(client, "Firm T9B", "admin-t9b@example.com", "password123")
    token_b = _login(client, "admin-t9b@example.com", "password123")

    edit_as_b = client.patch(
        f"/cases/{case_id}/drafts/{draft_id}",
        json={"content": "hijacked"},
        headers=_auth_headers(token_b),
    )
    assert edit_as_b.status_code == 404

    export_as_b = client.get(
        f"/cases/{case_id}/drafts/{draft_id}/export", headers=_auth_headers(token_b)
    )
    assert export_as_b.status_code == 404
