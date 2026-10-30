from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Complaint, User
from ..schemas import ComplaintCreate, ComplaintStatusUpdate
from ..security import current_user, require_roles
from ..ai import classify_and_summarize_incident
import secrets

router = APIRouter()

def make_code(db):
    while True:
        code = f"PA{secrets.randbelow(900000)+100000}"
        if not db.scalar(select(Complaint).where(Complaint.code == code)):
            return code

@router.post("")
def create(data: ComplaintCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    if not user.student_id:
        raise HTTPException(400, "Tài khoản chưa liên kết sinh viên")
    content = data.content.strip()
    
    # Tự động phân loại và tóm tắt sự cố bằng AI ngay khi gửi
    ai_res = classify_and_summarize_incident(content)
    category = ai_res.get("nhom_su_co", "Khác")
    ai_summary = ai_res.get("tom_tat", "")
    
    c = Complaint(
        code=make_code(db),
        student_id=user.student_id,
        content=content,
        category=category,
        ai_summary=ai_summary
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return {
        "id": c.id,
        "code": c.code,
        "status": c.status,
        "category": c.category,
        "ai_summary": c.ai_summary
    }

@router.get("")
def list_all(db: Session = Depends(get_db), user=Depends(require_roles("quanly"))):
    rows = db.scalars(select(Complaint).order_by(Complaint.created_at.desc())).all()
    return [
        {
            "id": x.id,
            "code": x.code,
            "student": x.student.full_name,
            "mssv": x.student.mssv,
            "content": x.content,
            "category": x.category or "Chưa phân loại",
            "status": x.status,
            "ai_summary": x.ai_summary or "",
            "created_at": x.created_at.isoformat()
        }
        for x in rows
    ]

@router.get("/my")
def my(db: Session = Depends(get_db), user: User = Depends(current_user)):
    if not user.student_id:
        raise HTTPException(400, "Tài khoản chưa liên kết sinh viên")
    rows = db.scalars(select(Complaint).where(Complaint.student_id == user.student_id).order_by(Complaint.created_at.desc())).all()
    return [
        {
            "id": x.id,
            "code": x.code,
            "content": x.content,
            "category": x.category,
            "ai_summary": x.ai_summary,
            "status": x.status,
            "created_at": x.created_at.isoformat()
        }
        for x in rows
    ]

@router.post("/{complaint_id}/summarize")
def summarize(complaint_id: int, db: Session = Depends(get_db), user=Depends(require_roles("quanly"))):
    c = db.get(Complaint, complaint_id)
    if not c:
        raise HTTPException(404, "Không tìm thấy phản ánh")
    
    # Gọi AI Phân loại & Tóm tắt sự cố (chuẩn hóa nhóm cố định & <15 từ)
    res = classify_and_summarize_incident(c.content)
    c.category = res.get("nhom_su_co", c.category or "Khác")
    c.ai_summary = res.get("tom_tat", "")
    db.commit()
    
    return {
        "id": c.id,
        "category": c.category,
        "summary": c.ai_summary,
        "details": res
    }

@router.patch("/{complaint_id}/status")
def update_status(complaint_id: int, data: ComplaintStatusUpdate, db: Session = Depends(get_db), user=Depends(require_roles("quanly"))):
    c = db.get(Complaint, complaint_id)
    if not c:
        raise HTTPException(404, "Không tìm thấy phản ánh")
    c.status = data.status
    db.commit()
    return {"id": c.id, "status": c.status}
