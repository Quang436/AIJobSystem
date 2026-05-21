# 🎬 Demo Workflow - Hệ Thống Hoàn Chỉnh

## 🎯 Kịch Bản 1: Người Tìm Việc

### Bước 1: Đăng ký và đăng nhập
```
1. Truy cập: http://localhost:8000/html/register.html
2. Đăng ký tài khoản job_seeker
3. Đăng nhập
```

### Bước 2: Cập nhật profile
```
1. Vào Profile
2. Cập nhật:
   - Vị trí (latitude, longitude)
   - Kỹ năng: Python, Django, FastAPI
   - Mức lương mong muốn: 10-15 triệu
```

### Bước 3: Bật "Sẵn sàng làm việc"
```
API: POST /api/ready-to-work/toggle
→ Hệ thống tự động tìm công việc phù hợp
→ Gửi thông báo cho bạn
```

### Bước 4: Xem công việc phù hợp
```
API: GET /api/matching/find-jobs
→ Hiển thị danh sách công việc với:
  - Match Score (điểm phù hợp)
  - Khoảng cách
  - Lý do phù hợp
```

### Bước 5: Lọc công việc
```
Tìm kiếm với filter:
- Loại: Full-time
- Lương: 10-20 triệu
- Kỹ năng: Python
- Bán kính: 5km

API: GET /api/jobs/search?job_type=full-time&salary_min=10&salary_max=20&skills=python&radius=5
```

### Bước 6: Xem công việc từ Crawler
```
Công việc từ TopCV/VietnamWorks/ITviec có:
- Link gốc (source_url)
- Lương cụ thể
- Địa chỉ cụ thể
```

### Bước 7: Ứng tuyển
```
Nếu công việc từ crawler:
→ Click "Ứng tuyển" → Chuyển sang trang gốc

Nếu công việc nội bộ:
→ Click "Ứng tuyển" → Lưu vào hệ thống
```

### Bước 8: Nhận đánh giá
```
Sau khi hoàn thành công việc:
→ Nhà tuyển dụng đánh giá
→ Hiển thị số sao (1-5)
→ Rating trung bình được cập nhật
```

---

## 👔 Kịch Bản 2: Nhà Tuyển Dụng

### Bước 1: Đăng ký Employer
```
1. Truy cập: http://localhost:8000/html/register.html
2. Chọn role: employer
3. Điền thông tin công ty
```

### Bước 2: Đăng nhập Employer Dashboard
```
Truy cập: http://localhost:8000/html/employer-dashboard.html
```

### Bước 3: Đăng tin tuyển dụng
```
1. Click "Đăng tin mới"
2. Điền thông tin:
   - Tiêu đề: Python Developer
   - Loại: Full-time
   - Lương: 15-20 triệu
   - Địa chỉ: Hà Nội
   - Kỹ năng: Python, Django
```

### Bước 4: Xem ứng viên đã apply
```
1. Click "Xem ứng viên" trên công việc
2. Hiển thị danh sách với:
   - Tên, email, phone
   - CV
   - Rating (số sao)
   - Số lượng đánh giá
   - Trạng thái
```

### Bước 5: Tìm ứng viên phù hợp (AI)
```
1. Click "Tìm ứng viên"
2. Hệ thống AI tìm ứng viên phù hợp:
   - Tính điểm phù hợp
   - Hiển thị khoảng cách
   - Hiển thị lý do phù hợp
   - Xem rating
```

### Bước 6: Gửi thông báo cho ứng viên
```
1. Click "Gửi thông báo cho tất cả ứng viên phù hợp"
2. Hệ thống gửi thông báo tự động
3. Ứng viên nhận thông báo
4. Ứng viên có thể ứng tuyển
```

### Bước 7: Kiểm duyệt đơn ứng tuyển
```
1. Xem danh sách ứng viên đã apply
2. Xem CV và rating
3. Cập nhật trạng thái:
   - Pending → Reviewing
   - Reviewing → Accepted/Rejected
4. Ứng viên nhận thông báo về trạng thái
```

### Bước 8: Đánh giá ứng viên
```
Sau khi hoàn thành công việc:
1. Đánh giá 1-5 sao
2. Viết comment
3. Rating của ứng viên được cập nhật
```

---

## 🕷️ Kịch Bản 3: Admin - Chạy Crawler

### Bước 1: Đăng nhập Admin
```
1. Tạo tài khoản admin: python scratch/create_admin.py
2. Đăng nhập
```

### Bước 2: Chạy Crawler
```
API: POST /api/crawler/run
Parameters:
- keyword: python
- location: hanoi
- max_pages: 3
- source: topcv (hoặc vietnamworks, itviec, all)
```

### Bước 3: Xem kết quả
```
API: GET /api/crawler/status
→ Hiển thị:
  - Tổng số công việc đã thu thập
  - Số công việc từ mỗi nguồn
  - Thời gian thu thập gần nhất
```

### Bước 4: Công việc được lưu vào database
```
Công việc từ crawler có:
- source_name: topcv/vietnamworks/itviec
- source_url: Link gốc
- external_id: ID từ nguồn (chống trùng)
- salary_min, salary_max: Lương cụ thể
- address_raw: Địa chỉ cụ thể
- job_type: full-time/part-time
```

---

## 🧪 Test Từng Tính Năng

### Test 1: Lọc công việc
```bash
# Lọc Full-time
curl "http://localhost:8000/api/jobs/search?job_type=full-time"

# Lọc theo lương
curl "http://localhost:8000/api/jobs/search?salary_min=10&salary_max=20"

# Lọc theo kỹ năng
curl "http://localhost:8000/api/jobs/search?skills=python,django"

# Lọc tổng hợp
curl "http://localhost:8000/api/jobs/search?job_type=full-time&salary_min=10&skills=python&radius=5"
```

### Test 2: Ready to Work
```bash
# Bật Ready to Work (cần token)
curl -X POST "http://localhost:8000/api/ready-to-work/toggle" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Tìm công việc phù hợp
curl "http://localhost:8000/api/matching/find-jobs" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test 3: Crawler
```bash
# Chạy crawler (cần admin token)
curl -X POST "http://localhost:8000/api/crawler/run?keyword=python&location=hanoi&source=topcv" \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Xem status
curl "http://localhost:8000/api/crawler/status" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### Test 4: Đánh giá
```bash
# Tạo đánh giá (cần token)
curl -X POST "http://localhost:8000/api/reviews" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reviewee_id": 2,
    "rating": 5,
    "comment": "Làm việc rất tốt!"
  }'

# Xem đánh giá
curl "http://localhost:8000/api/reviews/user/2"
```

### Test 5: Employer - Tìm ứng viên
```bash
# Tìm ứng viên phù hợp (cần employer token)
curl "http://localhost:8000/api/matching/find-candidates?job_id=1" \
  -H "Authorization: Bearer EMPLOYER_TOKEN"

# Gửi thông báo
curl -X POST "http://localhost:8000/api/matching/notify-candidates?job_id=1" \
  -H "Authorization: Bearer EMPLOYER_TOKEN"
```

### Test 6: Cập nhật trạng thái đơn
```bash
# Cập nhật trạng thái (cần employer token)
curl -X PUT "http://localhost:8000/api/applications/1/status?status=accepted" \
  -H "Authorization: Bearer EMPLOYER_TOKEN"
```

---

## 📊 Kiểm Tra Database

### Xem công việc từ crawler
```sql
SELECT id, title, company, source_name, source_url, job_type, salary_min, salary_max
FROM jobs
WHERE source_name IN ('topcv', 'vietnamworks', 'itviec');
```

### Xem đánh giá
```sql
SELECT u.full_name, u.average_rating, u.total_reviews
FROM users u
WHERE u.total_reviews > 0
ORDER BY u.average_rating DESC;
```

### Xem người sẵn sàng làm việc
```sql
SELECT id, full_name, email, is_ready_to_work, latitude, longitude
FROM users
WHERE is_ready_to_work = 1;
```

### Xem thông báo
```sql
SELECT n.title, n.message, n.type, u.full_name
FROM notifications n
JOIN users u ON n.user_id = u.id
ORDER BY n.created_at DESC;
```

---

## ✅ Checklist Tính Năng

- [x] Lọc công việc Part-time/Full-time/Freelance
- [x] Lọc theo lương cụ thể
- [x] Lọc theo kỹ năng
- [x] Crawler TopCV
- [x] Crawler VietnamWorks
- [x] Crawler ITviec
- [x] Công việc có link gốc
- [x] Nút ứng tuyển chuyển sang trang gốc
- [x] Trang Employer Dashboard
- [x] Đăng tin tuyển dụng
- [x] Lọc danh sách người dùng (tìm ứng viên)
- [x] Nút "Sẵn sàng làm việc"
- [x] Tính toán khoảng cách
- [x] Tính toán mục tiêu công việc
- [x] Lọc và báo người phù hợp
- [x] Thông báo tự động
- [x] Kiểm duyệt đơn ứng tuyển
- [x] Xem thông tin đánh giá
- [x] Hệ thống đánh giá (1-5 sao)
- [x] Hiển thị số sao cho người dùng

---

## 🎉 Kết Luận

**TẤT CẢ** các tính năng bạn yêu cầu đã được triển khai đầy đủ!

Bạn có thể test ngay bằng cách:
1. Truy cập: http://localhost:8000/docs
2. Test từng API endpoint
3. Hoặc sử dụng frontend: http://localhost:8000/html/

**Hệ thống hoàn toàn sẵn sàng!** 🚀
