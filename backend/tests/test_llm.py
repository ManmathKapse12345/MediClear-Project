import json
from typing import get_args

import pytest
from google.genai import errors

from app.config import settings
from app.kb import get_kb
from app.llm import prompts
from app.llm.gemini import GeminiClient, Label, LLMError


def test_missing_api_key_fails_clearly():
    with pytest.raises(LLMError, match="GEMINI_API_KEY"):
        GeminiClient(api_key="", model="m")


def test_labels_match_redteam_file():
    redteam = json.loads((settings.data_dir / "redteam.json").read_text(encoding="utf-8"))
    assert {q["expected"] for q in redteam["questions"]} <= set(get_args(Label))


@pytest.mark.parametrize("lang", ["en", "hi", "mr"])
def test_explain_prompt_builds_for_every_drug(lang, monkeypatch):
    client = GeminiClient(api_key="test", model="m")
    sent = []
    monkeypatch.setattr(client, "_generate", lambda contents, schema: sent.append(contents))
    for drug in get_kb().drugs.values():
        client.explain(drug, lang)
    assert len(sent) == len(get_kb().drugs)
    assert all(prompts.LANGUAGES[lang] in p for p in sent)


def test_explain_sends_only_facts_not_urls(monkeypatch):
    client = GeminiClient(api_key="test", model="m")
    sent = []
    monkeypatch.setattr(client, "_generate", lambda contents, schema: sent.append(contents))
    drug = get_kb().drugs["paracetamol"]
    client.explain(drug, "hi")
    assert drug["used_for"] in sent[0] and drug["source"] not in sent[0]


def test_api_error_becomes_llm_error(monkeypatch):
    client = GeminiClient(api_key="test", model="m")

    def boom(**kwargs):
        raise errors.ServerError(503, {"error": {"code": 503, "message": "busy", "status": "UNAVAILABLE"}})
    monkeypatch.setattr(client.client.models, "generate_content", boom)
    with pytest.raises(LLMError):
        client.classify_question("hi", None)

def test_server_error_falls_back_to_second_model(monkeypatch):
    client = GeminiClient(api_key="test", model="main", fallback_model="backup")
    tried = []

    class Resp:
        parsed = "ok"

    def fake(model, contents, config):
        tried.append(model)
        assert config is not None and config.temperature == 0  # catches a broken config
        if model == "main":
            raise errors.ServerError(503, {"error": {"code": 503, "message": "busy", "status": "UNAVAILABLE"}})
        return Resp()
    monkeypatch.setattr(client.client.models, "generate_content", fake)
    assert client._generate("hi", None) == "ok"
    assert tried == ["main", "backup"]
