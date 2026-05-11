from fastapi import APIRouter, Depends
from app.schemas.user_schema import (
    UserRegister,
    UserLogin,
    UserProfileUpdate
)
from app.utils.auth import (
    hash_password,
    verify_password
)
from app.utils.jwt_handler import (
    create_access_token
)
from app.database.database import get_connection
from app.middleware.auth_middleware import get_current_user

router = APIRouter()

@router.post("/register")
def register(user: UserRegister):

    conn = get_connection()
    cursor = conn.cursor()

    hashed_pw = hash_password(
        user.password
    )

    cursor.execute("""
        INSERT INTO users
        (
            fullname,
            email,
            password_hash,
            role
        )
        VALUES (?, ?, ?, ?)
    """,
    (
        user.fullname,
        user.email,
        hashed_pw,
        user.role
    ))

    conn.commit()

    return {
        "message": "Register success"
    }

@router.post("/login")
def login(user: UserLogin):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE email = ?
    """, (user.email,))

    db_user = cursor.fetchone()

    if not db_user:
        return {
            "message": "Email not found"
        }

    stored_password = db_user.password_hash

    is_valid = verify_password(
        user.password,
        stored_password
    )

    if not is_valid:
        return {
            "message": "Wrong password"
        }

    token = create_access_token({
        "user_id": db_user.id,
        "email": db_user.email,
        "role": db_user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/profile")
def get_profile(current_user: dict = Depends(get_current_user)):
    """
    Protected endpoint - Yêu cầu JWT token
    Trả về thông tin user hiện tại
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            id,
            fullname,
            email,
            role,
            gps_lat,
            gps_lng,
            ready_to_work,
            created_at
        FROM users
        WHERE id = ?
    """, (current_user["user_id"],))
    
    user = cursor.fetchone()
    
    if not user:
        return {
            "message": "User not found"
        }
    
    return {
        "id": user.id,
        "fullname": user.fullname,
        "email": user.email,
        "role": user.role,
        "gps_lat": user.gps_lat,
        "gps_lng": user.gps_lng,
        "ready_to_work": user.ready_to_work,
        "created_at": str(user.created_at)
    }


@router.put("/profile/update")
def update_profile(
    profile_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Protected endpoint - Yêu cầu JWT token
    Update thông tin profile của user hiện tại
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Build dynamic UPDATE query based on provided fields
    update_fields = []
    update_values = []
    
    if profile_data.fullname is not None:
        update_fields.append("fullname = ?")
        update_values.append(profile_data.fullname)
    
    if profile_data.gps_lat is not None:
        update_fields.append("gps_lat = ?")
        update_values.append(profile_data.gps_lat)
    
    if profile_data.gps_lng is not None:
        update_fields.append("gps_lng = ?")
        update_values.append(profile_data.gps_lng)
    
    if profile_data.ready_to_work is not None:
        update_fields.append("ready_to_work = ?")
        update_values.append(profile_data.ready_to_work)
    
    # If no fields to update
    if not update_fields:
        return {
            "message": "No fields to update"
        }
    
    # Add user_id to values
    update_values.append(current_user["user_id"])
    
    # Execute UPDATE query
    query = f"""
        UPDATE users
        SET {', '.join(update_fields)}
        WHERE id = ?
    """
    
    cursor.execute(query, tuple(update_values))
    conn.commit()
    
    return {
        "message": "Profile updated successfully",
        "updated_by": current_user["email"]
    }