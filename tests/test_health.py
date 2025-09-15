from http import HTTPStatus

from fastapi.testclient import TestClient

from app.app import create_app


def test_health_ok():
    app = create_app()
    client = TestClient(app)
    r = client.get("/api/health")
    assert r.status_code == HTTPStatus.OK
    assert r.json() == {"status": "ok"}
