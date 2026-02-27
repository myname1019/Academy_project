// static/common/js/navbar_theme.js
(function () {
  const key = "theme"; // base쪽과 같은 키면 모드가 공유됨

  function applyTheme(isDark, btn) {
    // ✅ 핵심: html + body 둘 다 dark 토글
    document.documentElement.classList.toggle("dark", isDark);
    document.body.classList.toggle("dark", isDark);

    if (btn) btn.textContent = isDark ? "☀️" : "🌙";
    localStorage.setItem(key, isDark ? "dark" : "light");
  }

  function init() {
    const btn = document.getElementById("themeToggle");
    if (!btn) return;

    const saved = localStorage.getItem(key);
    const prefersDark =
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches;

    const startDark = saved === "dark" || (!saved && prefersDark);

    // ✅ 초기 적용
    applyTheme(startDark, btn);

    btn.addEventListener("click", () => {
      const isDark = !document.body.classList.contains("dark");
      applyTheme(isDark, btn);
    });
  }

  // 어디에 script가 들어가도 안전하게
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();