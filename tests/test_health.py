from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_serves_html() -> None:
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers.get("content-type", "")
    assert "Clerk" in r.text


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert "clerk_configured" in data


def test_debug_token_invalid() -> None:
    r = client.post("/debug/token", json={"token": "not.a.jwt"})
    assert r.status_code in (400, 500)


def test_protected_requires_auth() -> None:
    r = client.get("/users/me")
    assert r.status_code == 401


def test_openapi_exists() -> None:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    assert r.json()["openapi"].startswith("3.")
