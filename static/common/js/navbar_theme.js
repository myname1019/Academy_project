// static/common/js/navbar_theme.js
(function () {
  const key = "theme"; // base쪽과 같은 키면 모드가 공유됨

  function init() {
    const btn = document.getElementById("themeToggle");
    if (!btn) return;

    const saved = localStorage.getItem(key);
    const prefersDark =
      window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;

    const startDark = saved === "dark" || (!saved && prefersDark);

    document.body.classList.toggle("dark", startDark);
    btn.textContent = startDark ? "☀️" : "🌙";

    btn.addEventListener("click", () => {
      document.body.classList.toggle("dark");
      const isDark = document.body.classList.contains("dark");
      localStorage.setItem(key, isDark ? "dark" : "light");
      btn.textContent = isDark ? "☀️" : "🌙";
    });
  }

  // 어디에 script가 들어가도 안전하게
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();