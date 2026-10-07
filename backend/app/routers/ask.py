from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.explain import explain
from app.kb import get_kb
from app.llm.gemini import GeminiClient, LLMError, get_llm
from app.safety import MESSAGES, route
from app.schemas import AskRequest, AskResponse
from app.store import get_session

router = APIRouter(prefix="/api", tags=["ask"])


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest, session: Session = Depends(get_session), llm: GeminiClient = Depends(get_llm)):
    drug = None
    if req.drug_key is not None:
        drug = get_kb().drugs.get(req.drug_key)
        if drug is None:
            raise HTTPException(404, "unknown medicine")

    label = route(req.question, drug, llm)
    if label != "answer_from_db":
        return AskResponse(label=label, message=MESSAGES[label][req.lang])

    # route() only returns answer_from_db when drug exists and has a trusted source
    try:
        expl = explain(drug, req.lang, session, llm)
    except LLMError:
        expl = explain(drug, "en", session, llm)  # English comes from the DB and never calls the LLM
    return AskResponse(label=label, explanation=expl)
