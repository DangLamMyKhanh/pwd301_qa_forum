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


// 3.1. Xử lý sự kiện bấm nút Vote Câu hỏi (AJAX theo Rubric Step 6: POST /api/questions/<id>/vote)
function initQuestionVoteButtons() {
    const questionVoteButtons = document.querySelectorAll('.vote-question-btn');
    if (!questionVoteButtons.length) return;

    questionVoteButtons.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const questionId = btn.getAttribute('data-question-id');
            const voteType = btn.getAttribute('data-type') || 'up';
            if (!questionId) return;

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

                // Gọi đúng API endpoint: POST /api/questions/<id>/vote
                const response = await fetch(`/api/questions/${questionId}/vote`, {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify({ type: voteType })
                });

                const data = await response.json();

                if (response.ok && data.status === 'success') {
                    // Cập nhật điểm vote câu hỏi trên giao diện ngay lập tức
                    const votesElem = document.getElementById(`q-votes-${questionId}`);
                    if (votesElem) {
                        votesElem.textContent = data.new_upvotes;

                        // Hiệu ứng nhảy số & đổi màu
                        votesElem.classList.add('text-primary', 'fw-bolder');
                        setTimeout(() => {
                            votesElem.classList.remove('text-primary', 'fw-bolder');
                        }, 400);
                    }

                    // Cập nhật trạng thái màu sắc 2 nút Up / Down
                    const btnUp = document.getElementById(`btn-q-up-${questionId}`);
                    const btnDown = document.getElementById(`btn-q-down-${questionId}`);

                    if (btnUp && btnDown) {
                        // Reset cả 2 về mặc định (btn-light)
                        btnUp.className = 'btn btn-light border btn-sm mb-1 vote-question-btn';
                        btnDown.className = 'btn btn-light border btn-sm mt-1 vote-question-btn';

                        // Áp dụng màu theo trạng thái vote của user
                        if (data.user_vote === 1) {
                            btnUp.className = 'btn btn-success text-white border btn-sm mb-1 vote-question-btn';
                        } else if (data.user_vote === -1) {
                            btnDown.className = 'btn btn-danger text-white border btn-sm mt-1 vote-question-btn';
                        }
                    }
                } else {
                    console.warn('Thông báo vote câu hỏi:', data.message);
                    alert(data.message || 'Không thể thực hiện bình chọn cho câu hỏi!');
                }
            } catch (err) {
                console.error('Lỗi khi thực hiện AJAX fetch vote câu hỏi:', err);
                alert('Có lỗi xảy ra khi kết nối máy chủ!');
            } finally {
                btn.disabled = false;
            }
        });
    });
}

// 3.2. Xử lý đánh dấu Best Answer bằng AJAX (Tác giả câu hỏi theo Rubric Step 7)
function initBestAnswerButtons() {
    const bestBtns = document.querySelectorAll('.best-answer-btn');
    if (!bestBtns.length) return;

    bestBtns.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const answerId = btn.getAttribute('data-answer-id');
            if (!answerId) return;

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

                const response = await fetch(`/api/answers/${answerId}/best`, {
                    method: 'POST',
                    headers: headers
                });

                const data = await response.json();

                if (response.ok && data.status === 'success') {
                    // Reset tất cả các nút Best Answer khác trên trang
                    bestBtns.forEach(b => {
                        b.className = 'btn btn-outline-success btn-sm best-answer-btn';
                        const span = b.querySelector('span');
                        if (span) span.textContent = 'Chọn Best Answer';
                    });

                    // Xóa class border-success và badge ở các card khác
                    document.querySelectorAll('.card[id^="answer-card-"]').forEach(card => {
                        card.classList.remove('border-success', 'border-2');
                        const badges = card.querySelectorAll('.badge.bg-success');
                        badges.forEach(bg => {
                            if (bg.textContent.includes('Best Answer')) {
                                bg.parentElement.remove();
                            }
                        });
                    });

                    if (data.is_best) {
                        btn.className = 'btn btn-success text-white btn-sm best-answer-btn';
                        const span = btn.querySelector('span');
                        if (span) span.textContent = 'Đã chọn Best Answer';

                        const card = document.getElementById(`answer-card-${answerId}`);
                        if (card) {
                            card.classList.add('border-success', 'border-2');
                            const body = card.querySelector('.card-body');
                            if (body && !body.querySelector('.badge.bg-success')) {
                                const badgeDiv = document.createElement('div');
                                badgeDiv.className = 'mb-2';
                                badgeDiv.innerHTML = '<span class="badge bg-success py-1 px-2 fs-6"><i class="fa-solid fa-circle-check me-1"></i> Câu trả lời hay nhất (Best Answer)</span>';
                                body.insertBefore(badgeDiv, body.firstChild);
                            }
                        }
                    }
                } else {
                    alert(data.message || 'Không thể thực hiện đánh dấu!');
                }
            } catch (err) {
                console.error('Lỗi khi đánh dấu Best Answer qua AJAX:', err);
                alert('Có lỗi xảy ra khi kết nối máy chủ!');
            } finally {
                btn.disabled = false;
            }
        });
    });
}

// 4. Cảnh báo khi người dùng đang nhập dở nội dung (đặt câu hỏi hoặc đổi mật khẩu) mà rời trang
function initBeforeUnloadWarning() {
    const askForm = document.querySelector('form[action*="ask"]');
    const passwordForm = document.querySelector('form[action*="change-password"]');

    if (!askForm && !passwordForm) return;

    let isSubmitting = false;

    // 4.1. Khi người dùng bấm nút submit thì không cảnh báo
    if (askForm) {
        askForm.addEventListener('submit', () => {
            isSubmitting = true;
        });
    }
    if (passwordForm) {
        passwordForm.addEventListener('submit', () => {
            isSubmitting = true;
        });
    }

    // 4.2. Bắt sự kiện khi người dùng bấm vào các thẻ link <a> (như nút 'Quay lại', navbar,...)
    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', (e) => {
            if (isSubmitting) return;

            // Kiểm tra form Đặt câu hỏi
            if (askForm) {
                const title = document.getElementById('title')?.value.trim();
                const content = document.getElementById('content')?.value.trim();
                if (title || content) {
                    if (!confirm('Bạn đang nhập dở câu hỏi và chưa đăng. Bạn có chắc chắn muốn rời khỏi trang này?')) {
                        e.preventDefault();
                        return;
                    }
                }
            }

            // Kiểm tra form Đổi mật khẩu
            if (passwordForm) {
                const oldPass = document.getElementById('old_password')?.value;
                const newPass = document.getElementById('new_password')?.value;
                const confirmPass = document.getElementById('confirm_password')?.value;
                if (oldPass || newPass || confirmPass) {
                    if (!confirm('Bạn đang nhập dở mật khẩu mới và chưa lưu. Bạn có chắc chắn muốn rời khỏi trang này?')) {
                        e.preventDefault();
                        return;
                    }
                }
            }
        });
    });

    // 4.3. Bắt sự kiện trình duyệt khi người dùng tắt tab, reload hoặc bấm nút Back của browser
    window.addEventListener('beforeunload', (e) => {
        if (isSubmitting) return;

        let hasUnsavedChanges = false;

        if (askForm) {
            const title = document.getElementById('title')?.value.trim();
            const content = document.getElementById('content')?.value.trim();
            if (title || content) hasUnsavedChanges = true;
        }

        if (passwordForm) {
            const oldPass = document.getElementById('old_password')?.value;
            const newPass = document.getElementById('new_password')?.value;
            const confirmPass = document.getElementById('confirm_password')?.value;
            if (oldPass || newPass || confirmPass) hasUnsavedChanges = true;
        }

        if (hasUnsavedChanges) {
            e.preventDefault();
            e.returnValue = ''; // Kích hoạt hộp thoại xác nhận rời trang mặc định của trình duyệt
            return '';
        }
    });
}


// ===========================================================================
// 5. CLIENT-SIDE INPUT VALIDATION (Rubric Tiêu chí 8: Input validation on both client-side and server-side)
// ===========================================================================
function showInputError(inputElem, message) {
    if (!inputElem) return;
    inputElem.classList.add('is-invalid');
    let parent = inputElem.closest('.input-group') || inputElem.parentElement;
    let feedback = parent.querySelector('.invalid-feedback.client-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback client-feedback text-danger small mt-1';
        parent.appendChild(feedback);
    }
    feedback.textContent = message;
    feedback.style.display = 'block';
}

function clearInputError(inputElem) {
    if (!inputElem) return;
    inputElem.classList.remove('is-invalid');
    let parent = inputElem.closest('.input-group') || inputElem.parentElement;
    const feedback = parent.querySelector('.invalid-feedback.client-feedback');
    if (feedback) {
        feedback.remove();
    }
}

function initClientValidation() {
    // 5.1. Client-side Validation: Form Đăng ký tài khoản
    const registerForm = document.querySelector('form[action*="register"]');
    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            const username = document.getElementById('username');
            const email = document.getElementById('email');
            const pass = document.getElementById('password');
            const confirmPass = document.getElementById('confirm_password');

            let isValid = true;

            // Kiểm tra username: 3-20 ký tự, chỉ chữ cái, số và gạch dưới
            if (username) {
                const uVal = username.value.trim();
                const uRegex = /^[a-zA-Z0-9_]{3,20}$/;
                if (!uRegex.test(uVal)) {
                    showInputError(username, 'Tên đăng nhập phải từ 3 đến 20 ký tự và chỉ chứa chữ cái, số, dấu gạch dưới.');
                    isValid = false;
                } else {
                    clearInputError(username);
                }
            }

            // Kiểm tra email sinh viên: @*.edu.vn hoặc @*.edu
            if (email) {
                const eVal = email.value.trim();
                const eRegex = /^[a-zA-Z0-9._%+-]+@([a-zA-Z0-9-]+\.)*(edu\.vn|edu)$/i;
                if (!eRegex.test(eVal)) {
                    showInputError(email, 'Email phải là email sinh viên (có đuôi @*.edu.vn hoặc @*.edu, ví dụ: sv@fpt.edu.vn).');
                    isValid = false;
                } else {
                    clearInputError(email);
                }
            }

            // Kiểm tra mật khẩu: tối thiểu 6 ký tự
            if (pass) {
                if (pass.value.length < 6) {
                    showInputError(pass, 'Mật khẩu phải có ít nhất 6 ký tự.');
                    isValid = false;
                } else {
                    clearInputError(pass);
                }
            }

            // Kiểm tra xác nhận mật khẩu khớp
            if (pass && confirmPass) {
                if (pass.value !== confirmPass.value) {
                    showInputError(confirmPass, 'Mật khẩu xác nhận không khớp với mật khẩu đã nhập.');
                    isValid = false;
                } else {
                    clearInputError(confirmPass);
                }
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    }

    // 5.2. Client-side Validation: Form Đổi mật khẩu
    const changePassForm = document.querySelector('form[action*="change-password"]');
    if (changePassForm) {
        changePassForm.addEventListener('submit', (e) => {
            const oldPass = document.getElementById('old_password');
            const newPass = document.getElementById('new_password');
            const confirmPass = document.getElementById('confirm_password');
            let isValid = true;

            if (oldPass && !oldPass.value) {
                showInputError(oldPass, 'Vui lòng nhập mật khẩu hiện tại.');
                isValid = false;
            } else if (oldPass) {
                clearInputError(oldPass);
            }

            if (newPass && newPass.value.length < 6) {
                showInputError(newPass, 'Mật khẩu mới phải có ít nhất 6 ký tự.');
                isValid = false;
            } else if (newPass) {
                clearInputError(newPass);
            }

            if (newPass && confirmPass && newPass.value !== confirmPass.value) {
                showInputError(confirmPass, 'Mật khẩu xác nhận không khớp với mật khẩu mới.');
                isValid = false;
            } else if (confirmPass) {
                clearInputError(confirmPass);
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    }

    // 5.3. Client-side Validation: Form Đặt câu hỏi
    const askForm = document.querySelector('form[action*="ask"]');
    if (askForm) {
        askForm.addEventListener('submit', (e) => {
            const title = document.getElementById('title');
            const content = document.getElementById('content');
            const tags = document.getElementById('tags');
            let isValid = true;

            if (title && title.value.trim().length < 5) {
                showInputError(title, 'Tiêu đề câu hỏi phải có ít nhất 5 ký tự.');
                isValid = false;
            } else if (title) {
                clearInputError(title);
            }

            if (content && content.value.trim().length < 10) {
                showInputError(content, 'Nội dung câu hỏi phải có ít nhất 10 ký tự chi tiết.');
                isValid = false;
            } else if (content) {
                clearInputError(content);
            }

            if (tags && !tags.value.trim()) {
                showInputError(tags, 'Vui lòng nhập ít nhất một nhãn (ví dụ: Python, Flask).');
                isValid = false;
            } else if (tags) {
                clearInputError(tags);
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    }
}


// 6. Kích hoạt khi trang web tải xong DOM
document.addEventListener('DOMContentLoaded', () => {
    console.log("File main.js đã tải thành công và sẵn sàng hoạt động!");
    checkApiHealth();
    initVoteButtons();
    initQuestionVoteButtons();
    initBestAnswerButtons();
    initBeforeUnloadWarning();
    initClientValidation();
});
