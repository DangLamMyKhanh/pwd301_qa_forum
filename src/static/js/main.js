// ===========================================================================
// main.js - Client-side AJAX & Tương tác giao diện (Trường)
// ===========================================================================

// 1. Hàm lấy CSRF Token từ thẻ meta (bảo mật Flask-WTF)
function getCsrfToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    return metaTag ? metaTag.getAttribute('content') : '';
}

// 2. Hàm fetch() kiểm tra kết nối API Backend qua AJAX
async function checkApiHealth() {
    try {
        console.log("Đang kiểm tra kết nối API qua AJAX fetch()...");

        const response = await fetch('/api/test', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (!response.ok) {
            throw new Error(`Lỗi kết nối HTTP! Mã lỗi: ${response.status}`);
        }

        const data = await response.json();
        console.log("Kết nối AJAX thành công với Backend:", data);
    } catch (error) {
        console.error("Lỗi khi thực hiện AJAX fetch():", error);
    }
}

// 3. Xử lý sự kiện bấm nút Vote (Kiểm soát 1 người chỉ vote 1 lần 1 câu)
function initVoteButtons() {
    const voteButtons = document.querySelectorAll('.vote-btn');
    if (!voteButtons.length) return;

    voteButtons.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const answerId = btn.getAttribute('data-answer-id');
            const voteType = btn.getAttribute('data-type') || 'up';
            if (!answerId) return;

            // Khóa nút tạm thời để tránh double click liên tục
            btn.disabled = true;

            try {
                const csrfToken = getCsrfToken();
                const headers = {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                };
                if (csrfToken) {
                    headers['X-CSRFToken'] = csrfToken;
                }

                // Gọi đúng API endpoint thực tế: POST /api/vote/answer/<id>
                const response = await fetch(`/api/vote/answer/${answerId}`, {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify({ type: voteType })
                });

                const data = await response.json();

                if (response.ok && data.status === 'success') {
                    // Cập nhật điểm vote trên giao diện ngay lập tức
                    const votesElem = document.getElementById(`votes-${answerId}`);
                    if (votesElem) {
                        votesElem.textContent = data.new_upvotes;

                        // Hiệu ứng nhảy số & đổi màu
                        votesElem.classList.add('text-primary', 'fw-bolder');
                        setTimeout(() => {
                            votesElem.classList.remove('text-primary', 'fw-bolder');
                        }, 400);
                    }

                    // Cập nhật trạng thái màu sắc 2 nút Up / Down theo user_vote
                    const btnUp = document.getElementById(`btn-up-${answerId}`);
                    const btnDown = document.getElementById(`btn-down-${answerId}`);

                    if (btnUp && btnDown) {
                        // Reset cả 2 về mặc định (btn-light)
                        btnUp.className = 'btn btn-light border btn-sm mb-1 vote-btn';
                        btnDown.className = 'btn btn-light border btn-sm mt-1 vote-btn';

                        // Áp dụng màu theo trạng thái vote của user
                        if (data.user_vote === 1) {
                            btnUp.className = 'btn btn-success text-white border btn-sm mb-1 vote-btn';
                        } else if (data.user_vote === -1) {
                            btnDown.className = 'btn btn-danger text-white border btn-sm mt-1 vote-btn';
                        }
                    }
                } else {
                    console.warn('Thông báo vote:', data.message);
                    alert(data.message || 'Không thể thực hiện bình chọn!');
                }
            } catch (err) {
                console.error('Lỗi khi thực hiện AJAX fetch vote:', err);
                alert('Có lỗi xảy ra khi kết nối máy chủ!');
            } finally {
                btn.disabled = false;
            }
        });
    });
}

// 4. Kích hoạt khi trang web tải xong DOM
document.addEventListener('DOMContentLoaded', () => {
    console.log("File main.js đã tải thành công và sẵn sàng hoạt động!");
    checkApiHealth();
    initVoteButtons();
});
