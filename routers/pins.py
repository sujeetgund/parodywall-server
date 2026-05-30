from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func, cast, String
from datetime import datetime, timezone, timedelta
from uuid import UUID

from database import get_db
from models import Pin, PinLike, PinSave, PinReport, User
from schemas import PinCreate, PinResponse, ReportCreate
from dependencies import get_current_user, get_optional_user

router = APIRouter(prefix="/pins", tags=["pins"])

DAILY_PIN_LIMIT = 3
VALID_CATEGORIES = {"Funny", "Deep Thoughts", "Memes", "Confessions", "Rants"}


def _pin_to_response(pin: Pin, user: User, likes_count: int, is_liked: bool, is_saved: bool) -> dict:
    return {
        "id": pin.id,
        "type": pin.type,
        "text_content": pin.text_content,
        "image_url": pin.image_url,
        "bg_color": pin.bg_color,
        "categories": pin.categories or [],
        "author_alias": user.alias,
        "author_avatar": user.avatar,
        "is_superuser": user.is_superuser,
        "user_id": user.id,
        "likes_count": likes_count,
        "is_liked": is_liked,
        "is_saved": is_saved,
        "created_at": pin.created_at,
    }


def _enrich_pins(db: Session, pins_with_authors: list, viewer_id: UUID | None) -> list[dict]:
    """Batch-enrich a list of (Pin, User) tuples with like/save counts."""
    if not pins_with_authors:
        return []

    pin_ids = [p.id for p, _ in pins_with_authors]

    # Batch: like counts
    like_counts_q = (
        db.query(PinLike.pin_id, sa_func.count(PinLike.id))
        .filter(PinLike.pin_id.in_(pin_ids))
        .group_by(PinLike.pin_id)
        .all()
    )
    like_counts = dict(like_counts_q)

    # Batch: viewer's likes & saves
    liked_ids: set[UUID] = set()
    saved_ids: set[UUID] = set()
    if viewer_id:
        liked_ids = {
            row[0]
            for row in db.query(PinLike.pin_id)
            .filter(PinLike.pin_id.in_(pin_ids), PinLike.user_id == viewer_id)
            .all()
        }
        saved_ids = {
            row[0]
            for row in db.query(PinSave.pin_id)
            .filter(PinSave.pin_id.in_(pin_ids), PinSave.user_id == viewer_id)
            .all()
        }

    return [
        _pin_to_response(
            pin, author,
            likes_count=like_counts.get(pin.id, 0),
            is_liked=pin.id in liked_ids,
            is_saved=pin.id in saved_ids,
        )
        for pin, author in pins_with_authors
    ]


# ── Create ─────────────────────────────────────────────

@router.post("/", response_model=PinResponse, status_code=status.HTTP_201_CREATED)
def create_pin(req: PinCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Validate type
    if req.type not in ("text", "image", "both"):
        raise HTTPException(status_code=400, detail="Invalid pin type")

    if req.type in ("text", "both") and not req.text_content:
        raise HTTPException(status_code=400, detail="Text content is required for this pin type")
    if req.type in ("image", "both") and not req.image_url:
        raise HTTPException(status_code=400, detail="Image URL is required for this pin type")

    # Validate categories
    if not req.categories:
        raise HTTPException(status_code=400, detail="At least one category is required")
    invalid = set(req.categories) - VALID_CATEGORIES
    if invalid:
        raise HTTPException(status_code=400, detail=f"Invalid categories: {invalid}")

    # Daily limit (superusers bypass)
    if not user.is_superuser:
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = db.query(sa_func.count(Pin.id)).filter(
            Pin.user_id == user.id,
            Pin.created_at >= today_start,
        ).scalar()
        if today_count >= DAILY_PIN_LIMIT:
            raise HTTPException(status_code=429, detail="Daily pin limit reached (3 per day)")

    pin = Pin(
        type=req.type,
        text_content=req.text_content,
        image_url=req.image_url,
        bg_color=req.bg_color,
        categories=req.categories,
        user_id=user.id,
    )
    db.add(pin)
    db.commit()
    db.refresh(pin)

    return _pin_to_response(pin, user, likes_count=0, is_liked=False, is_saved=False)


# ── Read ───────────────────────────────────────────────

@router.get("/remaining")
def get_remaining_pins(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.is_superuser:
        return {"remaining": -1}  # -1 = unlimited
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = db.query(sa_func.count(Pin.id)).filter(
        Pin.user_id == user.id,
        Pin.created_at >= today_start,
    ).scalar()
    return {"remaining": max(0, DAILY_PIN_LIMIT - today_count)}


@router.get("/me", response_model=list[PinResponse])
def get_my_pins(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    pins = (
        db.query(Pin, User)
        .join(User, Pin.user_id == User.id)
        .filter(Pin.user_id == user.id)
        .order_by(Pin.created_at.desc())
        .all()
    )
    return _enrich_pins(db, pins, user.id)


@router.get("/saved", response_model=list[PinResponse])
def get_saved_pins(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    pins = (
        db.query(Pin, User)
        .join(User, Pin.user_id == User.id)
        .join(PinSave, PinSave.pin_id == Pin.id)
        .filter(PinSave.user_id == user.id)
        .order_by(PinSave.created_at.desc())
        .all()
    )
    return _enrich_pins(db, pins, user.id)


@router.get("/{pin_id}", response_model=PinResponse)
def get_pin(pin_id: UUID, db: Session = Depends(get_db), viewer: User | None = Depends(get_optional_user)):
    result = db.query(Pin, User).join(User, Pin.user_id == User.id).filter(Pin.id == pin_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Pin not found")
    enriched = _enrich_pins(db, [result], viewer.id if viewer else None)
    return enriched[0]


@router.get("/", response_model=list[PinResponse])
def list_pins(
    category: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    viewer: User | None = Depends(get_optional_user),
):
    q = db.query(Pin, User).join(User, Pin.user_id == User.id)
    if category:
        q = q.filter(Pin.categories.any(category))
    q = q.order_by(Pin.created_at.desc()).offset(offset).limit(limit)
    pins = q.all()
    return _enrich_pins(db, pins, viewer.id if viewer else None)


# ── Delete ─────────────────────────────────────────────

@router.delete("/{pin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pin(pin_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    pin = db.query(Pin).filter(Pin.id == pin_id).first()
    if not pin:
        raise HTTPException(status_code=404, detail="Pin not found")
    if pin.user_id != user.id and not user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to delete this pin")
    db.delete(pin)
    db.commit()


# ── Like ───────────────────────────────────────────────

@router.post("/{pin_id}/like")
def toggle_like(pin_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    pin = db.query(Pin).filter(Pin.id == pin_id).first()
    if not pin:
        raise HTTPException(status_code=404, detail="Pin not found")

    existing = db.query(PinLike).filter(PinLike.pin_id == pin_id, PinLike.user_id == user.id).first()
    if existing:
        db.delete(existing)
        db.commit()
        count = db.query(sa_func.count(PinLike.id)).filter(PinLike.pin_id == pin_id).scalar()
        return {"liked": False, "likes_count": count}
    else:
        db.add(PinLike(pin_id=pin_id, user_id=user.id))
        db.commit()
        count = db.query(sa_func.count(PinLike.id)).filter(PinLike.pin_id == pin_id).scalar()
        return {"liked": True, "likes_count": count}


# ── Save ───────────────────────────────────────────────

@router.post("/{pin_id}/save")
def toggle_save(pin_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    pin = db.query(Pin).filter(Pin.id == pin_id).first()
    if not pin:
        raise HTTPException(status_code=404, detail="Pin not found")

    existing = db.query(PinSave).filter(PinSave.pin_id == pin_id, PinSave.user_id == user.id).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {"saved": False}
    else:
        db.add(PinSave(pin_id=pin_id, user_id=user.id))
        db.commit()
        return {"saved": True}


# ── Report ─────────────────────────────────────────────

@router.post("/{pin_id}/report")
def report_pin(pin_id: UUID, body: ReportCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    pin = db.query(Pin).filter(Pin.id == pin_id).first()
    if not pin:
        raise HTTPException(status_code=404, detail="Pin not found")

    existing = db.query(PinReport).filter(PinReport.pin_id == pin_id, PinReport.user_id == user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already reported this pin")

    db.add(PinReport(pin_id=pin_id, user_id=user.id, reason=body.reason))
    db.commit()
    return {"reported": True}
