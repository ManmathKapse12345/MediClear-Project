from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json()["status"] == "ok"


def test_identify_text_known_brand():
    body = client.post("/api/identify/text", json={"query": "Telma AM"}).json()
    assert body["status"] == "ok" and body["brand"] == "Telma-AM" and body["disclaimer"]


def test_interactions_rejects_unknown_keys():
    r = client.post("/api/interactions/check", json={"medicines": [{"label": "X", "ingredients": ["madeup"]}]})
    assert r.status_code == 422
