from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Room, Bed, Building
from ..security import current_user, require_roles
from ..schemas import RoomSuggestionRequest, BuildingCreate, RoomCreate

router = APIRouter()

@router.get("/buildings")
def list_buildings(db: Session = Depends(get_db), user=Depends(current_user)):
    buildings = db.scalars(select(Building).order_by(Building.code)).all()
    return [{"id": b.id, "code": b.code, "name": b.name, "floors": b.floors, "room_count": len(b.rooms)} for b in buildings]

@router.get("")
def list_rooms(db: Session = Depends(get_db), user=Depends(current_user)):
    rooms = db.scalars(select(Room).order_by(Room.code)).all()
    return [{
        "id": r.id,
        "code": r.code,
        "building": r.building.code,
        "capacity": r.capacity,
        "floor": r.floor,
        "occupied": sum(1 for b in r.beds if b.status != "Trống"),
        "available": sum(1 for b in r.beds if b.status == "Trống"),
        "status": r.status,
    } for r in rooms]

@router.post("/buildings")
def create_building(data: BuildingCreate, db: Session = Depends(get_db), user=Depends(require_roles("quanly"))):
    if db.scalar(select(Building).where(Building.code == data.code.strip())):
        raise HTTPException(409, "Mã tòa đã tồn tại")
    b = Building(code=data.code.strip(), name=data.name.strip(), floors=data.floors)
    db.add(b)
    db.commit()
    db.refresh(b)
    return {"id": b.id, "code": b.code, "name": b.name, "floors": b.floors}

@router.post("")
def create_room(data: RoomCreate, db: Session = Depends(get_db), user=Depends(require_roles("quanly"))):
    if db.scalar(select(Room).where(Room.code == data.code.strip())):
        raise HTTPException(409, "Mã phòng đã tồn tại")
    building = db.scalar(select(Building).where(Building.code == data.building_code.strip()))
    if not building:
        raise HTTPException(404, f"Không tìm thấy tòa {data.building_code}")
    if data.floor > building.floors:
        raise HTTPException(400, "Tầng phòng vượt quá số tầng của tòa")
    room = Room(code=data.code.strip(), building_id=building.id, capacity=data.capacity,
                floor=data.floor, gender=data.gender, status="Hoạt động")
    db.add(room)
    db.flush()
    for bed_no in range(1, data.capacity + 1):
        db.add(Bed(room_id=room.id, bed_no=bed_no, status="Trống"))
    db.commit()
    db.refresh(room)
    return {"id": room.id, "code": room.code, "building": building.code,
            "capacity": room.capacity, "floor": room.floor, "available": room.capacity}

@router.post("/suggest")
def suggest_room(data: RoomSuggestionRequest, db: Session = Depends(get_db), user=Depends(require_roles("quanly"))):
    rooms = db.scalars(select(Room)).all()
    candidates = []
    for r in rooms:
        available = sum(1 for b in r.beds if b.status == "Trống")
        if available <= 0: continue
        if data.building and data.building != "Tất cả" and r.building.code != data.building: continue
        if data.capacity and r.capacity != data.capacity: continue
        score = available
        if "gần" in data.criteria.lower(): score += 0.2
        candidates.append((score, r, available))
    candidates.sort(key=lambda x: (x[0], x[2]), reverse=True)
    return [{"room": r.code, "building": r.building.code, "capacity": r.capacity,
             "available": a, "score": round(sc, 2)} for sc, r, a in candidates[:5]]
