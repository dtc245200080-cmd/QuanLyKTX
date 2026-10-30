from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Fee, User, Student, Bed, Room
from ..schemas import FeeCreate
from ..security import current_user, require_roles

router=APIRouter()

def room_for_student(db, student):
    if not student.current_bed_id: return None
    bed=db.get(Bed, student.current_bed_id)
    room=db.get(Room, bed.room_id) if bed else None
    return room.code if room else None

@router.get("/fees")
def fees(db:Session=Depends(get_db), user=Depends(current_user)):
    rows=db.scalars(select(Fee).order_by(Fee.month.desc(), Fee.id.desc())).all()
    if user.role=="sinhvien": rows=[x for x in rows if x.student_id==user.student_id]
    return [{"id":x.id,"student":x.student.full_name,"mssv":x.student.mssv,"room":room_for_student(db,x.student),
             "month":x.month,"amount":x.amount,"due_date":x.due_date.isoformat(),"status":x.status} for x in rows]

@router.post("/fees")
def create_fee(data: FeeCreate, db:Session=Depends(get_db), user=Depends(require_roles("quanly","ketoan"))):
    student=db.get(Student,data.student_id)
    if not student: raise HTTPException(404,"Không tìm thấy sinh viên")
    old=db.scalar(select(Fee).where(Fee.student_id==data.student_id, Fee.month==data.month))
    if old: raise HTTPException(409,"Sinh viên đã có khoản thu cho tháng này")
    f=Fee(student_id=data.student_id,month=data.month,amount=data.amount,due_date=data.due_date,status="Chưa thu")
    db.add(f); db.commit(); db.refresh(f)
    return {"id":f.id,"status":f.status}

@router.patch("/fees/{fee_id}/pay")
def pay_fee(fee_id:int, db:Session=Depends(get_db), user=Depends(require_roles("ketoan","quanly"))):
    f=db.get(Fee,fee_id)
    if not f: raise HTTPException(404,"Không tìm thấy khoản thu")
    f.status="Đã thu"; db.commit()
    return {"id":f.id,"status":f.status}

@router.get("/summary")
def summary(db:Session=Depends(get_db), user=Depends(require_roles("quanly","ketoan"))):
    rows=db.scalars(select(Fee)).all()
    total=sum(x.amount for x in rows); collected=sum(x.amount for x in rows if x.status=="Đã thu")
    return {"total":total,"collected":collected,"debt":total-collected,"collection_rate":round(collected/total*100,2) if total else 0}
