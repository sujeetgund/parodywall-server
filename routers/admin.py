from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from uuid import UUID

from database import get_db
from models import Pin, User, Admin, PinLike, PinSave, PinReport
from dependencies import get_current_admin

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    total_users = db.query(func.count(User.id)).scalar()
    total_pins = db.query(func.count(Pin.id)).scalar()
    
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    pins_today = db.query(func.count(Pin.id)).filter(Pin.created_at >= today_start).scalar()
    
    return {
        "total_users": total_users,
        "total_pins": total_pins,
        "pins_today": pins_today
    }

@router.get("/users")
def get_users(db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    users = db.query(
        User,
        func.count(Pin.id).label("pins_count")
    ).outerjoin(Pin, Pin.user_id == User.id).group_by(User.id).order_by(User.created_at.desc()).all()
    
    result = []
    for u, count in users:
        result.append({
            "id": u.id,
            "email": u.email,
            "alias": u.alias,
            "is_superuser": u.is_superuser,
            "created_at": u.created_at,
            "pins_count": count
        })
    return result

@router.delete("/users/{user_id}")
def delete_user(user_id: UUID, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"success": True}

@router.get("/pins")
def get_pins(db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    pins = db.query(Pin, User).join(User, Pin.user_id == User.id).order_by(Pin.created_at.desc()).all()
    result = []
    for p, u in pins:
        result.append({
            "id": p.id,
            "title": p.text_content if p.text_content else (f"{p.type.capitalize()} Pin"),
            "image": p.image_url,
            "type": p.type,
            "created_at": p.created_at,
            "author_alias": u.alias,
            "author_id": u.id
        })
    return result

@router.delete("/pins/{pin_id}")
def delete_pin(pin_id: UUID, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    pin = db.query(Pin).filter(Pin.id == pin_id).first()
    if not pin:
        raise HTTPException(status_code=404, detail="Pin not found")
    db.delete(pin)
    db.commit()
    return {"success": True}

@router.get("/reports")
def get_reports(db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    # Group reports by pin_id and join with Pin and User
    # to get pin details and report count.
    reports = db.query(
        Pin,
        User,
        func.count(PinReport.id).label("report_count")
    ).join(PinReport, Pin.id == PinReport.pin_id)\
     .join(User, Pin.user_id == User.id)\
     .group_by(Pin.id, User.id)\
     .order_by(func.count(PinReport.id).desc()).all()
    
    result = []
    for p, u, count in reports:
        result.append({
            "id": p.id,
            "title": p.text_content if p.text_content else (f"{p.type.capitalize()} Pin"),
            "image": p.image_url,
            "type": p.type,
            "created_at": p.created_at,
            "author_alias": u.alias,
            "author_id": u.id,
            "report_count": count
        })
    return result

@router.delete("/reports/{pin_id}/dismiss")
def dismiss_pin_reports(pin_id: UUID, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    db.query(PinReport).filter(PinReport.pin_id == pin_id).delete()
    db.commit()
    return {"success": True}
