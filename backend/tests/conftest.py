import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.llm.gemini import ExplainResult, VisionResult, get_llm
from app.main import app
from app.store import get_session


@pytest.fixture
def session():
    # "sqlite://" = in-memory DB; StaticPool keeps one connection so all code sees the same DB
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


@pytest.fixture
def client(session):
    app.dependency_overrides[get_session] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()


class FakeLLM:
    """Stands in for Gemini in tests. Set .vision / .label to control answers; .calls counts requests."""
    def __init__(self):
        self.vision = VisionResult(readable=True, brand_text="Telma-AM", confidence=0.95)
        self.label = "answer_from_db"
        self.calls = 0

    def vision_extract(self, image, mime_type):
        self.calls += 1
        return self.vision

    def explain(self, drug, lang):
        self.calls += 1
        return ExplainResult(used_for=f"[{lang}] {drug['used_for']}", how_it_works=drug["how_it_works"] or "",
                             how_to_take=drug["how_to_take"], avoid=drug["avoid"],
                             side_effects=drug["common_side_effects"], see_doctor_if=drug["serious_warnings"])

    def classify_question(self, question, drug_name):
        self.calls += 1
        return self.label


@pytest.fixture
def fake_llm():
    fake = FakeLLM()
    app.dependency_overrides[get_llm] = lambda: fake
    yield fake
    app.dependency_overrides.pop(get_llm, None)
