from fastapi import APIRouter

from app.kb import KnowledgeBase, get_kb
from app.matcher import MatchResult, identify_text
from app.schemas import IdentifyResponse, IdentifyTextRequest, IngredientInfo

router = APIRouter(prefix="/api", tags=["identify"])


def to_response(kb: KnowledgeBase, r: MatchResult) -> IdentifyResponse:
    strengths = {i["key"]: i["strength"] for i in kb.brands[r.brand]["ingredients"]} if r.brand else {}
    ingredients = [IngredientInfo(key=k, name=kb.drugs[k]["name"], strength=strengths.get(k),
                                  source=kb.drugs[k]["source"], verified=kb.drugs[k]["verified"])
                   for k in r.ingredients]
    return IdentifyResponse(status=r.status, brand=r.brand, ingredients=ingredients, unverified=r.unverified)


@router.post("/identify/text", response_model=IdentifyResponse)
def identify_by_text(req: IdentifyTextRequest):
    kb = get_kb()
    return to_response(kb, identify_text(kb, req.query))
