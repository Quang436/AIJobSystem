# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, BackgroundTasks
from app.database.database import get_connection
from app.middleware.auth_middleware import get_current_user
from app.utils.location import calculate_distance
from typing import List

router = APIRouter()

@router.post("/ready-to-work/toggle")
def toggle_ready_to_work(current_user: dict = Depends(get_current_user)):
    """Bật/tắt trạng thái sẵn sàng làm việc"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Lấy trạng thái hiện tại
        cursor.execute("SELECT is_ready_to_work FROM users WHERE id = ?", (current_user["user_id"],))
        row = cursor.fetchone()
        current_status = row[0] if row else False
        
        # Đảo trạng thái
        new_status = not current_status
        
        cursor.execute("""
            UPDATE users 
            SET is_ready_to_work = ?, location_updated_at = GETUTCDATE()
            WHERE id = ?
        """, (1 if new_status else 0, current_user["user_id"]))
        
        conn.commit()
        
        return {
            "message": "Status updated",
            "is_ready_to_work": new_status
        }
    finally:
        conn.close()

@router.get("/matching/find-jobs")
def find_matching_jobs(current_user: dict = Depends(get_current_user)):
    """Tìm công việc phù hợp dựa trên vị trí, kỹ năng và mức lương mong muốn"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Lấy thông tin user
        cursor.execute("""
            SELECT latitude, longitude, preferred_radius_km, 
                   preferred_salary_min, preferred_skills, job_seeker_type
            FROM users WHERE id = ?
        """, (current_user["user_id"],))
        
        user_data = cursor.fetchone()
        if not user_data:
            return {"message": "User not found"}
        
        user_lat, user_lng, radius, min_salary, skills, job_type = user_data
        
        if not user_lat or not user_lng:
            return {"message": "Please update your location first"}
        
        # Lấy tất cả công việc active
        cursor.execute("""
            SELECT id, title, company, description, salary_raw, salary_min, salary_max,
                   address_raw, latitude, longitude, skills, job_type, source_url
            FROM jobs 
            WHERE status = 'approved' OR status = 'active'
        """)
        
        jobs = cursor.fetchall()
        matched_jobs = []
        
        for job in jobs:
            job_id, title, company, desc, salary_raw, sal_min, sal_max, address, lat, lng, job_skills, jtype, source_url = job
            
            if not lat or not lng:
                continue
            
            # Tính khoảng cách
            distance = calculate_distance(user_lat, user_lng, lat, lng)
            
            # Lọc theo bán kính
            if radius and distance > radius:
                continue
            
            # Tính điểm phù hợp
            match_score = 0
            reasons = []
            
            # 1. Khoảng cách (40 điểm)
            if distance <= 2:
                match_score += 40
                reasons.append("Rất gần bạn")
            elif distance <= 5:
                match_score += 30
                reasons.append("Gần bạn")
            elif distance <= 10:
                match_score += 20
                reasons.append("Trong khu vực")
            else:
                match_score += 10
            
            # 2. Kỹ năng (30 điểm)
            if skills and job_skills:
                user_skills_list = [s.strip().lower() for s in skills.split(',')]
                job_skills_list = [s.strip().lower() for s in job_skills.split(',')]
                
                matching_skills = set(user_skills_list) & set(job_skills_list)
                if matching_skills:
                    skill_match_ratio = len(matching_skills) / len(user_skills_list)
                    match_score += int(skill_match_ratio * 30)
                    reasons.append(f"Phù hợp {len(matching_skills)} kỹ năng")
            
            # 3. Lương (20 điểm)
            if min_salary and sal_min:
                if sal_min >= min_salary:
                    match_score += 20
                    reasons.append("Lương phù hợp")
                elif sal_min >= min_salary * 0.8:
                    match_score += 10
            
            # 4. Loại công việc (10 điểm)
            if job_type and jtype:
                if job_type.lower() in jtype.lower():
                    match_score += 10
                    reasons.append("Đúng loại công việc")
            
            # Chỉ lấy job có điểm >= 40
            if match_score >= 40:
                matched_jobs.append({
                    "id": job_id,
                    "title": title,
                    "company": company,
                    "salary": salary_raw,
                    "address": address,
                    "distance_km": round(distance, 2),
                    "match_score": match_score,
                    "match_reasons": reasons,
                    "source_url": source_url,
                    "job_type": jtype
                })
        
        # Sắp xếp theo điểm phù hợp
        matched_jobs.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "total": len(matched_jobs),
            "jobs": matched_jobs[:20]  # Top 20
        }
    finally:
        conn.close()

@router.get("/matching/find-candidates")
def find_matching_candidates(
    job_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Tìm ứng viên phù hợp cho công việc (dành cho employer)"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Kiểm tra quyền
        if current_user["role"] not in ["employer", "admin"]:
            return {"message": "Only employers can access this"}
        
        # Lấy thông tin job
        cursor.execute("""
            SELECT title, latitude, longitude, skills, salary_min, job_type
            FROM jobs WHERE id = ?
        """, (job_id,))
        
        job_data = cursor.fetchone()
        if not job_data:
            return {"message": "Job not found"}
        
        job_title, job_lat, job_lng, job_skills, job_salary, job_type = job_data
        
        # Lấy danh sách ứng viên sẵn sàng làm việc
        cursor.execute("""
            SELECT id, full_name, email, phone, latitude, longitude, 
                   preferred_skills, preferred_salary_min, job_seeker_type,
                   average_rating, total_reviews, cv_file_url
            FROM users 
            WHERE role = 'job_seeker' AND is_ready_to_work = 1
                  AND latitude IS NOT NULL AND longitude IS NOT NULL
        """)
        
        candidates = cursor.fetchall()
        matched_candidates = []
        
        for candidate in candidates:
            user_id, name, email, phone, lat, lng, skills, min_salary, seeker_type, rating, reviews, cv_url = candidate
            
            # Tính khoảng cách
            distance = calculate_distance(job_lat, job_lng, lat, lng)
            
            # Tính điểm phù hợp
            match_score = 0
            reasons = []
            
            # 1. Khoảng cách (30 điểm)
            if distance <= 5:
                match_score += 30
                reasons.append("Gần địa điểm làm việc")
            elif distance <= 10:
                match_score += 20
            elif distance <= 20:
                match_score += 10
            
            # 2. Kỹ năng (40 điểm)
            if skills and job_skills:
                user_skills_list = [s.strip().lower() for s in skills.split(',')]
                job_skills_list = [s.strip().lower() for s in job_skills.split(',')]
                
                matching_skills = set(user_skills_list) & set(job_skills_list)
                if matching_skills:
                    skill_match_ratio = len(matching_skills) / len(job_skills_list)
                    match_score += int(skill_match_ratio * 40)
                    reasons.append(f"{len(matching_skills)} kỹ năng phù hợp")
            
            # 3. Mức lương (20 điểm)
            if min_salary and job_salary:
                if min_salary <= job_salary:
                    match_score += 20
                    reasons.append("Mức lương phù hợp")
                elif min_salary <= job_salary * 1.2:
                    match_score += 10
            
            # 4. Đánh giá (10 điểm)
            if rating and rating >= 4.0:
                match_score += 10
                reasons.append(f"Đánh giá cao ({rating:.1f}⭐)")
            elif rating and rating >= 3.0:
                match_score += 5
            
            if match_score >= 30:
                matched_candidates.append({
                    "user_id": user_id,
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "distance_km": round(distance, 2),
                    "match_score": match_score,
                    "match_reasons": reasons,
                    "rating": rating,
                    "total_reviews": reviews,
                    "cv_url": cv_url,
                    "job_seeker_type": seeker_type
                })
        
        # Sắp xếp theo điểm
        matched_candidates.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "job_title": job_title,
            "total": len(matched_candidates),
            "candidates": matched_candidates
        }
    finally:
        conn.close()

@router.post("/matching/notify-candidates")
def notify_matching_candidates(
    job_id: int,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Gửi thông báo cho các ứng viên phù hợp"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Kiểm tra quyền
        if current_user["role"] not in ["employer", "admin"]:
            return {"message": "Only employers can access this"}
        
        # Lấy danh sách ứng viên phù hợp
        result = find_matching_candidates(job_id, current_user)
        
        if "candidates" not in result:
            return {"message": "No candidates found"}
        
        # Lấy thông tin job
        cursor.execute("SELECT title, company FROM jobs WHERE id = ?", (job_id,))
        job_info = cursor.fetchone()
        job_title, company = job_info
        
        # Tạo thông báo cho từng ứng viên
        notified_count = 0
        for candidate in result["candidates"]:
            if candidate["match_score"] >= 50:  # Chỉ thông báo cho ứng viên có điểm cao
                cursor.execute("""
                    INSERT INTO notifications (user_id, title, message, type)
                    VALUES (?, ?, ?, ?)
                """, (
                    candidate["user_id"],
                    f"Công việc phù hợp: {job_title}",
                    f"{company} đang tìm kiếm ứng viên cho vị trí {job_title}. Bạn phù hợp {candidate['match_score']}%. Hãy ứng tuyển ngay!",
                    "job_match"
                ))
                notified_count += 1
        
        conn.commit()
        
        return {
            "message": f"Notified {notified_count} candidates",
            "total_matched": len(result["candidates"])
        }
    finally:
        conn.close()
