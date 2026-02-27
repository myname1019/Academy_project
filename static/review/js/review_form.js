// static/review/js/review_form.js
(function () {
  const stars = document.querySelectorAll(".star-rating .star");
  const ratingInput = document.querySelector("input[name='rating']");

  if (!stars.length || !ratingInput) return;

  function setRating(value) {
    ratingInput.value = String(value);

    stars.forEach((s, idx) => {
      const v = idx + 1;
      s.classList.toggle("active", v <= value);
      s.setAttribute("aria-checked", v === value ? "true" : "false");
    });
  }

  // ✅ 페이지 로드시 기존 값(수정 화면/유효성 실패 후 재렌더) 반영
  const initial = parseInt(ratingInput.value || "0", 10);
  if (!Number.isNaN(initial) && initial > 0) setRating(initial);

  stars.forEach((star) => {
    star.addEventListener("click", () => {
      const value = parseInt(star.dataset.value, 10);
      if (!Number.isNaN(value)) setRating(value);
    });

    // 키보드 접근성(Enter/Space)
    star.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        const value = parseInt(star.dataset.value, 10);
        if (!Number.isNaN(value)) setRating(value);
      }
    });
  });
})();