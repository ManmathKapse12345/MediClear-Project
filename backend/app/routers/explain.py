from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.explain import explain
from app.kb import get_kb
from app.llm.gemini import GeminiClient, LLMError, get_llm
from app.schemas import Explanation, Lang
from app.store import get_session

router = APIRouter(prefix="/api", tags=["explain"])


@router.get("/explain/{drug_key}", response_model=Explanation)
def get_explanation(drug_key: str, lang: Lang = "en", session: Session = Depends(get_session),
                    llm: GeminiClient = Depends(get_llm)):
    drug = get_kb().drugs.get(drug_key)
    if drug is None:
        raise HTTPException(404, "unknown medicine")
    try:
        return explain(drug, lang, session, llm)
    except LLMError:
        raise HTTPException(503, "The translation service is busy. Please try again, or read it in English.")
