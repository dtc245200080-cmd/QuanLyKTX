from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Contract, Student, Bed, Room
from ..schemas import ContractCreate
from ..security import require_roles, current_user

router = APIRouter()

def room_for_student(db, student):
    if not student.current_bed_id:
        return None
    bed = db.get(Bed, student.current_bed_id)
    room = db.get(Room, bed.room_id) if bed else None
    return room.code if room else None

@router.get("")
def list_contracts(db: Session = Depends(get_db), user=Depends(require_roles("quanly", "ketoan"))):
    rows = db.scalars(select(Contract).order_by(Contract.start_date.desc(), Contract.id.desc())).all()
    return [{"id": x.id, "code": x.code, "student_id": x.student_id, "mssv": x.student.mssv,
             "student": x.student.full_name, "room_code": x.room_code,
             "start_date": x.start_date.isoformat(), "end_date": x.end_date.isoformat(),
             "status": x.status} for x in rows]

@router.post("")
def create_contract(data: ContractCreate, db: Session = Depends(get_db), user=Depends(require_roles("quanly"))):
    if data.end_date < data.start_date:
        raise HTTPException(400, "Ngày kết thúc phải sau ngày bắt đầu")
    student = db.get(Student, data.student_id)
    if not student:
        raise HTTPException(404, "Không tìm thấy sinh viên")
    room = room_for_student(db, student)
    if not room:
        raise HTTPException(400, "Sinh viên chưa được xếp phòng")
    active = db.scalar(select(Contract).where(Contract.student_id == student.id, Contract.status == "Đang hiệu lực"))
    if active:
        raise HTTPException(409, "Sinh viên đã có hợp đồng đang hiệu lực")
    code = f"HD{date.today().strftime('%Y%m%d')}-{student.mssv}"
    if db.scalar(select(Contract).where(Contract.code == code)):
        code = f"HD{student.id}-{date.today().strftime('%Y%m%d%H%M%S')}"
    c = Contract(code=code, student_id=student.id, room_code=room, start_date=data.start_date,
                 end_date=data.end_date, status="Đang hiệu lực")
    db.add(c); db.commit(); db.refresh(c)
    return {"id": c.id, "code": c.code, "status": c.status}

@router.get("/students")
def students_without_active_contract(db: Session = Depends(get_db), user=Depends(require_roles("quanly"))):
    students = db.scalars(select(Student).order_by(Student.full_name)).all()
    result=[]
    for s in students:
        active = db.scalar(select(Contract).where(Contract.student_id == s.id, Contract.status == "Đang hiệu lực"))
        room = room_for_student(db, s)
        if not active and room:
            result.append({"id": s.id, "mssv": s.mssv, "full_name": s.full_name, "room": room})
    return result
