from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Student, Room, Bed, Fee, Complaint, Contract, StayRequest
from ..security import require_roles

router=APIRouter()

@router.get("")
def statistics(db:Session=Depends(get_db), user=Depends(require_roles("quanly","ketoan"))):
    students=db.scalars(select(Student)).all()
    rooms=db.scalars(select(Room)).all()
    beds=db.scalars(select(Bed)).all()
    fees=db.scalars(select(Fee)).all()
    complaints=db.scalars(select(Complaint)).all()
    contracts=db.scalars(select(Contract)).all()
    pending=db.scalars(select(StayRequest).where(StayRequest.status=="Chờ duyệt")).all()
    occupied=sum(1 for b in beds if b.status=="Đang ở")
    capacity=sum(r.capacity for r in rooms)
    total=sum(f.amount for f in fees)
    collected=sum(f.amount for f in fees if f.status=="Đã thu")
    return {
        "students":len(students), "rooms":len(rooms), "capacity":capacity,
        "occupied":occupied, "available":max(0,capacity-occupied),
        "occupancy_rate":round(occupied/capacity*100,2) if capacity else 0,
        "fees_total":total, "fees_collected":collected, "fees_debt":total-collected,
        "collection_rate":round(collected/total*100,2) if total else 0,
        "complaints_total":len(complaints),
        "complaints_open":sum(1 for c in complaints if c.status!="Đã xử lý"),
        "complaints_done":sum(1 for c in complaints if c.status=="Đã xử lý"),
        "contracts_active":sum(1 for c in contracts if c.status=="Đang hiệu lực"),
        "pending_stays":len(pending)
    }
