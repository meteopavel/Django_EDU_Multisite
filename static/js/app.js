/* Единый бандл фронтенда (раньше ES-модули в features/, components/, lib/).
 * Собран в один файл, потому что хостинг кэширует статику на год: импорты
 * внутри модулей не версионируются, и правки не доходили до посетителей.
 * Пересборка — вручную из git-истории, файл правится напрямую. */


/* === ajax.js === */
const LOADING_HTML = '<p>Загрузка...</p>';


function getErrorHTML(label = 'данные') {
    return `<p>Не удалось загрузить ${label}.</p>`;
}


async function fetchJSON(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
    };
    const response = await fetch(url, { ...defaultOptions, ...options });
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
}


function handleAJAXResponse(container, data, successCallback, label = 'данные') {
    if (data.success && typeof successCallback === 'function') {
        successCallback(data.html);
    } else {
        container.innerHTML = getErrorHTML(label);
        console.error(`API error (${label}):`, data);
    }
}


function withErrorHandling(container, label = 'данные') {
    return {
        onSuccess: (data, render) => {
            handleAJAXResponse(container, data, render, label);
        },
        onError: (err) => {
            console.error(`AJAX error (${label}):`, err);
            container.innerHTML = getErrorHTML(label);
        }
    };
}


async function fetchWithFeedback(container, url, options = {}, label = 'данные') {
    container.innerHTML = '<p>Загрузка...</p>';
    try {
        const data = await fetchJSON(url, options);

        if (data.success && data.html) {
            container.innerHTML = data.html;
            return { success: true, data };
        } else {
            container.innerHTML = `<p>Не удалось загрузить ${label}.</p>`;
            console.error(`API error (${label}):`, data);
            return { success: false, data };
        }
    } catch (err) {
        console.error(`AJAX error (${label}):`, err);
        container.innerHTML = `<p>Ошибка при загрузке ${label}.</p>`;
        return { success: false, error: err };
    }
}

/* === constants.js === */
const SELECTORS = {
    newsContainer: 'news-content-container',
    newsButton: '.show-more-news',
    newsTitle: 'news-section-title',
    partnersContainer: 'partners-content-container',
    partnersButton: '.show-all-partner-news-btn',
    partnersTitle: '#partners .section__title',
    svgTemplate: 'svg-show-all-template'
};

/* === svg.js === */
function cloneButtonSVG(templateId, isFlipped = false) {
    const template = document.getElementById(templateId);
    if (!template || !template.firstElementChild) return null;
    const clone = template.firstElementChild.cloneNode(true);
    clone.style.transform = isFlipped ? 'scaleX(1)' : 'scaleX(-1)';
    return clone;
}


function updateButton(button, text, isBack = false, svgTemplateId = 'svg-show-all-template') {
    if (!button) return;
    button.innerHTML = text + (isBack ? '\u00A0' : '');
    const svg = cloneButtonSVG(svgTemplateId, isBack);
    if (svg) button.appendChild(svg);
    button.classList.toggle('back-to-list-btn', isBack);
    button.classList.toggle('hide-news-btn', !isBack && text === 'Закрыть');
}

/* === accordion.js === */
class Accordion {
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

/* === detail-loader.js === */
class DetailLoader {
    constructor(config) {
        this.container = config.container;
        this.button = config.button;
        this.title = config.title;
        this.baseUrl = config.baseUrl || window.location.pathname;
        this.endpoint = config.endpoint;
        this.config = {
            label: 'материал',
            useHistory: false,
            onLoaded: null,
            svgTemplateId: 'svg-show-all-template',
            section: 'news',
            ...config.config
        };
        this.originalContent = this.container.innerHTML;
        this.originalTitle = this.title?.textContent || '';
    }
    async load(slug, params = {}, addToHistory = true) {
        this.currentSlug = slug;
        this.container.innerHTML = LOADING_HTML;
        this._updateButton({ text: 'Загрузка...', loading: true });
        try {
            const url = (this.config.slugInPath && slug)
                ? `${this.endpoint}${slug}/` + (Object.keys(params).length ? `?${new URLSearchParams(params)}` : '')
                : `${this.endpoint}?${new URLSearchParams({ ...(slug && { slug }), ...params })}`;
            const data = await fetchJSON(url);
            if (data.success && data.html) {
                this.container.innerHTML = data.html;
                this._updateTitleFromContent(data.html);
                this._updateButton({ text: this.config.backText || 'Назад', back: true });
                if (addToHistory && this.config.useHistory) {
                    this._pushHistory({ state: 'detail', slug, params });
                }
                this.config.onLoaded?.(this.container);
            } else {
                this.container.innerHTML = getErrorHTML(this.config.label);
            }
        } catch (err) {
            if (err.name === 'AbortError') return;
            console.error(`AJAX error (${this.config.label}):`, err);
            this.container.innerHTML = getErrorHTML(this.config.label);
        }
    }
    restore() {
        this.container.innerHTML = this.originalContent;
        if (this.title) this.title.textContent = this.originalTitle;
        this._updateButton({
            text: this.config.restoreText || 'Все новости',
            back: false
        });
        if (this.config.useHistory) {
            history.replaceState(
                { state: 'list', slug: null, section: this.config.section },
                '',
                this.baseUrl
            );
        }
    }
    _updateButton({ text, back = false, loading = false }) {
        if (!this.button) return;
        if (loading) {
            this.button.innerHTML = text;
            this.button.disabled = true;
            return;
        }
        this.button.disabled = false;
        this.button.innerHTML = '';
        this.button.appendChild(document.createTextNode(text));
        if (back) this.button.appendChild(document.createTextNode('\u00A0'));
        if (this.config.svgTemplateId) {
            const svgTemplate = document.getElementById(this.config.svgTemplateId);
            if (svgTemplate?.firstElementChild) {
                const svgClone = svgTemplate.firstElementChild.cloneNode(true);
                svgClone.style.transform = back ? 'scaleX(-1)' : 'scaleX(1)';
                this.button.appendChild(svgClone);
            }
        }
        this.button.classList.toggle('back-to-list-btn', back);
        this.button.classList.toggle('hide-news-btn', !back && text === 'Скрыть');
    }
    _updateTitleFromContent(html) {
        if (!this.title) return;
        const tmp = document.createElement('div');
        tmp.innerHTML = html;
        const h2 = tmp.querySelector('h2');
        if (h2) this.title.textContent = h2.textContent.trim();
    }
    _pushHistory({ state, slug, params }) {
        const url = new URL(this.baseUrl, window.location.origin);
        Object.entries({ slug, ...params }).forEach(([key, value]) => {
            if (value) url.searchParams.set(key, value);
        });
        history.pushState(
            { state, slug, params, section: this.config.section },
            '',
            url.pathname + url.search
        );
    }
}

/* === modal.js === */
let modalInstance = null;


class ImageModal {
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


function initModal() {
    if (!modalInstance) {
        modalInstance = new ImageModal();
    }
    return modalInstance;
}

/* === education.js === */
function initEducation() {
    const groups = document.querySelectorAll('[data-accordion-group="education-accordion"]');
    if (!groups.length) return;
    groups.forEach(group => {
        new Accordion('[data-accordion-group="education-accordion"]', {
            onToggle: (item, isOpen) => {
                if (!isOpen) return;
                const content = item.querySelector('.accordion-content');
                const materialSlug = item.dataset.materialSlug;
                const isDocuments = item.dataset.documents === 'true';
                if (content.innerHTML.trim() !== LOADING_HTML && content.innerHTML.trim() !== '') {
                    return;
                }
                if (isDocuments) {
                    loadDocuments(content);
                } else if (materialSlug) {
                    loadMaterial(content, materialSlug);
                }
            }
        });
    });
}


async function loadDocuments(container) {
    container.innerHTML = LOADING_HTML;
    try {
        const data = await fetchJSON('/ajax/documents/');
        const { onSuccess } = withErrorHandling(container, 'документы');
        onSuccess(data, (html) => {
            container.innerHTML = html;
        });
    } catch (err) {
        const { onError } = withErrorHandling(container, 'документы');
        onError(err);
    }
}


async function loadMaterial(container, materialSlug) {
    container.innerHTML = LOADING_HTML;
    try {
        const data = await fetchJSON(`/ajax/material-description/${materialSlug}/`);
        const { onSuccess } = withErrorHandling(container, 'материал');
        onSuccess(data, (html) => {
            container.innerHTML = html;
        });
    } catch (err) {
        const { onError } = withErrorHandling(container, 'материал');
        onError(err);
    }
}

/* === maps.js === */
function initMaps() {
    if (window.yaMapsInitialized) return;
    window.yaMapsInitialized = true;
    const contactsMap = document.getElementById('contacts__map');
    const serviceCards = document.querySelectorAll('.service-card-parking');
    if (!contactsMap && !serviceCards.length) return;
    const apiKey = window.APP_CONFIG?.YANDEX_MAPS_API_KEY || '';
    function initAllMaps() {
        initContactsMap(contactsMap);
        initServiceMaps(serviceCards);
    }
    const script = document.createElement('script');
    script.src = `https://api-maps.yandex.ru/2.1/?apikey=${apiKey}&lang=ru_RU`;
    script.type = 'text/javascript';
    script.onload = initAllMaps;
    document.head.appendChild(script);
}


function initContactsMap(contactsMap) {
    if (!contactsMap) return;
    const mapCenter = contactsMap.dataset.center;
    const balloonText = contactsMap.dataset.balloon || 'Офис';
    let centerCoords = [52.267482, 104.310026]; // fallback
    try {
        centerCoords = JSON.parse(mapCenter);
    } catch (e) {
        console.error('Invalid map center coordinates:', mapCenter);
    }
    ymaps.ready(function() {
        const myMap = new ymaps.Map('contacts__map', {
            center: centerCoords,
            zoom: 17,
            controls: ['smallMapDefaultSet']
        });
        const myPlacemark = new ymaps.Placemark(centerCoords, {
            balloonContent: balloonText
        });
        myMap.geoObjects.add(myPlacemark);
    });
}


function initServiceMaps(serviceCards) {
    if (!serviceCards.length) return;
    serviceCards.forEach((card, index) => {
        const mapId = `map-${index + 1}`;
        const mapContainer = card.querySelector(`#${mapId}`);
        if (!mapContainer) return;
        const coordsStr = card.dataset.coords;
        let coords = [52.267482, 104.310026]; // fallback
        try {
            coords = JSON.parse(coordsStr);
        } catch (e) {
            console.warn('Invalid coords:', coordsStr);
        }
        ymaps.ready(function() {
            const myMap = new ymaps.Map(mapId, {
                center: coords,
                zoom: 17,
                controls: ['smallMapDefaultSet']
            });
            const myPlacemark = new ymaps.Placemark(coords, {
                balloonContent: card.dataset.address || 'Автостоянка'
            });
            myMap.geoObjects.add(myPlacemark);
            myMap.events.add('click', function() {
                myPlacemark.balloon.open();
            });
        });
    });
}

/* === materials.js === */
function createHideButton(onClick) {
    const btn = document.createElement('button');
    btn.className = 'material-close-button';
    btn.textContent = 'Скрыть';
    btn.type = 'button';
    btn.addEventListener('click', onClick);
    return btn;
}


function initMaterials() {
    const groups = document.querySelectorAll('[data-accordion-group="material-cards"]');
    if (!groups.length) return;
    groups.forEach(group => {
        const cards = group.querySelectorAll('[data-material-slug]');
        const descBlock = group.querySelector('.material-description-block');
        const descContent = group.querySelector('.material-description-content');
        if (!descBlock || !descContent) return;
        const sectionHeader = group.closest('.section')?.querySelector('.section__header') || group;
        const departmentSlug = group.dataset.department || '';

        cards.forEach(card => {
            const slug = card.dataset.materialSlug;
            const isExam = (slug === 'exameny');
            const loader = new DetailLoader({
                container: descContent,
                button: null,
                title: null,
                baseUrl: window.location.pathname,
                endpoint: isExam ? '/ajax/exam-info/' : '/ajax/material-description/',
                config: {
                    label: isExam ? 'информацию об экзаменах' : 'материал',
                    useHistory: false,
                    backText: 'Скрыть',
                    restoreText: '',
                    slugInPath: !isExam,  // ✅ Только материалы используют slug в пути
                    onLoaded: (container) => {
                        container.appendChild(createHideButton(() => {
                            descBlock.style.display = 'none';
                            sectionHeader?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        }));
                        descBlock.style.display = 'block';
                        descBlock.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                }
            });
            card.addEventListener('click', function(e) {
                if (e.target.closest('a:not([data-material-slug])')) return;
                if (descBlock.style.display === 'block' && loader.currentSlug === slug) {
                    descBlock.style.display = 'none';
                    return;
                }
                sectionHeader?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                loader.load(isExam ? '' : slug, isExam ? { department: departmentSlug } : {}, false);
            });
        });
    });
}

/* === news-partners.js === */
let newsLoader = null;
let partnersLoader = null;


function initNews() {
    const container = document.getElementById(SELECTORS.newsContainer);
    const button = document.querySelector(SELECTORS.newsButton);
    const title = document.getElementById(SELECTORS.newsTitle);
    if (!container || !button) return;
    const departmentSlug = button.dataset.department;
    const baseUrl = window.location.pathname;
    const urlParams = new URLSearchParams(window.location.search);
    const newsSlug = urlParams.get('news');
    const year = urlParams.get('year');
    newsLoader = new DetailLoader({
        container,
        button,
        title,
        baseUrl,
        endpoint: '/ajax/news-detail/',
        config: {
            label: 'новость',
            useHistory: true,
            backText: 'Назад',
            restoreText: 'Все новости',
            onLoaded: () => attachYearHandlers(departmentSlug),
            section: 'news'
        }
    });
    if (newsSlug || year) {
        window.history.replaceState({
            newsState: 'list',
            department: departmentSlug,
            section: 'news'
        }, '', baseUrl);
        if (newsSlug) {
            setTimeout(() => newsLoader.load(newsSlug, { department: departmentSlug }, true), 0);
        } else if (year) {
            setTimeout(() => loadNewsList(departmentSlug, { year }, true), 0);
        }
    }
    if (!window.history.state?.initialized) {
        window.history.replaceState({
            initialized: true,
            newsState: 'list',
            department: departmentSlug,
            section: 'news'
        }, '', baseUrl);
    }
    window.addEventListener('popstate', (event) => handleNewsPopState(event, departmentSlug));
    button.addEventListener('click', function(e) {
        e.preventDefault();
        if (button.classList.contains('back-to-list-btn')) {
            window.history.back();
            return;
        }
        if (container.innerHTML !== newsLoader.originalContent) {
            newsLoader.restore();
            return;
        }
        loadNewsList(departmentSlug, { view: 'all' }, true);
    });
    container.addEventListener('click', function(e) {
        const cardLink = e.target.closest('.news-card-link');
        if (!cardLink) return;
        e.preventDefault();
        const slug = cardLink.dataset.slug;
        if (!slug) return;
        document.getElementById('latest_news')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        newsLoader.load(slug, { department: departmentSlug }, true);
    });
    attachYearHandlers(departmentSlug);
}


function initPartners() {
    const container = document.getElementById(SELECTORS.partnersContainer);
    const button = document.querySelector(SELECTORS.partnersButton);
    const title = document.querySelector(SELECTORS.partnersTitle);
    if (!container || !button || !title) return;
    const originalContent = container.innerHTML;
    const initialTitle = title.textContent;
    partnersLoader = new DetailLoader({
        container,
        button,
        title,
        baseUrl: window.location.pathname,
        endpoint: '/ajax/news-detail/',
        config: {
            label: 'информацию о партнёре',
            useHistory: false,
            backText: 'Закрыть',
            restoreText: '',
            svgTemplateId: SELECTORS.svgTemplate,
            onLoaded: () => button.classList.remove('hidden')
        }
    });
    container.addEventListener('click', function(e) {
        const cardLink = e.target.closest('.partner-card-link');
        if (!cardLink) return;
        e.preventDefault();
        const slug = cardLink.dataset.slug;
        if (!slug) return;
        document.getElementById('partners')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        partnersLoader.load(slug, {}, false);
    });
    button.addEventListener('click', function(e) {
        e.preventDefault();
        partnersLoader.restore();
        button.classList.add('hidden');
    });
}


async function loadNewsList(deptSlug, options = {}, addToHistory = true) {
    const { year = null, view = 'all' } = options;
    const button = document.querySelector(SELECTORS.newsButton);
    const container = document.getElementById(SELECTORS.newsContainer);
    const title = document.getElementById(SELECTORS.newsTitle);
    const baseUrl = window.location.pathname;
    const queryParams = new URLSearchParams({ department: deptSlug });
    const historyState = { newsState: 'list', department: deptSlug, section: 'news' };
    if (year) {
        queryParams.set('year', year);
        historyState.newsState = 'year';
        historyState.year = year;
    } else if (view === 'all') {
        queryParams.set('view', 'all');
        historyState.newsState = 'all';
    }
    if (addToHistory) {
        window.history.pushState(historyState, '', `${baseUrl}?${queryParams}`);
    }
    updateButton(button, 'Закрыть', false, SELECTORS.svgTemplate);
    const result = await fetchWithFeedback(container, `/ajax/all-news/?${queryParams}`, {}, 'новости');
    if (result.success) {
        attachYearHandlers(deptSlug);
        if (year && title) {
            title.textContent = `Новости за ${year} год`;
        }
    }
}


function handleNewsPopState(event, deptSlug) {
    const state = event.state;
    if (state?.section && state.section !== 'news') return;
    if (!state?.newsState) {
        newsLoader?.restore();
        return;
    }
    const actions = {
        list: () => newsLoader?.restore(),
        all: () => loadNewsList(deptSlug, { view: 'all' }, false),
        year: () => loadNewsList(deptSlug, { year: state.year }, false),
        detail: () => newsLoader?.load(state.slug, state.params || {}, false)
    };
    actions[state.newsState]?.();
}


function attachYearHandlers(deptSlug) {
    const yearButtons = document.querySelectorAll('.year-btn[data-year]');
    yearButtons.forEach(btn => {
        const newBtn = btn.cloneNode(true);
        btn.parentNode.replaceChild(newBtn, btn);
        newBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const year = this.dataset.year;
            loadNewsList(deptSlug, { year }, true);
        });
    });
}

/* === bootstrap === */
document.addEventListener('DOMContentLoaded', () => {
    initModal();
    if (document.querySelector('[data-accordion-group="education-accordion"]')) {initEducation();}
    if (document.querySelector('[data-accordion-group="material-cards"]')) {initMaterials();}
    if (document.getElementById('news-content-container')) {initNews();}
    if (document.getElementById('partners-content-container')) {initPartners();}
    if (document.getElementById('contacts__map') || document.querySelector('.service-card-parking')) {initMaps();}
});
