import uuid

D1, D2 = str(uuid.uuid4()), str(uuid.uuid4())
TELMA = {"label": "Telma-AM", "ingredients": ["telmisartan", "amlodipine"]}
ECOSPRIN = {"label": "Ecosprin 150", "ingredients": ["aspirin"]}


def h(device):
    return {"X-Device-Id": device}


def test_save_two_and_see_interaction(client):
    for med in (TELMA, ECOSPRIN):
        assert client.post("/api/medicines", json=med, headers=h(D1)).status_code == 201
    body = client.get("/api/medicines", headers=h(D1)).json()
    assert [m["label"] for m in body["medicines"]] == ["Telma-AM", "Ecosprin 150"]
    assert {tuple(a["ingredients"]) for a in body["alerts"]} == {("telmisartan", "aspirin"), ("amlodipine", "aspirin")}
    assert body["disclaimer"]


def test_other_device_sees_nothing(client):
    client.post("/api/medicines", json=TELMA, headers=h(D1))
    body = client.get("/api/medicines", headers=h(D2)).json()
    assert body["medicines"] == [] and body["alerts"] == []


def test_cannot_delete_other_devices_medicine(client):
    med_id = client.post("/api/medicines", json=TELMA, headers=h(D1)).json()["id"]
    assert client.delete(f"/api/medicines/{med_id}", headers=h(D2)).status_code == 404
    assert client.delete(f"/api/medicines/{med_id}", headers=h(D1)).status_code == 204
    assert client.get("/api/medicines", headers=h(D1)).json()["medicines"] == []


def test_rejects_bad_or_missing_device_id(client):
    assert client.get("/api/medicines", headers=h("not-a-uuid")).status_code == 400
    assert client.get("/api/medicines").status_code == 422


def test_rejects_unknown_ingredient(client):
    r = client.post("/api/medicines", json={"label": "X", "ingredients": ["madeup"]}, headers=h(D1))
    assert r.status_code == 422
