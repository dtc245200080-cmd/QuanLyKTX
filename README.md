# KTX-AI - dữ liệu động

Project sử dụng FastAPI + SQLite. Các trang quản lý không còn chứa số liệu demo cố định.

## Chạy trên Windows PowerShell

```powershell
cd backend
python -m app.seed
uvicorn app.main:app --reload
```

Sau đó mở trình duyệt tại:

`http://127.0.0.1:8000/`

## Tài khoản ban đầu

- Quản lý: `quanly` / `123456`
- Kế toán: `ketoan` / `123456`

Tài khoản sinh viên được tạo tự động khi quản lý thêm sinh viên. Mật khẩu mặc định là `123456` nếu quản lý không nhập mật khẩu riêng.

## Thứ tự nhập dữ liệu thật

1. Quản lý thêm sinh viên.
2. Quản lý thêm tòa nhà và phòng. Hệ thống tự tạo giường theo sức chứa.
3. Sinh viên đăng nhập bằng MSSV và gửi đăng ký phòng. Quản lý duyệt, hệ thống tự gán giường và cập nhật chỗ trống.
4. Quản lý tạo hợp đồng cho sinh viên đã được xếp phòng.
5. Quản lý/kế toán tạo khoản thu thực tế và kế toán xác nhận đã thu.
6. Sinh viên gửi phản ánh, quản lý cập nhật trạng thái.
7. Quản lý nhập nội quy thật của trường/KTX.
8. Chatbot truy hồi nội quy trong SQLite để trả lời; không có nội quy phù hợp thì nói rõ không tìm thấy.
9. Trang thống kê tính trực tiếp từ database.

## Database

File SQLite được tạo tại `backend/ktx_ai.db`. Nếu muốn bắt đầu lại hoàn toàn, tắt server rồi xóa file này và chạy lại `python -m app.seed`.

Không cần Docker hoặc MySQL cho phiên bản này.
