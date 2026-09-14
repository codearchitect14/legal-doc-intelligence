def _register_firm(client, firm_name: str, email: str, password: str) -> None:
    response = client.post(
        "/auth/register-firm",
        json={"firm_name": firm_name, "admin_email": email, "admin_password": password},
    )
    assert response.status_code == 201, response.text


def _login(client, email: str, password: str) -> str:
    response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_firm_cannot_read_another_firms_case(client):
    _register_firm(client, "Firm A", "admin-a@example.com", "password123")
    _register_firm(client, "Firm B", "admin-b@example.com", "password123")

    token_a = _login(client, "admin-a@example.com", "password123")
    token_b = _login(client, "admin-b@example.com", "password123")

    create_response = client.post(
        "/cases", json={"title": "Firm A confidential case"}, headers=_auth_headers(token_a)
    )
    assert create_response.status_code == 201, create_response.text
    case_a_id = create_response.json()["id"]

    # Firm B must not be able to fetch Firm A's case by ID.
    get_as_b = client.get(f"/cases/{case_a_id}", headers=_auth_headers(token_b))
    assert get_as_b.status_code == 404

    # Firm B's case list must not contain Firm A's case.
    list_as_b = client.get("/cases", headers=_auth_headers(token_b))
    assert list_as_b.status_code == 200
    assert all(case["id"] != case_a_id for case in list_as_b.json())

    # Firm A can still read its own case.
    get_as_a = client.get(f"/cases/{case_a_id}", headers=_auth_headers(token_a))
    assert get_as_a.status_code == 200
    assert get_as_a.json()["id"] == case_a_id


def test_login_rejects_wrong_password(client):
    _register_firm(client, "Firm C", "admin-c@example.com", "password123")
    response = client.post(
        "/auth/login", data={"username": "admin-c@example.com", "password": "wrong"}
    )
    assert response.status_code == 401
