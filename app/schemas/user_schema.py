from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserRegister(BaseModel):
    fullname: str
    email: EmailStr
    password: str
    role: str
    job_seeker_type: Optional[str] = None
    cv_url: Optional[str] = None
    cccd_number: Optional[str] = None
    cccd_front_url: Optional[str] = None
    cccd_back_url: Optional[str] = None
    certificate_urls: Optional[str] = None
    
    experience_years: Optional[float] = None
    education_level: Optional[str] = None
    portfolio_url: Optional[str] = None
    is_freelancer: Optional[bool] = False
    available_hours: Optional[str] = None
    service_areas: Optional[str] = None
    hourly_rate: Optional[float] = None
    
    company_name: Optional[str] = None
    employer_type: Optional[str] = None
    manager_name: Optional[str] = None
    manager_phone: Optional[str] = None
    business_license_url: Optional[str] = None
    facility_images: Optional[str] = None
    
    tax_code: Optional[str] = None
    representative_name: Optional[str] = None
    establishment_date: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    headquarters_address: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfileUpdate(BaseModel):
    fullname: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    ready_to_work: Optional[bool] = None

# --- Custom Registration Schemas based on Endpoint specs ---

class CandidateCommon(BaseModel):
    full_name: str
    phone: str
    email: EmailStr
    password: str

class CandidateEducation(BaseModel):
    degree_level: str
    institution_name: str
    certificate_urls: List[str]

class CandidateCareer(BaseModel):
    desired_level: str
    industry: str
    desired_salary: int
    job_category: Optional[str] = "office"

class CandidateAttachment(BaseModel):
    cv_url: str

class CandidateRegisterReq(BaseModel):
    common_info: CandidateCommon
    education_info: CandidateEducation
    career_info: CandidateCareer
    attachment: CandidateAttachment


class GigWorkerCommon(BaseModel):
    full_name: str
    phone: str
    email: EmailStr
    password: str

class GigWorkerSkillset(BaseModel):
    professional_category: str
    skills: List[str]
    license_urls: List[str]

class GigWorkerPricing(BaseModel):
    min_price_per_task: int
    max_price_per_task: int

class GigWorkerWorkingConfig(BaseModel):
    max_travel_distance_km: float
    pricing_range: GigWorkerPricing

class LocationCoordinates(BaseModel):
    latitude: float
    longitude: float

class GigWorkerRealtimeStatus(BaseModel):
    is_available: bool
    current_location: LocationCoordinates

class GigworkerRegisterReq(BaseModel):
    common_info: GigWorkerCommon
    skill_set: GigWorkerSkillset
    working_config: GigWorkerWorkingConfig
    realtime_status: GigWorkerRealtimeStatus


class EmployerLegalInfo(BaseModel):
    tax_code: str
    legal_company_name: str

class EmployerContactVerif(BaseModel):
    hr_hotline: str
    corporate_email: EmailStr
    password: str

class BranchLocation(BaseModel):
    branch_name: str
    address: str
    coordinates: LocationCoordinates

class EmployerLocationData(BaseModel):
    headquarter_address: str
    branches: List[BranchLocation]

class EmployerMedia(BaseModel):
    logo_url: str
    office_image_urls: List[str]

class EmployerRegisterReq(BaseModel):
    legal_info: EmployerLegalInfo
    contact_verification: EmployerContactVerif
    location_data: EmployerLocationData
    media: EmployerMedia