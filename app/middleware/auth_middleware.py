from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# Chuyển sang HTTPBearer để Swagger hiện ô dán Token (Bearer Token)
security = HTTPBearer()


def get_current_user(auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    Middleware để verify JWT token và trả về thông tin user hiện tại
    auth.credentials chính là chuỗi token sau chữ 'Bearer '
    """
    token = auth.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM]
        )
        
        # Lấy thông tin từ payload
        user_id: int = payload.get("user_id")
        email: str = payload.get("email")
        role: str = payload.get("role")
        
        if user_id is None or email is None:
            raise credentials_exception
            
        return {
            "user_id": user_id,
            "email": email,
            "role": role
        }
        
    except JWTError:
        raise credentials_exception


def require_role(allowed_roles: list):
    """
    Middleware để kiểm tra role của user
    Sử dụng: Depends(require_role(["admin", "employer"]))
    """
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user["role"].lower() if current_user["role"] else ""
        allowed_roles_lower = [r.lower() for r in allowed_roles]
        if user_role not in allowed_roles_lower:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return role_checker
