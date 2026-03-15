import { LOADING_HTML, getErrorHTML, fetchJSON } from '../lib/ajax.js';


export class DetailLoader {
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