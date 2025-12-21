(function () {
    let modal = document.getElementById('image-modal');
    let modalImg, modalCaption;
    function closeModal() {
        if (modal) {
            modal.style.display = 'none';
        }
    }
    function handleModalClick(e) {
        if (e.target === modal) {
            closeModal();
        }
    }
    function handleEscapeKey(e) {
        if (e.key === 'Escape' && modal && modal.style.display === 'block') {
            closeModal();
        }
    }
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'image-modal';
        modal.className = 'modal';
        modal.innerHTML = `
            <span class="modal-close">&times;</span>
            <img class="modal-content" id="modal-image">
            <div class="modal-caption" id="modal-caption"></div>
        `;
        document.body.appendChild(modal);
        modalImg = modal.querySelector('.modal-content');
        modalCaption = modal.querySelector('#modal-caption');
        const modalClose = modal.querySelector('.modal-close');
        modalClose.addEventListener('click', closeModal);
        modal.addEventListener('click', handleModalClick);
        document.addEventListener('keydown', handleEscapeKey);
    } else {
        modalImg = modal.querySelector('.modal-content');
        modalCaption = modal.querySelector('#modal-caption');
        const modalClose = modal.querySelector('.modal-close');
        if (modalClose) {
            modalClose.addEventListener('click', closeModal);
            modal.addEventListener('click', handleModalClick);
            document.addEventListener('keydown', handleEscapeKey);
        }
    }
    document.addEventListener('click', function (e) {
        const img = e.target.closest('img.modal-image');
        if (!img || !modalImg || !modalCaption) return;
        modal.style.display = 'block';
        modalImg.src = img.src;
        modalImg.alt = img.alt || '';
        modalCaption.textContent = img.alt || img.title || '';
    });
})();