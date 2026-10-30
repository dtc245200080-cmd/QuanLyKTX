from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import StayRequest, Student, User, Room, Bed
from ..schemas import StayRequestCreate
from ..security import current_user, require_roles

router = APIRouter()


# =========================================================
# SINH VIÊN GỬI YÊU CẦU
# =========================================================
@router.post("")
def create_stay(
    data: StayRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user)
):
    if not user.student_id:
        raise HTTPException(
            status_code=400,
            detail="Tài khoản chưa liên kết sinh viên"
        )

    s = StayRequest(
        student_id=user.student_id,
        request_type=data.request_type,
        desired_room=data.desired_room,
        current_room=data.current_room,
        note=data.note
    )

    db.add(s)
    db.commit()
    db.refresh(s)

    return {
        "id": s.id,
        "status": s.status
    }


# =========================================================
# QUẢN LÝ XEM TẤT CẢ YÊU CẦU
# =========================================================
@router.get("")
def list_stays(
    db: Session = Depends(get_db),
    user=Depends(require_roles("quanly"))
):
    rows = db.scalars(
        select(StayRequest)
        .order_by(StayRequest.created_at.desc())
    ).all()

    return [
        {
            "id": x.id,
            "student": x.student.full_name,
            "mssv": x.student.mssv,
            "request_type": x.request_type,
            "desired_room": x.desired_room,
            "current_room": x.current_room,
            "note": x.note,
            "status": x.status,
            "created_at": x.created_at.isoformat()
        }
        for x in rows
    ]


# =========================================================
# SINH VIÊN XEM YÊU CẦU CỦA MÌNH
# =========================================================
@router.get("/my")
def my_stays(
    db: Session = Depends(get_db),
    user: User = Depends(current_user)
):
    if not user.student_id:
        raise HTTPException(
            status_code=400,
            detail="Tài khoản chưa liên kết sinh viên"
        )

    rows = db.scalars(
        select(StayRequest)
        .where(StayRequest.student_id == user.student_id)
        .order_by(StayRequest.created_at.desc())
    ).all()

    return [
        {
            "id": x.id,
            "request_type": x.request_type,
            "desired_room": x.desired_room,
            "current_room": x.current_room,
            "note": x.note,
            "status": x.status,
            "created_at": x.created_at.isoformat()
        }
        for x in rows
    ]


# =========================================================
# SINH VIÊN XEM PHÒNG HIỆN TẠI
# =========================================================
@router.get("/my-room")
def my_room(
    db: Session = Depends(get_db),
    user: User = Depends(current_user)
):
    if not user.student_id:
        raise HTTPException(
            status_code=400,
            detail="Tài khoản chưa liên kết sinh viên"
        )

    student = db.get(Student, user.student_id)

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy sinh viên"
        )

    # Chưa có giường
    if not student.current_bed_id:
        return {
            "room": None,
            "bed": None,
            "message": "Chưa có phòng"
        }

    bed = db.get(Bed, student.current_bed_id)

    if not bed:
        return {
            "room": None,
            "bed": None,
            "message": "Chưa có phòng"
        }

    room = db.get(Room, bed.room_id)

    if not room:
        return {
            "room": None,
            "bed": None,
            "message": "Chưa có phòng"
        }

    return {
        "room": room.code,
        "bed": bed.bed_no,
        "building": room.building.code if room.building else None,
        "capacity": room.capacity
    }


# =========================================================
# QUẢN LÝ DUYỆT / TỪ CHỐI
# =========================================================
@router.patch("/{request_id}/{action}")
def process(
    request_id: int,
    action: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles("quanly"))
):
    x = db.get(StayRequest, request_id)

    if not x:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy yêu cầu"
        )

    if action not in ("approve", "reject"):
        raise HTTPException(
            status_code=400,
            detail="Action không hợp lệ"
        )

    # Không cho duyệt lại
    if x.status != "Chờ duyệt":
        raise HTTPException(
            status_code=400,
            detail=f"Yêu cầu hiện đang ở trạng thái: {x.status}"
        )

    # =====================================================
    # TỪ CHỐI
    # =====================================================
    if action == "reject":
        x.status = "Từ chối"
        db.commit()

        return {
            "id": x.id,
            "status": x.status
        }

    # =====================================================
    # DUYỆT CHUYỂN PHÒNG
    # =====================================================
    student = db.get(Student, x.student_id)

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy sinh viên"
        )

    # -----------------------------------------------------
    # TRẢ PHÒNG
    # -----------------------------------------------------
    if x.request_type == "Trả phòng":

        if student.current_bed_id:
            old_bed = db.get(Bed, student.current_bed_id)

            if old_bed:
                old_bed.status = "Trống"

        student.current_bed_id = None
        student.status = "Đã trả phòng"

    # -----------------------------------------------------
    # ĐĂNG KÝ Ở / CHUYỂN PHÒNG
    # -----------------------------------------------------
    elif x.request_type in ("Đăng ký ở", "Chuyển phòng"):

        if not x.desired_room:
            raise HTTPException(
                status_code=400,
                detail="Chưa có phòng mong muốn"
            )

        # Tìm phòng mới
        new_room = db.scalar(
            select(Room)
            .where(Room.code == x.desired_room)
        )

        if not new_room:
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy phòng {x.desired_room}"
            )

        # Tìm giường trống
        new_bed = db.scalar(
            select(Bed)
            .where(
                Bed.room_id == new_room.id,
                Bed.status == "Trống"
            )
            .order_by(Bed.bed_no)
        )

        if not new_bed:
            raise HTTPException(
                status_code=400,
                detail=f"Phòng {x.desired_room} hiện không còn giường trống"
            )

        # -----------------------------------------------
        # Giải phóng giường cũ
        # -----------------------------------------------
        if student.current_bed_id:

            old_bed = db.get(
                Bed,
                student.current_bed_id
            )

            if old_bed:
                old_bed.status = "Trống"

        # -----------------------------------------------
        # Gán giường mới
        # -----------------------------------------------
        new_bed.status = "Đang ở"

        student.current_bed_id = new_bed.id
        student.status = "Đang ở"

        # Cập nhật phòng hiện tại của yêu cầu
        x.current_room = new_room.code

    # -----------------------------------------------------
    # Không xác định loại yêu cầu
    # -----------------------------------------------------
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Loại yêu cầu không được hỗ trợ: {x.request_type}"
        )

    # Đánh dấu đã duyệt
    x.status = "Đã duyệt"

    db.commit()
    db.refresh(x)

    return {
        "id": x.id,
        "status": x.status,
        "message": "Đã duyệt và cập nhật phòng cho sinh viên"
    }