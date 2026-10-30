from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Student, User, Bed, Room
from ..security import current_user, require_roles, hash_password
from ..schemas import StudentCreate

router = APIRouter()

def student_room(db, student):
    if not student.current_bed_id:
        return None
    bed = db.get(Bed, student.current_bed_id)
    if not bed:
        return None
    room = db.get(Room, bed.room_id)
    return room.code if room else None

@router.get("")
def list_students(db: Session = Depends(get_db), user=Depends(require_roles("quanly", "ketoan"))):
    students = db.scalars(select(Student).order_by(Student.id.desc())).all()
    return [{
        "id": s.id, "mssv": s.mssv, "full_name": s.full_name,
        "class_name": s.class_name, "phone": s.phone, "status": s.status,
        "room": student_room(db, s)
    } for s in students]

@router.post("")
def create_student(data: StudentCreate, db: Session = Depends(get_db), user=Depends(require_roles("quanly"))):
    mssv = data.mssv.strip()
    if db.scalar(select(Student).where(Student.mssv == mssv)):
        raise HTTPException(409, "MSSV đã tồn tại")
    if db.scalar(select(User).where(User.username == mssv)):
        raise HTTPException(409, "Tài khoản sinh viên đã tồn tại")
    student = Student(mssv=mssv, full_name=data.full_name.strip(), class_name=data.class_name.strip(),
                      phone=data.phone.strip(), status="Chưa xếp phòng")
    db.add(student)
    db.flush()
    account = User(username=mssv, password_hash=hash_password(data.password or "123456"),
                   role="sinhvien", full_name=student.full_name, student_id=student.id)
    db.add(account)
    db.commit()
    db.refresh(student)
    return {"id": student.id, "mssv": student.mssv, "full_name": student.full_name,
            "class_name": student.class_name, "phone": student.phone, "status": student.status,
            "username": account.username, "password": data.password or "123456"}

@router.get("/me")
def my_student(db: Session = Depends(get_db), user: User = Depends(current_user)):
    if not user.student_id:
        return {"student": None}
    s = db.get(Student, user.student_id)
    if not s:
        return {"student": None}
    return {"id": s.id, "mssv": s.mssv, "full_name": s.full_name,
            "class_name": s.class_name, "phone": s.phone, "status": s.status,
            "room": student_room(db, s)}
