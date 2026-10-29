# BÁO CÁO YÊU CẦU HỆ THỐNG (SOFTWARE REQUIREMENTS SPECIFICATION - SRS)
## DỰ ÁN: HỆ THỐNG QUẢN LÝ KÝ TÚC XÁ THÔNG MINH TÍCH HỢP AI (KTX-AI)

**Học phần:** Ứng dụng Trí tuệ Nhân tạo  
**Dự án:** KTX-AI / KTX-ICTU  
**Môi trường phát triển:** Python 3.13, FastAPI, SQLite 3, OpenAI API / Gemini, HTML5/CSS3/Vanilla JS  
**Phiên bản:** 1.0  
**Ngày lập báo cáo:** Tháng 10/2026  

---

## MỤC LỤC
1. [Giới thiệu Chung & Mục tiêu Dự án](#1-giới-thiệu-chung--mục-tiêu-dự-án)
2. [Yêu cầu Môi trường & Ngăn xếp Công nghệ (Tech Stack)](#2-yêu-cầu-môi-trường--ngăn-xếp-công-nghệ-tech-stack)
3. [Yêu cầu Chức năng (Functional Requirements - FR)](#3-yêu-cầu-chức-năng-functional-requirements---fr)
   - [FR-01: Quản lý Xác thực & Phân quyền Người dùng](#fr-01-quản-lý-xác-thực--phân-quyền-người-dùng)
   - [FR-02: Quản lý Hạ tầng Ký túc xá (Tòa nhà, Phòng, Giường)](#fr-02-quản-lý-hạ-tầng-ký-túc-xá-tòa-nhà-phòng-giường)
   - [FR-03: Quản lý Hồ sơ Sinh viên & Cấp Tài khoản](#fr-03-quản-lý-hồ-sơ-sinh-viên--cấp-tài-khoản)
   - [FR-04: Quản lý Lưu trú & Vòng đời Đơn Đăng ký](#fr-04-quản-lý-lưu-trú--vòng-đời-đơn-đăng-ký)
   - [FR-05: AI Gợi ý Xếp phòng Tự động theo 3 Nguyên tắc (Core AI 1)](#fr-05-ai-gợi-ý-xếp-phòng-tự-động-theo-3-nguyên-tắc-core-ai-1)
   - [FR-06: Phân loại & Tóm tắt Sự cố Tự động bằng AI (Core AI 2)](#fr-06-phân-loại--tóm-tắt-sự-cố-tự-động-bằng-ai-core-ai-2)
   - [FR-07: Chatbot AI Tra cứu Nội quy KTX qua RAG (Core AI 3)](#fr-07-chatbot-ai-tra-cứu-nội-quy-ktx-qua-rag-core-ai-3)
   - [FR-08: Quản lý Hợp đồng Lưu trú](#fr-08-quản-lý-hợp-đồng-lưu-trú)
   - [FR-09: Quản lý Thu phí & Tài chính](#fr-09-quản-lý-thu-phí--tài-chính)
   - [FR-10: Báo cáo Thống kê Thời gian thực](#fr-10-báo-cáo-thống-kê-thời-gian-thực)
4. [Yêu cầu Phi chức năng (Non-Functional Requirements - NFR)](#4-yêu-cầu-phi-chức-năng-non-functional-requirements---nfr)
   - [NFR-01: Hiệu năng & Thời gian đáp ứng (Performance)](#nfr-01-hiệu-năng--thời-gian-đáp-ứng-performance)
   - [NFR-02: Tính sẵn sàng & Độ tin cậy (Availability & Fault Tolerance)](#nfr-02-tính-sẵn-sàng--độ-tin-cậy-availability--fault-tolerance)
   - [NFR-03: An toàn & Bảo mật Thông tin (Security & Privacy)](#nfr-03-an-toàn--bảo-mật-thông-tin-security--privacy)
   - [NFR-04: Tính toàn vẹn Dữ liệu & Nghiệp vụ (Data Integrity)](#nfr-04-tính-toàn-vẹn-dữ-liệu--nghiệp-vụ-data-integrity)
   - [NFR-05: Khả năng Tương thích & Triển khai (Portability & Deployability)](#nfr-05-khả-năng-tương-thích--triển-khai-portability--deployability)
   - [NFR-06: Khả năng Mở rộng (Scalability & Extensibility)](#nfr-06-khả-năng-mở-rộng-scalability--extensibility)
   - [NFR-07: Tính Tiện dụng & Trải nghiệm Người dùng (Usability & UX)](#nfr-07-tính-tiện-dụng--trải-nghiệm-người-dùng-usability--ux)
5. [Yêu cầu Giao diện & Tích hợp (Interfaces Requirements)](#5-yêu-cầu-giao-diện--tích-hợp-interfaces-requirements)
   - [5.1. Giao diện Người dùng Web (UI Requirements)](#51-giao-diện-người-dùng-web-ui-requirements)
   - [5.2. Giao diện Lập trình Ứng dụng (REST API Requirements)](#52-giao-diện-lập-trình-ứng-dụng-rest-api-requirements)
   - [5.3. Giao diện Kết nối Dịch vụ AI (External AI Service)](#53-giao-diện-kết-nối-dịch-vụ-ai-external-ai-service)
6. [Ma trận Đánh giá & Mức độ Ưu tiên Yêu cầu (Priority Matrix)](#6-ma-trận-đánh-giá--mức-độ-ưu-tiên-yêu-cầu-priority-matrix)

---

## 1. GIỚI THIỆU CHUNG & MỤC TIÊU DỰ ÁN

Dự án **KTX-AI** là hệ thống phần mềm quản lý ký túc xá thông minh được xây dựng nhằm giải quyết các bất cập trong quản lý vận hành truyền thống:
- **Tự động hóa phân bổ chỗ ở:** Sử dụng mô hình Trí tuệ nhân tạo (LLM / Heuristic Optimization) để ghép nối tự động hàng trăm sinh viên vào giường trống theo 3 nguyên tắc phân tầng (Giới tính $\rightarrow$ Ngành/Khóa $\rightarrow$ Nguyện vọng loại phòng), giảm thiểu tối đa sai sót thủ công.
- **Tiếp nhận & phân loại sự cố thông minh:** Sử dụng công nghệ xử lý ngôn ngữ tự nhiên (NLP) để đọc hiểu phản ánh của sinh viên, tự động gán nhãn cố định vào 5 nhóm (`Điện`, `Nước`, `Cơ sở vật chất`, `An ninh`, `Khác`) và tóm tắt kỹ thuật cực ngắn ($\le 15$ từ) để ban quản lý điều động thợ sửa chữa tức thì.
- **Tư vấn nội quy tự động (RAG Chatbot):** Hỗ trợ sinh viên tra cứu quy định KTX 24/7 thông qua kỹ thuật Tìm kiếm tăng cường tạo sinh (RAG), đảm bảo câu trả lời luôn có nguồn trích dẫn từ CSDL và không bị ảo giác (hallucination).
- **Số hóa toàn diện dữ liệu động:** Toàn bộ dữ liệu về sinh viên, phòng, giường, hợp đồng, tài chính công nợ và sự cố đều được quản lý động qua CSDL SQLite và API RESTful, loại bỏ hoàn toàn các trang HTML tĩnh demo số liệu giả.

---

## 2. YÊU CẦU MÔI TRƯỜNG & NGĂN XẾP CÔNG NGHỆ (TECH STACK)

Dựa trên mã nguồn hiện hữu của dự án, các yêu cầu kỹ thuật nền tảng bao gồm:

### 2.1. Backend Framework & Ngôn ngữ
- **Ngôn ngữ:** Python $\ge$ 3.10 (Môi trường kiểm thử hiện tại: Python 3.13).
- **Web Framework:** FastAPI $\ge$ 0.116 (kiến trúc RESTful API bất đồng bộ).
- **Web Server:** Uvicorn $\ge$ 0.35 (`uvicorn[standard]`).
- **ORM & CSDL:** SQLAlchemy $\ge$ 2.0 kết hợp với CSDL nhúng SQLite 3 (`backend/ktx_ai.db`).
- **Xác thực & Mã hóa:** `python-jose[cryptography] >= 3.5` (JWT token), `pwdlib[argon2] >= 0.2` (Băm mật khẩu an toàn).
- **Tải tệp & Dữ liệu form:** `python-multipart >= 0.0.20`.

### 2.2. Trí tuệ Nhân tạo & LLM
- **Thư viện AI:** `openai >= 1.100`.
- **Mô hình AI mặc định:** `gpt-4o-mini` hoặc mô hình tương đương (cấu hình qua biến môi trường `OPENAI_MODEL`).
- **Fallback Algorithm:** Thuật toán nội bộ viết bằng Python thuần, đảm bảo hệ thống luôn xử lý được yêu cầu khi không có API key.

### 2.3. Frontend & Client
- **Công nghệ:** HTML5, CSS3 hiện đại, Vanilla JavaScript (ES6+).
- **Giao tiếp API:** Sử dụng Native Fetch API và hàm tiện ích xác thực `api()` (`js/auth.js`).
- **Không phụ thuộc thư viện nặng:** Không sử dụng React/Vue/Node.js phức tạp, tối ưu cho việc nạp trang nhanh và triển khai trực tiếp từ FastAPI StaticFiles.

---

## 3. YÊU CẦU CHỨC NĂNG (FUNCTIONAL REQUIREMENTS - FR)

### FR-01: Quản lý Xác thực & Phân quyền Người dùng
- **FR-01.1:** Hệ thống phải hỗ trợ đăng nhập qua API `POST /api/auth/login` bằng `username` và `password`.
- **FR-01.2:** Hệ thống phải phân quyền nghiêm ngặt theo 3 vai trò (Role-Based Access Control):
  - `quanly`: Toàn quyền quản trị sinh viên, phòng, duyệt đơn lưu trú, hợp đồng, sự cố, nội quy và chạy AI xếp phòng.
  - `ketoan`: Quyền quản lý tài chính, tạo khoản thu và xác nhận thu tiền.
  - `sinhvien`: Quyền xem phòng/giường cá nhân, nộp đơn lưu trú, gửi phản ánh, tra cứu phí và chat với AI nội quy.
- **FR-01.3:** Hệ thống phải cấp mã `access_token` định dạng JWT có hiệu lực, kèm chức năng đăng xuất xóa token khỏi `localStorage`.

### FR-02: Quản lý Hạ tầng Ký túc xá (Tòa nhà, Phòng, Giường)
- **FR-02.1:** Cho phép quản lý thêm mới tòa nhà (mã tòa duy nhất, tên tòa, tổng số tầng) qua `POST /api/rooms/buildings`.
- **FR-02.2:** Cho phép quản lý tạo phòng mới thuộc tòa nhà, chỉ định sức chứa (capacity: 4, 6, 8 chỗ), tầng và quy định giới tính (`Nam`, `Nữ`, `Nam/Nữ`).
- **FR-02.3:** Khi tạo phòng thành công, hệ thống phải tự động sinh đúng số lượng giường tương ứng trong bảng `beds` từ số 1 đến `capacity` với trạng thái ban đầu là `Trống`.
- **FR-02.4:** Hệ thống phải tự động tính toán số người đang ở (`occupied`) và số chỗ trống (`available`) của từng phòng dựa trên trạng thái thực tế của các giường.

### FR-03: Quản lý Hồ sơ Sinh viên & Cấp Tài khoản
- **FR-03.1:** Quản lý có thể thêm mới sinh viên gồm: MSSV (duy nhất), Họ tên, Lớp/Ngành/Khóa, Số điện thoại và Mật khẩu.
- **FR-03.2:** Hệ thống phải tự động sinh tài khoản người dùng (`users`) tương ứng với vai trò `sinhvien` và liên kết với hồ sơ sinh viên vừa tạo (`student_id`).
- **FR-03.3:** Hiển thị danh sách sinh viên kèm trạng thái lưu trú hiện tại (`Chưa xếp phòng`, `Đang ở`, `Đã trả phòng`) và phòng đang ở.

### FR-04: Quản lý Lưu trú & Vòng đời Đơn Đăng ký
- **FR-04.1:** Sinh viên có thể nộp 3 loại đơn lưu trú: `Đăng ký ở`, `Chuyển phòng`, `Trả phòng` kèm nguyện vọng phòng mong muốn và ghi chú.
- **FR-04.2:** Quản lý xem danh sách đơn ở trạng thái `Chờ duyệt` và thực hiện `Duyệt (Approve)` hoặc `Từ chối (Reject)`.
- **FR-04.3:** Khi duyệt đơn:
  - Hệ thống phải kiểm tra phòng mong muốn còn giường trống hay không.
  - Tự động gán giường trống đầu tiên cho sinh viên, cập nhật trạng thái giường thành `Đang ở`.
  - Nếu sinh viên đang có giường cũ, hệ thống phải tự động giải phóng giường cũ về trạng thái `Trống`.
  - Cập nhật trạng thái đơn thành `Đã duyệt` và trạng thái sinh viên thành `Đang ở`.

### FR-05: AI Gợi ý Xếp phòng Tự động theo 3 Nguyên tắc (Core AI 1)
- **FR-05.1:** Hệ thống phải cung cấp endpoint `POST /api/ai/auto-allocate` tiếp nhận dữ liệu danh sách sinh viên chờ duyệt và danh sách giường trống.
- **FR-05.2:** Quá trình phân bổ bắt buộc phải tuân thủ nghiêm ngặt 3 nguyên tắc theo thứ bậc ưu tiên:
  1. **Nguyên tắc 1 (Tuyệt đối):** Nam ở phòng Nam, Nữ ở phòng Nữ. Tuyệt đối không xếp lẫn giới tính hoặc xếp sai giới tính quy định của phòng.
  2. **Nguyên tắc 2 (Ưu tiên cao):** Ưu tiên xếp sinh viên cùng ngành/khóa vào chung một phòng.
  3. **Nguyên tắc 3 (Ưu tiên nguyện vọng):** Ưu tiên tối đa thỏa mãn loại phòng mong muốn của sinh viên (sức chứa, tòa nhà).
- **FR-05.3:** Kết quả trả về phải là chuỗi JSON sạch (Valid Raw JSON) có cấu trúc chuẩn:
  - `danh_sach_phan_bo`: Chứa thông tin phân phòng kèm lý do giải thích rõ ràng.
  - `danh_sach_chua_xep`: Chứa các trường hợp không thể xếp do hết giường đúng giới tính/loại phòng.
  - `thong_ke`: Tổng số sinh viên, số đã xếp, số chưa xếp, tỷ lệ thành công.
- **FR-05.4:** Hệ thống phải có thuật toán Fallback nội bộ bằng Python để tự động chạy khi chưa cấu hình `OPENAI_API_KEY` hoặc khi mạng gặp lỗi.

### FR-06: Phân loại & Tóm tắt Sự cố Tự động bằng AI (Core AI 2)
- **FR-06.1:** Tiếp nhận mô tả sự cố văn bản tự do từ sinh viên thông qua form phản ánh.
- **FR-06.2:** Hệ thống AI phải tự động phân loại sự cố vào DUY NHẤT 1 trong 5 nhóm cố định:
  - `Điện`
  - `Nước`
  - `Cơ sở vật chất`
  - `An ninh`
  - `Khác`
- **FR-06.3:** Hệ thống AI phải tạo một câu tóm tắt nội dung đáp ứng đồng thời 2 ràng buộc cứng:
  - Độ dài: **Bắt buộc không quá 15 từ** ($\le 15$ words).
  - Nội dung: Phải nêu rõ **Bản chất vấn đề** và **Vị trí cụ thể** (phòng, tầng, tòa, khu vực).
- **FR-06.4:** Lưu trữ kết quả AI vào cột `category` và `ai_summary` của bảng `complaints`.
- **FR-06.5:** Quản lý có thể cập nhật tiến trình xử lý sự cố (`Chưa xử lý` $\rightarrow$ `Đang xử lý` $\rightarrow$ `Đã xử lý`).

### FR-07: Chatbot AI Tra cứu Nội quy KTX qua RAG (Core AI 3)
- **FR-07.1:** Quản lý có thể thêm, sửa, xóa các điều khoản nội quy trong bảng `policies`.
- **FR-07.2:** Khi sinh viên đặt câu hỏi, module Retriever phải tìm kiếm Top-4 điều khoản nội quy có độ liên quan cao nhất từ SQLite.
- **FR-07.3:** AI phải trả lời bằng tiếng Việt, ngắn gọn, chỉ dựa trên nội dung nội quy được trích xuất (Strict Context). Nếu không có quy định liên quan, phải trả lời rõ ràng không tìm thấy, tuyệt đối không bịa đặt.
- **FR-07.4:** Câu trả lời phải kèm theo danh sách mã điều khoản dẫn nguồn (`sources`).

### FR-08: Quản lý Hợp đồng Lưu trú
- **FR-08.1:** Cho phép quản lý lập hợp đồng lưu trú cho sinh viên đã có phòng, tự sinh mã hợp đồng duy nhất (`HDxxxxxx`).
- **FR-08.2:** Quản lý ngày bắt đầu, ngày hết hạn và trạng thái hiệu lực của hợp đồng.

### FR-09: Quản lý Thu phí & Tài chính
- **FR-09.1:** Kế toán hoặc Quản lý có thể tạo khoản thu theo tháng (`MM/YYYY`), số tiền và hạn nộp cho từng sinh viên.
- **FR-09.2:** Kế toán có chức năng xác nhận thanh toán (`pay`), chuyển trạng thái khoản thu thành `Đã thu`.
- **FR-09.3:** Hệ thống tự động tính toán tổng phải thu, số tiền đã thu, nợ đọng (công nợ) và tỷ lệ thu phí (%).

### FR-10: Báo cáo Thống kê Thời gian thực
- **FR-10.1:** Cung cấp API `GET /api/stats` tính toán số liệu trực tiếp từ các bảng CSDL.
- **FR-10.2:** Hiển thị trực quan: Tổng số sinh viên, tổng số phòng, công suất sử dụng giường (Occupancy Rate %), số đơn lưu trú chờ duyệt, tổng số tiền thu được, tổng nợ, tỷ lệ xử lý sự cố.

---

## 4. YÊU CẦU PHI CHỨC NĂNG (NON-FUNCTIONAL REQUIREMENTS - NFR)

### NFR-01: Hiệu năng & Thời gian đáp ứng (Performance)
- **NFR-01.1:** Các truy vấn nghiệp vụ thông thường (xác thực, xem danh sách phòng, sinh viên, tài chính) phải phản hồi trong thời gian $\le 200$ ms.
- **NFR-01.2:** Xử lý AI phân bổ phòng và phân loại sự cố:
  - Khi gọi OpenAI API qua mạng: Thời gian phản hồi trung bình $\le 3$ giây.
  - Khi chạy chế độ Fallback Algorithm nội bộ: Thời gian phản hồi $\le 100$ ms.
- **NFR-01.3:** Tải trang Web ban đầu (HTML, CSS, JS) phải hoàn tất dưới 1 giây trên mạng cục bộ do không phụ thuộc các thư viện cồng kềnh.

### NFR-02: Tính sẵn sàng & Độ tin cậy (Availability & Fault Tolerance)
- **NFR-02.1:** **Graceful Degradation:** Nếu không có kết nối Internet hoặc chưa cấu hình biến môi trường `OPENAI_API_KEY`, toàn bộ hệ thống vẫn hoạt động bình thường nhờ cơ chế Fallback Heuristic trong `backend/app/ai.py`. Không bao giờ gây sập tiến trình server FastAPI.
- **NFR-02.2:** Tính năng xếp phòng AI luôn đảm bảo không bao giờ sinh ra lỗi trùng giường (1 giường chỉ gán cho 1 người) và không vượt quá sức chứa phòng.

### NFR-03: An toàn & Bảo mật Thông tin (Security & Privacy)
- **NFR-03.1:** Toàn bộ mật khẩu người dùng phải được băm bằng thuật toán Argon2 hoặc PBKDF2 với độ phức tạp cao, không bao giờ lưu mật khẩu dạng văn bản thô (Plain Text).
- **NFR-03.2:** Xác thực API thông qua Bearer Token JWT tiêu chuẩn; mọi endpoint nhạy cảm (duyệt phòng, thu tiền, cấu hình hệ thống) phải được bảo vệ bởi middleware `require_roles`.
- **NFR-03.3:** **Bảo mật dữ liệu gửi AI:** Dữ liệu gửi đến mô hình LLM chỉ gồm các trường định danh kỹ thuật (MSSV, lớp, giới tính, nguyện vọng, nội dung phản ánh), tuyệt đối không gửi mật khẩu, thông tin tài khoản ngân hàng hoặc dữ liệu cá nhân nhạy cảm khác.

### NFR-04: Tính toàn vẹn Dữ liệu & Nghiệp vụ (Data Integrity)
- **NFR-04.1:** Toàn bộ khóa chính (PK) phải duy nhất và tự động tăng; các trường mã nghiệp vụ (`username`, `mssv`, `code`) phải có ràng buộc Unique Index.
- **NFR-04.2:** Khi một phòng bị xóa, toàn bộ các giường thuộc phòng đó phải tự động được xóa theo cơ chế Cascade Delete (`cascade="all, delete-orphan"`).
- **NFR-04.3:** Không cho phép xếp lẫn sinh viên Nam và Nữ trong cùng một phòng ở bất kỳ tình huống nào.

### NFR-05: Khả năng Tương thích & Triển khai (Portability & Deployability)
- **NFR-05.1:** Hệ thống phải chạy được mượt mà trên hệ điều hành Windows (PowerShell/CMD), macOS và Linux.
- **NFR-05.2:** Không yêu cầu cài đặt phần mềm máy chủ CSDL phức tạp (như MySQL, PostgreSQL, Oracle) hoặc Docker; hệ thống hoạt động độc lập ngay với SQLite đi kèm Python.
- **NFR-05.3:** Cung cấp sẵn các tập lệnh chạy nhanh: `run.bat`, `run.ps1` và script khởi tạo dữ liệu `seed.py`.

### NFR-06: Khả năng Mở rộng (Scalability & Extensibility)
- **NFR-06.1:** Nhờ sử dụng kiến trúc SQLAlchemy 2.0 ORM, hệ thống có thể chuyển đổi sang PostgreSQL hoặc MySQL chỉ bằng cách thay đổi một dòng cấu hình `DATABASE_URL` trong file `.env` mà không phải sửa code.
- **NFR-06.2:** Kiến trúc RESTful API tách biệt hoàn toàn cho phép tích hợp thêm ứng dụng di động (Flutter / React Native) hoặc cổng dịch vụ công của nhà trường trong tương lai.

### NFR-07: Tính Tiện dụng & Trải nghiệm Người dùng (Usability & UX)
- **NFR-07.1:** Giao diện sử dụng 100% tiếng Việt có dấu, thuật ngữ rõ ràng, bố cục trực quan với thanh Sidebar điều hướng nhanh.
- **NFR-07.2:** Các thông báo thành công hoặc lỗi phải hiển thị rõ lý do (vd: *"Phòng hiện không còn giường trống"*, *"MSSV đã tồn tại"*).
- **NFR-07.3:** Kết quả gợi ý từ AI phải hiển thị kèm theo lý do cụ thể để cán bộ quản lý dễ dàng thẩm định trước khi ra quyết định duyệt.

---

## 5. YÊU CẦU GIAO DIỆN & TÍCH HỢP (INTERFACES REQUIREMENTS)

### 5.1. Giao diện Người dùng Web (UI Requirements)

| Phân hệ | Đường dẫn trang | Chức năng giao diện chính |
|---|---|---|
| **Đăng nhập** | `/index.html` | Form đăng nhập chung cho tất cả các vai trò, tự động điều hướng theo quyền. |
| **Sinh viên** | `/sinhvien/home.html` | Hiển thị phòng/giường đang ở, khung chat với AI nội quy. |
| | `/sinhvien/dangky.html` | Form gửi đơn đăng ký ở, chuyển phòng, trả phòng và lịch sử đơn. |
| | `/sinhvien/phananh.html` | Form gửi phản ánh hư hỏng, xem tiến độ giải quyết sự cố. |
| | `/sinhvien/taichinh.html` | Danh sách các khoản tiền phòng/điện nước cần thanh toán. |
| **Quản lý** | `/quanly/home.html` | Bảng điều khiển thống kê tổng quan (phòng, sinh viên, đơn chờ). |
| | `/quanly/sinhvien.html` | Danh sách sinh viên, form thêm sinh viên và tài khoản tự động. |
| | `/quanly/phong.html` | Danh mục tòa nhà, danh mục phòng, sức chứa và chỗ trống. |
| | `/quanly/luutru.html` | Bảng đơn lưu trú, **nút kích hoạt AI Gợi ý Xếp phòng Tự động**. |
| | `/quanly/phananh.html` | Bảng sự cố hiển thị **Nhóm (AI)**, **Tóm tắt (AI)** và nút **⚡ AI Tóm tắt**. |
| | `/quanly/hopdong.html` | Quản lý hợp đồng thuê phòng của sinh viên. |
| | `/quanly/noiquy.html` | Nhập và lưu trữ kho quy chế, nội quy phục vụ AI RAG. |
| | `/quanly/thongke.html` | Báo cáo tỷ lệ lấp đầy, thu phí và các chỉ số vận hành. |
| **Kế toán** | `/ketoan/home.html` | Lập khoản thu, xác nhận thu tiền, theo dõi nợ đọng. |

---

### 5.2. Giao diện Lập trình Ứng dụng (REST API Requirements)

Toàn bộ hệ thống giao tiếp qua RESTful API định dạng JSON chuẩn:

```text
/api
├── /auth
│   └── POST   /login                       # Đăng nhập xác thực cấp JWT
├── /students
│   ├── GET    /                            # Danh sách sinh viên
│   ├── POST   /                            # Thêm sinh viên & cấp tài khoản
│   └── GET    /me                          # Xem hồ sơ cá nhân của sinh viên
├── /rooms
│   ├── GET    /                            # Danh sách phòng & số chỗ trống
│   ├── POST   /                            # Thêm phòng & tự sinh giường
│   ├── GET    /buildings                   # Danh sách tòa nhà
│   └── POST   /buildings                   # Thêm tòa nhà mới
├── /stays
│   ├── GET    /                            # Quản lý xem toàn bộ đơn lưu trú
│   ├── POST   /                            # Sinh viên nộp đơn lưu trú mới
│   ├── GET    /my                          # Sinh viên xem đơn của mình
│   ├── GET    /my-room                     # Sinh viên xem phòng/giường hiện tại
│   └── PATCH  /{id}/{action}               # Duyệt (approve) hoặc Từ chối (reject)
├── /ai
│   ├── POST   /chat                        # Chatbot hỏi đáp nội quy qua RAG
│   ├── POST   /auto-allocate               # AI Gợi ý Xếp phòng Tự động (3 tiêu chí)
│   ├── POST   /classify-incident           # AI Phân loại & Tóm tắt Sự cố (<=15 từ)
│   └── POST   /room-suggestion             # AI giải thích phòng phù hợp
├── /complaints
│   ├── GET    /                            # Danh sách phản ánh sự cố
│   ├── POST   /                            # Gửi phản ánh (tự động chạy AI)
│   ├── POST   /{id}/summarize              # AI tóm tắt & gán nhãn sự cố theo yêu cầu
│   └── PATCH  /{id}/status                 # Cập nhật trạng thái xử lý
├── /contracts
│   ├── GET    /                            # Danh sách hợp đồng
│   ├── POST   /                            # Tạo hợp đồng mới
│   └── GET    /students                    # Danh sách sinh viên đã có phòng
├── /finance
│   ├── GET    /fees                        # Danh sách khoản thu
│   ├── POST   /fees                        # Thêm khoản thu phí mới
│   ├── PATCH  /fees/{id}/pay               # Xác nhận đã nộp tiền
│   └── GET    /summary                     # Tổng hợp số liệu tài chính
├── /policies
│   ├── GET    /                            # Danh sách nội quy
│   ├── POST   /                            # Thêm nội quy mới
│   └── DELETE /{id}                        # Xóa nội quy
└── /stats
    └── GET    /                            # Thống kê tổng hợp thời gian thực
```

---

### 5.3. Giao diện Kết nối Dịch vụ AI (External AI Service)
- **Phương thức tích hợp:** Gọi REST API thông qua thư viện `openai`.
- **System & User Prompts:** Sử dụng các khuôn mẫu prompt chuẩn hóa được đặc tả chi tiết tại tài liệu [AI_PROMPTS.md](file:///d:/Ứng%20dụng%20trí%20tuệ%20nhân%20tạo/code/KTX/AI_PROMPTS.md).
- **Ràng buộc đầu ra:** Định dạng JSON thuần túy (Clean Raw JSON), hỗ trợ hàm tiện ích `clean_json_output()` bóc tách tự động khi có code fence.

---

## 6. MA TRẬN ĐÁNH GIÁ & MỨC ĐỘ ƯU TIÊN YÊU CẦU (PRIORITY MATRIX)

Phân loại các yêu cầu theo thang đo chuẩn **MoSCoW**:
- **Must Have (Bắt buộc phải có):** Các chức năng cốt lõi để hệ thống vận hành tối thiểu.
- **Should Have (Nên có):** Các tính năng thông minh tạo nên giá trị đột phá của KTX-AI.
- **Could Have (Có thể có):** Các tính năng nâng cao tiện ích cho người dùng.
- **Won't Have (Chưa thực hiện ở phiên bản này):** Dành cho các phiên bản tương lai.

| Mã Yêu cầu | Tên Yêu cầu Hệ thống | Phân loại MoSCoW | Trạng thái Hiện tại |
|---|---|---|---|
| **FR-01** | Xác thực JWT & Phân quyền 3 vai trò | **Must Have** | Đã hoàn thành 100% |
| **FR-02** | Quản lý Tòa nhà, Phòng & Tự động tạo Giường | **Must Have** | Đã hoàn thành 100% |
| **FR-03** | Quản lý Sinh viên & Tự động cấp Tài khoản | **Must Have** | Đã hoàn thành 100% |
| **FR-04** | Đăng ký & Duyệt đơn lưu trú, cập nhật Giường | **Must Have** | Đã hoàn thành 100% |
| **FR-05** | **AI Gợi ý Xếp phòng Tự động (3 nguyên tắc)** | **Must Have** | Đã hoàn thành 100% |
| **FR-06** | **AI Phân loại & Tóm tắt Sự cố ($\le 15$ từ)** | **Must Have** | Đã hoàn thành 100% |
| **FR-07** | **Chatbot AI Tra cứu Nội quy KTX (RAG)** | **Should Have** | Đã hoàn thành 100% |
| **FR-08** | Lập & Theo dõi Hợp đồng Lưu trú | **Should Have** | Đã hoàn thành 100% |
| **FR-09** | Quản lý Tài chính, Khoản thu & Xác nhận Thu | **Must Have** | Đã hoàn thành 100% |
| **FR-10** | Báo cáo Thống kê Động từ CSDL | **Should Have** | Đã hoàn thành 100% |
| **NFR-02** | Cơ chế Dự phòng (Fallback Algorithm) khi mất mạng/API Key | **Must Have** | Đã hoàn thành 100% |
| **NFR-03** | Mã hóa Argon2 & Bảo vệ Endpoint nhạy cảm | **Must Have** | Đã hoàn thành 100% |
| **EXT-01** | Tích hợp Cổng Thanh toán Trực tuyến (VNPAY/Momo) | *Won't Have* | Dành cho Phiên bản 2.0 |
| **EXT-02** | Ứng dụng Di động Native (Mobile App) | *Won't Have* | Dành cho Phiên bản 2.0 |

