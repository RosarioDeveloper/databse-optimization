from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.main import app


def test_health_checks_database(monkeypatch):
    query = AsyncMock(return_value=[{"ok": 1}])
    monkeypatch.setattr("app.main.repository.query", query)

    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": True}
    query.assert_awaited_once_with("SELECT 1 AS ok;")


def test_openapi_is_available():
    response = TestClient(app).get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Database Performance Lab"
