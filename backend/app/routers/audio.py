from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session

from app.explain import explain
from app.kb import get_kb
from app.llm.gemini import GeminiClient, LLMError, get_llm
from app.schemas import Lang
from app.store import get_session
from app.tts import TTSError, cached_mp3, speech_text

router = APIRouter(prefix="/api", tags=["audio"])


@router.get("/audio/{drug_key}", response_class=Response)
def get_audio(drug_key: str, lang: Lang = "en", session: Session = Depends(get_session),
              llm: GeminiClient = Depends(get_llm)):
    drug = get_kb().drugs.get(drug_key)
    if drug is None:
        raise HTTPException(404, "unknown medicine")
    try:
        text = speech_text(explain(drug, lang, session, llm))
        mp3 = cached_mp3(text, lang, session)
    except (LLMError, TTSError):
        raise HTTPException(503, "The voice service is busy. Please try again.")
    return Response(mp3, media_type="audio/mpeg")
