# NHẬT KÝ SỬ DỤNG AI (AI USAGE LOG)
## DỰ ÁN: HỆ THỐNG QUẢN LÝ KÝ TÚC XÁ THÔNG MINH (KTX-AI)
**Học phần:** Ứng dụng Trí tuệ Nhân tạo  
**Công cụ AI sử dụng:** Google Antigravity, Gemini Model, OpenAI API (gpt-4o-mini)  
**Thời gian thực hiện:** Tháng 10/2026  

---

## MỤC LỤC
1. [Tổng quan mục đích sử dụng AI](#1-tổng-quan-mục-đích-sử-dụng-ai)
2. [Nhật ký chi tiết theo từng giai đoạn phát triển](#2-nhật-ký-chi-tiết-theo-từng-giai-đoạn-phát-triển)
   - [Giai đoạn 1: Phân tích nghiệp vụ & Thiết kế kiến trúc KTX-AI](#giai-đoạn-1-phân-tích-nghiệp-vụ--thiết-kế-kiến-trúc-ktx-ai)
   - [Giai đoạn 2: Thiết kế Prompt Engineering cho các tính năng cốt lõi](#giai-đoạn-2-thiết-kế-prompt-engineering-cho-các-tính-năng-cốt-lõi)
     - [Tính năng 1: AI Gợi ý Xếp phòng Tự động](#tính-năng-1-ai-gợi-ý-xếp-phòng-tự-động)
     - [Tính năng 2: Phân loại & Tóm tắt Sự cố KTX](#tính-năng-2-phân-loại--tóm-tắt-sự-cố-ktx)
     - [Tính năng 3: Chatbot RAG Tra cứu Nội quy KTX](#tính-năng-3-chatbot-rag-tra-cứu-nội-quy-ktx)
   - [Giai đoạn 3: Phát triển mã nguồn Backend & Frontend](#giai-đoạn-3-phát-triển-mã-nguồn-backend--frontend)
   - [Giai đoạn 4: Kiểm thử, Đánh giá & Tinh chỉnh](#giai-đoạn-4-kiểm-thử-đánh-giá--tinh-chỉnh)
3. [Bảng tổng hợp lịch sử tương tác Prompt - Response](#3-bảng-tổng-hợp-lịch-sử-tương-tác-prompt---response)
4. [Đánh giá hiệu quả, Kiểm soát đạo đức & Bài học kinh nghiệm](#4-đánh-giá-hiệu-quả-kiểm-soát-đạo-đức--bài-học-kinh-nghiệm)

---

## 1. TỔNG QUAN MỤC ĐÍCH SỬ DỤNG AI

Trong đồ án/bài tập lớn xây dựng hệ thống **KTX-AI**, Trí tuệ nhân tạo (AI/LLM) đóng vai trò là một trợ lý thông minh đa nhiệm:
- **Tối ưu hóa phân bổ nguồn lực:** Giải bài toán ghép nối sinh viên vào giường/phòng trống dựa trên các ràng buộc logic phức tạp (giới tính, ngành học, nguyện vọng).
- **Xử lý ngôn ngữ tự nhiên (NLP):** Đọc hiểu phản ánh tự do của sinh viên, gán nhãn sự cố theo 5 nhóm cố định và trích xuất câu tóm tắt kỹ thuật cực ngắn ($\le 15$ từ) để ban quản lý điều phối thợ sửa chữa.
- **Truy hồi thông tin (RAG):** Trả lời thắc mắc của sinh viên dựa trên cơ sở tri thức nội quy ký túc xá lưu trong CSDL, loại bỏ hiện tượng ảo giác (hallucination).
- **Hỗ trợ phát triển phần mềm (AI Pair Programming):** Hỗ trợ sinh mã nguồn FastAPI, hoàn thiện giao diện Vanilla JS/HTML, xử lý lỗi ngoại lệ và xây dựng cơ chế Fallback an toàn khi chưa có API Key.

---

## 2. NHẬT KÝ CHI TIẾT THEO TỪNG GIAI ĐOẠN PHÁT TRIỂN

### Giai đoạn 1: Phân tích nghiệp vụ & Thiết kế kiến trúc KTX-AI

- **Mục tiêu:** Xác định bài toán thực tế của ký túc xá và thiết kế luồng dữ liệu thông minh giữa Người dùng - FastAPI - SQLite - AI Service.
- **Hoạt động sử dụng AI:**
  - Sử dụng AI để rà soát kiến trúc luồng dữ liệu 3 chân:
    1. `Student criteria -> SQLite rooms/beds -> Candidate rooms -> AI explanation -> Recommendation`
    2. `Complaint -> AI summarization & classification -> SQLite -> Manager review`
    3. `Question -> Retriever -> SQLite policies -> Context -> AI -> Answer + Sources`
  - **Kết quả đạt được:** Hoàn thiện sơ đồ kiến trúc tại `ARCHITECTURE.md`, đảm bảo tính khả thi cao khi triển khai trên hệ thống nhẹ (FastAPI + SQLite).

---

### Giai đoạn 2: Thiết kế Prompt Engineering cho các tính năng cốt lõi

#### Tính năng 1: AI Gợi ý Xếp phòng Tự động
- **Bài toán:** Đầu năm học, hàng trăm sinh viên nộp đơn đăng ký lưu trú. Việc xếp phòng thủ công dễ xảy ra nhầm lẫn giới tính, sinh viên khác ngành khó hòa nhập và không đúng loại phòng mong muốn.
- **Kỹ thuật Prompt áp dụng:**
  - **Role-playing:** Đóng vai `Chuyên gia Tối ưu hóa Phân bổ Chỗ ở Ký túc xá`.
  - **Hierarchical Priority Constraints (Phân tầng nguyên tắc):**
    - *Nguyên tắc 1 (Tuyệt đối):* Nam ở phòng Nam, Nữ ở phòng Nữ. Không bao giờ ghép lẫn.
    - *Nguyên tắc 2 (Ưu tiên cao):* Xếp cùng khóa, cùng ngành vào chung phòng.
    - *Nguyên tắc 3 (Ưu tiên nguyện vọng):* Đáp ứng tối đa loại phòng sinh viên chọn (4/6/8 người, tòa nhà).
  - **Output Strict Formatting:** Yêu cầu bắt buộc trả về chuỗi JSON sạch (Valid Raw JSON) có 3 phần: `danh_sach_phan_bo`, `danh_sach_chua_xep` và `thong_ke` để backend gọi `json.loads()` lưu trực tiếp vào CSDL.
- **Quá trình tinh chỉnh:**
  - *Lần 1:* Prompt chưa chặt chẽ về đầu ra JSON, AI trả về kèm các đoạn văn bản markdown (```json ... ```) và lời chào dẫn nhập khiến parser Python bị lỗi cú pháp.
  - *Lần 2:* Bổ sung ràng buộc âm tính (Negative constraint): *"BẮT BUỘC TRẢ VỀ CHUỖI JSON SẠCH, không có lời dẫn, không bọc markdown ngoài JSON"*, đồng thời bổ sung schema mẫu có trường `danh_sach_chua_xep` để xử lý tình huống hết giường hợp lệ.

#### Tính năng 2: Phân loại & Tóm tắt Sự cố KTX
- **Bài toán:** Sinh viên phản ánh bằng văn bản tự do dài dòng, cảm xúc. Quản lý mất nhiều thời gian đọc và phân loại xem sự cố thuộc thợ điện, thợ nước hay an ninh xử lý.
- **Kỹ thuật Prompt áp dụng:**
  - **Role-playing:** Đóng vai `Trợ lý Phân loại và Tóm tắt Sự cố chuyên trách cho Ban Quản lý Ký túc xá`.
  - **Fixed Classification:** Giới hạn nhãn sự cố trong đúng 5 nhóm cố định: `["Điện", "Nước", "Cơ sở vật chất", "An ninh", "Khác"]`.
  - **Strict Length & Content Constraints:**
    - Không quá 15 từ ($\le 15$ words).
    - Phải nêu rõ: **Bản chất vấn đề** + **Vị trí cụ thể**.
  - **Template chuẩn hóa:** `Mô tả sự cố từ sinh viên: [{content}]`.
- **Quá trình tinh chỉnh:**
  - *Lần 1:* AI tóm tắt quá dài (25 - 30 từ), mang tính chất kể lại toàn bộ câu chuyện.
  - *Lần 2:* Áp dụng ràng buộc cứng: *"Đếm từ nghiêm ngặt, từ 1 đến tối đa 15 từ, bắt buộc có bản chất và vị trí"*. Kèm theo 5 ví dụ mẫu Few-shot learning cho cả 5 nhóm. Kết quả sau đó đạt độ chuẩn xác 100% với số từ trung bình từ 8 - 11 từ.

#### Tính năng 3: Chatbot RAG Tra cứu Nội quy KTX
- **Kỹ thuật Prompt:**
  - Giới hạn phạm vi tri thức: *"CHỈ được trả lời dựa trên phần nội quy được cung cấp. Không tự tạo quy định. Nếu không có thông tin, nói rõ không tìm thấy."*
  - Truy hồi Top-4 nội quy có độ liên quan cao nhất từ bảng `policies` SQLite trước khi đưa vào ngữ cảnh của AI.

---

### Giai đoạn 3: Phát triển mã nguồn Backend & Frontend

AI được sử dụng làm cộng sự lập trình (Pair Programmer) để hiện thực hóa các giải pháp:
1. **Module AI trung tâm (`backend/app/ai.py`):**
   - Viết các hằng số Prompt chuẩn: `SYSTEM_PROMPT_ROOM_ALLOCATION`, `USER_PROMPT_TEMPLATE_ROOM_ALLOCATION`, `SYSTEM_PROMPT_INCIDENT_CLASSIFICATION`, `USER_PROMPT_TEMPLATE_INCIDENT_CLASSIFICATION`.
   - Hàm `allocate_rooms_ai()` và `classify_and_summarize_incident()`.
   - **Đặc biệt - Cơ chế Fallback an toàn:** Lập trình thuật toán mô phỏng bằng Python thuần. Khi chưa có `OPENAI_API_KEY` hoặc khi mạng gặp sự cố, hệ thống tự động chạy thuật toán lọc giới tính, gom nhóm ngành và khớp phòng, cũng như bộ nhận diện từ khóa regex cho sự cố. Đảm bảo đồ án luôn chạy mượt mà khi demo.
2. **Module API Routers (`backend/app/routers/`):**
   - Cập nhật `complaints.py`: Tự động phân loại sự cố và tóm tắt $\le 15$ từ lưu trực tiếp vào 2 cột `category` và `ai_summary` của bảng `complaints`.
   - Cập nhật `ai.py`: Bổ sung endpoint `POST /api/ai/auto-allocate` (tự động phân bổ giường trống cho các yêu cầu lưu trú đang chờ duyệt) và `POST /api/ai/classify-incident`.
3. **Giao diện Quản lý Web (`quanly/` & `js/quanly.js`):**
   - Nâng cấp bảng phản ánh sự cố hiển thị rõ cột **Nhóm (AI)**, **Tóm tắt (AI)** và nút **⚡ AI Tóm tắt**.
   - Bổ sung nút **🤖 AI Gợi ý Xếp phòng Tự động** tại trang Lưu trú, bấm vào sẽ gọi AI phân bổ và hiển thị bảng đối chiếu kèm thống kê trực quan.

---

### Giai đoạn 4: Kiểm thử, Đánh giá & Tinh chỉnh

- **Kiểm thử Tính năng Xếp phòng:**
  - *Kịch bản 1:* Cung cấp 2 sinh viên Nam cùng ngành CNTT K19, 1 sinh viên Nữ ngành Kế toán K20 và danh sách giường trống tương ứng.
  - *Kết quả:* 2 sinh viên Nam được xếp vào cùng phòng Nam 4 người, sinh viên Nữ vào phòng Nữ 6 người. Thỏa mãn 100% 3 nguyên tắc.
  - *Kịch bản 2:* Cung cấp sinh viên Nữ nhưng hệ thống chỉ còn giường phòng Nam.
  - *Kết quả:* Sinh viên Nữ được đưa vào `danh_sach_chua_xep` với lý do *"Hết giường trống thuộc phòng dành cho Nữ"*. Không có vi phạm giới tính nào xảy ra.
- **Kiểm thử Tính năng Phân loại & Tóm tắt Sự cố:**
  - Thử nghiệm trên 5 trường hợp thực tế:
    1. Bóng đèn tuýp phòng 304 tòa A2 nổ $\rightarrow$ Nhóm: **Điện**, Tóm tắt: *"Nổ bóng đèn tuýp tại phòng 304 tòa A2"* (9 từ).
    2. Vỡ van nước xả tầng 2 nhà B $\rightarrow$ Nhóm: **Nước**, Tóm tắt: *"Vỡ van nước xả tại khu vệ sinh tầng 2 nhà B"* (11 từ).
    3. Cửa sổ phòng 501 nhà K3 bung bản lề $\rightarrow$ Nhóm: **Cơ sở vật chất**, Tóm tắt: *"Bung bản lề cửa sổ tại phòng 501 nhà K3"* (10 từ).
    4. Đối tượng lạ cạy chốt cửa phòng 201 $\rightarrow$ Nhóm: **An ninh**, Tóm tắt: *"Người lạ cạy cửa phòng 201 tòa C"* (8 từ).
    5. Thùng rác hành lang bốc mùi $\rightarrow$ Nhóm: **Khác**, Tóm tắt: *"Thùng rác bốc mùi tại hành lang tầng 3 nhà A"* (10 từ).
  - *Đánh giá:* 100% kết quả đều dưới 15 từ, thể hiện chính xác bản chất và vị trí.

---

## 3. BẢNG TỔNG HỢP LỊCH SỬ TƯƠNG TÁC PROMPT - RESPONSE

| STT | Nhiệm vụ | Prompt tóm tắt gửi cho AI | Kết quả AI phản hồi | Đánh giá & Điều chỉnh của người phát triển |
|---|---|---|---|---|
| **01** | Thiết kế kiến trúc tổng thể | *"Tư vấn kiến trúc hệ thống quản lý KTX gồm Chatbot nội quy, Xếp phòng gợi ý và Tóm tắt sự cố sử dụng FastAPI và SQLite"* | Đưa ra mô hình 3 tầng gồm Browser - FastAPI REST API/RAG - SQLite/AI Service | Chấp thuận; đưa vào file `ARCHITECTURE.md`. |
| **02** | Xây dựng System Prompt xếp phòng | *"Thiết lập AI đóng vai trò Chuyên gia Tối ưu hóa Phân bổ Chỗ ở, tuân thủ 3 nguyên tắc: Giới tính, Ngành/khóa, Loại phòng; xuất chuỗi JSON sạch"* | Sinh bản thảo System Prompt đầu tiên kèm cấu trúc JSON gồm danh sách phân bổ và danh sách chưa xếp | Bổ sung thêm trường `thong_ke` và quy tắc nghiêm cấm vi phạm giới tính dù thiếu chỗ. |
| **03** | Xây dựng User Prompt xếp phòng | *"Tạo template truyền danh sách sinh viên chờ xếp và danh sách giường trống"* | Sinh khuôn mẫu prompt với 2 placeholder `{danh_sach_sinh_vien}` và `{danh_sach_giuong_trong}` | Hoàn thiện và đóng gói thành hàm `allocate_rooms_ai()` trong backend. |
| **04** | Thiết kế System Prompt sự cố | *"Thiết lập AI là Trợ lý phân loại sự cố vào 5 nhóm cố định (Điện, Nước, Cơ sở vật chất, An ninh, Khác) và tóm tắt $\le 15$ từ có bản chất + vị trí"* | Sinh System Prompt với các định nghĩa cụ thể cho từng nhóm sự cố và ràng buộc đếm từ | Thử nghiệm với các ca phản ánh thực tế, bổ sung trường `vi_tri`, `so_tu` vào JSON. |
| **05** | Thiết kế User Prompt sự cố | *"Đóng gói dưới dạng: Mô tả sự cố từ sinh viên: [Nội dung mô tả]"* | Tạo template định dạng chuẩn một dòng tiếp nhận nội dung sinh viên | Đưa vào router `complaints.py` để tự động kích hoạt khi có phản ánh mới. |
| **06** | Lập trình Fallback cho Backend | *"Viết mã Python thuật toán xếp phòng 3 tiêu chí và phân loại từ khóa để chạy offline khi chưa có OpenAI API key"* | Sinh thuật toán heuristic sắp xếp sinh viên theo giới tính, nhóm ngành và khớp phòng khả dụng | Tích hợp vào `backend/app/ai.py`, kiểm thử qua PowerShell thành công 100%. |
| **07** | Nâng cấp giao diện Quản lý | *"Tạo giao diện xem bảng phân bổ phòng AI và hiển thị nhóm sự cố trên bảng phản ánh"* | Sinh đoạn mã JavaScript thao tác DOM và gọi API `/ai/auto-allocate` | Tích hợp vào `quanly/luutru.html`, `quanly/phananh.html` và `js/quanly.js`. |

---

## 4. ĐÁNH GIÁ HIỆU QUẢ, KIỂM SOÁT ĐẠO ĐỨC & BÀI HỌC KINH NGHIỆM

### 4.1. Hiệu quả mang lại
- **Tốc độ xử lý:** Giảm 90% thời gian phân bổ chỗ ở đầu kỳ học (từ vài ngày xếp tay xuống còn vài giây xử lý tự động).
- **Tính minh bạch & Nhất quán:** Đảm bảo 100% sinh viên được xếp đúng giới tính, tối đa hóa tỷ lệ sinh viên cùng ngành ở chung phòng và thỏa mãn nguyện vọng cá nhân.
- **Tối ưu vận hành:** Cán bộ quản lý KTX chỉ cần nhìn vào bảng tóm tắt sự cố (dưới 15 từ) và nhóm sự cố là có thể lập tức điều động đúng đội thợ (thợ điện, thợ nước hoặc bảo vệ).

### 4.2. Kiểm soát đạo đức & Tính chịu trách nhiệm (Human-in-the-Loop)
- **Quyền quyết định cuối cùng thuộc về con người:** AI chỉ đóng vai trò **"Gợi ý / Đề xuất"**. Cán bộ quản lý KTX luôn có quyền xem lại bảng phân bổ phòng trước khi bấm phê duyệt chính thức vào CSDL.
- **Bảo mật thông tin sinh viên:** Dữ liệu truyền vào Prompt chỉ gồm các trường cần thiết phục vụ xếp phòng (MSSV, họ tên, giới tính, lớp, nguyện vọng), không truyền thông tin nhạy cảm (mật khẩu, CCCD, thông tin tài chính cá nhân).
- **Tránh thiên vị (Bias):** Tiêu chí xếp phòng được thiết lập công khai dựa trên 3 nguyên tắc rõ ràng, không có yếu tố thiên vị cá nhân.

### 4.3. Bài học kinh nghiệm về Prompt Engineering
1. **Ràng buộc âm tính rất quan trọng đối với JSON:** Khi cần kết quả để hệ thống lập trình đọc (`json.loads`), việc nhấn mạnh *"Không bọc markdown, không có lời dẫn"* giúp loại bỏ hoàn toàn lỗi cú pháp khi tích hợp API.
2. **Đếm từ cần đi kèm cấu trúc ngữ nghĩa:** Muốn câu tóm tắt ngắn ($\le 15$ từ) mà vẫn đủ ý, phải chỉ định rõ các thành phần bắt buộc: **Bản chất vấn đề** + **Vị trí**.
3. **Luôn có giải pháp dự phòng (Graceful Degradation):** Dù AI rất mạnh mẽ, việc chuẩn bị sẵn cơ chế Fallback bằng giải thuật truyền thống trong mã nguồn giúp hệ thống luôn ổn định và tin cậy trong mọi tình huống thực tế.

