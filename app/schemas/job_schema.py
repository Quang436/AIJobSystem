from pydantic import BaseModel
from typing import Optional

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
    job_type: Optional[str] = "full-time"  # full-time, part-time, freelance
    requirements: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    source_url: Optional[str] = None
    external_id: Optional[str] = None
    deadline: Optional[str] = None
    # Không cần created_by nữa vì lấy từ JWT token

class JobFilter(BaseModel):
    keyword: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None  # full-time, part-time, freelance
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    skills: Optional[str] = None
    radius_km: Optional[float] = None