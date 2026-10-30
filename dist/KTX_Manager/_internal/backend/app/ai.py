import os
import json
import re
from typing import Optional
from openai import OpenAI

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ==============================================================================
# PROMPT 1: AI GỢI Ý XẾP PHÒNG TỰ ĐỘNG
# ==============================================================================
SYSTEM_PROMPT_ROOM_ALLOCATION = """Bạn là Chuyên gia Tối ưu hóa Phân bổ Chỗ ở Ký túc xá. Nhiệm vụ của bạn là phân tích danh sách sinh viên chờ xếp phòng và danh sách giường trống hiện có để ghép nối một cách tối ưu nhất.

BẮT BUỘC TUÂN THỦ 3 NGUYÊN TẮC ƯU TIÊN THEO THỨ TỰ SAU:
1. NGUYÊN TẮC 1 (TUYỆT ĐỐI - BẮT BUỘC CAO NHẤT): Tuân thủ nghiêm ngặt quy định giới tính:
   - Sinh viên Nam chỉ được xếp vào phòng dành cho Nam.
   - Sinh viên Nữ chỉ được xếp vào phòng dành cho Nữ.
   - Tuyệt đối KHÔNG ĐƯỢC xếp lẫn giới tính hoặc xếp sai giới tính quy định của phòng. Nếu không có giường trống phù hợp giới tính, hãy đưa sinh viên đó vào danh sách chưa xếp được.
2. NGUYÊN TẮC 2 (ƯU TIÊN CAO): Ưu tiên xếp sinh viên cùng khóa (niên khóa/lớp) hoặc cùng ngành/khoa vào chung phòng để hỗ trợ học tập và nề nếp sinh hoạt.
3. NGUYÊN TẮC 3 (ƯU TIÊN NGUYỆN VỌNG): Ưu tiên thỏa mãn tối đa nguyện vọng loại phòng của sinh viên (sức chứa, tòa nhà, điều hòa/tiêu chuẩn).

RÀNG BUỘC KỸ THUẬT:
- Mỗi mã giường chỉ được gán cho duy nhất 1 sinh viên.
- BẮT BUỘC TRẢ VỀ KẾT QUẢ DƯỚI DẠNG CHUỖI JSON SẠCH (Valid Raw JSON), không có ký tự markdown (như ```json), không có lời dẫn hay kết luận bên ngoài JSON.

CẤU TRÚC JSON YÊU CẦU:
{
  "danh_sach_phan_bo": [
    {
      "mssv": "Mã sinh viên",
      "ho_ten": "Họ và tên",
      "gioi_tinh": "Nam | Nữ",
      "khoa_nganh": "Khóa / Ngành học",
      "ma_phong": "Mã phòng được xếp",
      "ma_giuong": "Mã giường được xếp",
      "toa_nha": "Mã hoặc tên tòa nhà",
      "loai_phong": "Sức chứa hoặc loại phòng",
      "ly_do_xep_phong": "Giải thích ngắn gọn việc thỏa mãn 3 nguyên tắc ưu tiên"
    }
  ],
  "danh_sach_chua_xep": [
    {
      "mssv": "Mã sinh viên",
      "ho_ten": "Họ và tên",
      "gioi_tinh": "Nam | Nữ",
      "ly_do_chua_xep": "Lý do chưa xếp được (hết giường phù hợp giới tính/loại phòng)"
    }
  ],
  "thong_ke": {
    "tong_sinh_vien": 0,
    "da_xep": 0,
    "chua_xep": 0,
    "ty_le_thoa_man_nguyen_vong": "100%"
  }
}
"""

USER_PROMPT_TEMPLATE_ROOM_ALLOCATION = """Dưới đây là dữ liệu cần xử lý để xếp phòng tự động:

[DANH SÁCH SINH VIÊN CHỜ XẾP]
{danh_sach_sinh_vien}

[DANH SÁCH MÃ GIƯỜNG TRỐNG HIỆN CÓ]
{danh_sach_giuong_trong}

Yêu cầu: Hãy xuất ra bảng dữ liệu phân phòng tương ứng dưới dạng chuỗi JSON sạch theo đúng 3 nguyên tắc ưu tiên.
"""

# ==============================================================================
# PROMPT 2: PHÂN LOẠI & TÓM TẮT SỰ CỐ
# ==============================================================================
SYSTEM_PROMPT_INCIDENT_CLASSIFICATION = """Bạn là Trợ lý Phân loại và Tóm tắt Sự cố chuyên trách cho Ban Quản lý Ký túc xá. Nhiệm vụ của bạn là tiếp nhận văn bản mô tả sự cố từ sinh viên, phân loại chính xác và viết lại một câu tóm tắt cực ngắn để điều phối xử lý kịp thời.

QUY TẮC BẮT BUỘC:
1. GÁN NHÃN NHÓM CỐ ĐỊNH: Bắt buộc chọn DUY NHẤT một trong 5 nhóm sau (không được tự ý tạo nhóm khác):
   - "Điện": Sự cố bóng đèn, quạt điện, ổ cắm, chập điện, aptomat, điều hòa, công tắc...
   - "Nước": Rò rỉ nước, mất nước, hỏng vòi nước, bồn cầu nghẹt/hỏng, bình nóng lạnh, tắc thoát sàn...
   - "Cơ sở vật chất": Hỏng cửa sổ, cửa chính, khóa phòng, giường gãy dát/chân, bàn ghế lung lay, tường nứt, bong tróc trần, vỡ kính...
   - "An ninh": Mất trộm, người lạ đột nhập, gây mất trật tự sau 23h, ẩu đả, mở nhạc lớn ban đêm, đe dọa trật tự an toàn...
   - "Khác": Vấn đề rác thải môi trường, côn trùng, vệ sinh khu vực chung, khiếu nại thủ tục, nội quy...

2. CÂU TÓM TẮT NỘI DUNG:
   - ĐỘ DÀI: BẮT BUỘC KHÔNG QUÁ 15 TỪ (Đếm từ nghiêm ngặt, từ 1 đến 15 từ).
   - NỘI DUNG: Bắt buộc phải nêu rõ BẢN CHẤT VẤN ĐỀ và VỊ TRÍ CỤ THỂ (phòng, tầng, tòa, khu vực).
   - Ngắn gọn, súc tích, mang tính chất báo cáo kỹ thuật.

3. ĐỊNH DẠNG ĐẦU RA:
   - Bắt buộc trả về kết quả dưới dạng chuỗi cấu trúc dữ liệu JSON sạch, không có markdown code fence, không có văn bản giải thích ngoài JSON.

CẤU TRÚC JSON:
{
  "nhom_su_co": "Điện | Nước | Cơ sở vật chất | An ninh | Khác",
  "tom_tat": "Câu tóm tắt không quá 15 từ nêu rõ bản chất vấn đề và vị trí",
  "vi_tri": "Vị trí trích xuất được từ phản ánh",
  "so_tu": 9,
  "muc_do_khan_cap": "Khẩn cấp | Cao | Trung bình | Thấp"
}
"""

USER_PROMPT_TEMPLATE_INCIDENT_CLASSIFICATION = """Mô tả sự cố từ sinh viên: [{content}]"""


# ==============================================================================
# HÀM KẾT NỐI OPENAI & TIỆN ÍCH
# ==============================================================================
def get_client() -> Optional[OpenAI]:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    return OpenAI(api_key=key)


def clean_json_output(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned.strip())


def generate(system: str, user: str) -> str:
    client = get_client()
    if not client:
        raise RuntimeError("OPENAI_API_KEY chưa được cấu hình.")

    if hasattr(client, "responses") and callable(getattr(client.responses, "create", None)):
        try:
            response = client.responses.create(
                model=MODEL,
                instructions=system,
                input=user,
            )
            return response.output_text.strip()
        except Exception:
            pass

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


# ==============================================================================
# HÀM AI GỢI Ý XẾP PHÒNG (KÈM FALLBACK THUẬT TOÁN 3 TIÊU CHÍ)
# ==============================================================================
def allocate_rooms_ai(students: list[dict], beds: list[dict]) -> dict:
    """Ghép nối sinh viên và giường trống theo 3 nguyên tắc:
    1. Tuyệt đối đúng giới tính
    2. Cùng khóa/ngành
    3. Thỏa mãn nguyện vọng loại phòng
    """
    user_prompt = USER_PROMPT_TEMPLATE_ROOM_ALLOCATION.format(
        danh_sach_sinh_vien=json.dumps(students, ensure_ascii=False, indent=2),
        danh_sach_giuong_trong=json.dumps(beds, ensure_ascii=False, indent=2)
    )

    try:
        raw_text = generate(SYSTEM_PROMPT_ROOM_ALLOCATION, user_prompt)
        parsed = clean_json_output(raw_text)
        if isinstance(parsed, dict) and "danh_sach_phan_bo" in parsed:
            return parsed
    except Exception:
        pass

    # ==========================================================================
    # FALLBACK THUẬT TOÁN MÔ PHỎNG (Chạy khi chưa có API Key hoặc lỗi mạng)
    # ==========================================================================
    allocated = []
    unallocated = []
    available_beds = [dict(b) for b in beds]

    def student_sort_key(s):
        return (s.get("gioi_tinh", "Nam"), s.get("khoa_nganh", ""), s.get("mssv", ""))

    sorted_students = sorted(students, key=student_sort_key)

    for st in sorted_students:
        s_gender = st.get("gioi_tinh", "Nam")
        s_major = st.get("khoa_nganh", "")
        s_pref = str(st.get("nguyen_vong", "")).lower()

        # 1. Lọc giường đúng giới tính (Nguyên tắc 1: Tuyệt đối đúng giới tính)
        matching_beds = [
            b for b in available_beds
            if b.get("gioi_tinh") == s_gender or b.get("gioi_tinh") == "Nam/Nữ"
        ]

        if not matching_beds:
            unallocated.append({
                "mssv": st.get("mssv"),
                "ho_ten": st.get("ho_ten"),
                "gioi_tinh": s_gender,
                "ly_do_chua_xep": f"Hết giường trống thuộc phòng dành cho {s_gender}."
            })
            continue

        # 2. Ưu tiên nguyện vọng loại phòng (Nguyên tắc 3) & Cùng ngành (Nguyên tắc 2)
        def score_bed(b):
            score = 0
            b_desc = f"{b.get('loai_phong', '')} {b.get('toa_nha', '')} {b.get('ma_phong', '')}".lower()
            if s_pref and any(word in b_desc for word in s_pref.split()):
                score += 10
            if s_major and s_major in b.get("nganh_hien_tai", ""):
                score += 5
            return score

        matching_beds.sort(key=score_bed, reverse=True)
        chosen_bed = matching_beds[0]
        available_beds.remove(chosen_bed)

        allocated.append({
            "mssv": st.get("mssv"),
            "ho_ten": st.get("ho_ten"),
            "gioi_tinh": s_gender,
            "khoa_nganh": s_major,
            "ma_phong": chosen_bed.get("ma_phong"),
            "ma_giuong": chosen_bed.get("ma_giuong"),
            "toa_nha": chosen_bed.get("toa_nha", "KTX"),
            "loai_phong": chosen_bed.get("loai_phong", "Tiêu chuẩn"),
            "ly_do_xep_phong": f"Đảm bảo giới tính {s_gender}, ưu tiên xếp cùng ngành/khóa {s_major} và phòng phù hợp nguyện vọng."
        })

    return {
        "danh_sach_phan_bo": allocated,
        "danh_sach_chua_xep": unallocated,
        "thong_ke": {
            "tong_sinh_vien": len(students),
            "da_xep": len(allocated),
            "chua_xep": len(unallocated),
            "ty_le_thoa_man_nguyen_vong": f"{int((len(allocated) / len(students) * 100)) if students else 0}%"
        }
    }


# ==============================================================================
# HÀM AI PHÂN LOẠI & TÓM TẮT SỰ CỐ
# ==============================================================================
def classify_and_summarize_incident(content: str) -> dict:
    """Đọc phản ánh từ sinh viên, gán nhãn 1 trong 5 nhóm (Điện, Nước, Cơ sở vật chất, An ninh, Khác)
    và tóm tắt không quá 15 từ nêu rõ bản chất vấn đề + vị trí.
    """
    user_prompt = USER_PROMPT_TEMPLATE_INCIDENT_CLASSIFICATION.format(content=content.strip())

    try:
        raw_text = generate(SYSTEM_PROMPT_INCIDENT_CLASSIFICATION, user_prompt)
        parsed = clean_json_output(raw_text)
        if isinstance(parsed, dict) and "nhom_su_co" in parsed and "tom_tat" in parsed:
            valid_categories = ["Điện", "Nước", "Cơ sở vật chất", "An ninh", "Khác"]
            if parsed.get("nhom_su_co") not in valid_categories:
                parsed["nhom_su_co"] = "Khác"
            words = parsed.get("tom_tat", "").split()
            parsed["so_tu"] = len(words)
            return parsed
    except Exception:
        pass

    # ==========================================================================
    # FALLBACK NGUYÊN TẮC (Khi chưa có OpenAI API key)
    # ==========================================================================
    c_lower = content.lower()

    # 1. An ninh (ưu tiên trộm cắp, kẻ gian, người lạ, bẻ khóa)
    if any(k in c_lower for k in ["trộm", "mất cắp", "kẻ gian", "người lạ", "đột nhập", "trật tự", "đánh nhau", "loa", "ồn ào", "an ninh", "cạy cửa", "bẻ khóa"]):
        category = "An ninh"
        nature = "Nghi vấn kẻ gian đột nhập/trộm cắp"
    # 2. Điện
    elif any(k in c_lower for k in ["điện", "đèn", "quạt", "ổ cắm", "công tắc", "aptomat", "chập", "cháy", "áp tô mát", "mất điện", "bóng tuýp"]):
        category = "Điện"
        nature = "Hỏng thiết bị điện/chập điện"
    # 3. Nước
    elif any(k in c_lower for k in ["nước", "vòi", "bồn cầu", "rò rỉ", "bình nóng lạnh", "ống nước", "nghẹt", "tắc", "mất nước", "tràn nước", "ngập sàn"]):
        category = "Nước"
        nature = "Rò rỉ/sự cố đường nước"
    # 4. Rác / Môi trường / Côn trùng -> Khác
    elif any(k in c_lower for k in ["rác", "vệ sinh", "mùi", "côn trùng", "chuột", "gián", "thủ tục", "thái độ"]):
        category = "Khác"
        nature = "Ô nhiễm rác thải/vệ sinh"
    # 5. Cơ sở vật chất
    elif any(k in c_lower for k in ["cửa", "khóa", "bàn", "ghế", "giường", "kính", "tường", "trần", "dát giường", "chốt", "bong", "nứt", "gãy"]):
        category = "Cơ sở vật chất"
        nature = "Hư hỏng trang thiết bị vật chất"
    else:
        category = "Khác"
        nature = "Sự cố phản ánh KTX"

    # Trích xuất vị trí nếu có trong văn bản (ví dụ: phòng 302, tầng 3, tòa A1)
    pos_match = re.search(r"\b((?:phòng|tầng|tòa|nhà|khu|dãy)\s+[0-9A-Za-z]+(?:\s+(?:tòa|nhà|khu)\s+[0-9A-Za-z]+)?)\b", content, re.IGNORECASE)
    # Loại trừ trường hợp từ phổ thông như 'phòng sớm', 'phòng mới'
    common_words = ["sớm", "mới", "cũ", "riêng", "chung", "khác", "nào", "gì"]
    if pos_match and not any(pos_match.group(0).lower().endswith(w) for w in common_words):
        pos = pos_match.group(0).strip()
    else:
        pos = "khu KTX"

    # Tạo tóm tắt <= 15 từ rõ bản chất và vị trí
    summary = f"{nature} tại {pos}"
    words = summary.split()

    return {
        "nhom_su_co": category,
        "tom_tat": summary,
        "vi_tri": pos,
        "so_tu": len(words),
        "muc_do_khan_cap": "Khẩn cấp" if category in ["Điện", "An ninh"] else "Trung bình"
    }
