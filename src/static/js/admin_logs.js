// ===========================================================================
// admin_logs.js - Live Monitoring Dashboard Script cho trang Quản trị (Admin)
// ===========================================================================

document.addEventListener('DOMContentLoaded', () => {
    const tbody = document.getElementById('logsTableBody');
    if (!tbody) return;

    // Đọc cấu hình từ data attribute của bảng
    const currentPage = parseInt(tbody.dataset.currentPage || '1', 10);
    let lastKnownId = parseInt(tbody.dataset.lastId || '0', 10);
    let isLive = true;
    let pollTimer = null;

    // Hàm sinh Badge màu theo loại sự kiện
    function getBadgeHtml(action) {
        if (!action) return '<span class="badge bg-secondary me-1">Log</span>';

        if (action.includes('Nỗ lực truy cập trái phép') || action.includes('thất bại') || action.includes('IDOR')) {
            return '<span class="badge bg-danger me-1"><i class="fa-solid fa-user-xmark me-1"></i>Unauthorized</span>';
        } else if (action.includes('Sự kiện xác thực')) {
            return '<span class="badge bg-success me-1"><i class="fa-solid fa-check me-1"></i>Auth Success</span>';
        } else if (action.includes('CSRF')) {
            return '<span class="badge bg-danger me-1">CSRF Alert</span>';
        } else if (action.includes('Spam')) {
            return '<span class="badge bg-warning text-dark me-1">Spam Alert</span>';
        } else if (action.includes('403')) {
            return '<span class="badge bg-danger bg-opacity-75 me-1">403 Forbidden</span>';
        } else if (action.includes('404')) {
            return '<span class="badge bg-secondary me-1">404 Not Found</span>';
        } else {
            return '<span class="badge bg-info text-dark me-1">Notice</span>';
        }
    }

    // Hàm gọi API lấy danh sách logs mới nhất
    async function fetchLogs(isManual = false) {
        const refreshIcon = document.getElementById('refreshIcon');
        if (isManual && refreshIcon) refreshIcon.classList.add('fa-spin');

        try {
            const response = await fetch('/api/admin/logs');
            if (!response.ok) return;

            const data = await response.json();
            if (data.status !== 'success') return;

            // Cập nhật thống kê số liệu
            const statTotal = document.getElementById('stat-total');
            const statAuthFail = document.getElementById('stat-auth-fail');
            const statCsrfSpam = document.getElementById('stat-csrf-spam');
            const statError = document.getElementById('stat-error');
            const lastUpdated = document.getElementById('lastUpdated');

            if (statTotal) statTotal.textContent = data.total;
            if (statAuthFail) statAuthFail.textContent = data.auth_fail_count;
            if (statCsrfSpam) statCsrfSpam.textContent = data.csrf_count + data.spam_count;
            if (statError) statError.textContent = data.error_count;

            const now = new Date();
            if (lastUpdated) lastUpdated.textContent = `Cập nhật lúc: ${now.toLocaleTimeString()}`;

            // Chỉ cập nhật bảng tự động khi đang ở trang 1 để không làm gián đoạn khi Admin đang duyệt trang lịch sử cũ
            if (currentPage === 1 && data.logs && data.logs.length > 0 && data.logs[0].id !== lastKnownId) {
                let html = '';

                data.logs.forEach(log => {
                    const isNew = log.id > lastKnownId;
                    const userHtml = (log.user_id && log.username)
                        ? `<a href="/user/${log.user_id}" class="badge bg-light text-dark border text-decoration-none"><i class="fa-solid fa-user me-1"></i>${log.username}</a>`
                        : '<span class="text-secondary small fst-italic">Khách (Chưa đăng nhập)</span>';

                    const badge = getBadgeHtml(log.action);
                    const highlightClass = isNew ? 'table-warning' : '';

                    html += `
                        <tr id="log-row-${log.id}" class="${highlightClass}">
                            <td class="fw-semibold text-secondary">#${log.id}</td>
                            <td class="small text-muted">${log.timestamp}</td>
                            <td><code>${log.ip_address}</code></td>
                            <td>${userHtml}</td>
                            <td>${badge} <span class="text-dark">${log.action}</span></td>
                        </tr>
                    `;
                });

                tbody.innerHTML = html;
                lastKnownId = data.logs[0].id;

                // Xóa hiệu ứng highlight vàng sau 1.5 giây
                setTimeout(() => {
                    document.querySelectorAll('.table-warning').forEach(el => el.classList.remove('table-warning'));
                }, 1500);
            }
        } catch (err) {
            console.warn('Lỗi khi fetch logs:', err);
        } finally {
            if (isManual && refreshIcon) refreshIcon.classList.remove('fa-spin');
        }
    }

    // Cấu hình Bật / Tắt Live Monitoring
    const liveToggle = document.getElementById('liveToggle');
    const livePulse = document.getElementById('livePulse');
    const liveText = document.getElementById('liveText');
    const refreshBtn = document.getElementById('refreshBtn');

    function startPolling() {
        if (!pollTimer) {
            pollTimer = setInterval(() => fetchLogs(false), 3000);
        }
    }

    function stopPolling() {
        if (pollTimer) {
            clearInterval(pollTimer);
            pollTimer = null;
        }
    }

    if (liveToggle) {
        liveToggle.addEventListener('change', (e) => {
            isLive = e.target.checked;
            if (isLive) {
                if (livePulse) livePulse.classList.remove('d-none');
                if (liveText) {
                    liveText.textContent = 'Live (3s)';
                    liveText.className = 'text-success';
                }
                startPolling();
            } else {
                if (livePulse) livePulse.classList.add('d-none');
                if (liveText) {
                    liveText.textContent = 'Đã dừng';
                    liveText.className = 'text-secondary';
                }
                stopPolling();
            }
        });
    }

    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => fetchLogs(true));
    }

    // Tự động bắt đầu polling khi mở trang
    startPolling();
});

