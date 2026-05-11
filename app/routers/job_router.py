from fastapi import APIRouter, Depends

from app.database.database import get_connection
from app.schemas.job_schema import JobCreate
from app.utils.location import calculate_distance
from app.services.recommend_service import recommend_jobs
from app.middleware.auth_middleware import get_current_user, require_role

router = APIRouter()

# CREATE JOB - Chỉ admin và employer mới được tạo job
@router.post("/jobs")
def create_job(
    job: JobCreate,
    current_user: dict = Depends(require_role(["admin", "employer"]))
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO jobs
        (
            title,
            company,
            description,
            salary,
            address,
            gps_lat,
            gps_lng,
            skills,
            source,
            status,
            created_by
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        job.title,
        job.company,
        job.description,
        job.salary,
        job.address,
        job.gps_lat,
        job.gps_lng,
        job.skills,
        job.source,
        job.status,
        current_user["user_id"]  # Lấy user_id từ JWT token
    ))

    conn.commit()

    return {
        "message": "Job created",
        "created_by": current_user["email"]
    }

# GET ALL JOBS
@router.get("/jobs")

def get_jobs():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM jobs
    """)

    jobs = cursor.fetchall()

    result = []

    for job in jobs:

        result.append({
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "salary": job.salary,
            "address": job.address,
            "gps_lat": job.gps_lat,
            "gps_lng": job.gps_lng
            # "skills": job.skills,
            # "source": job.source,
            # "status": job.status,
            # "created_by": job.created_by
        })

    return result

# GET JOB DETAIL
@router.get("/jobs/{job_id}")

def get_job_detail(job_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM jobs
        WHERE id = ?
    """, (job_id,))

    job = cursor.fetchone()

    if not job:
        return {
            "message": "Job not found"
        }

    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "description": job.description,
        "salary": job.salary,
        "address": job.address,
        "gps_lat": job.gps_lat,
        "gps_lng": job.gps_lng,
        "skills": job.skills,
        "source": job.source,
        "status": job.status,
        "created_by": job.created_by
    }

@router.post("/apply/{job_id}")
def apply_job(
    job_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Apply job - Yêu cầu đăng nhập
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Kiểm tra xem đã apply chưa
    cursor.execute("""
        SELECT * FROM applications
        WHERE user_id = ? AND job_id = ?
    """, (current_user["user_id"], job_id))
    
    existing = cursor.fetchone()
    
    if existing:
        return {
            "message": "You already applied to this job"
        }

    cursor.execute("""
        INSERT INTO applications
        (
            user_id,
            job_id
        )
        VALUES (?, ?)
    """,
    (
        current_user["user_id"],
        job_id
    ))

    conn.commit()

    return {
        "message": "Apply success",
        "user_email": current_user["email"]
    }


# UPDATE JOB - Chỉ admin và employer mới được update
@router.put("/jobs/{job_id}")
def update_job(
    job_id: int,
    job: JobCreate,
    current_user: dict = Depends(require_role(["admin", "employer"]))
):
    """
    Update job - Chỉ admin hoặc người tạo job mới được update
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Kiểm tra job có tồn tại không
    cursor.execute("""
        SELECT created_by FROM jobs
        WHERE id = ?
    """, (job_id,))
    
    existing_job = cursor.fetchone()
    
    if not existing_job:
        return {
            "message": "Job not found"
        }
    
    # Kiểm tra quyền: chỉ admin hoặc người tạo job mới được update
    if current_user["role"] != "admin" and existing_job.created_by != current_user["user_id"]:
        return {
            "message": "You don't have permission to update this job"
        }
    
    cursor.execute("""
        UPDATE jobs
        SET
            title = ?,
            company = ?,
            description = ?,
            salary = ?,
            address = ?,
            gps_lat = ?,
            gps_lng = ?,
            skills = ?,
            source = ?,
            status = ?
        WHERE id = ?
    """,
    (
        job.title,
        job.company,
        job.description,
        job.salary,
        job.address,
        job.gps_lat,
        job.gps_lng,
        job.skills,
        job.source,
        job.status,
        job_id
    ))
    
    conn.commit()
    
    return {
        "message": "Job updated successfully",
        "updated_by": current_user["email"]
    }


# DELETE JOB - Chỉ admin và employer mới được delete
@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    current_user: dict = Depends(require_role(["admin", "employer"]))
):
    """
    Delete job - Chỉ admin hoặc người tạo job mới được delete
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Kiểm tra job có tồn tại không
    cursor.execute("""
        SELECT created_by FROM jobs
        WHERE id = ?
    """, (job_id,))
    
    existing_job = cursor.fetchone()
    
    if not existing_job:
        return {
            "message": "Job not found"
        }
    
    # Kiểm tra quyền: chỉ admin hoặc người tạo job mới được delete
    if current_user["role"] != "admin" and existing_job.created_by != current_user["user_id"]:
        return {
            "message": "You don't have permission to delete this job"
        }
    
    # Xóa các applications liên quan trước
    cursor.execute("""
        DELETE FROM applications
        WHERE job_id = ?
    """, (job_id,))
    
    # Xóa job
    cursor.execute("""
        DELETE FROM jobs
        WHERE id = ?
    """, (job_id,))
    
    conn.commit()
    
    return {
        "message": "Job deleted successfully",
        "deleted_by": current_user["email"]
    }

@router.get("/jobs-distance")

def jobs_distance():

    user_lat = 16.0544
    user_lon = 108.2022

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM jobs
    """)

    jobs = cursor.fetchall()

    result = []

    for job in jobs:

        distance = calculate_distance(
            user_lat,
            user_lon,
            job.gps_lat,
            job.gps_lng
        )

        result.append({
            "title": job.title,
            "company": job.company,
            "distance_km": distance
        })

    return result

@router.get("/recommend")
def recommend(skill: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM jobs")

    rows = cursor.fetchall()

    jobs = []

    for row in rows:
        jobs.append({
            "id": row.id,
            "title": row.title,
            "company": row.company,
            "skills": row.skills
        })

    conn.close()

    result = recommend_jobs(skill, jobs)

    return result