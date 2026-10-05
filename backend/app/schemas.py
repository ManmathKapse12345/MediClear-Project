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
