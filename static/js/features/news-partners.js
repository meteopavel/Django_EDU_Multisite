import { DetailLoader } from '../components/detail-loader.js';
import { fetchWithFeedback } from '../lib/ajax.js';
import { updateButton } from '../lib/svg.js';

const SELECTORS = {
    newsContainer: 'news-content-container',
    newsButton: '.show-more-news',
    newsTitle: 'news-section-title',
    partnersContainer: 'partners-content-container',
    partnersButton: '.show-all-partner-news-btn',
    partnersTitle: '#partners .section__title',
    svgTemplate: 'svg-show-all-template'
};

let newsLoader = null;
let partnersLoader = null;


export function initNews() {
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


export function initPartners() {
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