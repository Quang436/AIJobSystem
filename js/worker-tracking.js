/**
 * Worker Tracking Service for GeoJob
 * Chịu trách nhiệm vận hành định vị ngầm, đo lường khoảng cách theo Haversine Formula,
 * và trigger đồng bộ API nhịp nhàng để tối ưu hóa bộ nhớ và pin.
 */

class WorkerTrackingService {
    constructor() {
        this.watchId = null;
        this.syncIntervalId = null;
        this.lastLat = null;
        this.lastLng = null;
        this.currentHeading = null;
        this.isTracking = false;
        this.workerId = null;

        // Yêu cầu logic: 30s hoặc tự động khi lệch > 50m
        this.SYNC_INTERVAL_MS = 30 * 1000;
        this.DISTANCE_THRESHOLD_M = 50;
    }

    /**
     * Bật trạng thái Sẵn sàng (Toggle ON)
     */
    startTracking(workerId) {
        if (this.isTracking) return;
        if (!navigator.geolocation) {
            this.handleError({ message: "Trình duyệt của bạn không hỗ trợ công nghệ Geolocation." });
            return;
        }

        this.workerId = workerId;
        this.isTracking = true;

        // 1. Khởi tạo Hook theo dõi vị trí liên tục theo hệ thống điện thoại
        const options = {
            enableHighAccuracy: true,  // Bắt buộc dùng GPS High Accuracy cho Worker
            maximumAge: 10000,         // Cache lâu nhất 10s để đỡ pin 
            timeout: 20000             // Hủy tìm nếu >20s
        };

        this.watchId = navigator.geolocation.watchPosition(
            this.onPositionSuccess.bind(this),
            this.onPositionError.bind(this),
            options
        );

        // 2. Chạy worker ngầm - Cứ 30s đồng bộ dữ liệu (Bất luận đứng yên)
        // Trick: SetInterval sẽ hoạt động như Background Task mượt mà trên Desktop/PWA
        this.syncIntervalId = setInterval(() => {
            this.syncLocationToApi(false); // False: Không phải do out >50m
        }, this.SYNC_INTERVAL_MS);

        console.log(`[WorkerTracking] Bắt đầu vào trạng thái làm việc (Worker: ${this.workerId})`);
    }

    /**
     * Tắt chế độ làm việc (Toggle OFF) - Dọn dẹp RAM & GPS
     */
    stopTracking() {
        if (!this.isTracking) return;

        // Hủy đăng ký lắng nghe GPS -> Tắt biểu tượng GPS trên thanh trạng thái điện thoại
        if (this.watchId !== null) {
            navigator.geolocation.clearWatch(this.watchId);
            this.watchId = null;
        }

        // Dừng tiến trình ngầm 30s
        if (this.syncIntervalId !== null) {
            clearInterval(this.syncIntervalId);
            this.syncIntervalId = null;
        }

        this.isTracking = false;
        this.lastLat = null;
        this.lastLng = null;
        this.currentHeading = null;

        console.log("[WorkerTracking] Đã TĂT chế độ làm việc. Giải phóng tài nguyên GPS.");
    }

    /**
     * Pipeline xử lý sau khi nhận định vị mới từ Chipset
     */
    onPositionSuccess(position) {
        const { latitude, longitude, heading } = position.coords;

        // Logic: Lần đầu tiên bắt được sóng
        if (this.lastLat === null || this.lastLng === null) {
            this.lastLat = latitude;
            this.lastLng = longitude;
            this.currentHeading = heading;
            this.syncLocationToApi(true); // Gửi API lập tức
            return;
        }

        // Logic: Tính toán quãng đường xem Thợ đã chạy khỏi vị trí cũ xa không?
        const distanceMeters = this.calculateDistanceMeters(
            this.lastLat, this.lastLng,
            latitude, longitude
        );

        // Thỏa điều kiện dịch chuyển > 50m -> Xả tọa độ mới ngay và luôn (không đợi 30s)
        if (distanceMeters > this.DISTANCE_THRESHOLD_M) {
            this.lastLat = latitude;
            this.lastLng = longitude;
            this.currentHeading = heading;
            console.log(`[WorkerTracking] Thợ đã dy chuyển ${Math.round(distanceMeters)}m -> Buộc đồng bộ!`);
            this.syncLocationToApi(true);
        }
    }

    /**
     * Xử lý Ngoại lệ Định vị & Ép UI Tắt switch
     */
    onPositionError(error) {
        let msg = "";
        switch (error.code) {
            case error.PERMISSION_DENIED:
                msg = "Bạn đã từ chối quyền GPS. Vui lòng vào Cài đặt để cấp quyền cho GeoJob nhận việc.";
                // IMPORTANT: Phóng hook để Giao diện chớp/tắt cái nút Toggle về trạng thái TẮT
                document.dispatchEvent(new CustomEvent('workerTrackingPermissionDenied'));
                this.stopTracking(); // Tử hủy tiến trình
                break;
            case error.POSITION_UNAVAILABLE:
                msg = "Chưa nhận diện được phần cứng GPS. Vui lòng di chuyển ra khu vực thoáng sóng.";
                break;
            case error.TIMEOUT:
                msg = "Chờ vị trí GPS mất quá nhiều thời gian.";
                break;
            default:
                msg = "Lỗi hệ thống định vị không xác định.";
                break;
        }
        this.handleError({ message: msg });
    }

    handleError(err) {
        console.warn("[WorkerTracking] Lỗi Ngoại Lệ:", err.message);
        // Nếu có hàm UI toast thì nhét vào đây:
        // UIHelpers.showToast(err.message, 'error');
    }

    /**
     * Gọi API Đồng Bộ Tọa Độ
     */
    async syncLocationToApi(isImmediateTrigger) {
        if (this.lastLat === null || this.lastLng === null) return;

        const payload = {
            worker_id: this.workerId,
            latitude: Number(this.lastLat.toFixed(6)),
            longitude: Number(this.lastLng.toFixed(6)),
            bearing: this.currentHeading || 0,
        };

        try {
            // Giả lập hoặc liên kết thực tế API:
            const url = '/api/v1/worker/location';
            const token = localStorage.getItem('access_token');

            const response = await fetch(url, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                console.log(`[WorkerTracking] Sync OK ${isImmediateTrigger ? '(By Distance)' : '(By Timer)'} - Lat: ${payload.latitude}`);

                // --- TÍNH NĂNG THÔNG BÁO VIỆC MỚI LIỀN TAY ---
                this.checkNearbyJobsForAlert(payload.latitude, payload.longitude);

            } else {
                console.warn("[WorkerTracking] Lỗi đẩy lên Cloud, Thách thức kết nối mạng?");
            }
        } catch (e) {
            console.error("[WorkerTracking] Failed fetch:", e);
        }
    }

    /**
     * Tự động quét và Báo cáo Công việc gần đó (Real-time Alerter)
     */
    async checkNearbyJobsForAlert(lat, lng) {
        try {
            const url = `/api/v1/jobs/jobs-distance?lat=${lat}&lng=${lng}`;
            const token = localStorage.getItem('access_token');
            const res = await fetch(url, { headers: { 'Authorization': `Bearer ${token}` } });
            if (!res.ok) return;

            const jobs = await res.json();

            // Giả lập tiêu chí: Lọc lấy Job dưới 5km
            const nearbyJobs = jobs.filter(j => j.distance_km <= 5.0);

            // Chống Spam bằng Cache Cache (Lưu vết các Jobs đã Notify)
            let notifiedQueue = JSON.parse(localStorage.getItem('notified_job_alerts')) || [];

            let newFinds = 0;
            for (const job of nearbyJobs) {
                const cacheKey = job.title; // Sử dụng Tên job hoặc UUID (từ Api)
                if (!notifiedQueue.includes(cacheKey)) {
                    notifiedQueue.push(cacheKey);
                    newFinds++;

                    // Đẩy Notification ra Giao diện hoặc dùng Web Push API
                    if (window.UIHelpers && typeof window.UIHelpers.showToast === 'function') {
                        window.UIHelpers.showToast(`🔥 VIỆC GẦN ĐÂY: ${job.title} (Cách ${job.distance_km.toFixed(1)} km)`, "success");
                    } else {
                        // Fallback Alert
                        console.warn(`[Alert] Có việc mới: ${job.title}`);
                    }
                }
            }

            // Flush cache để không đầy bộ nhớ RAM đt
            if (notifiedQueue.length > 200) notifiedQueue = notifiedQueue.slice(-100);
            localStorage.setItem('notified_job_alerts', JSON.stringify(notifiedQueue));

        } catch (e) {
            console.error("[WorkerTracking] Lỗi quét Job Alerts:", e);
        }
    }

    /**
     * Core Algorithm: (Toán học) Haversine tính toán khoảng cách cầu hai điểm Tọa độ (Lat/Lng) bằng mét
     */
    calculateDistanceMeters(lat1, lon1, lat2, lon2) {
        const R = 6371e3; // Bán kính trái đất (mét)
        const toRad = p => p * Math.PI / 180;

        const p1 = toRad(lat1);
        const p2 = toRad(lat2);
        const dp = toRad(lat2 - lat1);
        const dl = toRad(lon2 - lon1);

        const a = Math.sin(dp / 2) * Math.sin(dp / 2) +
            Math.cos(p1) * Math.cos(p2) *
            Math.sin(dl / 2) * Math.sin(dl / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

        return R * c;
    }
}

// Bơm vào Window Array để mọi file HTML/View đều có thể chích xuất
window.WorkerTracker = new WorkerTrackingService();
