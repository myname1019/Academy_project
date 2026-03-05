console.log("course_students.js loaded");
// static/teacherpage/js/course_students.js
document.addEventListener("DOMContentLoaded", () => {
  // course_students.html에서 course.id를 JS로 쓰기 위해 data 속성 한 줄만 추가하면 더 깔끔하지만,
  // 초보 단계에서는 URL에서 course_id를 추출하는 방식도 가능해.
  // 다만 가장 안전한 방법은 템플릿에서 course id를 넘겨주는 것.
  // 아래에서는 HTML에 data-course-id가 있다고 가정하지 않고,
  // URL 패턴에서 course_id를 뽑는 방식(최소 의존)으로 처리해둠.

  // 현재 페이지 URL 예: /teacher/course/1/students/
  const pathParts = window.location.pathname.split("/").filter(Boolean);
  // ["teacher", "course", "1", "students"] 같은 형태라고 가정
  const courseId = Number(pathParts[pathParts.indexOf("course") + 1]);

  // 배지 DOM들
  const badges = document.querySelectorAll(".js-unread-badge");

  // 학생별 배지 숨김 초기화
  function clearBadges() {
    badges.forEach((b) => {
      b.style.display = "none";
      b.textContent = "";
    });
  }

  // counts: {"학생id": 숫자, ...}
  function applyCounts(counts) {
    clearBadges();

    badges.forEach((b) => {
      const studentId = b.dataset.studentId;
      const n = Number(counts[studentId] || 0);

      if (n > 0) {
        b.textContent = String(n);
        b.style.display = "inline-block";
      }
    });
  }

  // 서버에서 학생별 unread_count를 가져오는 API
  // 이 URL은 4번 단계에서 TeacherPage/urls.py에 추가할거야.
  const apiUrl = `/teacher/course/${courseId}/unread-counts/`;

  async function refreshUnreadBadges() {
    try {
      const res = await fetch(apiUrl, { credentials: "same-origin" });
      if (!res.ok) {
        console.log("unread-counts API 응답 실패:", res.status);
        return;
      }
      const data = await res.json();
      applyCounts(data.counts || {});
    } catch (e) {
      console.log("unread-counts API 호출 실패");
    }
  }

  // 최초 1회 갱신
  refreshUnreadBadges();

  // notify WebSocket 연결
  const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
  const wsUrl = `${wsScheme}://${window.location.host}/ws/notify/`;

  let socket = null;
  let reconnectTimer = null;
  let attempt = 0;

  function reconnectDelayMs(a) {
    const base = 500;
    const max = 10000;
    const delay = Math.min(max, base * Math.pow(2, a));
    return delay + Math.floor(Math.random() * 250);
  }

  function connectNotify() {
    if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      attempt = 0;
      // 연결되면 한 번 갱신해서 초기 동기화
      refreshUnreadBadges();
    };

    socket.onmessage = (e) => {
      let payload;
      try {
        payload = JSON.parse(e.data);
      } catch {
        return;
      }

      // unread_count 이벤트가 오면 학생별 숫자 다시 갱신
      if (payload.event === "unread_count") {
        refreshUnreadBadges();
      }
    };

    socket.onclose = () => {
      if (reconnectTimer) return;

      const delay = reconnectDelayMs(attempt);
      attempt += 1;

      reconnectTimer = window.setTimeout(() => {
        reconnectTimer = null;
        connectNotify();
      }, delay);
    };

    socket.onerror = () => {
      console.log("notify ws error");
    };
  }

  connectNotify();

  // 탭을 다시 보면 끊겨있을 수 있어서 복구
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") {
      if (!socket || socket.readyState === WebSocket.CLOSED) {
        connectNotify();
      }
    }
  });
});