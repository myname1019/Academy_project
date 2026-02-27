// teacherpage/js/course_students.js
(function () {
  // 옵션: 검색창이 있으면 필터링 동작
  // (나중에 HTML에 <input id="studentSearch"> 추가하면 바로 사용 가능)
  const input = document.getElementById("studentSearch");
  const list = document.querySelector(".student-list");
  if (!input || !list) return;

  input.addEventListener("input", function () {
    const q = input.value.trim().toLowerCase();
    const cards = list.querySelectorAll(".student-card");
    cards.forEach((card) => {
      const text = card.innerText.toLowerCase();
      card.style.display = text.includes(q) ? "" : "none";
    });
  });
})();