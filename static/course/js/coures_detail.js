// static/course/js/course_detail.js
document.addEventListener("DOMContentLoaded", () => {
  document.addEventListener("click", (e) => {
    const btn = e.target.closest(".js-review-toggle");
    if (!btn) return;

    const item = btn.closest(".review-item");
    if (!item) return;

    item.classList.toggle("review-collapsed");
    btn.textContent = item.classList.contains("review-collapsed") ? "더보기" : "접기";
  });
});