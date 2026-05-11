from pydantic import BaseModel

class JobCreate(BaseModel):
    title: str
    company: str
    description: str
    salary: str
    address: str
    gps_lat: float
    gps_lng: float
    skills: str
    source: str
    status: str
    # Không cần created_by nữa vì lấy từ JWT token