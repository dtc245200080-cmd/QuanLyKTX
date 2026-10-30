from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Policy
from ..schemas import PolicyCreate, PolicyUpdate
from ..security import require_roles

router=APIRouter()

@router.get("")
def list_policies(db:Session=Depends(get_db), user=Depends(require_roles("quanly"))):
    rows=db.scalars(select(Policy).order_by(Policy.code)).all()
    return [{"id":p.id,"code":p.code,"title":p.title,"content":p.content,"active":p.active} for p in rows]

@router.post("")
def create_policy(data:PolicyCreate, db:Session=Depends(get_db), user=Depends(require_roles("quanly"))):
    code=data.code.strip()
    if db.scalar(select(Policy).where(Policy.code==code)): raise HTTPException(409,"Mã nội quy đã tồn tại")
    p=Policy(code=code,title=data.title.strip(),content=data.content.strip(),active=True)
    db.add(p); db.commit(); db.refresh(p)
    return {"id":p.id,"code":p.code,"title":p.title}

@router.patch("/{policy_id}")
def update_policy(policy_id:int,data:PolicyUpdate,db:Session=Depends(get_db),user=Depends(require_roles("quanly"))):
    p=db.get(Policy,policy_id)
    if not p: raise HTTPException(404,"Không tìm thấy nội quy")
    p.title=data.title.strip(); p.content=data.content.strip(); p.active=data.active
    db.commit(); return {"id":p.id,"status":"Đã cập nhật"}

@router.delete("/{policy_id}")
def delete_policy(policy_id:int,db:Session=Depends(get_db),user=Depends(require_roles("quanly"))):
    p=db.get(Policy,policy_id)
    if not p: raise HTTPException(404,"Không tìm thấy nội quy")
    db.delete(p); db.commit(); return {"id":policy_id,"status":"Đã xóa"}
