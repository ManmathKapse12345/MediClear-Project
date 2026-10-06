from app.kb import get_kb
from app.llm.gemini import LLMError


def test_english_comes_from_db_without_llm(client, fake_llm):
    body = client.get("/api/explain/paracetamol?lang=en").json()
    assert body["generated_by"] == "database" and fake_llm.calls == 0
    assert body["used_for"] == get_kb().drugs["paracetamol"]["used_for"]
    assert body["sources"][0].startswith("https://") and body["disclaimer"]


def test_hindi_calls_llm_once_then_uses_cache(client, fake_llm):
    first = client.get("/api/explain/paracetamol?lang=hi").json()
    second = client.get("/api/explain/paracetamol?lang=hi").json()
    assert first == second and first["generated_by"] == "llm"
    assert first["used_for"].startswith("[hi]")
    assert fake_llm.calls == 1


def test_cache_is_per_language(client, fake_llm):
    client.get("/api/explain/paracetamol?lang=hi")
    client.get("/api/explain/paracetamol?lang=mr")
    assert fake_llm.calls == 2


def test_no_trusted_source_never_calls_llm(client, fake_llm):
    for lang in ("en", "hi", "mr"):
        body = client.get(f"/api/explain/serratiopeptidase?lang={lang}").json()
        assert body["available"] is False and body["message"] and body["generated_by"] == "none"
    assert fake_llm.calls == 0


def test_unknown_drug_or_language(client, fake_llm):
    assert client.get("/api/explain/madeup").status_code == 404
    assert client.get("/api/explain/paracetamol?lang=fr").status_code == 422


def test_llm_failure_returns_503_and_caches_nothing(client, fake_llm, monkeypatch):
    def boom(drug, lang):
        raise LLMError("busy")
    monkeypatch.setattr(fake_llm, "explain", boom)
    assert client.get("/api/explain/paracetamol?lang=hi").status_code == 503
    monkeypatch.undo()
    assert client.get("/api/explain/paracetamol?lang=hi").json()["generated_by"] == "llm"
