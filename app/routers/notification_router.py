# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends
from app.database.database import get_connection
from app.middleware.auth_middleware import get_current_user

router = APIRouter()

@router.get("/notifications")
def get_notifications(current_user: dict = Depends(get_current_user)):
    """Lấy danh sách thông báo của user"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, message, type, is_read, created_at
            FROM notifications
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (current_user["user_id"],))
        
        notifications = []
        for row in cursor.fetchall():
            notifications.append({
                "id": row[0],
                "title": row[1],
                "message": row[2],
                "type": row[3],
                "is_read": bool(row[4]),
                "created_at": str(row[5])
            })
        
        return notifications
    finally:
        conn.close()

@router.get("/notifications/unread-count")
def get_unread_count(current_user: dict = Depends(get_current_user)):
    """Đếm số thông báo chưa đọc"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM notifications
            WHERE user_id = ? AND is_read = 0
        """, (current_user["user_id"],))
        
        count = cursor.fetchone()[0]
        return {"unread_count": count}
    finally:
        conn.close()

@router.put("/notifications/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Đánh dấu thông báo đã đọc"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE notifications
            SET is_read = 1
            WHERE id = ? AND user_id = ?
        """, (notification_id, current_user["user_id"]))
        
        conn.commit()
        return {"message": "Notification marked as read"}
    finally:
        conn.close()

@router.put("/notifications/read-all")
def mark_all_as_read(current_user: dict = Depends(get_current_user)):
    """Đánh dấu tất cả thông báo đã đọc"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE notifications
            SET is_read = 1
            WHERE user_id = ? AND is_read = 0
        """, (current_user["user_id"],))
        
        conn.commit()
        return {"message": "All notifications marked as read"}
    finally:
        conn.close()

@router.delete("/notifications/{notification_id}")
def delete_notification(
    notification_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Xóa thông báo"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM notifications
            WHERE id = ? AND user_id = ?
        """, (notification_id, current_user["user_id"]))
        
        conn.commit()
        return {"message": "Notification deleted"}
    finally:
        conn.close()
