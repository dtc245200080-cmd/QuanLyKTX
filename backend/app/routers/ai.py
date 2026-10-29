
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Room, Bed
from ..security import current_user, require_roles
from ..schemas import ChatRequest, RoomSuggestionRequest, SummaryRequest
from ..rag import retrieve_policies, context_text
from ..ai import generate

router=APIRouter()

@router.post("/chat")
def chatbot(data:ChatRequest, db:Session=Depends(get_db), user:User=Depends(current_user)):
    policies=retrieve_policies(db,data.question,top_k=4)
    if not policies:
        return {"answer":"Tôi không tìm thấy nội quy liên quan trong kho nội quy được cung cấp.","sources":[]}
    context=context_text(policies)
    system=("Bạn là trợ lý ký túc xá KTX-AI. CHỈ được trả lời dựa trên phần nội quy được cung cấp. "
            "Không tự tạo quy định. Nếu nội dung không đủ để trả lời, nói rõ không tìm thấy quy định phù hợp. "
            "Trả lời ngắn gọn, dễ hiểu bằng tiếng Việt.")
    try:
        answer=generate(system, f"Nội quy liên quan:\n{context}\n\nCâu hỏi: {data.question}")
    except RuntimeError:
        answer="Theo nội quy liên quan: " + policies[0].content
    return {"answer":answer,"sources":[{"code":p.code,"title":p.title} for p in policies]}

@router.post("/room-suggestion")
def room_suggestion(
    data:RoomSuggestionRequest, 
    db:Session=Depends(get_db), 
    user=Depends(require_roles("quanly"))):
    from .rooms import suggest_room
    candidates=suggest_room(data,db)
    if not candidates: return {"suggestions":[],"explanation":"Không có phòng phù hợp."}
    top=candidates[:3]
    prompt=f"Danh sách phòng có thể xếp: {top}. Tiêu chí: {data.criteria}. Hãy giải thích ngắn gọn vì sao phòng đầu tiên phù hợp."
    try: explanation=generate("Bạn là trợ lý xếp phòng KTX. Chỉ giải thích từ dữ liệu được cung cấp.",prompt)
    except RuntimeError: explanation=f"Phòng {top[0]['room']} có {top[0]['available']} chỗ trống và phù hợp tiêu chí."
    return {"suggestions":top,"explanation":explanation}

@router.post("/summarize")
def summarize(data:SummaryRequest, user=Depends(require_roles("quanly"))):
    try:
        result=generate("Bạn là trợ lý KTX. Tóm tắt phản ánh bằng tiếng Việt, giữ nguyên sự kiện, nêu vấn đề chính và mức ưu tiên. Không bịa.",
                          data.content)
    except RuntimeError:
        result=f"Tóm tắt mô phỏng: {data.content[:200]}"
    return {"summary":result}
