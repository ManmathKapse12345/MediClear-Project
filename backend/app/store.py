"""SQLite storage: saved medicines per device, and cached LLM explanations."""
import json
from datetime import datetime, timezone

from sqlmodel import Field, Session, SQLModel, create_engine

from app.config import settings

# check_same_thread=False: FastAPI runs sync endpoints in a thread pool
engine = create_engine(f"sqlite:///{settings.db_path}", connect_args={"check_same_thread": False})


class SavedMedicine(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    device_id: str = Field(index=True)
    label: str
    ingredients: str  # JSON list of drugs.json keys, e.g. '["telmisartan", "amlodipine"]'
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def ingredient_keys(self) -> list[str]:
        return json.loads(self.ingredients)


class ExplanationCache(SQLModel, table=True):
    drug_key: str = Field(primary_key=True)
    lang: str = Field(primary_key=True)
    prompt_version: str = Field(primary_key=True)
    body: str  # the Explanation as JSON


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


class AudioCache(SQLModel, table=True):
    text_hash: str = Field(primary_key=True)  # sha256 of lang + the exact text spoken
    mp3: bytes
