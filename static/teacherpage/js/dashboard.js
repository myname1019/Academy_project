// teacherpage/js/dashboard.js

(function () {
  const $ = (sel) => document.querySelector(sel);

  function showBioEdit() {
    const display = $("#bio-display");
    const editBtn = $("#bioEditBtn");
    const input = $("#bio-input");
    const btnGroup = $("#btn-group");

    if (display) display.style.display = "none";
    if (editBtn) editBtn.style.display = "none";
    if (input) input.style.display = "block";
    if (btnGroup) btnGroup.style.display = "flex";
    if (input) input.focus();
  }

  function hideBioEdit() {
    const display = $("#bio-display");
    const editBtn = $("#bioEditBtn");
    const input = $("#bio-input");
    const btnGroup = $("#btn-group");

    if (display) display.style.display = "block";
    if (editBtn) editBtn.style.display = "inline-block";
    if (input) input.style.display = "none";
    if (btnGroup) btnGroup.style.display = "none";
  }

  function openDeleteModal() {
    const overlay = $("#deleteOverlay");
    if (!overlay) return;
    overlay.style.display = "flex";
  }

  function closeDeleteModal() {
    const overlay = $("#deleteOverlay");
    if (!overlay) return;
    overlay.style.display = "none";
  }

  document.addEventListener("DOMContentLoaded", () => {
    const bioEditBtn = $("#bioEditBtn");
    const bioCancelBtn = $("#bioCancelBtn");
    if (bioEditBtn) bioEditBtn.addEventListener("click", showBioEdit);
    if (bioCancelBtn) bioCancelBtn.addEventListener("click", hideBioEdit);

    const deleteOpenBtn = $("#deleteOpenBtn");
    const deleteCancelBtn = $("#deleteCancelBtn");
    const overlay = $("#deleteOverlay");

    if (deleteOpenBtn) deleteOpenBtn.addEventListener("click", openDeleteModal);
    if (deleteCancelBtn) deleteCancelBtn.addEventListener("click", closeDeleteModal);

    if (overlay) {
      overlay.addEventListener("click", (e) => {
        if (e.target === overlay) closeDeleteModal();
      });
    }

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeDeleteModal();
    });
  });
})();