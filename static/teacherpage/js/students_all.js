(function () {
  const input = document.getElementById("studentSearch");
  const list = document.getElementById("studentsList");
  if (!input || !list) return;

  input.addEventListener("input", function () {
    const q = input.value.trim().toLowerCase();
    const cards = list.querySelectorAll(".student-card");

    cards.forEach((card) => {
      const key = (card.getAttribute("data-key") || "").toLowerCase();
      card.style.display = key.includes(q) ? "" : "none";
    });
  });
})();