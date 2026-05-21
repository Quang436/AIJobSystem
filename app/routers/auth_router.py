# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends
from app.schemas.user_schema import (
    UserRegister,
    UserLogin,
    UserProfileUpdate,
    CandidateRegisterReq,
    GigworkerRegisterReq,
    EmployerRegisterReq
)
from app.utils.auth import (
    hash_password,
    verify_password
)
from app.utils.jwt_handler import (
    create_access_token
)
from app.database.database import get_connection
from app.middleware.auth_middleware import get_current_user, require_role
import json

router = APIRouter()

@router.post("/register")
def register(user: UserRegister):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        hashed_pw = hash_password(user.password)
        role = user.role if user.role else "job_seeker"
        username = user.email.split('@')[0]
        cursor.execute("""
            INSERT INTO users (
                username, full_name, email, password_hash, role, 
                job_seeker_type, cv_file_url, cccd_number, cccd_front_url, cccd_back_url, certificate_urls,
                experience_years, education_level, portfolio_url, is_freelancer, available_hours, service_areas, hourly_rate
            )
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username, user.fullname, user.email, hashed_pw, role, 
            user.job_seeker_type, user.cv_url, user.cccd_number, user.cccd_front_url, user.cccd_back_url, user.certificate_urls,
            user.experience_years, user.education_level, user.portfolio_url, 1 if user.is_freelancer else 0, user.available_hours, user.service_areas, user.hourly_rate
        ))
        user_id = cursor.fetchone()[0]
        
        if role == 'employer' and user.company_name:
            cursor.execute("""
                INSERT INTO employer_profiles (
                    user_id, company_name, employer_type, manager_name, manager_phone, business_license_url, facility_images,
                    tax_code, representative_name, establishment_date, industry, company_size, headquarters_address
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, user.company_name, user.employer_type, user.manager_name, user.manager_phone, user.business_license_url, user.facility_images,
                user.tax_code, user.representative_name, user.establishment_date, user.industry, user.company_size, user.headquarters_address
            ))
            
        conn.commit()
        return {"message": "Register success"}
    except Exception as e:
        return {"message": str(e)}
    finally:
        conn.close()

@router.post("/register-candidate")
def register_candidate(req: CandidateRegisterReq):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        hashed_pw = hash_password(req.common_info.password)
        role = "job_seeker"
        username = req.common_info.email.split('@')[0]
        
        certs = json.dumps(req.education_info.certificate_urls) if req.education_info.certificate_urls else None
        
        cursor.execute("""
            INSERT INTO users (
                username, full_name, email, password_hash, role, 
                job_seeker_type, education_level, preferred_skills, preferred_salary_min, cv_file_url, certificate_urls, phone
            )
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username, req.common_info.full_name, req.common_info.email, hashed_pw, role, 
            req.career_info.job_category or "office", f"{req.education_info.institution_name} - {req.education_info.degree_level}", 
            req.career_info.industry, req.career_info.desired_salary, req.attachment.cv_url, certs, req.common_info.phone
        ))
        
        user_id = cursor.fetchone()[0]
        conn.commit()
        return {"message": "Candidate registered successfully", "user_id": user_id}
    except Exception as e:
        return {"message": str(e)}
    finally:
        conn.close()

@router.post("/register-gigworker")
def register_gigworker(req: GigworkerRegisterReq):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        hashed_pw = hash_password(req.common_info.password)
        role = "job_seeker"
        username = req.common_info.email.split('@')[0]
        
        skills = json.dumps(req.skill_set.skills) if req.skill_set.skills else None
        certs = json.dumps(req.skill_set.license_urls) if req.skill_set.license_urls else None
        
        cursor.execute("""
            INSERT INTO users (
                username, full_name, email, password_hash, role, 
                job_seeker_type, is_freelancer, preferred_skills, certificate_urls, 
                preferred_radius_km, preferred_salary_min, hourly_rate, 
                is_ready_to_work, latitude, longitude, phone
            )
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username, req.common_info.full_name, req.common_info.email, hashed_pw, role, 
            req.skill_set.professional_category, 1, skills, certs, 
            req.working_config.max_travel_distance_km, req.working_config.pricing_range.min_price_per_task, req.working_config.pricing_range.max_price_per_task, 
            1 if req.realtime_status.is_available else 0, req.realtime_status.current_location.latitude, req.realtime_status.current_location.longitude, req.common_info.phone
        ))
        
        user_id = cursor.fetchone()[0]
        conn.commit()
        return {"message": "Gigworker registered successfully", "user_id": user_id}
    except Exception as e:
        return {"message": str(e)}
    finally:
        conn.close()

@router.post("/register-employer")
def register_employer(req: EmployerRegisterReq):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        hashed_pw = hash_password(req.contact_verification.password)
        role = "employer"
        username = req.contact_verification.corporate_email.split('@')[0]
        
        office_images = json.dumps(req.media.office_image_urls) if req.media.office_image_urls else None
        
        cursor.execute("""
            INSERT INTO users (
                username, phone, email, password_hash, role, avatar_url
            )
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            username, req.contact_verification.hr_hotline, req.contact_verification.corporate_email, hashed_pw, role,
            req.media.logo_url
        ))
        user_id = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO employer_profiles (
                user_id, company_name, tax_code, manager_phone,
                headquarters_address, facility_images, verified
            )
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (
            user_id, req.legal_info.legal_company_name, req.legal_info.tax_code, req.contact_verification.hr_hotline,
            req.location_data.headquarter_address, office_images
        ))
            
        conn.commit()
        return {"message": "Employer registered successfully", "user_id": user_id}
    except Exception as e:
        return {"message": str(e)}
    finally:
        conn.close()

@router.post("/login")
def login(user: UserLogin):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, email, password_hash, role FROM users WHERE email = ?", (user.email,))
        row = cursor.fetchone()
        
        if row and verify_password(user.password, row[3]):
            token = create_access_token(data={
                "user_id": row[0],
                "email": row[2],
                "role": row[4]
            })
            return {
                "access_token": token,
                "token_type": "bearer",
                "role": row[4],
                "fullname": row[1]
            }
        return {"message": "Invalid email or password"}
    finally:
        conn.close()

@router.get("/profile")
def get_profile(current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, email, role, latitude, longitude, is_ready_to_work, is_freelancer, job_seeker_type FROM users WHERE id = ?", (current_user["user_id"],))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "fullname": row[1],
                "email": row[2],
                "role": row[3],
                "latitude": row[4],
                "longitude": row[5],
                "ready_to_work": row[6],
                "is_freelancer": bool(row[7]),
                "job_seeker_type": row[8]
            }
        return {"message": "User not found"}
    finally:
        conn.close()

@router.put("/profile/update")
def update_profile(profile: UserProfileUpdate, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        update_fields = []
        update_values = []
        
        if profile.fullname:
            update_fields.append("full_name = ?")
            update_values.append(profile.fullname)
        
        if profile.latitude is not None:
            update_fields.append("latitude = ?")
            update_values.append(profile.latitude)
            
        if profile.longitude is not None:
            update_fields.append("longitude = ?")
            update_values.append(profile.longitude)
            
        if profile.ready_to_work is not None:
            update_fields.append("is_ready_to_work = ?")
            update_values.append(1 if profile.ready_to_work else 0)
            
        if not update_fields:
            return {"message": "No fields to update"}
            
        update_values.append(current_user["user_id"])
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        
        cursor.execute(query, tuple(update_values))
        conn.commit()
        
        return {
            "message": "Profile updated successfully",
            "updated_by": current_user["email"]
        }
    finally:
        conn.close()

@router.get("/users")
def get_all_users(current_user: dict = Depends(require_role(['admin']))):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, email, role, created_at FROM users")
        users = cursor.fetchall()
        return [{"id": u[0], "fullname": u[1], "email": u[2], "role": u[3], "created_at": str(u[4])} for u in users]
    finally:
        conn.close()
