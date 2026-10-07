import json

import pytest

from app.config import settings
from app.kb import get_kb
from app.llm.gemini import LLMError
from app.safety import MESSAGES, SAFETY_ORDER, keyword_label, route

REDTEAM = json.loads((settings.data_dir / "redteam.json").read_text(encoding="utf-8"))["questions"]
DANGEROUS = [q for q in REDTEAM if q["expected"] in ("emergency_112", "refuse_to_doctor")]
HARMLESS = [q for q in REDTEAM if q["expected"] == "answer_from_db"]


@pytest.mark.parametrize("q", DANGEROUS, ids=lambda q: str(q["id"]))
def test_keywords_catch_dangerous_questions_even_if_llm_is_wrong(q, fake_llm):
    fake_llm.label = "answer_from_db"  # worst case: the LLM says "safe to answer"
    got = route(q["question"], None, fake_llm)
    assert SAFETY_ORDER.index(got) <= SAFETY_ORDER.index(q["expected"])


@pytest.mark.parametrize("q", HARMLESS, ids=lambda q: str(q["id"]))
def test_keywords_leave_normal_questions_alone(q):
    assert keyword_label(q["question"]) is None


def test_llm_failure_fails_safe(fake_llm, monkeypatch):
    def boom(question, drug_name):
        raise LLMError("busy")
    monkeypatch.setattr(fake_llm, "classify_question", boom)
    assert route("Can I take it with food?", get_kb().drugs["paracetamol"], fake_llm) == "refuse_to_doctor"


def test_answer_needs_trusted_facts(fake_llm):
    drugs = get_kb().drugs
    assert route("What is it for?", None, fake_llm) == "not_in_db"
    assert route("What is it for?", drugs["serratiopeptidase"], fake_llm) == "not_in_db"
    assert route("What is it for?", drugs["paracetamol"], fake_llm) == "answer_from_db"


def test_every_reply_exists_in_every_language():
    for label in SAFETY_ORDER[:-1]:  # all except answer_from_db
        assert set(MESSAGES[label]) == {"en", "hi", "mr"}
    assert all("112" in m for m in MESSAGES["emergency_112"].values())
