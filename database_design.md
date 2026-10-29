# THIẾT KẾ CƠ SỞ DỮ LIỆU (DATABASE DESIGN)
## HỆ THỐNG QUẢN LÝ KÝ TÚC XÁ THÔNG MINH (KTX-AI)

**Học phần:** Ứng dụng Trí tuệ Nhân tạo  
**Hệ quản trị CSDL:** SQLite 3 (ORM: SQLAlchemy 2.0)  
**File CSDL:** `backend/ktx_ai.db`  
**Phiên bản tài liệu:** 1.0  

---

## MỤC LỤC
1. [Tổng quan Kiến trúc Dữ liệu](#1-tổng-quan-kiến-trúc-dữ-liệu)
2. [Sơ đồ Thực thể - Mối quan hệ (ERD)](#2-sơ-đồ-thực-thể---mối-quan-hệ-erd)
3. [Từ điển Dữ liệu Chi tiết (Data Dictionary)](#3-từ-điển-dữ-liệu-chi-tiết-data-dictionary)
   - [3.1. Bảng `users` (Tài khoản người dùng)](#31-bảng-users-tài-khoản-người-dùng)
   - [3.2. Bảng `students` (Hồ sơ sinh viên)](#32-bảng-students-hồ-sơ-sinh-viên)
   - [3.3. Bảng `buildings` (Tòa nhà KTX)](#33-bảng-buildings-tòa-nhà-ktx)
   - [3.4. Bảng `rooms` (Phòng ở)](#34-bảng-rooms-phòng-ở)
   - [3.5. Bảng `beds` (Giường ký túc xá)](#35-bảng-beds-giường-ký-túc-xá)
   - [3.6. Bảng `stay_requests` (Yêu cầu lưu trú)](#36-bảng-stay_requests-yêu-cầu-lưu-trú)
   - [3.7. Bảng `contracts` (Hợp đồng lưu trú)](#37-bảng-contracts-hợp-đồng-lưu-trú)
   - [3.8. Bảng `fees` (Khoản thu / Công nợ phí)](#38-bảng-fees-khoản-thu--công-nợ-phí)
   - [3.9. Bảng `complaints` (Phản ánh & Sự cố KTX - Tích hợp AI)](#39-bảng-complaints-phản-ánh--sự-cố-ktx---tích-hợp-ai)
   - [3.10. Bảng `violations` (Ghi nhận nề nếp / Vi phạm)](#310-bảng-violations-ghi-nhận-nề-nếp--vi-phạm)
   - [3.11. Bảng `policies` (Kho tri thức nội quy - RAG Chatbot)](#311-bảng-policies-kho-tri-thức-nội-quy---rag-chatbot)
4. [Các Ràng buộc Nghiệp vụ & Toàn vẹn Dữ liệu](#4-các-ràng-buộc-nghiệp-vụ--toàn-vẹn-dữ-liệu)
5. [Tích hợp Trí tuệ Nhân tạo vào Cấu trúc CSDL](#5-tích-hợp-trí-tuệ-nhân-tạo-vào-cấu-trúc-csdl)
6. [Chiến lược Đánh chỉ mục & Tối ưu hóa truy vấn](#6-chiến-lược-đánh-chỉ-mục--tối-ưu-hóa-truy-vấn)
7. [Bảo trì, Sao lưu & Lộ trình Nâng cấp CSDL](#7-bảo-trì-sao-lưu--lộ-trình-nâng-cấp-csdl)

---

## 1. TỔNG QUAN KIẾN TRÚC DỮ LIỆU

Hệ thống **KTX-AI** phục vụ công tác quản lý toàn diện ký túc xá kết hợp với các mô hình Trí tuệ nhân tạo (Generative AI & RAG). 

- **Môi trường lưu trữ:** SQLite 3 gọn nhẹ, không yêu cầu cài đặt server riêng biệt, phù hợp triển khai nhanh và thử nghiệm nghiên cứu.
- **Tầng ánh xạ dữ liệu (ORM):** SQLAlchemy 2.0 áp dụng cú pháp `Mapped` và `mapped_column`, mang lại khả năng kiểm soát kiểu dữ liệu tĩnh (Static Typing) và tự động tạo bảng thông qua `Base.metadata.create_all(engine)`.
- **Cơ chế luồng (Threading):** Thiết lập `connect_args={"check_same_thread": False}` nhằm hỗ trợ xử lý đa luồng bất đồng bộ trên nền FastAPI.
- **Mục tiêu thiết kế:** Đạt chuẩn dạng chuẩn 3 (3NF), phân định rõ ràng giữa thực thể hạ tầng (Tòa nhà, Phòng, Giường), thực thể con người (Tài khoản, Sinh viên), các giao dịch nghiệp vụ (Lưu trú, Hợp đồng, Tài chính) và các bảng hỗ trợ AI (Phản ánh sự cố, Nội quy RAG).

---

## 2. SƠ ĐỒ THỰC THỂ - MỐI QUAN HỆ (ERD)

```mermaid
erDiagram
    BUILDINGS ||--|{ ROOMS : "chứa"
    ROOMS ||--|{ BEDS : "gồm có (cascade delete)"
    BEDS ||--o| STUDENTS : "được gán cho (current_bed_id)"
    STUDENTS ||--o| USERS : "liên kết tài khoản"
    STUDENTS ||--o{ STAY_REQUESTS : "gửi yêu cầu"
    STUDENTS ||--o{ CONTRACTS : "ký hợp đồng"
    STUDENTS ||--o{ FEES : "phát sinh phí"
    STUDENTS ||--o{ COMPLAINTS : "gửi phản ánh sự cố"
    STUDENTS ||--o{ VIOLATIONS : "ghi nhận vi phạm"

    BUILDINGS {
        int id PK
        string code UK "Mã tòa"
        string name "Tên tòa"
        int floors "Số tầng"
    }

    ROOMS {
        int id PK
        string code UK "Mã phòng"
        int building_id FK "Tòa nhà"
        int capacity "Sức chứa"
        int floor "Tầng"
        string gender "Giới tính quy định"
        string status "Trạng thái hoạt động"
    }

    BEDS {
        int id PK
        int room_id FK "Thuộc phòng"
        int bed_no "Số thứ tự giường"
        string status "Trống / Đang ở"
    }

    STUDENTS {
        int id PK
        string mssv UK "Mã số sinh viên"
        string full_name "Họ và tên"
        string class_name "Lớp / Ngành / Khóa"
        string phone "Số điện thoại"
        string status "Đang ở / Chưa xếp / Đã trả"
        int current_bed_id FK "Giường hiện tại"
    }

    USERS {
        int id PK
        string username UK "Tên đăng nhập"
        string password_hash "Mật khẩu mã hóa"
        string role "quanly / ketoan / sinhvien"
        string full_name "Tên hiển thị"
        int student_id FK "Liên kết sinh viên"
        boolean active "Trạng thái kích hoạt"
    }

    STAY_REQUESTS {
        int id PK
        int student_id FK "Sinh viên gửi"
        string request_type "Đăng ký / Chuyển / Trả"
        string desired_room "Phòng mong muốn"
        string current_room "Phòng hiện tại"
        text note "Ghi chú nguyện vọng"
        string status "Chờ duyệt / Đã duyệt / Từ chối"
        datetime created_at "Thời gian tạo"
    }

    CONTRACTS {
        int id PK
        string code UK "Mã hợp đồng"
        int student_id FK "Sinh viên"
        string room_code "Mã phòng ở"
        date start_date "Ngày bắt đầu"
        date end_date "Ngày kết thúc"
        string status "Đang hiệu lực / Hết hạn"
    }

    FEES {
        int id PK
        int student_id FK "Sinh viên"
        string month "Tháng thu (MM/YYYY)"
        float amount "Số tiền"
        date due_date "Hạn nộp"
        string status "Chưa thu / Đã thu"
    }

    COMPLAINTS {
        int id PK
        string code UK "Mã phản ánh"
        int student_id FK "Sinh viên gửi"
        text content "Nội dung phản ánh thô"
        string category "Nhóm sự cố (AI gán nhãn)"
        string status "Chưa xử lý / Đang / Đã xử lý"
        text ai_summary "Tóm tắt sự cố (AI <=15 từ)"
        datetime created_at "Thời gian gửi"
    }

    VIOLATIONS {
        int id PK
        int student_id FK "Sinh viên vi phạm"
        text content "Nội dung vi phạm"
        string status "Chờ xử lý / Đã xử lý"
        datetime created_at "Thời gian ghi nhận"
    }

    POLICIES {
        int id PK
        string code UK "Mã điều khoản"
        string title "Tiêu đề nội quy"
        text content "Nội dung chi tiết quy định"
        boolean active "Hiệu lực tra cứu"
    }
```

---

## 3. TỪ ĐIỂN DỮ LIỆU CHI TIẾT (DATA DICTIONARY)

### 3.1. Bảng `users` (Tài khoản người dùng)
Quản lý thông tin xác thực, phân quyền truy cập hệ thống (Role-Based Access Control).

| Tên trường | Kiểu dữ liệu | Khóa / Chỉ mục | Nullable | Mặc định | Ý nghĩa & Nghiệp vụ |
|---|---|---|---|---|---|
| `id` | `INTEGER` | **PK**, Auto Increment | No | - | Định danh duy nhất của tài khoản |
| `username` | `VARCHAR(50)` | **Unique**, Index | No | - | Tên đăng nhập (quản lý, kế toán hoặc MSSV của sinh viên) |
| `password_hash` | `VARCHAR(255)` | - | No | - | Mật khẩu băm an toàn (Argon2 / PBKDF2) |
| `role` | `VARCHAR(20)` | Index | No | - | Vai trò người dùng: `quanly`, `ketoan`, `sinhvien` |
| `full_name` | `VARCHAR(120)` | - | No | - | Họ và tên hiển thị trên giao diện |
| `student_id` | `INTEGER` | **FK** $\rightarrow$ `students(id)` | Yes | `NULL` | Khóa ngoại trỏ tới hồ sơ sinh viên nếu tài khoản thuộc vai trò `sinhvien` |
| `active` | `BOOLEAN` | - | No | `TRUE` | Trạng thái kích hoạt tài khoản (`TRUE`: Đang hoạt động, `FALSE`: Bị khóa) |

---

### 3.2. Bảng `students` (Hồ sơ sinh viên)
Lưu trữ thông tin nhân khẩu học và học tập của sinh viên đăng ký lưu trú ký túc xá.

| Tên trường | Kiểu dữ liệu | Khóa / Chỉ mục | Nullable | Mặc định | Ý nghĩa & Nghiệp vụ |
|---|---|---|---|---|---|
| `id` | `INTEGER` | **PK**, Auto Increment | No | - | Định danh duy nhất của sinh viên trong hệ thống |
| `mssv` | `VARCHAR(30)` | **Unique**, Index | No | - | Mã số sinh viên chính thức do nhà trường cấp |
| `full_name` | `VARCHAR(120)` | - | No | - | Họ và tên đầy đủ của sinh viên |
| `class_name` | `VARCHAR(80)` | - | No | `""` | Tên lớp / Ngành đào tạo / Khóa học (vd: `KTPM K23A`, `CNTT K22B`) |
| `phone` | `VARCHAR(30)` | - | No | `""` | Số điện thoại liên hệ khẩn cấp |
| `status` | `VARCHAR(30)` | - | No | `"Đang ở"` | Trạng thái lưu trú: `Chưa xếp phòng`, `Đang ở`, `Đã trả phòng` |
| `current_bed_id`| `INTEGER` | **FK** $\rightarrow$ `beds(id)` | Yes | `NULL` | Mã giường sinh viên đang nằm (nếu `NULL` là chưa có giường) |

---

### 3.3. Bảng `buildings` (Tòa nhà KTX)
Quản lý các tòa nhà ký túc xá trong khuôn viên.

| Tên trường | Kiểu dữ liệu | Khóa / Chỉ mục | Nullable | Mặc định | Ý nghĩa & Nghiệp vụ |
|---|---|---|---|---|---|
| `id` | `INTEGER` | **PK**, Auto Increment | No | - | Định danh tòa nhà |
| `code` | `VARCHAR(20)` | **Unique** | No | - | Mã ký hiệu tòa nhà (vd: `A1`, `B2`, `K3`) |
| `name` | `VARCHAR(100)` | - | No | - | Tên đầy đủ của tòa nhà (vd: `Ký túc xá Nam Tòa A1`) |
| `floors` | `INTEGER` | - | No | `1` | Tổng số tầng của tòa nhà |

---

### 3.4. Bảng `rooms` (Phòng ở)
Quản lý danh mục phòng thuộc các tòa nhà, sức chứa và phân định giới tính.

| Tên trường | Kiểu dữ liệu | Khóa / Chỉ mục | Nullable | Mặc định | Ý nghĩa & Nghiệp vụ |
|---|---|---|---|---|---|
| `id` | `INTEGER` | **PK**, Auto Increment | No | - | Định danh phòng |
| `code` | `VARCHAR(30)` | **Unique**, Index | No | - | Mã định danh phòng (vd: `P101`, `P204`, `T1`) |
| `building_id` | `INTEGER` | **FK** $\rightarrow$ `buildings(id)` | No | - | Tòa nhà chứa phòng |
| `capacity` | `INTEGER` | - | No | - | Sức chứa tối đa (số giường thiết kế: 4, 6, 8 chỗ) |
| `floor` | `INTEGER` | - | No | - | Vị trí tầng của phòng |
| `gender` | `VARCHAR(20)` | - | No | `"Nam/Nữ"` | Quy định giới tính của phòng: `Nam`, `Nữ`, `Nam/Nữ` |
| `status` | `VARCHAR(30)` | - | No | `"Hoạt động"` | Tình trạng phòng: `Hoạt động`, `Sửa chữa`, `Tạm ngưng` |

---

### 3.5. Bảng `beds` (Giường ký túc xá)
Quản lý chi tiết từng vị trí giường trong phòng. Khi tạo phòng mới, hệ thống tự động sinh số giường theo sức chứa (`capacity`).

| Tên trường | Kiểu dữ liệu | Khóa / Chỉ mục | Nullable | Mặc định | Ý nghĩa & Nghiệp vụ |
|---|---|---|---|---|---|
| `id` | `INTEGER` | **PK**, Auto Increment | No | - | Định danh giường |
| `room_id` | `INTEGER` | **FK** $\rightarrow$ `rooms(id)` | No | - | Thuộc phòng nào (xóa phòng sẽ xóa giường - Cascade Delete) |
| `bed_no` | `INTEGER` | - | No | - | Số thứ tự giường trong phòng (1, 2, 3...) |
| `status` | `VARCHAR(30)` | - | No | `"Trống"` | Trạng thái giường: `Trống`, `Đang ở`, `Bảo trì` |

---

### 3.6. Bảng `stay_requests` (Yêu cầu lưu trú)
Quản lý các đơn đăng ký ở mới, đơn xin chuyển phòng hoặc trả phòng của sinh viên.

| Tên trường | Kiểu dữ liệu | Khóa / Chỉ mục | Nullable | Mặc định | Ý nghĩa & Nghiệp vụ |
|---|---|---|---|---|---|
| `id` | `INTEGER` | **PK**, Auto Increment | No | - | Định danh yêu cầu lưu trú |
| `student_id` | `INTEGER` | **FK** $\rightarrow$ `students(id)` | No | - | Sinh viên nộp đơn yêu cầu |
| `request_type` | `VARCHAR(30)` | - | No | - | Loại đơn: `Đăng ký ở`, `Chuyển phòng`, `Trả phòng` |
| `desired_room` | `VARCHAR(30)` | - | Yes | `NULL` | Phòng mong muốn được chuyển đến hoặc đăng ký |
| `current_room` | `VARCHAR(30)` | - | Yes | `NULL` | Phòng hiện tại sinh viên đang ở (nếu có) |
| `note` | `TEXT` | - | No | `""` | Nguyện vọng chi tiết (loại phòng, ở cùng bạn...) |
| `status` | `VARCHAR(30)` | - | No | `"Chờ duyệt"` | Tiến trình duyệt: `Chờ duyệt`, `Đã duyệt`, `Từ chối` |
| `created_at` | `DATETIME` | - | No | `utcnow()` | Thời điểm gửi đơn |

---

### 3.7. Bảng `contracts` (Hợp đồng lưu trú)
Lưu trữ văn bản hợp đồng ràng buộc giữa ký túc xá và sinh viên đã được bố trí phòng.

| Tên trường | Kiểu dữ liệu | Khóa / Chỉ mục | Nullable | Mặc định | Ý nghĩa & Nghiệp vụ |
|---|---|---|---|---|---|
| `id` | `INTEGER` | **PK**, Auto Increment | No | - | Định danh hợp đồng |
| `code` | `VARCHAR(40)` | **Unique** | No | - | Số hiệu hợp đồng (vd: `HD102938`) |
| `student_id` | `INTEGER` | **FK** $\rightarrow$ `students(id)` | No | - | Sinh viên ký hợp đồng |
| `room_code` | `VARCHAR(30)` | - | No | - | Mã phòng được thuê theo hợp đồng |
| `start_date` | `DATE` | - | No | - | Ngày bắt đầu có hiệu lực |
| `end_date` | `DATE` | - | No | - | Ngày hết hạn hợp đồng |
| `status` | `VARCHAR(30)` | - | No | `"Đang hiệu lực"`| Hiệu lực: `Đang hiệu lực`, `Hết hạn`, `Đã thanh lý` |

---

### 3.8. Bảng `fees` (Khoản thu / Công nợ phí)
Quản lý các khoản phí phòng, điện nước theo từng chu kỳ tháng của sinh viên.

| Tên trường | Kiểu dữ liệu | Khóa / Chỉ mục | Nullable | Mặc định | Ý nghĩa & Nghiệp vụ |
|---|---|---|---|---|---|
| `id` | `INTEGER` | **PK**, Auto Increment | No | - | Định danh khoản thu |
| `student_id` | `INTEGER` | **FK** $\rightarrow$ `students(id)` | No | - | Sinh viên có nghĩa vụ thanh toán |
| `month` | `VARCHAR(7)` | - | No | - | Kỳ thu phí theo định dạng `MM/YYYY` (vd: `10/2026`) |
| `amount` | `FLOAT` | - | No | - | Số tiền phải đóng (VNĐ) |
| `due_date` | `DATE` | - | No | - | Hạn cuối đóng tiền |
| `status` | `VARCHAR(30)` | - | No | `"Chưa thu"` | Tình trạng: `Chưa thu`, `Đã thu` |

---

### 3.9. Bảng `complaints` (Phản ánh & Sự cố KTX - Tích hợp AI)
Lưu trữ phản ánh từ sinh viên kèm kết quả xử lý của module Trí tuệ nhân tạo (Gán nhãn tự động & Tóm tắt $\le 15$ từ).

| Tên trường | Kiểu dữ liệu | Khóa / Chỉ mục | Nullable | Mặc định | Ý nghĩa & Nghiệp vụ |
|---|---|---|---|---|---|
| `id` | `INTEGER` | **PK**, Auto Increment | No | - | Định danh phản ánh |
| `code` | `VARCHAR(40)` | **Unique** | No | - | Mã tra cứu phản ánh (vd: `PA890323`) |
| `student_id` | `INTEGER` | **FK** $\rightarrow$ `students(id)` | No | - | Sinh viên gửi phản ánh |
| `content` | `TEXT` | - | No | - | Văn bản mô tả nguyên văn từ sinh viên |
| `category` | `VARCHAR(50)` | - | No | `"Chưa phân loại"`| **AI gán nhãn cố định**: `Điện`, `Nước`, `Cơ sở vật chất`, `An ninh`, `Khác` |
| `status` | `VARCHAR(30)` | - | No | `"Chưa xử lý"` | Tiến độ: `Chưa xử lý`, `Đang xử lý`, `Đã xử lý` |
| `ai_summary` | `TEXT` | - | No | `""` | **AI tóm tắt súc tích** $\le 15$ từ nêu rõ bản chất vấn đề và vị trí |
| `created_at` | `DATETIME` | - | No | `utcnow()` | Thời điểm sinh viên gửi |

---

### 3.10. Bảng `violations` (Ghi nhận nề nếp / Vi phạm)
Lưu trữ các lỗi vi phạm nội quy, giờ giấc, an toàn phòng cháy của sinh viên trong quá trình lưu trú.

| Tên trường | Kiểu dữ liệu | Khóa / Chỉ mục | Nullable | Mặc định | Ý nghĩa & Nghiệp vụ |
|---|---|---|---|---|---|
| `id` | `INTEGER` | **PK**, Auto Increment | No | - | Định danh biên bản vi phạm |
| `student_id` | `INTEGER` | **FK** $\rightarrow$ `students(id)` | No | - | Sinh viên vi phạm nề nếp |
| `content` | `TEXT` | - | No | - | Chi tiết hành vi vi phạm (về muộn, nấu ăn phòng...) |
| `status` | `VARCHAR(30)` | - | No | `"Chờ xử lý"` | Tình trạng: `Chờ xử lý`, `Đã trừ điểm rèn luyện` |
| `created_at` | `DATETIME` | - | No | `utcnow()` | Thời điểm lập biên bản |

---

### 3.11. Bảng `policies` (Kho tri thức nội quy - RAG Chatbot)
Cơ sở tri thức (Knowledge Base) phục vụ cơ chế Tìm kiếm tăng cường tạo sinh (RAG) cho Chatbot KTX.

| Tên trường | Kiểu dữ liệu | Khóa / Chỉ mục | Nullable | Mặc định | Ý nghĩa & Nghiệp vụ |
|---|---|---|---|---|---|
| `id` | `INTEGER` | **PK**, Auto Increment | No | - | Định danh điều khoản |
| `code` | `VARCHAR(30)` | **Unique** | No | - | Mã điều khoản (vd: `NQ-01`, `NQ-PCCC`) |
| `title` | `VARCHAR(150)` | - | No | - | Tên tiêu đề nội quy quy định |
| `content` | `TEXT` | - | No | - | Toàn văn nội dung quy định chi tiết |
| `active` | `BOOLEAN` | - | No | `TRUE` | `TRUE`: Đang áp dụng đưa vào context RAG; `FALSE`: Hết hiệu lực |

---

## 4. CÁC RÀNG BUỘC NGHIỆP VỤ & TOÀN VẸN DỮ LIỆU

### 4.1. Ràng buộc Toàn vẹn Thực thể & Tham chiếu
- **Khóa chính (Primary Key):** Toàn bộ 11 bảng đều sở hữu trường `id INTEGER PRIMARY KEY AUTOINCREMENT`.
- **Ràng buộc Duy nhất (Unique Constraints):**
  - `users.username`: Không trùng tên đăng nhập.
  - `students.mssv`: Mỗi sinh viên chỉ có một hồ sơ gốc.
  - `buildings.code` & `rooms.code`: Mã tòa nhà và mã phòng là duy nhất trên toàn hệ thống.
  - `contracts.code` & `complaints.code`: Đảm bảo tính pháp lý và tra cứu độc lập.
  - `policies.code`: Mã điều khoản nội quy duy nhất.
- **Quan hệ Xóa liên đới (Cascade Delete):**
  - Xóa một phòng (`rooms`) sẽ tự động xóa sạch các giường thuộc phòng đó (`beds`) thông qua cấu hình SQLAlchemy `cascade="all, delete-orphan"`.
  - Không cho phép xóa một sinh viên khi sinh viên đó đang có hợp đồng hoặc công nợ tài chính chưa xử lý.

### 4.2. Ràng buộc Nghiệp vụ Cốt lõi
1. **Ràng buộc Giới tính (Gender Constraint):**
   - Sinh viên Nam chỉ được xếp vào phòng có `rooms.gender = 'Nam'` hoặc `'Nam/Nữ'`.
   - Sinh viên Nữ chỉ được xếp vào phòng có `rooms.gender = 'Nữ'` hoặc `'Nam/Nữ'`.
   - Tuyệt đối không cho phép ghép lẫn Nam và Nữ trong cùng một phòng ở bất kỳ thời điểm nào.
2. **Ràng buộc Tính khả dụng của Giường (Bed Exclusivity):**
   - Một giường (`beds`) ở trạng thái `Đang ở` chỉ được liên kết với duy nhất 1 sinh viên (`students.current_bed_id`).
   - Sức chứa thực tế không bao giờ vượt quá `rooms.capacity`.
3. **Quy trình Quản lý Lưu trú (Lifecycle of Stay Request):**
   - Khi sinh viên nộp đơn đăng ký/chuyển phòng: đơn ở trạng thái `Chờ duyệt`.
   - Khi Quản lý duyệt:
     - Hệ thống kiểm tra giường trống còn lại tại phòng mong muốn (`beds.status = 'Trống'`).
     - Gán `beds.status = 'Đang ở'`.
     - Cập nhật `students.current_bed_id = new_bed.id`.
     - Nếu sinh viên đang có giường cũ, giường cũ lập tức chuyển trạng thái về `Trống`.

---

## 5. TÍCH HỢP TRÍ TUỆ NHÂN TẠO VÀO CẤU TRÚC CSDL

Kiến trúc CSDL được thiết kế tương thích trực tiếp với các module AI:

### 5.1. Module Gợi ý Xếp phòng Thông minh (`auto-allocate`)
- **Dữ liệu đầu vào AI:** Truy vấn các bản ghi `stay_requests` có `status = 'Chờ duyệt'`, kết hợp với bảng `students` để lấy `mssv`, `full_name`, `class_name` (chứa ngành/khóa), giới tính và bảng `beds` kết hợp `rooms` để lấy danh sách giường trống kèm loại phòng và giới tính.
- **Dữ liệu đầu ra:** AI phân tích và trả về cấu trúc JSON sạch, hệ thống backend đọc dữ liệu để tự động duyệt yêu cầu và gán `current_bed_id`.

### 5.2. Module Phân loại & Tóm tắt Sự cố (`complaints`)
- Trường `category`: Nhận giá trị được AI chuẩn hóa tự động vào 1 trong 5 nhóm: `Điện`, `Nước`, `Cơ sở vật chất`, `An ninh`, `Khác`.
- Trường `ai_summary`: Lưu trữ câu tóm tắt kỹ thuật ngắn gọn không quá 15 từ, giúp hiển thị tối ưu trên giao diện bảng điều khiển của cán bộ quản lý mà không bị vỡ bố cục.

### 5.3. Module Chatbot RAG (`policies`)
- Trường `content` trong bảng `policies` đóng vai trò là kho văn bản nguồn (Corpus).
- Thuật toán RAG thực hiện tìm kiếm từ khóa liên quan (Keyword/BM25 Matching) trong SQLite để trích xuất các điều khoản phù hợp nhất (`top_k=4`), ghép nối vào ngữ cảnh Prompt gửi tới AI để trả lời chính xác, kèm mã điều khoản dẫn nguồn (`sources`).

---

## 6. CHIẾN LƯỢC ĐÁNH CHỈ MỤC & TỐI ƯU HÓA TRUY VẤN

Để đảm bảo hiệu năng truy vấn nhanh chóng khi số lượng sinh viên và sự cố gia tăng, hệ thống áp dụng các chỉ mục sau:

1. **Chỉ mục Khóa chính & Unique:** Tự động tạo B-Tree Index cho `users.username`, `students.mssv`, `rooms.code`, `buildings.code`, `complaints.code`, `contracts.code`.
2. **Chỉ mục Phân quyền:** Tạo Index trên cột `users.role` để tăng tốc xác thực Token JWT và kiểm tra quyền hạn (Role Checking).
3. **Chỉ mục khuyến nghị khi mở rộng dữ liệu lớn:**
   - Tạo Index trên `complaints.created_at` để tối ưu sắp xếp lịch sử phản ánh mới nhất.
   - Tạo Composite Index trên `(room_id, status)` của bảng `beds` để truy vấn tức thì số giường trống của từng phòng:
     ```sql
     CREATE INDEX idx_beds_room_status ON beds(room_id, status);
     ```
   - Tạo Index trên `stay_requests.status` để bộ lọc đơn chờ duyệt của cán bộ quản lý đạt thời gian phản hồi dưới 5ms.

---

## 7. BẢO TRÌ, SAO LƯU & LỘ TRÌNH NÂNG CẤP CSDL

### 7.1. Sao lưu & Khôi phục (Backup & Restore)
- Do sử dụng SQLite, toàn bộ cơ sở dữ liệu được gói gọn trong file duy nhất `backend/ktx_ai.db`.
- **Sao lưu:** Sao chép file `ktx_ai.db` định kỳ hoặc trước khi thực hiện các đợt cập nhật lớn.
- **Khôi phục hoàn toàn về mặc định:** Tắt server backend, xóa file `ktx_ai.db` và chạy lệnh nạp dữ liệu mẫu:
  ```powershell
  python -m app.seed
  ```

### 7.2. Lộ trình Nâng cấp lên RDBMS phân tán
Khi hệ thống ký túc xá mở rộng lên quy mô toàn trường (trên 10.000 sinh viên) với hàng trăm lượt truy cập đồng thời:
1. Nhờ việc sử dụng SQLAlchemy 2.0 ORM, hệ thống hoàn toàn độc lập với phần cứng CSDL.
2. Để chuyển sang **PostgreSQL** hoặc **MySQL**, chỉ cần thay đổi chuỗi kết nối trong biến môi trường `.env`:
   ```env
   # SQLite hiện tại:
   DATABASE_URL=sqlite:///ktx_ai.db

   # Chuyển sang PostgreSQL:
   DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/ktx_ai
   ```
3. Toàn bộ các bảng, quan hệ và kiểu dữ liệu sẽ tự động tương thích 100% mà không cần sửa đổi bất kỳ dòng mã logic nào trong mã nguồn.

