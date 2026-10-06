from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.kb import KnowledgeBase, get_kb
from app.llm.gemini import GeminiClient, LLMError, get_llm
from app.matcher import MatchResult, identify_text
from app.pipeline import identify_photo
from app.schemas import IdentifyResponse, IdentifyTextRequest, IngredientInfo

MAX_IMAGE_BYTES = 8 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"}

router = APIRouter(prefix="/api", tags=["identify"])


def to_response(kb: KnowledgeBase, r: MatchResult) -> IdentifyResponse:
    strengths = {i["key"]: i["strength"] for i in kb.brands[r.brand]["ingredients"]} if r.brand else {}
    ingredients = [IngredientInfo(key=k, name=kb.drugs[k]["name"], strength=strengths.get(k),
                                  source=kb.drugs[k]["source"], verified=kb.drugs[k]["verified"])
                   for k in r.ingredients]
    return IdentifyResponse(status=r.status, brand=r.brand, ingredients=ingredients, unverified=r.unverified,reasons=r.reasons)


@router.post("/identify/text", response_model=IdentifyResponse)
def identify_by_text(req: IdentifyTextRequest):
    kb = get_kb()
    return to_response(kb, identify_text(kb, req.query))


@router.post("/identify", response_model=IdentifyResponse)
def identify_by_photo(image: UploadFile, llm: GeminiClient = Depends(get_llm)):
    if image.content_type not in ALLOWED_TYPES:
        raise HTTPException(415, "Please upload a JPEG, PNG, WEBP or HEIC photo.")
    data = image.file.read(MAX_IMAGE_BYTES + 1)
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(413, "The photo is larger than 8 MB.")
    kb = get_kb()
    try:
        return to_response(kb, identify_photo(kb, llm, data, image.content_type))
    except LLMError:
        return IdentifyResponse(status="error")

