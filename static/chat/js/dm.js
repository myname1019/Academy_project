console.log("dm.js loaded!");

document.addEventListener("DOMContentLoaded", () => {
  const dmRoot = document.getElementById("dmRoot");
  const chatBox = document.getElementById("chatBox");
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");

  if (!dmRoot || !chatBox || !chatForm || !chatInput) return;

  const myUserId = Number(dmRoot.dataset.myUserId);
  const conversationId = Number(dmRoot.dataset.conversationId);

  // XSS 방지
  function escapeHTML(str) {
    return String(str).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
  }

  // 스크롤 하단 이동
  function scrollToBottom() {
    setTimeout(() => {
      chatBox.scrollTop = chatBox.scrollHeight;
    }, 50);
  }
  scrollToBottom();

  // 읽음 UI 업데이트
  function markMessagesReadByIds(messageIds) {
    if (!Array.isArray(messageIds)) return;
    messageIds.forEach((id) => {
      const row = chatBox.querySelector(`.msg-row.me[data-message-id="${id}"]`);
      if (row) {
        const receipt = row.querySelector(".read-receipt");
        if (receipt) {
          receipt.textContent = "읽음";
          receipt.classList.add("read");
        }
      }
    });
  }

  // 메시지 화면에 추가 (기존 변수 명칭 그대로 유지)
  function appendMessage(data) {
    // 서버에서 온 데이터(data)를 직접 분해해서 사용
    const { message_id, sender_id, content, created_at, is_read } = data;
    const isMe = Number(sender_id) === myUserId;

    let timeText = "";
    if (created_at && created_at.includes("T")) {
      timeText = created_at.split("T")[1].slice(0, 5);
    }

    const wrapper = document.createElement("div");
    wrapper.className = isMe ? "msg-row me" : "msg-row other";
    if (isMe && message_id) {
      wrapper.setAttribute("data-message-id", String(message_id));
    }

    if (isMe) {
      const readText = is_read ? "읽음" : "안읽음";
      const readClass = is_read ? "read-receipt read" : "read-receipt";
      wrapper.innerHTML = `
        <div>
          <div class="bubble me">${escapeHTML(content)}</div>
          <div class="meta me">
            <span>${timeText}</span>
            <span class="${readClass}">${readText}</span>
          </div>
        </div>`;
    } else {
      wrapper.innerHTML = `
        <div>
          <div class="bubble other">${escapeHTML(content)}</div>
          <div class="meta"><span>${timeText}</span></div>
        </div>`;
    }
    chatBox.appendChild(wrapper);
    scrollToBottom();
  }

  // WebSocket 설정
  const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
  const wsUrl = `${wsScheme}://${window.location.host}/ws/chat/room/${conversationId}/`;
  let socket = new WebSocket(wsUrl);

  function sendSeen() {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ action: "seen" }));
    }
  }

  socket.onopen = () => {
    console.log("WebSocket connected");
    sendSeen();
  };

  socket.onmessage = (e) => {
    const payload = JSON.parse(e.data);
    const eventType = payload.event;
    const data = payload.data;

    if (eventType === "message") {
      // 채팅이 안 되었던 이유: 데이터를 분해하지 않고 그대로 전달했기 때문일 수 있음
      appendMessage(data); 
      if (Number(data.sender_id) !== myUserId) {
        sendSeen();
      }
    } 
    else if (eventType === "read") {
      const readerId = Number(data.reader_id);
      if (readerId !== myUserId) {
        markMessagesReadByIds(data.message_ids);
      }
    }
  };

  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const val = chatInput.value.trim();
    if (val && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ action: "send", content: val }));
      chatInput.value = "";
    }
  });

  setInterval(sendSeen, 10000);
});