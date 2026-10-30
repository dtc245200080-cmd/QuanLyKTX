from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: str

class StudentCreate(BaseModel):
    mssv: str = Field(min_length=1, max_length=30)
    full_name: str = Field(min_length=1, max_length=120)
    class_name: str = ""
    phone: str = ""
    password: str = "123456"

class StayRequestCreate(BaseModel):
    request_type: str = Field(pattern="^(Đăng ký ở|Chuyển phòng|Trả phòng)$")
    desired_room: Optional[str] = None
    current_room: Optional[str] = None
    note: str = ""

class ComplaintCreate(BaseModel):
    content: str = Field(min_length=5)

class ComplaintStatusUpdate(BaseModel):
    status: str = Field(pattern="^(Chưa xử lý|Đang xử lý|Đã xử lý)$")

class ChatRequest(BaseModel):
    question: str = Field(min_length=2)

class RoomSuggestionRequest(BaseModel):
    building: Optional[str] = None
    capacity: Optional[int] = None
    criteria: str = ""

class SummaryRequest(BaseModel):
    content: str = Field(min_length=5)

class PolicyCreate(BaseModel):
    code: str = Field(min_length=1, max_length=30)
    title: str = Field(min_length=1, max_length=150)
    content: str = Field(min_length=1)

class PolicyUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    content: str = Field(min_length=1)
    active: bool = True

class BuildingCreate(BaseModel):
    code: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=100)
    floors: int = Field(ge=1)

class RoomCreate(BaseModel):
    code: str = Field(min_length=1, max_length=30)
    building_code: str = Field(min_length=1, max_length=20)
    capacity: int = Field(ge=1)
    floor: int = Field(ge=1)
    gender: str = "Nam/Nữ"

class ContractCreate(BaseModel):
    student_id: int
    start_date: date
    end_date: date

class FeeCreate(BaseModel):
    student_id: int
    month: str = Field(pattern=r"^\d{2}/\d{4}$")
    amount: float = Field(gt=0)
    due_date: date
