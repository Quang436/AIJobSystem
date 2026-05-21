# API Documentation - AI Job Recommendation System v2.0

## 🎯 Các Tính Năng Mới

### 1. **Hệ Thống Đánh Giá (Reviews & Ratings)**
### 2. **Matching Tự Động (Ready to Work)**
### 3. **Web Crawler (TopCV, VietnamWorks, ITviec)**
### 4. **Lọc Công Việc Nâng Cao**
### 5. **Quản Lý Ứng Viên cho Nhà Tuyển Dụng**
### 6. **Hệ Thống Thông Báo**

---

## 📋 API Endpoints

### **Authentication** (`/api`)

#### POST `/api/register`
Đăng ký tài khoản mới

#### POST `/api/login`
Đăng nhập

#### GET `/api/profile`
Lấy thông tin profile (cần token)

#### PUT `/api/profile/update`
Cập nhật profile (cần token)

---

### **Jobs** (`/api`)

#### GET `/api/jobs`
Lấy tất cả công việc

#### GET `/api/jobs/search`
**Tìm kiếm công việc với filter nâng cao**

**Query Parameters:**
- `keyword` (string): Từ khóa tìm kiếm
- `location` (string): Địa điểm
- `job_type` (string): Loại công việc - `full-time`, `part-time`, `freelance`
- `salary_min` (float): Mức lương tối thiểu
- `salary_max` (float): Mức lương tối đa
- `skills` (string): Kỹ năng (phân cách bằng dấu phẩy)
- `lat` (float): Vĩ độ người dùng
- `lng` (float): Kinh độ người dùng
- `radius` (float): Bán kính tìm kiếm (km)

**Example:**
```
GET /api/jobs/search?keyword=python&location=hanoi&job_type=full-time&salary_min=10&radius=5
```

#### POST `/api/jobs`
Tạo công việc mới (employer/admin)

#### GET `/api/jobs/{job_id}`
Lấy chi tiết công việc

#### POST `/api/apply/{job_id}`
Ứng tuyển công việc (cần token)

#### GET `/api/jobs/{job_id}/applications`
**Lấy danh sách ứng viên đã apply (employer/admin)**

**Response:**
```json
{
  "job_id": 1,
  "total_applications": 5,
  "applications": [
    {
      "application_id": 1,
      "user_id": 10,
      "full_name": "Nguyễn Văn A",
      "email": "a@example.com",
      "phone": "0123456789",
      "cv_url": "https://...",
      "rating": 4.5,
      "total_reviews": 10,
      "status": "pending",
      "applied_at": "2026-05-19 10:00:00"
    }
  ]
}
```

#### PUT `/api/applications/{application_id}/status`
**Cập nhật trạng thái đơn ứng tuyển (employer/admin)**

**Body:**
```json
{
  "status": "accepted"  // pending, reviewing, accepted, rejected
}
```

---

### **Reviews & Ratings** (`/api`)

#### POST `/api/reviews`
**Tạo đánh giá cho người dùng**

**Body:**
```json
{
  "reviewee_id": 10,
  "job_id": 5,
  "rating": 5,
  "comment": "Làm việc rất tốt, chuyên nghiệp"
}
```

#### GET `/api/reviews/user/{user_id}`
**Lấy tất cả đánh giá của một người dùng**

**Response:**
```json
{
  "reviews": [...],
  "average_rating": 4.5,
  "total_reviews": 20
}
```

#### GET `/api/reviews/my-reviews`
Lấy các đánh giá mà tôi đã nhận được (cần token)

---

### **Matching System** (`/api`)

#### POST `/api/ready-to-work/toggle`
**Bật/tắt trạng thái "Sẵn sàng làm việc"**

Khi bật, hệ thống sẽ tự động tìm công việc phù hợp và gửi thông báo.

**Response:**
```json
{
  "message": "Status updated",
  "is_ready_to_work": true
}
```

#### GET `/api/matching/find-jobs`
**Tìm công việc phù hợp dựa trên:**
- Vị trí hiện tại
- Kỹ năng
- Mức lương mong muốn
- Loại công việc

**Response:**
```json
{
  "total": 15,
  "jobs": [
    {
      "id": 1,
      "title": "Python Developer",
      "company": "ABC Corp",
      "salary": "15-20 triệu",
      "address": "Hà Nội",
      "distance_km": 2.5,
      "match_score": 85,
      "match_reasons": [
        "Rất gần bạn",
        "Phù hợp 3 kỹ năng",
        "Lương phù hợp"
      ],
      "source_url": "https://...",
      "job_type": "full-time"
    }
  ]
}
```

#### GET `/api/matching/find-candidates`
**Tìm ứng viên phù hợp cho công việc (employer)**

**Query Parameters:**
- `job_id` (int): ID công việc

**Response:**
```json
{
  "job_title": "Python Developer",
  "total": 10,
  "candidates": [
    {
      "user_id": 5,
      "name": "Nguyễn Văn A",
      "email": "a@example.com",
      "phone": "0123456789",
      "distance_km": 3.2,
      "match_score": 90,
      "match_reasons": [
        "Gần địa điểm làm việc",
        "3 kỹ năng phù hợp",
        "Đánh giá cao (4.8⭐)"
      ],
      "rating": 4.8,
      "total_reviews": 15,
      "cv_url": "https://..."
    }
  ]
}
```

#### POST `/api/matching/notify-candidates`
**Gửi thông báo cho các ứng viên phù hợp**

**Query Parameters:**
- `job_id` (int): ID công việc

---

### **Web Crawler** (`/api`)

#### POST `/api/crawler/run`
**Chạy crawler để thu thập công việc (admin only)**

**Query Parameters:**
- `keyword` (string): Từ khóa tìm kiếm
- `location` (string): Địa điểm
- `max_pages` (int): Số trang tối đa (default: 2)
- `source` (string): Nguồn - `all`, `topcv`, `vietnamworks`, `itviec`

**Example:**
```
POST /api/crawler/run?keyword=python&location=hanoi&max_pages=3&source=topcv
```

**Response:**
```json
{
  "message": "Crawler started in background",
  "source": "topcv",
  "keyword": "python",
  "location": "hanoi"
}
```

#### GET `/api/crawler/status`
**Lấy thống kê crawler (admin only)**

**Response:**
```json
{
  "total_crawled_jobs": 150,
  "sources": [
    {
      "source": "topcv",
      "total_jobs": 50,
      "last_scraped": "2026-05-19 10:00:00"
    },
    {
      "source": "vietnamworks",
      "total_jobs": 60,
      "last_scraped": "2026-05-19 09:30:00"
    },
    {
      "source": "itviec",
      "total_jobs": 40,
      "last_scraped": "2026-05-19 09:00:00"
    }
  ]
}
```

---

### **Notifications** (`/api`)

#### GET `/api/notifications`
Lấy danh sách thông báo

#### GET `/api/notifications/unread-count`
Đếm số thông báo chưa đọc

#### PUT `/api/notifications/{notification_id}/read`
Đánh dấu thông báo đã đọc

#### PUT `/api/notifications/read-all`
Đánh dấu tất cả thông báo đã đọc

#### DELETE `/api/notifications/{notification_id}`
Xóa thông báo

---

## 🔐 Authentication

Tất cả các endpoint có đánh dấu "(cần token)" yêu cầu JWT token trong header:

```
Authorization: Bearer <your_token>
```

---

## 🎭 User Roles

- **job_seeker**: Người tìm việc
- **employer**: Nhà tuyển dụng
- **admin**: Quản trị viên

---

## 📊 Workflow

### **Cho Người Tìm Việc:**

1. Đăng ký/Đăng nhập
2. Cập nhật profile (vị trí, kỹ năng, mức lương mong muốn)
3. Bật "Ready to Work" để nhận thông báo công việc phù hợp
4. Tìm kiếm công việc với filter
5. Ứng tuyển công việc
6. Nhận thông báo về trạng thái đơn ứng tuyển
7. Nhận đánh giá từ nhà tuyển dụng

### **Cho Nhà Tuyển Dụng:**

1. Đăng ký tài khoản employer
2. Đăng tin tuyển dụng
3. Xem danh sách ứng viên đã apply
4. Tìm ứng viên phù hợp với công việc
5. Gửi thông báo cho ứng viên phù hợp
6. Cập nhật trạng thái đơn ứng tuyển
7. Đánh giá ứng viên sau khi hoàn thành công việc

### **Cho Admin:**

1. Quản lý tất cả users và jobs
2. Chạy crawler để thu thập công việc từ các trang tuyển dụng
3. Xem thống kê hệ thống
4. Kiểm duyệt công việc

---

## 🚀 Testing

Truy cập Swagger UI để test API:
```
http://localhost:8000/docs
```

---

## 📝 Notes

- Công việc từ crawler sẽ có `source_url` để người dùng có thể truy cập trang gốc
- Hệ thống matching tính điểm dựa trên: khoảng cách (40%), kỹ năng (30%), lương (20%), đánh giá (10%)
- Thông báo tự động được gửi khi:
  - Có công việc phù hợp (khi bật Ready to Work)
  - Trạng thái đơn ứng tuyển thay đổi
  - Nhà tuyển dụng gửi thông báo cho ứng viên phù hợp
