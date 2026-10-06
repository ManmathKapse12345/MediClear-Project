from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

DISCLAIMER = ("MediClear explains medicines. It does not replace your doctor or pharmacist. "
              "Always follow their instructions. Do not start, stop or change a medicine without asking them.")


class IdentifyTextRequest(BaseModel):
    query: str = Field(min_length=1, max_length=200)


class IngredientInfo(BaseModel):
    key: str
    name: str
    strength: str | None = None
    source: str | None = None
    verified: bool


class IdentifyResponse(BaseModel):
    status: Literal["ok", "unreadable", "low_confidence", "not_in_db", "error"]
    brand: str | None = None
    ingredients: list[IngredientInfo] = []
    unverified: list[str] = []
    disclaimer: str = DISCLAIMER
    reasons: list[str] = []


class MedIn(BaseModel):
    label: str
    ingredients: list[str]


class InteractionCheckRequest(BaseModel):
    medicines: list[MedIn] = Field(max_length=30)


class InteractionAlert(BaseModel):
    level: str
    kind: str
    between: list[str]
    ingredients: list[str]
    message: str
    sources: list[str]


class InteractionCheckResponse(BaseModel):
    alerts: list[InteractionAlert]
    disclaimer: str = DISCLAIMER


class SavedMedicineOut(BaseModel):
    id: int
    label: str
    ingredients: list[str]
    created_at: datetime


class MedicineListResponse(BaseModel):
    medicines: list[SavedMedicineOut]
    alerts: list[InteractionAlert]
    disclaimer: str = DISCLAIMER

Lang = Literal["en", "hi", "mr"]


class Explanation(BaseModel):
    drug_key: str
    name: str
    lang: Lang
    available: bool = True       # False when no trusted source exists
    message: str | None = None   # the fixed text shown when not available
    used_for: str = ""
    how_it_works: str = ""
    how_to_take: str = ""
    avoid: list[str] = []
    side_effects: list[str] = []
    see_doctor_if: list[str] = []
    sources: list[str] = []
    generated_by: Literal["database", "llm", "none"]
    disclaimer: str = DISCLAIMER
