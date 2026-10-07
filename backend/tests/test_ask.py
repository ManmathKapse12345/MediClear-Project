from app.llm.gemini import LLMError


def ask(client, **body):
    return client.post("/api/ask", json=body)


def test_safe_question_returns_db_explanation(client, fake_llm):
    body = ask(client, question="Can I take it with food?", drug_key="paracetamol").json()
    assert body["label"] == "answer_from_db" and body["message"] is None
    assert body["explanation"]["generated_by"] == "database" and body["disclaimer"]


def test_emergency_gets_fixed_message_in_every_language(client, fake_llm):
    fake_llm.label = "emergency_112"
    for lang in ("en", "hi", "mr"):
        body = ask(client, question="I feel strange", drug_key="paracetamol", lang=lang).json()
        assert body["label"] == "emergency_112" and "112" in body["message"]
        assert body["explanation"] is None


def test_translation_failure_falls_back_to_english(client, fake_llm, monkeypatch):
    def boom(drug, lang):
        raise LLMError("busy")
    monkeypatch.setattr(fake_llm, "explain", boom)
    r = ask(client, question="What is it for?", drug_key="paracetamol", lang="hi")
    assert r.status_code == 200 and r.json()["explanation"]["lang"] == "en"


def test_no_drug_means_not_in_db(client, fake_llm):
    assert ask(client, question="What is Crocin for?").json()["label"] == "not_in_db"


def test_bad_input(client, fake_llm):
    assert ask(client, question="hi", drug_key="madeup").status_code == 404
    assert ask(client, question="x" * 501).status_code == 422
    assert ask(client, question="").status_code == 422
