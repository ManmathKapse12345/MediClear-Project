import json

from sqlmodel import select

from app.store import ExplanationCache, SavedMedicine


def test_save_and_read_medicine(session):
    session.add(SavedMedicine(device_id="d1", label="Telma-AM",
                              ingredients=json.dumps(["telmisartan", "amlodipine"])))
    session.commit()
    row = session.exec(select(SavedMedicine).where(SavedMedicine.device_id == "d1")).one()
    assert row.id is not None and row.created_at is not None
    assert row.ingredient_keys() == ["telmisartan", "amlodipine"]


def test_cache_is_keyed_by_drug_lang_and_version(session):
    session.add(ExplanationCache(drug_key="paracetamol", lang="hi", prompt_version="v1", body="{}"))
    session.commit()
    assert session.get(ExplanationCache, ("paracetamol", "hi", "v1")) is not None
    assert session.get(ExplanationCache, ("paracetamol", "mr", "v1")) is None
    assert session.get(ExplanationCache, ("paracetamol", "hi", "v2")) is None
