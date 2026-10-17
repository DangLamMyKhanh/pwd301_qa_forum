

// 1. Hàm lấy CSRF Token từ thẻ meta (bảo mật Flask-WTF cho các request POST/PUT/DELETE sau này)
function getCsrfToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    return metaTag ? metaTag.getAttribute('content') : '';
}

// 2. Hàm fetch() gọi thử nghiệm API Backend qua AJAX
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

        // Kiểm tra mã trạng thái HTTP (200 OK)
        if (!response.ok) {
            throw new Error(`Lỗi kết nối HTTP! Mã lỗi: ${response.status}`);
        }

        const data = await response.json();
        console.log("Kết nối AJAX thành công với Backend:", data);
    } catch (error) {
        console.error("Lỗi khi thực hiện AJAX fetch():", error);
    }
}

// 3. Tự động kích hoạt khi trang web tải xong DOM
document.addEventListener('DOMContentLoaded', () => {
    console.log("File main.js đã tải thành công và sẵn sàng hoạt động!");
    // Gọi hàm kiểm tra API
    checkApiHealth();
});
