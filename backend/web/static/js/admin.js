let isAdmin = false;

function setAdmin() {
    isAdmin = true;
    document.getElementById("admin-controls").style.display = "block";
    document.getElementById("admin-modal").style.display = "none";
    alert("관리자 모드가 활성화되었습니다.");
}

function disableAdmin() {
    isAdmin = false;
    document.getElementById("admin-controls").style.display = "none";
    document.getElementById("admin-modal").style.display = "flex";
}

async function verifyAdmin() {
    const pass = document.getElementById("admin-pass").value;

    try {
        const response = await fetch("/api/web/token/check", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(pass)
        });

        if (response.ok) {
            setAdmin();
        } else {
            alert("인증토큰이 틀렸습니다.");
        }
    } catch (error) {
        console.error("요청 실패:", error);
        alert("서버 오류가 발생했습니다.");
    }
}


// 공지사항을 디스코드 봇으로 전송하는 함수
async function postNotice() {
    const title = document.getElementById("notice-title").value.trim();
    const body = document.getElementById("notice-body").value.trim();
    if (!title || !body) return alert("제목과 내용을 모두 입력해주세요.");

    // 디스코드 봇으로 공지 전송
    const success = await sendNoticeToDiscord(title, body);
    if (!success) {
        return;
    }

    // 공지사항 웹에 등록 (HTML 형식으로 표시)
    const list = document.getElementById("notice-list");
    const date = new Date().toISOString().split('T')[0];
    const li = document.createElement("li");
    li.innerHTML = `<h3>${title} <small>${date}</small></h3><p>${body}</p>`;
    list.insertBefore(li, list.firstChild);

    // 입력 값 초기화
    document.getElementById("notice-title").value = '';
    document.getElementById("notice-body").value = '';
}


// 디스코드 봇에 HTML 형식 공지사항을 보내는 함수
async function sendNoticeToDiscord(title, body) {
    try {
        const response = await fetch('/api/web/notification', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({title, body}),
        });

        if (response.status === 401) {
            alert("관리자 인증이 만료되었습니다. 다시 로그인해주세요.");
            disableAdmin();
            await logout();      // 서버에 쿠키 삭제 요청
            return false;
        }

        if (response.ok) {
            const data = await response.json();
            console.log('공지 전송 성공:', data);
            return true;
        } else {
            console.warn('공지 전송 실패, 상태 코드:', response.status);
            return false;
        }
    } catch (error) {
        console.error('공지 전송 오류:', error);
        return false;
    }
}


async function logout() {
    try {
        await fetch('/api/web/logout', {
            method: 'POST',
            credentials: 'include'  // 쿠키 포함
        });
    } catch (e) {
        console.warn('로그아웃 요청 실패 (무시함)', e);
    }
}
