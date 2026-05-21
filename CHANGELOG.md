# 📝 Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2026-05-19

### 🎉 Major Release - Complete Feature Set

### ✨ Added

#### Backend Features
- **Advanced Job Filtering**
  - Filter by job type (full-time, part-time, freelance)
  - Filter by salary range (min/max)
  - Filter by skills (multiple skills support)
  - Filter by radius (km)
  - Search by keyword and location

- **Web Crawler System**
  - TopCV.vn crawler
  - VietnamWorks.com crawler
  - ITviec.com crawler
  - Auto-deduplication by external_id
  - Save original source URL
  - Extract salary and location details

- **Review & Rating System**
  - Create reviews (1-5 stars)
  - Add comments to reviews
  - Auto-calculate average rating
  - View review history
  - Prevent self-review

- **Ready to Work & Matching**
  - Toggle "Ready to Work" status
  - Auto-find matching jobs
  - Calculate match score (distance 40%, skills 30%, salary 20%, rating 10%)
  - Find matching candidates for employers
  - Auto-send notifications

- **Employer Features**
  - View job applications
  - Update application status (pending/reviewing/accepted/rejected)
  - Find matching candidates with AI
  - Send notifications to candidates
  - View candidate CV and ratings

- **Notification System**
  - Job match notifications
  - Application status update notifications
  - Employer notifications
  - Unread count
  - Mark as read/delete

#### API Endpoints
- `GET /api/jobs/search` - Advanced search with filters
- `POST /api/crawler/run` - Run web crawler
- `GET /api/crawler/status` - Get crawler statistics
- `POST /api/reviews` - Create review
- `GET /api/reviews/user/{user_id}` - Get user reviews
- `POST /api/ready-to-work/toggle` - Toggle ready status
- `GET /api/matching/find-jobs` - Find matching jobs
- `GET /api/matching/find-candidates` - Find matching candidates
- `POST /api/matching/notify-candidates` - Notify candidates
- `GET /api/jobs/{job_id}/applications` - Get job applications
- `PUT /api/applications/{app_id}/status` - Update application status
- `GET /api/notifications` - Get notifications
- `GET /api/notifications/unread-count` - Get unread count
- `PUT /api/notifications/{id}/read` - Mark as read
- `DELETE /api/notifications/{id}` - Delete notification

#### Frontend
- **Employer Dashboard** (`html/employer-dashboard.html`)
  - Stats cards (total jobs, applications, pending, accepted)
  - Job list with actions
  - View applicants modal
  - Find matching candidates modal
  - Create job modal
  - Responsive design

- **Updated API Client** (`js/api.js`)
  - All new API methods
  - Employer-specific methods
  - Matching methods
  - Review methods
  - Notification methods
  - Crawler methods

#### Database
- **New Tables**
  - `reviews` - User reviews and ratings
  - `notifications` - System notifications
  - `job_corrections` - AI learning (reserved)

- **New Columns in `users`**
  - `average_rating` - Average rating score
  - `total_reviews` - Total number of reviews
  - `is_ready_to_work` - Ready to work status
  - `preferred_radius_km` - Preferred work radius
  - `preferred_salary_min` - Minimum salary expectation
  - `preferred_skills` - User skills

- **New Columns in `jobs`**
  - `job_type` - Job type (full-time, part-time, freelance)
  - `salary_min`, `salary_max` - Salary range
  - `source_url` - Original job posting URL
  - `external_id` - External source ID (for deduplication)
  - `requirements` - Job requirements

#### Services
- `app/services/job_crawler.py` - Web crawler implementation
  - `JobCrawler` - Base crawler class
  - `TopCVCrawler` - TopCV crawler
  - `VietnamWorksCrawler` - VietnamWorks crawler
  - `ITviecCrawler` - ITviec crawler
  - `crawl_all_sources()` - Crawl from all sources

#### Routers
- `app/routers/review_router.py` - Review management
- `app/routers/matching_router.py` - Matching algorithms
- `app/routers/crawler_router.py` - Crawler control
- `app/routers/notification_router.py` - Notification management

#### Schemas
- `app/schemas/review_schema.py` - Review data models
- Updated `app/schemas/job_schema.py` - Added JobFilter

#### Documentation
- `README.md` - Project overview
- `API_DOCUMENTATION.md` - Complete API documentation
- `FEATURES_COMPLETED.md` - Features checklist
- `DEPLOYMENT_GUIDE.md` - Deployment instructions
- `SUMMARY.md` - Project summary
- `QUICK_START.md` - Quick start guide
- `INDEX.md` - Documentation index
- `CHANGELOG.md` - This file
- `test_new_features.py` - Test script

### 🔧 Changed
- Updated `app/main.py` - Added new routers with `/api` prefix
- Updated `app/routers/job_router.py` - Enhanced search with filters
- Updated `js/api.js` - Added all new API methods
- Updated `requirements.txt` - Added beautifulsoup4, lxml, html5lib

### 🐛 Fixed
- Fixed API endpoint paths (added `/api` prefix)
- Fixed CORS configuration
- Fixed authentication middleware

### 📚 Dependencies Added
- `beautifulsoup4==4.14.3` - HTML parsing
- `lxml==6.1.1` - XML/HTML processing
- `html5lib==1.1` - HTML5 parser
- `requests==2.32.3` - HTTP library (already existed)

---

## [1.0.0] - 2026-05-18

### Initial Release

#### Features
- User authentication (JWT)
- Job listing and search
- Job application
- User profiles
- Admin dashboard
- Location-based search
- Interactive map (Leaflet.js)
- Basic recommendation system

#### Tech Stack
- FastAPI
- SQL Server
- HTML/CSS/JavaScript
- Leaflet.js

---

## Version History

- **v2.0.0** (2026-05-19) - Complete feature set with crawler, matching, reviews
- **v1.0.0** (2026-05-18) - Initial release with basic features

---

## Upcoming Features (Roadmap)

### v2.1.0 (Planned)
- [ ] WebSocket for real-time notifications
- [ ] Email notifications
- [ ] SMS notifications
- [ ] Enhanced UI for user dashboard
- [ ] Notification UI component

### v2.2.0 (Planned)
- [ ] Chat between employer and candidate
- [ ] Video interview integration
- [ ] Advanced analytics dashboard
- [ ] Mobile app (React Native)

### v3.0.0 (Future)
- [ ] AI-powered CV parsing
- [ ] Salary prediction model
- [ ] Job recommendation based on browsing history
- [ ] Multi-language support
- [ ] Payment integration

---

## Breaking Changes

### v2.0.0
- All API endpoints now have `/api` prefix
  - Old: `GET /jobs`
  - New: `GET /api/jobs`
- Updated authentication flow
- Database schema changes (new tables and columns)

---

## Migration Guide

### From v1.0.0 to v2.0.0

#### Database Migration
```sql
-- Run the updated findJob.sql script
-- It will drop and recreate the database with new schema
```

#### API Client Update
```javascript
// Update all API calls to include /api prefix
// Old
fetch('http://localhost:8000/jobs')

// New
fetch('http://localhost:8000/api/jobs')
```

#### Environment Variables
```env
# No changes required
# Same .env configuration works
```

---

## Contributors

- **Quốc** - Lead Developer

---

## License

MIT License

---

**For detailed information about each feature, see [FEATURES_COMPLETED.md](FEATURES_COMPLETED.md)**
