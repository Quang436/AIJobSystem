# 🚀 Hướng Dẫn Triển Khai

## Yêu Cầu Hệ Thống

### Phần Mềm Cần Thiết
- Python 3.9+
- SQL Server 2019+
- ODBC Driver 17 for SQL Server
- Git (optional)

### Thư Viện Python
Xem file `requirements.txt`

---

## 📦 Cài Đặt

### Bước 1: Clone Repository
```bash
git clone <repository-url>
cd CDNNLT
```

### Bước 2: Tạo Virtual Environment (Khuyến nghị)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Bước 3: Cài Đặt Dependencies
```bash
pip install -r requirements.txt
```

### Bước 4: Cài Đặt ODBC Driver

#### Windows:
Download và cài đặt từ:
https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

#### Linux (Ubuntu/Debian):
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

---

## 🗄️ Cấu Hình Database

### Bước 1: Tạo Database
1. Mở SQL Server Management Studio (SSMS)
2. Chạy file `findJob.sql`
3. Database `job_agent_db` sẽ được tạo với tất cả tables

### Bước 2: Kiểm Tra Kết Nối
```sql
USE job_agent_db;
SELECT COUNT(*) FROM users;
```

### Bước 3: Tạo Admin Account (Optional)
```bash
python scratch/create_admin.py
```

---

## ⚙️ Cấu Hình Environment

### Tạo file `.env` trong thư mục gốc:
```env
# Database Configuration
DB_SERVER=localhost
DB_DATABASE=job_agent_db
DB_USERNAME=
DB_PASSWORD=

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# Optional: Google Maps API (for geocoding)
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

**Lưu ý:**
- Nếu dùng Windows Authentication, để trống `DB_USERNAME` và `DB_PASSWORD`
- Nếu dùng SQL Server Authentication, điền username và password
- Đổi `JWT_SECRET_KEY` trong production!

---

## 🚀 Chạy Ứng Dụng

### Development Mode
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Với Gunicorn (Linux/Mac)
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 🌐 Truy Cập Ứng Dụng

### URLs
- **Frontend**: http://localhost:8000/html/index.html
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Admin Dashboard**: http://localhost:8000/html/admin-dashboard.html
- **Employer Dashboard**: http://localhost:8000/html/employer-dashboard.html

---

## 🔧 Cấu Hình Nâng Cao

### 1. CORS Settings
Trong `app/main.py`, cập nhật:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Thay * bằng domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Database Connection Pool
Trong `app/database/database.py`, thêm connection pooling:
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    connection_string,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

### 3. Logging
Tạo file `logging_config.py`:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

---

## 🐳 Docker Deployment (Optional)

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install ODBC Driver
RUN apt-get update && apt-get install -y \
    curl apt-transport-https gnupg2 \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_SERVER=sqlserver
      - DB_DATABASE=job_agent_db
      - DB_USERNAME=sa
      - DB_PASSWORD=YourPassword123
    depends_on:
      - sqlserver
    volumes:
      - .:/app

  sqlserver:
    image: mcr.microsoft.com/mssql/server:2019-latest
    environment:
      - ACCEPT_EULA=Y
      - SA_PASSWORD=YourPassword123
    ports:
      - "1433:1433"
    volumes:
      - sqldata:/var/opt/mssql

volumes:
  sqldata:
```

### Chạy với Docker
```bash
docker-compose up -d
```

---

## 🔒 Security Checklist

### Production Deployment
- [ ] Đổi `JWT_SECRET_KEY` thành giá trị ngẫu nhiên mạnh
- [ ] Cấu hình CORS với domain cụ thể (không dùng `*`)
- [ ] Sử dụng HTTPS (SSL/TLS)
- [ ] Giới hạn rate limiting
- [ ] Cấu hình firewall
- [ ] Backup database định kỳ
- [ ] Monitoring và logging
- [ ] Cập nhật dependencies thường xuyên
- [ ] Sử dụng environment variables cho secrets
- [ ] Disable debug mode

### Database Security
- [ ] Sử dụng strong password
- [ ] Giới hạn quyền truy cập database
- [ ] Encrypt sensitive data
- [ ] Regular backups
- [ ] SQL injection prevention (đã có với parameterized queries)

---

## 📊 Monitoring & Logging

### 1. Application Logs
```bash
# Xem logs real-time
tail -f app.log

# Tìm errors
grep ERROR app.log
```

### 2. Database Monitoring
```sql
-- Check active connections
SELECT * FROM sys.dm_exec_sessions WHERE is_user_process = 1;

-- Check slow queries
SELECT TOP 10 
    total_elapsed_time/execution_count AS avg_time,
    text
FROM sys.dm_exec_query_stats
CROSS APPLY sys.dm_exec_sql_text(sql_handle)
ORDER BY avg_time DESC;
```

### 3. API Monitoring
Sử dụng tools như:
- Prometheus + Grafana
- New Relic
- DataDog
- Sentry (error tracking)

---

## 🔄 Backup & Recovery

### Database Backup
```sql
-- Full backup
BACKUP DATABASE job_agent_db 
TO DISK = 'C:\Backups\job_agent_db.bak'
WITH FORMAT, INIT, NAME = 'Full Backup';

-- Restore
RESTORE DATABASE job_agent_db 
FROM DISK = 'C:\Backups\job_agent_db.bak'
WITH REPLACE;
```

### Automated Backup Script (Windows)
```batch
@echo off
set BACKUP_DIR=C:\Backups
set DATE=%date:~-4,4%%date:~-10,2%%date:~-7,2%
sqlcmd -S localhost -Q "BACKUP DATABASE job_agent_db TO DISK = '%BACKUP_DIR%\job_agent_db_%DATE%.bak'"
```

---

## 🧪 Testing

### Run Tests
```bash
# API tests
python test_new_features.py

# Unit tests (if available)
pytest tests/

# Coverage
pytest --cov=app tests/
```

---

## 🚨 Troubleshooting

### Lỗi: "No module named 'pyodbc'"
```bash
pip install pyodbc
```

### Lỗi: "ODBC Driver not found"
Cài đặt ODBC Driver 17 for SQL Server

### Lỗi: "Cannot connect to database"
1. Kiểm tra SQL Server đang chạy
2. Kiểm tra firewall
3. Kiểm tra connection string trong `.env`
4. Test connection:
```python
python -c "from app.database.database import get_connection; conn = get_connection(); print('Connected!')"
```

### Lỗi: "Port 8000 already in use"
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Crawler không hoạt động
1. Kiểm tra kết nối internet
2. Kiểm tra các trang web có thay đổi cấu trúc không
3. Thêm delay giữa requests
4. Sử dụng proxy nếu bị block

---

## 📈 Performance Optimization

### 1. Database Indexing
```sql
-- Đã có trong findJob.sql
CREATE INDEX IX_jobs_status ON jobs(status);
CREATE INDEX IX_jobs_location ON jobs(latitude, longitude);
```

### 2. Caching (Redis)
```python
# Install redis
pip install redis

# In app/main.py
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
```

### 3. Load Balancing
Sử dụng Nginx:
```nginx
upstream backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
    }
}
```

---

## 📞 Support

Nếu gặp vấn đề, kiểm tra:
1. Logs: `app.log`
2. API Docs: http://localhost:8000/docs
3. Database connection
4. Environment variables

---

## ✅ Deployment Checklist

- [ ] Database đã được tạo và migrate
- [ ] File `.env` đã được cấu hình
- [ ] Dependencies đã được cài đặt
- [ ] ODBC Driver đã được cài đặt
- [ ] Server chạy thành công
- [ ] API docs accessible
- [ ] Frontend accessible
- [ ] Admin account đã được tạo
- [ ] CORS đã được cấu hình
- [ ] SSL/HTTPS đã được setup (production)
- [ ] Backup strategy đã được thiết lập
- [ ] Monitoring đã được cấu hình

---

**Chúc bạn deploy thành công! 🎉**
