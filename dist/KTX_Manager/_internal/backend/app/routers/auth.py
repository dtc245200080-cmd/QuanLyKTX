
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import LoginRequest, LoginResponse
from ..security import verify_password, create_access_token, current_user

router=APIRouter()

@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session=Depends(get_db)):
    user=db.scalar(select(User).where(User.username==data.username))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Tài khoản hoặc mật khẩu không đúng")
    return LoginResponse(access_token=create_access_token(user), role=user.role, full_name=user.full_name)

@router.get("/me")
def me(user: User=Depends(current_user)):
    return {"id":user.id,"username":user.username,"role":user.role,"full_name":user.full_name,"student_id":user.student_id}
