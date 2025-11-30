from pydantic import BaseModel, EmailStr
from typing import Optional

# Dùng khi đăng ký
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone_number: Optional[str] = None
    #role: str  # attendee / organizer


# Dùng khi đăng nhập
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Phản hồi khi login thành công
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    email: str
    full_name: str
    phone: Optional[str] = None

# Update profile
class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
