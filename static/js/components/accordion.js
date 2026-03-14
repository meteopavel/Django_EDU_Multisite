export class Accordion {
    constructor(groupSelector, options = {}) {
        this.config = {
            itemSelector: '.accordion-item',
            headerSelector: '.accordion-header',
            contentSelector: '.accordion-content',
            toggleIconSelector: '.accordion-toggle',
            closeOthers: true,
            onToggle: null,
            ...options
        };
        this.groups = document.querySelectorAll(groupSelector);
        this.init();
    }
    init() {
        this.groups.forEach(group => this._initGroup(group));
    }
    _initGroup(group) {
        const items = group.querySelectorAll(this.config.itemSelector);
        items.forEach(item => {
            const header = item.querySelector(this.config.headerSelector);
            if (!header) return;
            header.addEventListener('click', (e) => {
                e.preventDefault();
                this._toggleItem(item, group, items);
            });
        });
    }
    _toggleItem(item, group, allItems) {
        const contentEl = item.querySelector(this.config.contentSelector);
        const iconEl = item.querySelector(this.config.toggleIconSelector);
        const isOpen = item.classList.contains('open');
        if (this.config.closeOthers && !isOpen) {
            allItems.forEach(otherItem => {
                if (otherItem !== item && otherItem.classList.contains('open')) {
                    this._closeItem(otherItem);
                }
            });
        }
        if (isOpen) {
            this._closeItem(item);
        } else {
            this._openItem(item);
        }
        if (typeof this.config.onToggle === 'function') {
            this.config.onToggle(item, !isOpen);
        }
    }
    _openItem(item) {
        const contentEl = item.querySelector(this.config.contentSelector);
        const iconEl = item.querySelector(this.config.toggleIconSelector);
        item.classList.add('open');
        if (contentEl) contentEl.style.display = 'block';
        if (iconEl) iconEl.textContent = '−';
    }
    _closeItem(item) {
        const contentEl = item.querySelector(this.config.contentSelector);
        const iconEl = item.querySelector(this.config.toggleIconSelector);
        item.classList.remove('open');
        if (contentEl) contentEl.style.display = 'none';
        if (iconEl) iconEl.textContent = '+';
    }
}