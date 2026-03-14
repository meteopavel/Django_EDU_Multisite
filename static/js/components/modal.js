let modalInstance = null;


export class ImageModal {
    constructor() {
        this.modal = null;
        this.modalImg = null;
        this.modalCaption = null;
        this.isOpen = false;
        this._bindMethods();
        this._init();
    }
    _bindMethods() {
        this.close = this.close.bind(this);
        this.handleClickOutside = this.handleClickOutside.bind(this);
        this.handleEscapeKey = this.handleEscapeKey.bind(this);
        this.handleClick = this.handleClick.bind(this);
    }
    _init() {
        this.modal = document.getElementById('image-modal');
        if (!this.modal) {
            this.modal = document.createElement('div');
            this.modal.id = 'image-modal';
            this.modal.className = 'modal';
            this.modal.innerHTML = `
                <span class="modal-close">&times;</span>
                <img class="modal-content" id="modal-image">
                <div class="modal-caption" id="modal-caption"></div>
            `;
            document.body.appendChild(this.modal);
        }
        this.modalImg = this.modal.querySelector('.modal-content');
        this.modalCaption = this.modal.querySelector('#modal-caption');
        const modalClose = this.modal.querySelector('.modal-close');
        modalClose.addEventListener('click', this.close);
        this.modal.addEventListener('click', this.handleClickOutside);
        document.addEventListener('keydown', this.handleEscapeKey);
        document.addEventListener('click', this.handleClick);
    }
    handleClick(e) {
        const img = e.target.closest('img.modal-image');
        if (!img) return;
        e.preventDefault();
        this.open(img.src, img.alt || img.title || '');
    }
    open(src, caption = '') {
        if (!this.modalImg || !this.modalCaption) return;
        this.modalImg.src = src;
        this.modalImg.alt = caption;
        this.modalCaption.textContent = caption;
        this.modal.style.display = 'block';
        this.isOpen = true;
        document.body.style.overflow = 'hidden';
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
        if (e.key === 'Escape' && this.isOpen) {
            this.close();
        }
    }
    destroy() {
        if (!this.modal) return;
        const modalClose = this.modal.querySelector('.modal-close');
        modalClose?.removeEventListener('click', this.close);
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