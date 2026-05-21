# 🚀 Quick Start Guide

## Bắt Đầu Nhanh trong 5 Phút

### Bước 1: Kiểm Tra SQL Server
```bash
# Mở SQL Server Management Studio (SSMS)
# Hoặc kiểm tra service đang chạy:
services.msc
# Tìm "SQL Server" và đảm bảo nó đang chạy
```

### Bước 2: Tạo Database
```sql
-- Mở SSMS và chạy file:
-- findJob.sql
```

### Bước 3: Cấu Hình .env
Tạo file `.env` trong thư mục gốc:
```env
DB_SERVER=localhost
DB_DATABASE=job_agent_db
DB_USERNAME=
DB_PASSWORD=

JWT_SECRET_KEY=my-super-secret-key-123
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440
```

**Lưu ý**: Nếu dùng Windows Authentication, để trống username và password

### Bước 4: Cài Đặt Dependencies
```bash
pip install -r requirements.txt
```

### Bước 5: Chạy Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Bước 6: Truy Cập
- Frontend: http://localhost:8000/html/index.html
- API Docs: http://localhost:8000/docs
- Employer Dashboard: http://localhost:8000/html/employer-dashboard.html

---

## 🔧 Khắc Phục Lỗi Thường Gặp

### Lỗi: "Cannot connect to SQL Server"

**Giải pháp 1**: Kiểm tra SQL Server đang chạy
```bash
# Windows: Mở Services
services.msc
# Tìm "SQL Server" và Start nếu chưa chạy
```

**Giải pháp 2**: Kiểm tra connection string
```python
# Test connection
python -c "from app.database.database import get_connection; conn = get_connection(); print('Connected!')"
```

**Giải pháp 3**: Sử dụng SQL Server Authentication
```env
# Trong .env
DB_SERVER=localhost
DB_DATABASE=job_agent_db
DB_USERNAME=sa
DB_PASSWORD=YourPassword
```

### Lỗi: "ODBC Driver not found"

**Giải pháp**: Cài đặt ODBC Driver 17
- Download: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
- Cài đặt và restart

### Lỗi: "Module not found"

**Giải pháp**: Cài đặt lại dependencies
```bash
pip install -r requirements.txt
```

---

## 📝 Tạo Tài Khoản Test

### Tạo Admin
```bash
python scratch/create_admin.py
```

### Tạo User qua API
```bash
# Truy cập: http://localhost:8000/docs
# Sử dụng endpoint POST /api/register
```

---

## 🎯 Test Các Tính Năng

### 1. Test Search với Filter
```
GET http://localhost:8000/api/jobs/search?job_type=full-time&salary_min=10
```

### 2. Test Crawler (cần admin token)
```
POST http://localhost:8000/api/crawler/run?keyword=python&location=hanoi&source=topcv
```

### 3. Test Matching
```
POST http://localhost:8000/api/ready-to-work/toggle
GET http://localhost:8000/api/matching/find-jobs
```

---

## 📚 Tài Liệu Chi Tiết

- **README.md** - Tổng quan
- **API_DOCUMENTATION.md** - API chi tiết
- **DEPLOYMENT_GUIDE.md** - Hướng dẫn deploy
- **FEATURES_COMPLETED.md** - Tính năng đã làm
- **SUMMARY.md** - Tổng kết dự án

---

## ✅ Checklist

- [ ] SQL Server đang chạy
- [ ] Database đã được tạo (chạy findJob.sql)
- [ ] File .env đã được tạo
- [ ] Dependencies đã được cài đặt
- [ ] Server chạy thành công
- [ ] Truy cập được http://localhost:8000/docs

---

**Nếu vẫn gặp lỗi, xem DEPLOYMENT_GUIDE.md để biết chi tiết!**
