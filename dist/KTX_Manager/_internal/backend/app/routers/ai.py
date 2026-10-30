from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Room, Bed, StayRequest, Student
from ..security import current_user, require_roles
from ..schemas import ChatRequest, RoomSuggestionRequest, SummaryRequest
from ..rag import retrieve_policies, context_text
from ..ai import (
    generate,
    allocate_rooms_ai,
    classify_and_summarize_incident
)

router = APIRouter()

@router.post("/chat")
def chatbot(data: ChatRequest, db: Session = Depends(get_db), user: User = Depends(current_user)):
    policies = retrieve_policies(db, data.question, top_k=4)
    if not policies:
        return {"answer": "Tôi không tìm thấy nội quy liên quan trong kho nội quy được cung cấp.", "sources": []}
    context = context_text(policies)
    system = (
        "Bạn là trợ lý ký túc xá KTX-AI. CHỈ được trả lời dựa trên phần nội quy được cung cấp. "
        "Không tự tạo quy định. Nếu nội dung không đủ để trả lời, nói rõ không tìm thấy quy định phù hợp. "
        "Trả lời ngắn gọn, dễ hiểu bằng tiếng Việt."
    )
    try:
        answer = generate(system, f"Nội quy liên quan:\n{context}\n\nCâu hỏi: {data.question}")
    except RuntimeError:
        answer = "Theo nội quy liên quan: " + policies[0].content
    return {"answer": answer, "sources": [{"code": p.code, "title": p.title} for p in policies]}

# ==============================================================================
# TÍNH NĂNG 1: AI GỢI Ý XẾP PHÒNG TỰ ĐỘNG (THEO 3 NGUYÊN TẮC ƯU TIÊN)
# ==============================================================================
@router.post("/auto-allocate")
def auto_allocate(
    data: dict = None,
    db: Session = Depends(get_db),
    user = Depends(require_roles("quanly"))
):
    """Phân bổ chỗ ở tự động dựa trên 3 nguyên tắc ưu tiên:
    1. Tuyệt đối đúng giới tính (Nam - phòng Nam, Nữ - phòng Nữ)
    2. Cùng ngành/khóa
    3. Thỏa mãn nguyện vọng loại phòng
    """
    data = data or {}
    students = data.get("students")
    beds = data.get("beds")

    # Nếu không truyền dữ liệu tùy chỉnh, tự động lấy dữ liệu thực tế từ Database
    if not students:
        pending_stays = db.scalars(
            select(StayRequest)
            .where(StayRequest.status == "Chờ duyệt")
            .order_by(StayRequest.created_at.asc())
        ).all()

        students = []
        for s in pending_stays:
            st = s.student
            # Nhận diện giới tính từ tên hoặc lớp nếu không có cột riêng
            full_lower = st.full_name.lower()
            is_female = any(w in full_lower.split() for w in ["thị", "hoa", "lan", "hương", "mai", "ngọc", "nga", "trang", "linh", "nhung", "yến"])
            gender = "Nữ" if is_female else "Nam"
            
            students.append({
                "mssv": st.mssv,
                "ho_ten": st.full_name,
                "gioi_tinh": gender,
                "khoa_nganh": st.class_name or "Chưa rõ",
                "nguyen_vong": s.desired_room or "Phòng tiêu chuẩn"
            })

    if not beds:
        empty_beds = db.scalars(
            select(Bed)
            .join(Bed.room)
            .where(Bed.status == "Trống")
            .order_by(Room.code, Bed.bed_no)
        ).all()

        beds = []
        for b in empty_beds:
            r = b.room
            beds.append({
                "ma_giuong": f"{r.code}-G{b.bed_no}",
                "ma_phong": r.code,
                "toa_nha": r.building.name if r.building else "KTX",
                "gioi_tinh": r.gender,
                "loai_phong": f"Phòng {r.capacity} người",
                "suc_chua": r.capacity
            })

    result = allocate_rooms_ai(students, beds)
    return result

@router.post("/room-suggestion")
def room_suggestion(
    data: RoomSuggestionRequest, 
    db: Session = Depends(get_db), 
    user = Depends(require_roles("quanly"))
):
    from .rooms import suggest_room
    candidates = suggest_room(data, db)
    if not candidates:
        return {"suggestions": [], "explanation": "Không có phòng phù hợp."}
    top = candidates[:3]
    prompt = f"Danh sách phòng có thể xếp: {top}. Tiêu chí: {data.criteria}. Hãy giải thích ngắn gọn vì sao phòng đầu tiên phù hợp."
    try:
        explanation = generate("Bạn là trợ lý xếp phòng KTX. Chỉ giải thích từ dữ liệu được cung cấp.", prompt)
    except RuntimeError:
        explanation = f"Phòng {top[0]['room']} có {top[0]['available']} chỗ trống và phù hợp tiêu chí."
    return {"suggestions": top, "explanation": explanation}

# ==============================================================================
# TÍNH NĂNG 2: PHÂN LOẠI & TÓM TẮT SỰ CỐ
# ==============================================================================
@router.post("/classify-incident")
def classify_incident(
    data: dict,
    user = Depends(current_user)
):
    """Phân loại sự cố vào 5 nhóm cố định và tóm tắt <= 15 từ nêu rõ bản chất + vị trí."""
    content = str(data.get("content", "")).strip()
    if not content:
        raise HTTPException(400, "Nội dung phản ánh không được để trống")
    return classify_and_summarize_incident(content)

@router.post("/summarize")
def summarize(data: SummaryRequest, user = Depends(require_roles("quanly"))):
    res = classify_and_summarize_incident(data.content)
    return {"summary": res.get("tom_tat", ""), "details": res}
