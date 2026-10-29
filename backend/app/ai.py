import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from openai import OpenAI

from .database import get_db
from .security import require_roles
from .schemas import RoomSuggestionRequest



router = APIRouter()


MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def get_client():
    key = os.getenv("OPENAI_API_KEY")

    if not key:
        return None

    return OpenAI(api_key=key)


def generate(system: str, user: str) -> str:
    client = get_client()

    if not client:
        raise RuntimeError(
            "OPENAI_API_KEY chưa được cấu hình."
        )

    response = client.responses.create(
        model=MODEL,
        instructions=system,
        input=user,
    )

    return response.output_text.strip()


# =========================
# AI GỢI Ý XẾP PHÒNG
# =========================

@router.post("/room-suggestion")
def room_suggestion(
    data: RoomSuggestionRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("quanly"))
):
    candidates = suggest_room(data, db)

    if not candidates:
        return {
            "suggestions": [],
            "explanation": "Không có phòng phù hợp."
        }

    top = candidates[:3]

    prompt = f"""
Danh sách phòng có thể xếp:

{top}

Tiêu chí:
{data.criteria}

Hãy giải thích ngắn gọn vì sao phòng đầu tiên phù hợp.
Chỉ sử dụng dữ liệu được cung cấp.
"""

    try:
        explanation = generate(
            "Bạn là trợ lý xếp phòng KTX.",
            prompt
        )
    except RuntimeError:
        explanation = (
            f"Phòng {top[0]['room']} có "
            f"{top[0]['available']} chỗ trống "
            f"và phù hợp tiêu chí."
        )

    return {
        "suggestions": top,
        "explanation": explanation
    }


# =========================
# AI TÓM TẮT PHẢN ÁNH
# =========================

@router.post("/summarize")
def summarize_report(
    data: dict,
    db: Session = Depends(get_db),
    user=Depends(require_roles("quanly"))
):
    content = str(data.get("content", "")).strip()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Nội dung phản ánh không được để trống."
        )

    prompt = f"""
Nội dung phản ánh:

{content}

Hãy:
1. Tóm tắt ngắn gọn.
2. Xác định nhóm vấn đề.
3. Nêu vấn đề chính cần xử lý.

Không tự thêm thông tin.
Trả lời bằng tiếng Việt.
"""

    try:
        summary = generate(
            """
Bạn là trợ lý AI hỗ trợ quản lý
ký túc xá.

Hãy tóm tắt phản ánh của sinh viên
một cách chính xác và ngắn gọn.
""",
            prompt
        )

    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    return {
        "summary": summary
    }