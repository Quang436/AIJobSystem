from pydantic import BaseModel
from typing import Optional

class ReviewCreate(BaseModel):
    reviewee_id: int
    job_id: Optional[int] = None
    rating: int  # 1-5
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    reviewer_id: int
    reviewer_name: str
    reviewee_id: int
    job_id: Optional[int]
    rating: int
    comment: Optional[str]
    created_at: str
