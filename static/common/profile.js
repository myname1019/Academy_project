function showEditForm() {
    document.getElementById('bio-display').style.display = 'none';

    const editBtn = document.querySelector('.edit-trigger');
    if (editBtn) editBtn.style.display = 'none';

    document.getElementById('bio-input').style.display = 'block';
    document.getElementById('btn-group').style.display = 'flex';
    document.getElementById('bio-input').focus();
}

function hideEditForm() {
    document.getElementById('bio-display').style.display = 'block';

    const editBtn = document.querySelector('.edit-trigger');
    if (editBtn) editBtn.style.display = 'block';

    document.getElementById('bio-input').style.display = 'none';
    document.getElementById('btn-group').style.display = 'none';
}

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
    if (overlay && e.target === overlay) {
        overlay.style.display = 'none';
    }
});