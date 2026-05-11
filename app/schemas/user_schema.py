from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    fullname: str
    email: EmailStr
    password: str
    role: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfileUpdate(BaseModel):
    fullname: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    ready_to_work: Optional[bool] = None