from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Complaint, User
from ..schemas import ComplaintCreate, ComplaintStatusUpdate
from ..security import current_user, require_roles
from ..ai import generate
import secrets

router=APIRouter()

def make_code(db):
    while True:
        code=f"PA{secrets.randbelow(900000)+100000}"
        if not db.scalar(select(Complaint).where(Complaint.code==code)): return code

@router.post("")
def create(data:ComplaintCreate, db:Session=Depends(get_db), user:User=Depends(current_user)):
    if not user.student_id: raise HTTPException(400,"Tài khoản chưa liên kết sinh viên")
    c=Complaint(code=make_code(db),student_id=user.student_id,content=data.content.strip())
    db.add(c); db.commit(); db.refresh(c)
    return {"id":c.id,"code":c.code,"status":c.status}

@router.get("")
def list_all(db:Session=Depends(get_db), user=Depends(require_roles("quanly"))):
    rows=db.scalars(select(Complaint).order_by(Complaint.created_at.desc())).all()
    return [{"id":x.id,"code":x.code,"student":x.student.full_name,"mssv":x.student.mssv,
             "content":x.content,"category":x.category,"status":x.status,"ai_summary":x.ai_summary,
             "created_at":x.created_at.isoformat()} for x in rows]

@router.get("/my")
def my(db:Session=Depends(get_db), user:User=Depends(current_user)):
    if not user.student_id: raise HTTPException(400,"Tài khoản chưa liên kết sinh viên")
    rows=db.scalars(select(Complaint).where(Complaint.student_id==user.student_id).order_by(Complaint.created_at.desc())).all()
    return [{"id":x.id,"code":x.code,"content":x.content,"status":x.status,"created_at":x.created_at.isoformat()} for x in rows]

@router.post("/{complaint_id}/summarize")
def summarize(complaint_id:int, db:Session=Depends(get_db), user=Depends(require_roles("quanly"))):
    c=db.get(Complaint,complaint_id)
    if not c: raise HTTPException(404,"Không tìm thấy phản ánh")
    try:
        text=generate("Bạn là trợ lý quản lý KTX. Tóm tắt phản ánh bằng tiếng Việt, xác định nhóm sự cố và mức ưu tiên. Không bịa.",f"Phản ánh: {c.content}")
    except RuntimeError:
        text=f"{c.content[:180]}"
    c.ai_summary=text; db.commit()
    return {"summary":text}

@router.patch("/{complaint_id}/status")
def update_status(complaint_id:int, data:ComplaintStatusUpdate, db:Session=Depends(get_db), user=Depends(require_roles("quanly"))):
    c=db.get(Complaint,complaint_id)
    if not c: raise HTTPException(404,"Không tìm thấy phản ánh")
    c.status=data.status; db.commit()
    return {"id":c.id,"status":c.status}
