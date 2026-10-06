import pytest

from app.llm.gemini import LLMError, VisionIngredient, VisionResult
from app.pipeline import numbers


def scan(client):
    return client.post("/api/identify", files={"image": ("pack.jpg", b"fake-bytes", "image/jpeg")})


def vision(brand, *ings, confidence=0.95, readable=True):
    return VisionResult(readable=readable, brand_text=brand, confidence=confidence,
                        ingredients=[VisionIngredient(name=n, strength=s) for n, s in ings])


def test_clear_telma_am_is_ok(client, fake_llm):
    fake_llm.vision = vision("Telma-AM", ("Telmisartan", "40 mg"), ("Amlodipine", "5 mg"))
    body = scan(client).json()
    assert body["status"] == "ok" and body["brand"] == "Telma-AM"
    assert [i["key"] for i in body["ingredients"]] == ["telmisartan", "amlodipine"]


def test_unreadable_photo(client, fake_llm):
    fake_llm.vision = vision(None, readable=False)
    assert scan(client).json()["status"] == "unreadable"


def test_blurry_photo_is_low_confidence(client, fake_llm):
    fake_llm.vision = vision("Telma-AM", confidence=0.3)
    assert scan(client).json()["status"] == "low_confidence"


def test_omez_d_name_with_esomeprazole_is_low_confidence(client, fake_llm):
    fake_llm.vision = vision("Omez-D", ("Esomeprazole", "40 mg"), ("Domperidone", "30 mg"))
    body = scan(client).json()
    assert body["status"] == "low_confidence" and "Esomeprazole" in body["reasons"][0]


def test_omez_d_plus_sr_is_ok(client, fake_llm):
    fake_llm.vision = vision("Omez-D+ SR", ("Esomeprazole", "40 mg"), ("Domperidone", "30 mg"))
    assert scan(client).json()["brand"] == "Omez-D Plus SR"


def test_wrong_strength_is_low_confidence(client, fake_llm):
    fake_llm.vision = vision("Telma-AM", ("Telmisartan", "80 mg"), ("Amlodipine", "5 mg"))
    assert scan(client).json()["status"] == "low_confidence"


def test_fuzzy_name_without_ingredients_is_low_confidence(client, fake_llm):
    fake_llm.vision = vision("Omez")  # could be plain Omez (omeprazole only): don't guess Omez-D
    assert scan(client).json()["status"] == "low_confidence"


def test_saridon_falls_back_to_ingredients(client, fake_llm):
    fake_llm.vision = vision("Saridon", ("Paracetamol", "250 mg"), ("Propyphenazone", "150 mg"), ("Caffeine", "50 mg"))
    body = scan(client).json()
    assert body["status"] == "ok" and body["brand"] is None
    assert [i["key"] for i in body["ingredients"]] == ["paracetamol"]
    assert body["unverified"] == ["Propyphenazone", "Caffeine"]


def test_gemini_failure_returns_error_status(client, fake_llm, monkeypatch):
    def boom(image, mime_type):
        raise LLMError("busy")
    monkeypatch.setattr(fake_llm, "vision_extract", boom)
    r = scan(client)
    assert r.status_code == 200 and r.json()["status"] == "error"


def test_rejects_non_images_and_huge_files(client, fake_llm):
    assert client.post("/api/identify", files={"image": ("a.pdf", b"x", "application/pdf")}).status_code == 415
    big = b"0" * (8 * 1024 * 1024 + 1)
    assert client.post("/api/identify", files={"image": ("a.jpg", big, "image/jpeg")}).status_code == 413
    assert fake_llm.calls == 0  # rejected before spending a Gemini call


@pytest.mark.parametrize("pack, db, same", [
    ("1 gm", "1000 mg (sustained release)", True),
    ("60000 IU", "60,000 IU (1500 mcg)", True),
    ("500 mg", "1.25 g calcium carbonate (500 mg calcium)", True),
    ("80 mg", "40 mg", False),
])
def test_strength_numbers(pack, db, same):
    assert bool(numbers(pack) & numbers(db)) == same
