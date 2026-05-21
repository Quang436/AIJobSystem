# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends
from app.schemas.review_schema import ReviewCreate, ReviewResponse
from app.database.database import get_connection
from app.middleware.auth_middleware import get_current_user

router = APIRouter()

@router.post("/reviews")
def create_review(
    review: ReviewCreate,
    current_user: dict = Depends(get_current_user)
):
    """Tạo đánh giá cho người dùng khác"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Kiểm tra rating hợp lệ
        if review.rating < 1 or review.rating > 5:
            return {"message": "Rating must be between 1 and 5"}
        
        # Không thể tự đánh giá bản thân
        if review.reviewee_id == current_user["user_id"]:
            return {"message": "Cannot review yourself"}
        
        # Tạo review
        cursor.execute("""
            INSERT INTO reviews (reviewer_id, reviewee_id, job_id, rating, comment)
            VALUES (?, ?, ?, ?, ?)
        """, (current_user["user_id"], review.reviewee_id, review.job_id, review.rating, review.comment))
        
        # Cập nhật average_rating của reviewee
        cursor.execute("""
            UPDATE users 
            SET average_rating = (
                SELECT AVG(CAST(rating AS FLOAT)) FROM reviews WHERE reviewee_id = ?
            ),
            total_reviews = (
                SELECT COUNT(*) FROM reviews WHERE reviewee_id = ?
            )
            WHERE id = ?
        """, (review.reviewee_id, review.reviewee_id, review.reviewee_id))
        
        conn.commit()
        return {"message": "Review created successfully"}
    except Exception as e:
        return {"message": str(e)}
    finally:
        conn.close()

@router.get("/reviews/user/{user_id}")
def get_user_reviews(user_id: int):
    """Lấy tất cả đánh giá của một người dùng"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id, r.reviewer_id, u.full_name, r.reviewee_id, r.job_id, 
                   r.rating, r.comment, r.created_at
            FROM reviews r
            JOIN users u ON r.reviewer_id = u.id
            WHERE r.reviewee_id = ? AND r.status = 'published'
            ORDER BY r.created_at DESC
        """, (user_id,))
        
        reviews = []
        for row in cursor.fetchall():
            reviews.append({
                "id": row[0],
                "reviewer_id": row[1],
                "reviewer_name": row[2],
                "reviewee_id": row[3],
                "job_id": row[4],
                "rating": row[5],
                "comment": row[6],
                "created_at": str(row[7])
            })
        
        # Lấy thống kê rating
        cursor.execute("""
            SELECT average_rating, total_reviews
            FROM users WHERE id = ?
        """, (user_id,))
        stats = cursor.fetchone()
        
        return {
            "reviews": reviews,
            "average_rating": stats[0] if stats else 0,
            "total_reviews": stats[1] if stats else 0
        }
    finally:
        conn.close()

@router.get("/reviews/my-reviews")
def get_my_reviews(current_user: dict = Depends(get_current_user)):
    """Lấy các đánh giá mà tôi đã nhận được"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id, r.reviewer_id, u.full_name, r.job_id, 
                   r.rating, r.comment, r.created_at
            FROM reviews r
            JOIN users u ON r.reviewer_id = u.id
            WHERE r.reviewee_id = ? AND r.status = 'published'
            ORDER BY r.created_at DESC
        """, (current_user["user_id"],))
        
        reviews = []
        for row in cursor.fetchall():
            reviews.append({
                "id": row[0],
                "reviewer_id": row[1],
                "reviewer_name": row[2],
                "job_id": row[3],
                "rating": row[4],
                "comment": row[5],
                "created_at": str(row[6])
            })
        
        return reviews
    finally:
        conn.close()
