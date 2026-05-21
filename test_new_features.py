"""
Script test các tính năng mới của hệ thống
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

# Test credentials
TEST_USER = {
    "email": "test_user@example.com",
    "password": "password123",
    "fullname": "Test User",
    "role": "job_seeker"
}

TEST_EMPLOYER = {
    "email": "test_employer@example.com",
    "password": "password123",
    "fullname": "Test Employer",
    "role": "employer",
    "company_name": "Test Company"
}

def print_response(title, response):
    """In kết quả response"""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(response.text)

def test_search_with_filters():
    """Test tìm kiếm với filter nâng cao"""
    print("\n🔍 TEST: Tìm kiếm công việc với filter")
    
    # Test 1: Tìm theo job_type
    response = requests.get(f"{BASE_URL}/jobs/search", params={
        "job_type": "full-time",
        "keyword": "python"
    })
    print_response("Tìm kiếm Full-time Python jobs", response)
    
    # Test 2: Tìm theo salary
    response = requests.get(f"{BASE_URL}/jobs/search", params={
        "salary_min": 10,
        "salary_max": 20
    })
    print_response("Tìm kiếm jobs lương 10-20 triệu", response)
    
    # Test 3: Tìm theo skills
    response = requests.get(f"{BASE_URL}/jobs/search", params={
        "skills": "python,django,fastapi"
    })
    print_response("Tìm kiếm jobs theo kỹ năng", response)

def test_ready_to_work(token):
    """Test chức năng Ready to Work"""
    print("\n✅ TEST: Ready to Work")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Toggle ready to work
    response = requests.post(f"{BASE_URL}/ready-to-work/toggle", headers=headers)
    print_response("Toggle Ready to Work", response)
    
    # Find matching jobs
    response = requests.get(f"{BASE_URL}/matching/find-jobs", headers=headers)
    print_response("Tìm công việc phù hợp", response)

def test_reviews(token, reviewee_id):
    """Test hệ thống đánh giá"""
    print("\n⭐ TEST: Reviews & Ratings")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create review
    review_data = {
        "reviewee_id": reviewee_id,
        "rating": 5,
        "comment": "Làm việc rất tốt, chuyên nghiệp!"
    }
    response = requests.post(f"{BASE_URL}/reviews", json=review_data, headers=headers)
    print_response("Tạo đánh giá", response)
    
    # Get user reviews
    response = requests.get(f"{BASE_URL}/reviews/user/{reviewee_id}")
    print_response(f"Xem đánh giá của user {reviewee_id}", response)

def test_crawler(admin_token):
    """Test web crawler"""
    print("\n🕷️ TEST: Web Crawler")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Run crawler
    response = requests.post(f"{BASE_URL}/crawler/run", 
                            params={
                                "keyword": "python",
                                "location": "hanoi",
                                "max_pages": 1,
                                "source": "topcv"
                            },
                            headers=headers)
    print_response("Chạy crawler TopCV", response)
    
    # Get crawler status
    response = requests.get(f"{BASE_URL}/crawler/status", headers=headers)
    print_response("Thống kê crawler", response)

def test_employer_features(employer_token, job_id):
    """Test các tính năng cho employer"""
    print("\n👔 TEST: Employer Features")
    
    headers = {"Authorization": f"Bearer {employer_token}"}
    
    # Get job applications
    response = requests.get(f"{BASE_URL}/jobs/{job_id}/applications", headers=headers)
    print_response(f"Xem ứng viên của job {job_id}", response)
    
    # Find matching candidates
    response = requests.get(f"{BASE_URL}/matching/find-candidates", 
                           params={"job_id": job_id},
                           headers=headers)
    print_response("Tìm ứng viên phù hợp", response)
    
    # Notify candidates
    response = requests.post(f"{BASE_URL}/matching/notify-candidates",
                            params={"job_id": job_id},
                            headers=headers)
    print_response("Gửi thông báo cho ứng viên", response)

def test_notifications(token):
    """Test hệ thống thông báo"""
    print("\n🔔 TEST: Notifications")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get notifications
    response = requests.get(f"{BASE_URL}/notifications", headers=headers)
    print_response("Lấy danh sách thông báo", response)
    
    # Get unread count
    response = requests.get(f"{BASE_URL}/notifications/unread-count", headers=headers)
    print_response("Đếm thông báo chưa đọc", response)

def main():
    """Chạy tất cả tests"""
    print("🚀 BẮT ĐẦU TEST CÁC TÍNH NĂNG MỚI")
    print("="*60)
    
    # Test 1: Search with filters (không cần token)
    test_search_with_filters()
    
    print("\n\n" + "="*60)
    print("ℹ️  Các test tiếp theo cần token")
    print("Vui lòng đăng nhập trước khi chạy:")
    print("1. Tạo tài khoản job_seeker")
    print("2. Tạo tài khoản employer")
    print("3. Tạo tài khoản admin")
    print("4. Uncomment các test bên dưới và thêm token")
    print("="*60)
    
    # Uncomment và thêm token để test các tính năng khác:
    
    # user_token = "YOUR_USER_TOKEN_HERE"
    # employer_token = "YOUR_EMPLOYER_TOKEN_HERE"
    # admin_token = "YOUR_ADMIN_TOKEN_HERE"
    
    # test_ready_to_work(user_token)
    # test_reviews(user_token, reviewee_id=2)
    # test_notifications(user_token)
    # test_employer_features(employer_token, job_id=1)
    # test_crawler(admin_token)
    
    print("\n\n✅ HOÀN THÀNH TEST!")

if __name__ == "__main__":
    main()
