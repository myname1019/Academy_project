// static/chat/js/dm.js
(function () {
  function init() {
    const box = document.getElementById("chatBox");
    if (box) box.scrollTop = box.scrollHeight;

    // Enter로 전송(기본 동작이 엔터 제출이긴 한데, 안전하게)
    const input = document.querySelector('.dm-footer input[name="content"]');
    const form = document.querySelector(".dm-footer form");
    if (input && form) {
      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          // IME(한글 조합중)일 때 오작동 방지
          if (e.isComposing) return;
          form.requestSubmit();
        }
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();