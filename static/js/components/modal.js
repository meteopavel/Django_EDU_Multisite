let modalInstance = null;


export class ImageModal {
    constructor() {
        this.modal = null;
        this.modalImg = null;
        this.modalCaption = null;
        this.isOpen = false;
        this.images = [];
        this.currentIndex = 0;
        this._bindMethods();
        this._init();
    }

    _bindMethods() {
        this.close = this.close.bind(this);
        this.handleClickOutside = this.handleClickOutside.bind(this);
        this.handleEscapeKey = this.handleEscapeKey.bind(this);
        this.handleClick = this.handleClick.bind(this);
        this.prev = this.prev.bind(this);
        this.next = this.next.bind(this);
    }

    _init() {
        this.modal = document.getElementById('image-modal');
        if (!this.modal) {
            this.modal = document.createElement('div');
            this.modal.id = 'image-modal';
            this.modal.className = 'modal';
            this.modal.innerHTML = `
                <span class="modal-close">&times;</span>
                <button class="modal-nav modal-prev">&#10094;</button>
                <img class="modal-content" id="modal-image">
                <button class="modal-nav modal-next">&#10095;</button>
                <div class="modal-caption" id="modal-caption"></div>
            `;
            document.body.appendChild(this.modal);
        }
        this.modalImg = this.modal.querySelector('.modal-content');
        this.modalCaption = this.modal.querySelector('#modal-caption');

        this.modal.querySelector('.modal-close').addEventListener('click', this.close);
        this.modal.querySelector('.modal-prev').addEventListener('click', (e) => { e.stopPropagation(); this.prev(); });
        this.modal.querySelector('.modal-next').addEventListener('click', (e) => { e.stopPropagation(); this.next(); });
        this.modal.addEventListener('click', this.handleClickOutside);
        document.addEventListener('keydown', this.handleEscapeKey);
        document.addEventListener('click', this.handleClick);
    }

    handleClick(e) {
        const img = e.target.closest('img.modal-image');
        if (!img) return;
        e.preventDefault();
        this.images = Array.from(document.querySelectorAll('img.modal-image'));
        this.currentIndex = this.images.indexOf(img);
        this._show(img.src, img.alt || img.title || '');
    }

    _show(src, caption = '') {
        if (!this.modalImg || !this.modalCaption) return;
        this.modalImg.src = src;
        this.modalImg.alt = caption;
        this.modalCaption.textContent = caption;
        this.modal.style.display = 'flex';
        this.isOpen = true;
        document.body.style.overflow = 'hidden';
        this._updateNav();
    }

    _updateNav() {
        const multiple = this.images.length > 1;
        this.modal.querySelector('.modal-prev').style.display = multiple ? '' : 'none';
        this.modal.querySelector('.modal-next').style.display = multiple ? '' : 'none';
    }

    prev() {
        if (this.images.length <= 1) return;
        this.currentIndex = (this.currentIndex - 1 + this.images.length) % this.images.length;
        const img = this.images[this.currentIndex];
        this._show(img.src, img.alt || img.title || '');
    }

    next() {
        if (this.images.length <= 1) return;
        this.currentIndex = (this.currentIndex + 1) % this.images.length;
        const img = this.images[this.currentIndex];
        this._show(img.src, img.alt || img.title || '');
    }

    open(src, caption = '') {
        this.images = Array.from(document.querySelectorAll('img.modal-image'));
        this.currentIndex = this.images.findIndex(img => img.src === src);
        if (this.currentIndex === -1) this.currentIndex = 0;
        this._show(src, caption);
    }

    close() {
        if (!this.modal) return;
        this.modal.style.display = 'none';
        this.isOpen = false;
        document.body.style.overflow = '';
    }

    handleClickOutside(e) {
        if (e.target === this.modal) {
            this.close();
        }
    }

    handleEscapeKey(e) {
        if (!this.isOpen) return;
        if (e.key === 'Escape') this.close();
        if (e.key === 'ArrowLeft') this.prev();
        if (e.key === 'ArrowRight') this.next();
    }

    destroy() {
        if (!this.modal) return;
        this.modal.querySelector('.modal-close')?.removeEventListener('click', this.close);
        this.modal.removeEventListener('click', this.handleClickOutside);
        document.removeEventListener('keydown', this.handleEscapeKey);
        document.removeEventListener('click', this.handleClick);
    }
}


export function initModal() {
    if (!modalInstance) {
        modalInstance = new ImageModal();
    }
    return modalInstance;
}
