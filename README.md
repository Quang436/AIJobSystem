# 🎯 AI Job Recommendation System v2.0

Hệ thống tìm việc thông minh với AI, matching tự động, và web crawler.

## ✨ Tính Năng Chính

### 🔍 **Tìm Kiếm & Lọc Công Việc**
- Tìm kiếm theo từ khóa, địa điểm
- Lọc theo loại công việc: Full-time, Part-time, Freelance
- Lọc theo mức lương
- Lọc theo kỹ năng
- Tìm kiếm theo bán kính (km)
- Hiển thị khoảng cách từ vị trí hiện tại

### 🤖 **AI Matching Tự Động**
- Bật nút "Sẵn sàng làm việc"
- Hệ thống tự động tìm công việc phù hợp dựa trên:
  - Vị trí địa lý (GPS)
  - Kỹ năng
  - Mức lương mong muốn
  - Loại công việc
- Tính điểm phù hợp (Match Score)
- Gửi thông báo tự động cho người dùng

### 🕷️ **Web Crawler**
Thu thập công việc từ các trang tuyển dụng:
- **TopCV.vn**
- **VietnamWorks.com**
- **ITviec.com**

Công việc từ crawler có:
- Link gốc để ứng tuyển trực tiếp
- Thông tin lương cụ thể
- Địa chỉ chi tiết
- Tự động chống trùng lặp

### ⭐ **Hệ Thống Đánh Giá**
- Đánh giá người dùng (1-5 sao)
- Hiển thị rating trung bình
- Comment đánh giá
- Lịch sử đánh giá

### 👔 **Dành Cho Nhà Tuyển Dụng**
- Đăng tin tuyển dụng
- Xem danh sách ứng viên đã apply
- Tìm ứng viên phù hợp với công việc
- Gửi thông báo cho ứng viên phù hợp
- Cập nhật trạng thái đơn ứng tuyển (pending, reviewing, accepted, rejected)
- Đánh giá ứng viên

### 🔔 **Hệ Thống Thông Báo**
- Thông báo công việc phù hợp
- Thông báo cập nhật đơn ứng tuyển
- Thông báo từ nhà tuyển dụng
- Đếm số thông báo chưa đọc

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Web framework
- **SQL Server** - Database
- **PyODBC** - Database connector
- **JWT** - Authentication
- **BeautifulSoup4** - Web scraping
- **Geopy** - Location & distance calculation
- **Scikit-learn** - AI/ML recommendation

### Frontend
- **HTML5/CSS3/JavaScript**
- **Leaflet.js** - Interactive maps
- **Fetch API** - HTTP requests

---

## 📦 Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd CDNNLT
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Database
Chạy file `findJob.sql` trong SQL Server để tạo database và tables.

### 4. Configure Environment
Tạo file `.env`:
```env
DB_SERVER=localhost
DB_DATABASE=job_agent_db
DB_USERNAME=
DB_PASSWORD=

JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440
```

### 5. Run Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🚀 Quick Start

### Truy cập ứng dụng:
- **Frontend**: http://localhost:8000/html/index.html
- **API Docs**: http://localhost:8000/docs
- **Admin Dashboard**: http://localhost:8000/html/admin-dashboard.html

### Tài khoản mặc định:
Tạo tài khoản admin bằng script:
```bash
python scratch/create_admin.py
```

---

## 📖 API Documentation

Xem chi tiết tại: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

### Các endpoint chính:

#### Authentication
- `POST /api/register` - Đăng ký
- `POST /api/login` - Đăng nhập
- `GET /api/profile` - Lấy profile
- `PUT /api/profile/update` - Cập nhật profile

#### Jobs
- `GET /api/jobs/search` - Tìm kiếm với filter
- `POST /api/jobs` - Tạo công việc
- `POST /api/apply/{job_id}` - Ứng tuyển
- `GET /api/jobs/{job_id}/applications` - Xem ứng viên

#### Matching
- `POST /api/ready-to-work/toggle` - Bật/tắt sẵn sàng làm việc
- `GET /api/matching/find-jobs` - Tìm công việc phù hợp
- `GET /api/matching/find-candidates` - Tìm ứng viên phù hợp

#### Crawler
- `POST /api/crawler/run` - Chạy crawler
- `GET /api/crawler/status` - Xem thống kê crawler

#### Reviews
- `POST /api/reviews` - Tạo đánh giá
- `GET /api/reviews/user/{user_id}` - Xem đánh giá

#### Notifications
- `GET /api/notifications` - Lấy thông báo
- `GET /api/notifications/unread-count` - Đếm chưa đọc

---

## 🎯 Use Cases

### 1. Người Tìm Việc
```
1. Đăng ký tài khoản
2. Cập nhật vị trí, kỹ năng, mức lương mong muốn
3. Bật "Sẵn sàng làm việc"
4. Nhận thông báo công việc phù hợp
5. Tìm kiếm và lọc công việc
6. Ứng tuyển (có thể chuyển sang trang gốc nếu từ crawler)
7. Theo dõi trạng thái đơn ứng tuyển
8. Nhận đánh giá từ nhà tuyển dụng
```

### 2. Nhà Tuyển Dụng
```
1. Đăng ký tài khoản employer
2. Đăng tin tuyển dụng
3. Xem danh sách ứng viên đã apply
4. Tìm ứng viên phù hợp (AI matching)
5. Gửi thông báo cho ứng viên phù hợp
6. Cập nhật trạng thái đơn ứng tuyển
7. Đánh giá ứng viên
```

### 3. Admin
```
1. Quản lý users và jobs
2. Chạy crawler để thu thập công việc
3. Xem thống kê hệ thống
4. Kiểm duyệt công việc
```

---

## 🔧 Configuration

### Crawler Settings
Trong `app/services/job_crawler.py`:
- Điều chỉnh `max_pages` để thu thập nhiều/ít trang hơn
- Thêm delay giữa các request để tránh bị block
- Customize parsing logic cho từng trang

### Matching Algorithm
Trong `app/routers/matching_router.py`:
- Điểm khoảng cách: 40%
- Điểm kỹ năng: 30%
- Điểm lương: 20%
- Điểm đánh giá: 10%

Có thể điều chỉnh tỷ lệ này theo nhu cầu.

---

## 📊 Database Schema

### Main Tables:
- `users` - Người dùng (job_seeker, employer, admin)
- `employer_profiles` - Thông tin nhà tuyển dụng
- `jobs` - Công việc
- `job_applications` - Đơn ứng tuyển
- `reviews` - Đánh giá
- `notifications` - Thông báo
- `facebook_groups` - Nhóm Facebook (cho crawler)
- `scrape_tasks` - Lịch chạy crawler

---

## 🐛 Troubleshooting

### Lỗi kết nối database:
```
Kiểm tra:
1. SQL Server đang chạy
2. Database đã được tạo
3. Thông tin kết nối trong .env đúng
4. ODBC Driver 17 for SQL Server đã cài đặt
```

### Crawler không hoạt động:
```
Kiểm tra:
1. Kết nối internet
2. Các trang web có thay đổi cấu trúc HTML không
3. Có bị block bởi anti-bot không
4. Thư viện beautifulsoup4, lxml đã cài đặt
```

### Matching không chính xác:
```
Kiểm tra:
1. User đã cập nhật vị trí (latitude, longitude)
2. User đã cập nhật kỹ năng và mức lương mong muốn
3. Jobs có thông tin đầy đủ (vị trí, kỹ năng, lương)
```

---

## 📝 TODO

- [ ] Thêm WebSocket cho real-time notifications
- [ ] Tích hợp Google Maps API cho geocoding tự động
- [ ] Thêm AI recommendation dựa trên lịch sử tìm kiếm
- [ ] Thêm chat giữa employer và candidate
- [ ] Mobile app (React Native)
- [ ] Email notifications
- [ ] Advanced analytics dashboard

---

## 👥 Contributors

- **Quốc** - Developer

---

## 📄 License

MIT License

---

## 📞 Contact

Email: [your-email@example.com]
GitHub: [your-github]
