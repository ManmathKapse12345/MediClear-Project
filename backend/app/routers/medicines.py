import json
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlmodel import Session, select

from app.interactions import Alert, Med, check
from app.kb import KnowledgeBase, get_kb
from app.schemas import (
    InteractionAlert,
    InteractionCheckRequest,
    InteractionCheckResponse,
    MedicineListResponse,
    MedIn,
    SavedMedicineOut,
)
from app.store import SavedMedicine, get_session

router = APIRouter(prefix="/api", tags=["medicines"])


def device_id(x_device_id: str = Header()) -> str:
    """The anonymous device UUID the frontend keeps in localStorage."""
    try:
        return str(uuid.UUID(x_device_id))
    except ValueError:
        raise HTTPException(400, "X-Device-Id must be a UUID")


def validate_keys(kb: KnowledgeBase, keys: list[str]) -> None:
    unknown = set(keys) - kb.drugs.keys()
    if unknown:
        raise HTTPException(422, f"unknown ingredient keys: {sorted(unknown)}")


def to_alerts(alerts: list[Alert]) -> list[InteractionAlert]:
    return [InteractionAlert(level=a.level, kind=a.kind, between=list(a.between), ingredients=list(a.ingredients),
                             message=a.message, sources=a.sources) for a in alerts]


def to_out(row: SavedMedicine) -> SavedMedicineOut:
    return SavedMedicineOut(id=row.id, label=row.label, ingredients=row.ingredient_keys(), created_at=row.created_at)


@router.post("/interactions/check", response_model=InteractionCheckResponse)
def check_interactions(req: InteractionCheckRequest):
    kb = get_kb()
    validate_keys(kb, [k for m in req.medicines for k in m.ingredients])
    alerts = check(kb, [Med(m.label, tuple(m.ingredients)) for m in req.medicines])
    return InteractionCheckResponse(alerts=to_alerts(alerts))


@router.get("/medicines", response_model=MedicineListResponse)
def list_medicines(device: str = Depends(device_id), session: Session = Depends(get_session)):
    rows = session.exec(select(SavedMedicine).where(SavedMedicine.device_id == device)
                        .order_by(SavedMedicine.id)).all()
    alerts = check(get_kb(), [Med(r.label, tuple(r.ingredient_keys())) for r in rows])
    return MedicineListResponse(medicines=[to_out(r) for r in rows], alerts=to_alerts(alerts))


@router.post("/medicines", response_model=SavedMedicineOut, status_code=201)
def save_medicine(med: MedIn, device: str = Depends(device_id), session: Session = Depends(get_session)):
    validate_keys(get_kb(), med.ingredients)
    row = SavedMedicine(device_id=device, label=med.label, ingredients=json.dumps(med.ingredients))
    session.add(row)
    session.commit()
    session.refresh(row)  # loads the id and created_at the DB just assigned
    return to_out(row)


@router.delete("/medicines/{med_id}", status_code=204)
def delete_medicine(med_id: int, device: str = Depends(device_id), session: Session = Depends(get_session)):
    row = session.get(SavedMedicine, med_id)
    if row is None or row.device_id != device:
        raise HTTPException(404, "medicine not found")
    session.delete(row)
    session.commit()
