# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, Query
from typing import Optional

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
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO jobs (title, company, description, salary_raw, address_raw, latitude, longitude, skills, source_name, status, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (job.title, job.company, job.description, job.salary, job.address, job.gps_lat, job.gps_lng, job.skills, job.source, job.status, current_user["user_id"]))
        conn.commit()
        return {"message": "Job created", "created_by": current_user["email"]}
    finally:
        conn.close()

# GET ALL JOBS
@router.get("/jobs")
def get_jobs():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, company, salary_raw, address_raw, latitude, longitude, skills, description, status FROM jobs")
        jobs = cursor.fetchall()
        result = []
        for job in jobs:
            result.append({
                "id": job[0],
                "title": job[1],
                "company": job[2],
                "salary": job[3],
                "address": job[4],
                "gps_lat": job[5],
                "gps_lng": job[6],
                "skills": job[7],
                "description": job[8],
                "status": job[9]
            })
        return result
    finally:
        conn.close()

# SEARCH JOBS - Tìm kiếm theo keyword và location với filter nâng cao
@router.get("/jobs/search")
def search_jobs(
    keyword: Optional[str] = Query(None, description="Từ khóa tìm kiếm"),
    location: Optional[str] = Query(None, description="Địa điểm"),
    job_type: Optional[str] = Query(None, description="Loại công việc: full-time, part-time, freelance"),
    salary_min: Optional[float] = Query(None, description="Mức lương tối thiểu"),
    salary_max: Optional[float] = Query(None, description="Mức lương tối đa"),
    skills: Optional[str] = Query(None, description="Kỹ năng cần tìm"),
    lat: Optional[float] = Query(None, description="Vĩ độ người dùng"),
    lng: Optional[float] = Query(None, description="Kinh độ người dùng"),
    radius: Optional[float] = Query(None, description="Bán kính tìm kiếm (km)")
):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Build dynamic query
        query = """
            SELECT id, title, company, description, salary_raw, salary_min, salary_max,
                   address_raw, latitude, longitude, skills, status, job_type, source_url
            FROM jobs WHERE 1=1
        """
        params = []
        
        if keyword:
            query += " AND (title LIKE ? OR company LIKE ? OR skills LIKE ? OR description LIKE ?)"
            like_param = f"%{keyword}%"
            params.extend([like_param, like_param, like_param, like_param])
        
        if location:
            query += " AND address_raw LIKE ?"
            params.append(f"%{location}%")
        
        # Lọc theo loại công việc
        if job_type:
            query += " AND job_type = ?"
            params.append(job_type)
        
        # Lọc theo mức lương
        if salary_min is not None:
            query += " AND (salary_min >= ? OR salary_max >= ?)"
            params.extend([salary_min, salary_min])
        
        if salary_max is not None:
            query += " AND (salary_max <= ? OR salary_min <= ?)"
            params.extend([salary_max, salary_max])
        
        # Lọc theo kỹ năng
        if skills:
            skill_list = [s.strip() for s in skills.split(',')]
            skill_conditions = []
            for skill in skill_list:
                skill_conditions.append("skills LIKE ?")
                params.append(f"%{skill}%")
            if skill_conditions:
                query += " AND (" + " OR ".join(skill_conditions) + ")"
        
        cursor.execute(query, tuple(params))
        jobs = cursor.fetchall()
        
        result = []
        for job in jobs:
            job_data = {
                "id": job[0],
                "title": job[1],
                "company": job[2],
                "description": job[3],
                "salary": job[4],
                "salary_min": job[5],
                "salary_max": job[6],
                "address": job[7],
                "gps_lat": job[8],
                "gps_lng": job[9],
                "skills": job[10],
                "status": job[11],
                "job_type": job[12],
                "source_url": job[13]
            }
            
            # Tính khoảng cách nếu có tọa độ user
            if lat is not None and lng is not None and job[8] is not None and job[9] is not None:
                distance = calculate_distance(lat, lng, job[8], job[9])
                job_data["distance_km"] = distance
                
                # Lọc theo bán kính nếu được chỉ định
                if radius is not None and distance > radius:
                    continue
            
            result.append(job_data)
        
        # Sắp xếp theo khoảng cách nếu có
        if lat is not None and lng is not None:
            result.sort(key=lambda x: x.get("distance_km", 9999))
        
        return result
    finally:
        conn.close()

@router.post("/jobs/urgent-guest")
def create_urgent_guest_job(
    title: str,
    description: str,
    phone: str,
    address: str,
    gps_lat: float,
    gps_lng: float,
    skills: str = ""
):
    """API cho phép khách hàng đăng tin khẩn cấp không cần đăng nhập"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO jobs (title, company, description, salary_raw, address_raw, latitude, longitude, skills, source_name, source_type, status, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title, 
            f"Khách lẻ ({phone})", 
            description, 
            "Thỏa thuận", 
            address, 
            gps_lat, 
            gps_lng, 
            skills, 
            'guest_urgent', 
            'freelance',
            'approved', 
            phone
        ))
        conn.commit()
        return {"message": "Urgent job posted successfully. Nearby workers will be notified."}
    finally:
        conn.close()

# GET DISTINCT JOB TYPES - Dùng để hiển thị danh mục trên trang đầu
@router.get("/jobs/types")
def get_job_types():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT job_type FROM jobs WHERE job_type IS NOT NULL")
        rows = cursor.fetchall()
        # rows is list of tuples, extract first element
        types = [row[0] for row in rows if row[0]]
        return {"job_types": types}
    finally:
        conn.close()

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, company, salary_raw, address_raw, latitude, longitude FROM jobs WHERE latitude IS NOT NULL AND longitude IS NOT NULL")
        jobs = cursor.fetchall()
        
        markers = []
        for job in jobs:
            markers.append({
                "id": job[0],
                "title": job[1],
                "company": job[2],
                "salary": job[3],
                "address": job[4],
                "lat": job[5],
                "lng": job[6]
            })
        
        # Tính trung tâm bản đồ
        if markers:
            center_lat = sum(m["lat"] for m in markers) / len(markers)
            center_lng = sum(m["lng"] for m in markers) / len(markers)
        else:
            center_lat = 16.0544  # Đà Nẵng mặc định
            center_lng = 108.2022
        
        return {
            "center_lat": center_lat,
            "center_lng": center_lng,
            "markers": markers
        }
    finally:
        conn.close()

# GET EMPLOYER'S JOBS - trả về công việc do doanh nghiệp tạo
@router.get("/jobs/employer")
def get_employer_jobs(current_user: dict = Depends(require_role(["employer"]))):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, company, salary_raw, address_raw, latitude, longitude, skills, description, status FROM jobs WHERE created_by = ?",
            (current_user["user_id"],)
        )
        jobs = cursor.fetchall()
        result = []
        for job in jobs:
            result.append({
                "id": job[0],
                "title": job[1],
                "company": job[2],
                "salary": job[3],
                "address": job[4],
                "gps_lat": job[5],
                "gps_lng": job[6],
                "skills": job[7],
                "description": job[8],
                "status": job[9]
            })
        return result
    finally:
        conn.close()

# GET JOB DETAIL
@router.get("/jobs/{job_id}")
def get_job_detail(job_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, company, description, salary_raw, address_raw, latitude, longitude, skills, source_name, status, created_by FROM jobs WHERE id = ?", (job_id,))
        job = cursor.fetchone()
        if not job:
            return {"message": "Job not found"}
        return {
            "id": job[0], "title": job[1], "company": job[2], "description": job[3],
            "salary": job[4], "address": job[5], "gps_lat": job[6], "gps_lng": job[7],
            "skills": job[8], "source": job[9], "status": job[10], "created_by": job[11]
        }
    finally:
        conn.close()

@router.post("/apply/{job_id}")
def apply_job(
    job_id: int,
    current_user: dict = Depends(get_current_user)
):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM job_applications WHERE user_id = ? AND job_id = ?", (current_user["user_id"], job_id))
        if cursor.fetchone():
            return {"message": "You already applied to this job"}
        
        cursor.execute("INSERT INTO job_applications (user_id, job_id) VALUES (?, ?)", (current_user["user_id"], job_id))
        
        # Lấy thông tin chủ job để thông báo
        cursor.execute("SELECT created_by, title FROM jobs WHERE id = ?", (job_id,))
        job_info = cursor.fetchone()
        if job_info and job_info[0]:
            employer_id = job_info[0]
            job_title = job_info[1]
            cursor.execute("""
                INSERT INTO notifications (user_id, title, message, type)
                VALUES (?, ?, ?, ?)
            """, (
                employer_id,
                "Ứng viên mới!",
                f"Ứng viên {current_user['email']} vừa ứng tuyển vào công việc '{job_title}' của bạn.",
                "new_application"
            ))
            
        conn.commit()
        return {"message": "Apply success", "user_email": current_user["email"]}
    finally:
        conn.close()

@router.put("/jobs/{job_id}")
def update_job(
    job_id: int,
    job: JobCreate,
    current_user: dict = Depends(require_role(["admin", "employer"]))
):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT created_by FROM jobs WHERE id = ?", (job_id,))
        existing_job = cursor.fetchone()
        if not existing_job:
            return {"message": "Job not found"}
        if current_user["role"] != "admin" and existing_job.created_by != current_user["user_id"]:
            return {"message": "You don't have permission to update this job"}
        cursor.execute("""
            UPDATE jobs SET title = ?, company = ?, description = ?, salary_raw = ?, address_raw = ?, latitude = ?, longitude = ?, skills = ?, source_name = ?, status = ?
            WHERE id = ?
        """, (job.title, job.company, job.description, job.salary, job.address, job.gps_lat, job.gps_lng, job.skills, job.source, job.status, job_id))
        conn.commit()
        return {"message": "Job updated successfully", "updated_by": current_user["email"]}
    finally:
        conn.close()

@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    current_user: dict = Depends(require_role(["admin", "employer"]))
):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT created_by FROM jobs WHERE id = ?", (job_id,))
        existing_job = cursor.fetchone()
        if not existing_job:
            return {"message": "Job not found"}
        if current_user["role"] != "admin" and existing_job.created_by != current_user["user_id"]:
            return {"message": "You don't have permission to delete this job"}
        cursor.execute("DELETE FROM job_applications WHERE job_id = ?", (job_id,))
        cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        conn.commit()
        return {"message": "Job deleted successfully", "deleted_by": current_user["email"]}
    finally:
        conn.close()

@router.get("/jobs-distance")
def jobs_distance(
    lat: Optional[float] = Query(16.0544, description="Vĩ độ người dùng"),
    lng: Optional[float] = Query(108.2022, description="Kinh độ người dùng")
):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT title, company, latitude, longitude FROM jobs")
        jobs = cursor.fetchall()
        result = []
        for job in jobs:
            if job.latitude and job.longitude:
                distance = calculate_distance(lat, lng, job.latitude, job.longitude)
                result.append({"title": job.title, "company": job.company, "distance_km": distance})
        result.sort(key=lambda x: x["distance_km"])
        return result
    finally:
        conn.close()

@router.get("/recommend")
def recommend(skill: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, company, skills FROM jobs")
        rows = cursor.fetchall()
        jobs = [{"id": row.id, "title": row.title, "company": row.company, "skills": row.skills} for row in rows]
        return recommend_jobs(skill, jobs)
    finally:
        conn.close()

# ADMIN STATS - Thống kê cho admin dashboard
@router.get("/admin/stats")
def get_admin_stats(
    current_user: dict = Depends(require_role(["admin"]))
):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM jobs")
        total_jobs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM job_applications")
        total_applications = cursor.fetchone()[0]
        
        # Công việc đang active
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE status = 'active'")
        active_jobs = cursor.fetchone()[0]
        
        # 5 đơn ứng tuyển gần nhất
        cursor.execute("""
            SELECT TOP 5 a.id, u.full_name, j.title, a.status, a.applied_at
            FROM job_applications a
            JOIN users u ON a.user_id = u.id
            JOIN jobs j ON a.job_id = j.id
            ORDER BY a.applied_at DESC
        """)
        recent_apps = []
        for row in cursor.fetchall():
            recent_apps.append({
                "id": row[0],
                "user_name": row[1],
                "job_title": row[2],
                "status": row[3],
                "applied_at": str(row[4])
            })
        
        # 5 user mới nhất
        cursor.execute("""
            SELECT TOP 5 id, full_name, email, role, created_at
            FROM users ORDER BY created_at DESC
        """)
        recent_users = []
        for row in cursor.fetchall():
            recent_users.append({
                "id": row[0],
                "fullname": row[1],
                "email": row[2],
                "role": row[3],
                "created_at": str(row[4])
            })
        
        return {
            "total_users": total_users,
            "total_jobs": total_jobs,
            "total_applications": total_applications,
            "active_jobs": active_jobs,
            "recent_applications": recent_apps,
            "recent_users": recent_users
        }
    finally:
        conn.close()

# MY APPLICATIONS - Đơn ứng tuyển của user hiện tại
@router.get("/my-applications")
def get_my_applications(
    current_user: dict = Depends(get_current_user)
):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, j.title, j.company, j.salary_raw, j.address_raw, a.status, a.applied_at
            FROM job_applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE a.user_id = ?
            ORDER BY a.applied_at DESC
        """, (current_user["user_id"],))
        
        result = []
        for row in cursor.fetchall():
            result.append({
                "id": row[0],
                "job_title": row[1],
                "company": row[2],
                "salary": row[3],
                "address": row[4],
                "status": row[5],
                "applied_at": str(row[6])
            })
        return result
    finally:
        conn.close()

# EMPLOYER: Lấy danh sách ứng viên đã apply vào công việc
@router.get("/jobs/{job_id}/applications")
def get_job_applications(
    job_id: int,
    current_user: dict = Depends(require_role(["employer", "admin"]))
):
    """Lấy danh sách ứng viên đã ứng tuyển vào công việc"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Kiểm tra quyền sở hữu job
        cursor.execute("SELECT created_by FROM jobs WHERE id = ?", (job_id,))
        job = cursor.fetchone()
        if not job:
            return {"message": "Job not found"}
        
        if current_user["role"] != "admin" and job[0] != current_user["user_id"]:
            return {"message": "You don't have permission to view applications for this job"}
        
        # Lấy danh sách applications
        cursor.execute("""
            SELECT a.id, a.user_id, u.full_name, u.email, u.phone, 
                   u.cv_file_url, u.average_rating, u.total_reviews,
                   a.status, a.applied_at, a.cover_letter
            FROM job_applications a
            JOIN users u ON a.user_id = u.id
            WHERE a.job_id = ?
            ORDER BY a.applied_at DESC
        """, (job_id,))
        
        applications = []
        for row in cursor.fetchall():
            applications.append({
                "application_id": row[0],
                "user_id": row[1],
                "full_name": row[2],
                "email": row[3],
                "phone": row[4],
                "cv_url": row[5],
                "rating": row[6],
                "total_reviews": row[7],
                "status": row[8],
                "applied_at": str(row[9]),
                "cover_letter": row[10]
            })
        
        return {
            "job_id": job_id,
            "total_applications": len(applications),
            "applications": applications
        }
    finally:
        conn.close()

# EMPLOYER: Cập nhật trạng thái application
@router.put("/applications/{application_id}/status")
def update_application_status(
    application_id: int,
    status: str,  # pending, reviewing, accepted, rejected
    current_user: dict = Depends(require_role(["employer", "admin"]))
):
    """Cập nhật trạng thái đơn ứng tuyển"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Kiểm tra application tồn tại và quyền
        cursor.execute("""
            SELECT a.job_id, j.created_by, a.user_id
            FROM job_applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE a.id = ?
        """, (application_id,))
        
        app_data = cursor.fetchone()
        if not app_data:
            return {"message": "Application not found"}
        
        job_id, job_creator, applicant_id = app_data
        
        if current_user["role"] != "admin" and job_creator != current_user["user_id"]:
            return {"message": "You don't have permission to update this application"}
        
        # Cập nhật status
        cursor.execute("""
            UPDATE job_applications 
            SET status = ?, updated_at = GETUTCDATE()
            WHERE id = ?
        """, (status, application_id))
        
        # Tạo thông báo cho ứng viên
        cursor.execute("SELECT title FROM jobs WHERE id = ?", (job_id,))
        job_title = cursor.fetchone()[0]
        
        notification_messages = {
            "reviewing": f"Đơn ứng tuyển của bạn cho vị trí '{job_title}' đang được xem xét",
            "accepted": f"Chúc mừng! Đơn ứng tuyển của bạn cho vị trí '{job_title}' đã được chấp nhận",
            "rejected": f"Rất tiếc, đơn ứng tuyển của bạn cho vị trí '{job_title}' chưa phù hợp lần này"
        }
        
        if status in notification_messages:
            cursor.execute("""
                INSERT INTO notifications (user_id, title, message, type)
                VALUES (?, ?, ?, ?)
            """, (
                applicant_id,
                "Cập nhật đơn ứng tuyển",
                notification_messages[status],
                "application_update"
            ))
        
        conn.commit()
        
        return {
            "message": "Application status updated",
            "application_id": application_id,
            "new_status": status
        }
    finally:
        conn.close()