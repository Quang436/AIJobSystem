import time
import logging
import asyncio
from app.database.database import get_connection
from app.services.recommend_service import recommend_jobs
from app.utils.location import calculate_distance

logger = logging.getLogger(__name__)

async def run_background_matching():
    """
    Background task that runs periodically to match 'Ready to work' users with suitable jobs.
    """
    logger.info("Starting background matching service...")
    while True:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # 1. Get all 'Ready to work' users
            cursor.execute("""
                SELECT id, full_name, email, preferred_skills, job_seeker_type, latitude, longitude, preferred_radius_km 
                FROM users 
                WHERE is_ready_to_work = 1 AND role = 'job_seeker'
            """)
            users = cursor.fetchall()
            
            for user in users:
                user_id, full_name, email, preferred_skills, job_seeker_type, user_lat, user_lng, pref_radius = user
                
                # Phân loại đối tượng: Lao động tự do (Skilled/Freelance) hoặc Văn phòng
                is_skilled = any(kw in (job_seeker_type or "").lower() for kw in ['skilled', 'thợ', 'lao động', 'freelance', 'tự do', 'part-time', 'phổ thông'])
                is_office = any(kw in (job_seeker_type or "").lower() for kw in ['office', 'văn phòng'])
                
                # 2. Lấy các công việc đã duyệt và chưa được thông báo cho user này
                cursor.execute("""
                    SELECT id, title, company, skills, description, job_type, latitude, longitude, address_raw
                    FROM jobs 
                    WHERE status = 'approved'
                    AND id NOT IN (
                        SELECT job_id FROM job_match_notifications WHERE user_id = ?
                    )
                """, (user_id,))
                
                jobs_rows = cursor.fetchall()
                if not jobs_rows:
                    continue
                
                for job_row in jobs_rows:
                    job_id, title, company, skills, desc, j_type, job_lat, job_lng, j_address = job_row
                    
                    notify = False
                    n_title = "Việc làm mới phù hợp!"
                    n_msg = f"Chúng tôi tìm thấy công việc '{title}' tại '{company}' có vẻ phù hợp với bạn."
                    n_type = "job_match"

                    # --- LOGIC 1: Lao động tự do (Ưu tiên Khoảng cách & Gấp) ---
                    # Nếu là job freelance và user là lao động tự do
                    if j_type == 'freelance' and is_skilled:
                        if user_lat and user_lng and job_lat and job_lng:
                            dist = calculate_distance(user_lat, user_lng, job_lat, job_lng)
                            radius = pref_radius or 10.0 # Mặc định 10km
                            
                            if dist <= radius:
                                notify = True
                                n_title = "Yêu cầu đặt việc ngay! (Gần bạn)"
                                n_msg = f"CẦN GẤP: '{title}' cách bạn {dist}km. Địa chỉ: {j_address}. Hãy nhận việc ngay!"
                                n_type = "urgent_booking"
                    
                    # --- LOGIC 2: Khối văn phòng (Ưu tiên Kỹ năng) ---
                    elif is_office:
                        # Bỏ qua nếu job là lao động chân tay rõ rệt (trừ khi có từ khóa IT/VP)
                        manual_labor_kws = ['sửa điện', 'nước', 'bốc xếp', 'giúp việc']
                        if any(kw in title.lower() for kw in manual_labor_kws) and not any(kw in title.lower() for kw in ['it', 'văn phòng']):
                            continue
                            
                        # Dùng TF-IDF so khớp kỹ năng
                        job_data = {
                            "id": job_id, "title": title, "company": company, 
                            "skills": skills or title, "description": desc
                        }
                        
                        office_kws = ['văn phòng', 'office', 'hành chính', 'nhân sự', 'kế toán', 'it', 'software', 'developer', 'thiết kế', 'marketing', 'kinh doanh', 'sales', 'lập trình']
                        if any(kw in (title + (desc or "")).lower() for kw in office_kws):
                            query = preferred_skills if (preferred_skills and preferred_skills.strip()) else (job_seeker_type or "văn phòng")
                            match_res = recommend_jobs(query, [job_data])
                            if match_res and match_res[0]['score'] >= 0.1:
                                notify = True

                    # --- GỬI THÔNG BÁO ---
                    if notify:
                        cursor.execute("""
                            INSERT INTO notifications (user_id, title, message, type, is_read)
                            VALUES (?, ?, ?, ?, 0)
                        """, (user_id, n_title, n_msg, n_type))
                        
                        cursor.execute("""
                            INSERT INTO job_match_notifications (user_id, job_id)
                            VALUES (?, ?)
                        """, (user_id, job_id))
                        
                        logger.info(f"Notified user {user_id} about job {job_id} (Type: {n_type})")
                
                conn.commit()
                
            conn.close()
            
        except Exception as e:
            logger.error(f"Error in background matching: {e}")
            if 'conn' in locals():
                conn.close()
        
        # Chờ 30 giây cho lần quét tiếp theo
        await asyncio.sleep(30) 
