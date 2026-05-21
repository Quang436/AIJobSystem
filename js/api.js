/**
 * GeoJob API Service
 * Quản lý toàn bộ kết nối giữa Frontend và Backend FastAPI
 */

const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',
    KEYS: {
        GOOGLE_MAPS: 'YOUR_GOOGLE_MAPS_API_KEY_HERE',
    },
};

// ==========================================
// Token Management - Quản lý JWT Token
// ==========================================
const TokenService = {
    getToken() {
        return localStorage.getItem('access_token');
    },
    setToken(token) {
        localStorage.setItem('access_token', token);
    },
    removeToken() {
        localStorage.removeItem('access_token');
    },
    getAuthHeaders() {
        const token = this.getToken();
        if (!token) return {};
        return {
            'Authorization': `Bearer ${token}`
        };
    },
    isLoggedIn() {
        return !!this.getToken();
    }
};

// ==========================================
// API Service - Gọi Backend
// ==========================================
const ApiService = {

    // ---------- Hàm fetch chung ----------
    async _request(url, options = {}) {
        const defaultHeaders = {
            'Content-Type': 'application/json',
            ...TokenService.getAuthHeaders()
        };

        const config = {
            ...options,
            headers: {
                ...defaultHeaders,
                ...options.headers
            }
        };

        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}${url}`, config);
            const data = await response.json();

            if (!response.ok) {
                // Nếu 401 - token hết hạn, redirect login
                if (response.status === 401) {
                    TokenService.removeToken();
                    localStorage.removeItem('userEmail');
                    localStorage.removeItem('userName');
                    localStorage.removeItem('userRole');
                    window.location.href = 'login.html';
                    return null;
                }
                throw { status: response.status, data };
            }

            return data;
        } catch (error) {
            if (error.status) throw error; // Re-throw API errors
            console.error('[API Error]', error);
            throw { status: 0, data: { message: 'Không thể kết nối đến server. Vui lòng kiểm tra backend.' } };
        }
    },

    // ==========================================
    // AUTH - Đăng ký, Đăng nhập, Profile
    // ==========================================

    /**
     * Đăng ký tài khoản Ứng viên (Nhân viên VP / IT / Fresher)
     */
    async registerCandidate(data) {
        return this._request('/api/register-candidate', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    /**
     * Đăng ký tài khoản Thợ kỹ thuật / Việc tự do
     */
    async registerGigworker(data) {
        return this._request('/api/register-gigworker', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    /**
     * Đăng ký tài khoản Employer
     */
    async registerEmployer(data) {
        return this._request('/api/register-employer', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    /**
     * Đăng nhập, nhận JWT token
     */
    async login(email, password) {
        const data = await this._request('/api/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });

        if (data && data.access_token) {
            TokenService.setToken(data.access_token);
            return data;
        }

        return data; // Trường hợp login sai trả về {message: "Invalid email or password"}
    },

    /**
     * Lấy profile user hiện tại
     */
    async getProfile() {
        return this._request('/api/profile');
    },

    /**
     * Cập nhật profile
     */
    async updateProfile(profileData) {
        return this._request('/api/profile/update', {
            method: 'PUT',
            body: JSON.stringify(profileData)
        });
    },

    // ==========================================
    // JOBS - Quản lý việc làm
    // ==========================================

    /**
     * Lấy danh sách tất cả việc làm
     */
    async getJobs() {
        return this._request('/api/jobs');
    },

    /**
     * Tìm kiếm việc làm
     */
    async searchJobs(keyword, location, lat, lng, radius) {
        const params = new URLSearchParams();
        if (keyword) params.append('keyword', keyword);
        if (location) params.append('location', location);
        if (lat != null) params.append('lat', lat);
        if (lng != null) params.append('lng', lng);
        if (radius != null) params.append('radius', radius);

        return this._request(`/api/jobs/search?${params.toString()}`);
    },

    /**
     * Lấy dữ liệu tọa độ việc làm cho bản đồ
     */
    async getMapData() {
        return this._request('/api/jobs/map');
    },

    /**
     * Lấy chi tiết một công việc
     */
    async getJobDetail(jobId) {
        return this._request(`/api/jobs/${jobId}`);
    },

    /**
     * Ứng tuyển công việc
     */
    async applyJob(jobId) {
        return this._request(`/api/apply/${jobId}`, {
            method: 'POST'
        });
    },

    /**
     * Tạo công việc mới (admin/employer)
     */
    async createJob(jobData) {
        return this._request('/api/jobs', {
            method: 'POST',
            body: JSON.stringify(jobData)
        });
    },

    /**
     * Cập nhật công việc (admin/employer)
     */
    async updateJob(jobId, jobData) {
        return this._request(`/api/jobs/${jobId}`, {
            method: 'PUT',
            body: JSON.stringify(jobData)
        });
    },

    /**
     * Xóa công việc (admin/employer)
     */
    async deleteJob(jobId) {
        return this._request(`/api/jobs/${jobId}`, {
            method: 'DELETE'
        });
    },

    /**
     * Tạo công việc khẩn cấp (không cần đăng nhập)
     */
    async createUrgentGuestJob(data) {
        const params = new URLSearchParams();
        params.append('title', data.title);
        params.append('description', data.description);
        params.append('phone', data.phone);
        params.append('address', data.address);
        params.append('gps_lat', data.gps_lat);
        params.append('gps_lng', data.gps_lng);
        if (data.skills) params.append('skills', data.skills);

        return this._request(`/api/jobs/urgent-guest?${params.toString()}`, {
            method: 'POST'
        });
    },

    // ==========================================
    // RECOMMENDATION & DISTANCE
    // ==========================================

    /**
     * Lấy gợi ý việc làm theo kỹ năng
     */
    async getRecommendations(skill) {
        return this._request(`/api/recommend?skill=${encodeURIComponent(skill)}`);
    },

    /**
     * Lấy việc làm sắp xếp theo khoảng cách
     */
    async getJobsByDistance(lat, lng) {
        return this._request(`/api/jobs-distance?lat=${lat}&lng=${lng}`);
    },

    // ==========================================
    // USER - Đơn ứng tuyển, Ứng dụng
    // ==========================================

    /**
     * Lấy danh sách đơn ứng tuyển của user
     */
    async getMyApplications() {
        return this._request('/api/my-applications');
    },

    // ==========================================
    // EMPLOYER - Dành cho nhà tuyển dụng
    // ==========================================

    /**
     * Lấy danh sách công việc của employer
     */
    async getEmployerJobs() {
        return this._request('/api/jobs/employer');
    },

    /**
     * Lấy danh sách ứng viên đã apply vào job
     */
    async getJobApplications(jobId) {
        return this._request(`/api/jobs/${jobId}/applications`);
    },

    /**
     * Cập nhật trạng thái đơn ứng tuyển
     */
    async updateApplicationStatus(applicationId, status) {
        return this._request(`/api/applications/${applicationId}/status?status=${status}`, {
            method: 'PUT'
        });
    },

    /**
     * Tìm ứng viên phù hợp cho công việc
     */
    async findMatchingCandidates(jobId) {
        return this._request(`/api/matching/find-candidates?job_id=${jobId}`);
    },

    /**
     * Gửi thông báo cho ứng viên phù hợp
     */
    async notifyMatchingCandidates(jobId) {
        return this._request(`/api/matching/notify-candidates?job_id=${jobId}`, {
            method: 'POST'
        });
    },

    // ==========================================
    // MATCHING - Tìm việc/ứng viên phù hợp
    // ==========================================

    /**
     * Bật/tắt trạng thái sẵn sàng làm việc
     */
    async toggleReadyToWork() {
        return this._request('/api/ready-to-work/toggle', {
            method: 'POST'
        });
    },

    /**
     * Tìm công việc phù hợp
     */
    async findMatchingJobs() {
        return this._request('/api/matching/find-jobs');
    },

    // ==========================================
    // REVIEWS - Đánh giá
    // ==========================================

    /**
     * Tạo đánh giá cho người dùng
     */
    async createReview(reviewData) {
        return this._request('/api/reviews', {
            method: 'POST',
            body: JSON.stringify(reviewData)
        });
    },

    /**
     * Lấy đánh giá của một người dùng
     */
    async getUserReviews(userId) {
        return this._request(`/api/reviews/user/${userId}`);
    },

    /**
     * Lấy đánh giá của tôi
     */
    async getMyReviews() {
        return this._request('/api/reviews/my-reviews');
    },

    // ==========================================
    // NOTIFICATIONS - Thông báo
    // ==========================================

    /**
     * Lấy danh sách thông báo
     */
    async getNotifications() {
        return this._request('/api/notifications');
    },

    /**
     * Đếm số thông báo chưa đọc
     */
    async getUnreadCount() {
        return this._request('/api/notifications/unread-count');
    },

    /**
     * Đánh dấu thông báo đã đọc
     */
    async markAsRead(notificationId) {
        return this._request(`/api/notifications/${notificationId}/read`, {
            method: 'PUT'
        });
    },

    /**
     * Đánh dấu tất cả đã đọc
     */
    async markAllAsRead() {
        return this._request('/api/notifications/read-all', {
            method: 'PUT'
        });
    },

    /**
     * Xóa thông báo
     */
    async deleteNotification(notificationId) {
        return this._request(`/api/notifications/${notificationId}`, {
            method: 'DELETE'
        });
    },

    // ==========================================
    // CRAWLER - Thu thập dữ liệu
    // ==========================================

    /**
     * Chạy crawler (admin only)
     */
    async runCrawler(keyword, location, maxPages, source) {
        const params = new URLSearchParams();
        if (keyword) params.append('keyword', keyword);
        if (location) params.append('location', location);
        if (maxPages) params.append('max_pages', maxPages);
        if (source) params.append('source', source);

        return this._request(`/api/crawler/run?${params.toString()}`, {
            method: 'POST'
        });
    },

    /**
     * Lấy thống kê crawler (admin only)
     */
    async getCrawlerStatus() {
        return this._request('/api/crawler/status');
    },

    // ==========================================
    // ADMIN
    // ==========================================

    /**
     * Lấy thống kê hệ thống (admin only)
     */
    async getAdminStats() {
        return this._request('/api/admin/stats');
    },
};

// ==========================================
// UI Helpers - Tiện ích hiển thị
// ==========================================
const UIHelpers = {
    /**
     * Hiển thị thông báo toast
     */
    showToast(message, type = 'info') {
        // Xóa toast cũ nếu có
        const existingToast = document.querySelector('.toast-notification');
        if (existingToast) existingToast.remove();

        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-icon">${type === 'success' ? '✅' : type === 'error' ? '❌' : type === 'warning' ? '⚠️' : 'ℹ️'}</span>
                <span class="toast-message">${message}</span>
            </div>
        `;

        // Inject styles nếu chưa có
        if (!document.getElementById('toast-styles')) {
            const style = document.createElement('style');
            style.id = 'toast-styles';
            style.textContent = `
                .toast-notification {
                    position: fixed;
                    top: 90px;
                    right: 24px;
                    z-index: 10000;
                    padding: 16px 24px;
                    border-radius: 12px;
                    font-family: 'Inter', sans-serif;
                    font-size: 14px;
                    font-weight: 500;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.12);
                    animation: toastSlideIn 0.4s cubic-bezier(0.4,0,0.2,1), toastFadeOut 0.4s 3s forwards;
                    backdrop-filter: blur(12px);
                    border: 1px solid rgba(255,255,255,0.3);
                }
                .toast-content {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                .toast-icon { font-size: 18px; }
                .toast-success {
                    background: linear-gradient(135deg, rgba(16,185,129,0.95), rgba(5,150,105,0.95));
                    color: white;
                }
                .toast-error {
                    background: linear-gradient(135deg, rgba(239,68,68,0.95), rgba(220,38,38,0.95));
                    color: white;
                }
                .toast-warning {
                    background: linear-gradient(135deg, rgba(245,158,11,0.95), rgba(217,119,6,0.95));
                    color: white;
                }
                .toast-info {
                    background: linear-gradient(135deg, rgba(79,70,229,0.95), rgba(67,56,202,0.95));
                    color: white;
                }
                @keyframes toastSlideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes toastFadeOut {
                    from { opacity: 1; transform: translateX(0); }
                    to { opacity: 0; transform: translateX(100%); }
                }
            `;
            document.head.appendChild(style);
        }

        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3500);
    },

    /**
     * Hiển thị loading spinner
     */
    showLoading(container) {
        if (!container) return;
        container.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p>Đang tải dữ liệu...</p>
            </div>
        `;

        if (!document.getElementById('loading-styles')) {
            const style = document.createElement('style');
            style.id = 'loading-styles';
            style.textContent = `
                .loading-spinner {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    padding: 48px 24px;
                    gap: 16px;
                }
                .loading-spinner p {
                    color: #6b7280;
                    font-size: 14px;
                    margin: 0;
                }
                .spinner {
                    width: 36px;
                    height: 36px;
                    border: 3px solid #e5e7eb;
                    border-top-color: #4F46E5;
                    border-radius: 50%;
                    animation: spin 0.8s linear infinite;
                }
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        }
    },

    /**
     * Render một job card HTML
     */
    renderJobCard(job, showApply = true) {
        const initial = (job.company || 'C').charAt(0).toUpperCase();
        const distance = job.distance_km ? `${job.distance_km} km • ` : '';
        const address = job.address || 'Chưa cập nhật';
        const salary = job.salary || 'Thỏa thuận';

        return `
            <article class="job-card" data-job-id="${job.id}" onclick="viewJobDetail(${job.id})">
                <div class="job-header">
                    <div class="company-info">
                        <div class="company-logo-placeholder" role="img" aria-label="Logo ${job.company}">
                            <span class="logo-text">${initial}</span>
                        </div>
                        <div class="job-title-section">
                            <h2 class="job-title">${job.title}</h2>
                            <p class="company-name">${job.company}</p>
                        </div>
                    </div>
                </div>
                <div class="job-details">
                    <div class="detail-item">
                        <span class="detail-icon-emoji">📍</span>
                        <span class="detail-text">${distance}${address}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-icon-emoji">💰</span>
                        <span class="detail-text">${salary}</span>
                    </div>
                    ${job.skills ? `
                    <div class="detail-item">
                        <span class="detail-icon-emoji">🛠️</span>
                        <span class="detail-text">${job.skills}</span>
                    </div>` : ''}
                </div>
                <div class="job-footer">
                    <div class="post-time">
                        <span class="time-text">${job.status || ''}</span>
                    </div>
                    ${showApply ? `
                    <div class="job-actions">
                        <button class="apply-btn" type="button" onclick="event.stopPropagation(); handleApply(${job.id})" aria-label="Ứng tuyển ${job.title}">
                            <span class="apply-text">Ứng Tuyển</span>
                        </button>
                    </div>` : ''}
                </div>
            </article>
        `;
    }
};
