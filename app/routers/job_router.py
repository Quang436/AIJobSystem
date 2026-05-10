from fastapi import APIRouter

from app.database.database import get_connection
from app.schemas.job_schema import JobCreate
from app.utils.location import calculate_distance
from app.services.recommend_service import recommend_jobs

router = APIRouter()

# CREATE JOB
@router.post("/jobs")

def create_job(job: JobCreate):

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
        job.created_by
    ))

    conn.commit()

    return {
        "message": "Job created"
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

def apply_job(job_id: int, user_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO applications
        (
            user_id,
            job_id
        )
        VALUES (?, ?)
    """,
    (
        user_id,
        job_id
    ))

    conn.commit()

    return {
        "message": "Apply success"
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