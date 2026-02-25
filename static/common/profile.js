function openDeleteModal() {
  const overlay = document.getElementById('deleteOverlay');
  if (overlay) overlay.style.display = 'flex';
}

function closeDeleteModal() {
  const overlay = document.getElementById('deleteOverlay');
  if (overlay) overlay.style.display = 'none';
}

document.addEventListener('click', function (e) {
  const overlay = document.getElementById('deleteOverlay');
  if (overlay && e.target === overlay) overlay.style.display = 'none';
});