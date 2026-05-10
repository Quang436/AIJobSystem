from fastapi import APIRouter
from app.schemas.user_schema import (
    UserRegister,
    UserLogin
)
from app.utils.auth import (
    hash_password,
    verify_password
)
from app.utils.jwt_handler import (
    create_access_token
)
from app.database.database import get_connection

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