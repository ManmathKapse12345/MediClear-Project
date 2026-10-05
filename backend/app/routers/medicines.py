from fastapi import APIRouter, HTTPException

from app.interactions import Med, check
from app.kb import get_kb
from app.schemas import InteractionAlert, InteractionCheckRequest, InteractionCheckResponse

router = APIRouter(prefix="/api", tags=["medicines"])


@router.post("/interactions/check", response_model=InteractionCheckResponse)
def check_interactions(req: InteractionCheckRequest):
    kb = get_kb()
    unknown = {k for m in req.medicines for k in m.ingredients} - kb.drugs.keys()
    if unknown:
        raise HTTPException(422, f"unknown ingredient keys: {sorted(unknown)}")
    alerts = check(kb, [Med(m.label, tuple(m.ingredients)) for m in req.medicines])
    return InteractionCheckResponse(alerts=[InteractionAlert(level=a.level, kind=a.kind, between=list(a.between),
                                                             ingredients=list(a.ingredients), message=a.message,
                                                             sources=a.sources) for a in alerts])
