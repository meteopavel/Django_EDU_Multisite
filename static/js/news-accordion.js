document.addEventListener('DOMContentLoaded', function () {
    // ========================================
    // СНАЧАЛА ОБЪЯВЛЯЕМ ВСЕ ЭЛЕМЕНТЫ
    // ========================================
    const showMoreBtn = document.querySelector('.show-more-news');
    const newsContainer = document.getElementById('news-content-container');
    const titleEl = document.getElementById('news-section-title');
    const baseUrl = window.location.pathname;

    // Проверяем наличие обязательных элементов
    if (!showMoreBtn || !newsContainer) {
        console.warn('Необходимые элементы не найдены на странице');
        return;
    }

    // ========================================
    // ПОЛУЧАЕМ DEPARTMENT SLUG ИЗ АТРИБУТА КНОПКИ (НЕ ИЗ URL!)
    // ========================================
    const departmentSlug = showMoreBtn.dataset.department;

    if (!departmentSlug) {
        console.warn('Department slug not found on show-more button.');
        return;
    }

    // ========================================
    // ПОЛУЧАЕМ ПАРАМЕТРЫ ИЗ URL ДЛЯ ИНИЦИАЛИЗАЦИИ
    // ========================================
    const urlParams = new URLSearchParams(window.location.search);
    const newsSlug = urlParams.get('news');
    const year = urlParams.get('year');

    let isInitializing = true;
    let isProcessingHistory = false;
    const initialTitle = titleEl ? titleEl.textContent : 'Последние новости';
    const initialContent = newsContainer.innerHTML;

    // ========================================
    // ИНИЦИАЛИЗАЦИЯ ПО URL - ДОБАВЛЯЕМ ИСТОРИЮ!
    // ========================================
    if (newsSlug || year) {
        console.log('Инициализация по URL:', { departmentSlug, newsSlug, year });

        // КРИТИЧЕСКИ ВАЖНО: добавляем начальное состояние в историю ПЕРЕД загрузкой
        window.history.replaceState({
            newsState: 'list',
            department: departmentSlug
        }, '', baseUrl);

        // Теперь загружаем контент и добавляем текущее состояние
        if (newsSlug) {
            // Загружаем детали новости и добавляем в историю
            setTimeout(() => {
                loadNewsDetail(newsSlug, departmentSlug, true);
            }, 0);
        } else if (year) {
            // Загружаем новости за год и добавляем в историю
            setTimeout(() => {
                loadNewsByYear(departmentSlug, year, true);
            }, 0);
        }

        isInitializing = false;
        // НЕ возвращаемся, продолжаем инициализацию обработчиков
    }

    // ========================================
    // ОСНОВНАЯ ИНИЦИАЛИЗАЦИЯ
    // ========================================
    if (!window.history.state?.initialized) {
        window.history.replaceState({
            initialized: true,
            newsState: 'list',
            department: departmentSlug
        }, '', baseUrl);
    }

    // ========================================
    // ОБРАБОТЧИК POPSTATE
    // ========================================
    window.addEventListener('popstate', function(event) {
        console.log('popstate обработан:', event.state);

        // Блокируем повторные вызовы во время обработки
        if (isProcessingHistory) {
            console.log('Пропускаем popstate - уже обрабатывается');
            return;
        }

        isProcessingHistory = true;

        // Если состояние отсутствует - возвращаемся к списку
        if (!event.state) {
            restoreNewsList();
            isProcessingHistory = false;
            return;
        }

        // Обрабатываем состояние
        switch(event.state.newsState) {
            case 'list':
                restoreNewsList();
                break;
            case 'all':
                loadAllNews(event.state.department, false);
                break;
            case 'detail':
                loadNewsDetail(event.state.slug, event.state.department, false);
                break;
            case 'year':
                loadNewsByYear(event.state.department, event.state.year, false);
                break;
            default:
                restoreNewsList();
        }

        // Сбрасываем блокировку после короткой задержки
        setTimeout(() => {
            isProcessingHistory = false;
        }, 100);
    });

    // ========================================
    // ОБРАБОТЧИКИ СОБЫТИЙ
    // ========================================

    // Клик по кнопке "Показать все / Скрыть / Назад"
    showMoreBtn.addEventListener('click', function(e) {
        e.preventDefault();

        // Если кнопка "Назад" - идем назад в истории
        if (showMoreBtn.classList.contains('back-to-list-btn')) {
            window.history.back();
            return;
        }

        // Если текущий контент не начальный - возвращаемся к начальному состоянию
        if (newsContainer.innerHTML !== initialContent) {
            restoreNewsList();
            return;
        }

        // Иначе загружаем все новости
        loadAllNews(departmentSlug, true);
    });

    // Клик по карточке новости
    newsContainer.addEventListener('click', function(e) {
        const cardLink = e.target.closest('.news-card-link');
        if (!cardLink) return;

        e.preventDefault();
        const slug = cardLink.dataset.slug;
        if (!slug) return;

        const newsSection = document.getElementById('latest_news');
        if (newsSection) {
            newsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        loadNewsDetail(slug, departmentSlug, true);
    });

    // ========================================
    // ФУНКЦИИ ЗАГРУЗКИ ДАННЫХ
    // ========================================

    /**
     * Загрузка всех новостей
     */
    function loadAllNews(deptSlug, addToHistory = true) {
        const url = `/ajax/all-news/?department=${encodeURIComponent(deptSlug)}`;

        // Добавляем в историю, если нужно
        if (addToHistory) {
            const newState = {
                newsState: 'all',
                department: deptSlug
            };
            window.history.pushState(newState, '', `${baseUrl}?department=${deptSlug}&view=all`);
        }

        // Обновляем кнопку на "Скрыть"
        updateButtonTextToHide(showMoreBtn);

        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    newsContainer.innerHTML = data.html;
                    attachYearHandlers(deptSlug);
                } else {
                    newsContainer.innerHTML = '<p>Ошибка загрузки новостей.</p>';
                }
            })
            .catch(err => {
                console.error('AJAX Error:', err);
                newsContainer.innerHTML = '<p>Ошибка загрузки.</p>';
            });
    }

    /**
     * Загрузка новостей за определенный год
     */
    function loadNewsByYear(deptSlug, year, addToHistory = true) {
        const url = `/ajax/all-news/?department=${encodeURIComponent(deptSlug)}&year=${year}`;

        // Добавляем в историю, если нужно
        if (addToHistory) {
            const newState = {
                newsState: 'year',
                department: deptSlug,
                year: year
            };
            window.history.pushState(newState, '', `${baseUrl}?department=${deptSlug}&year=${year}`);
        }

        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    newsContainer.innerHTML = data.html;
                    attachYearHandlers(deptSlug);

                    // Обновляем заголовок
                    if (titleEl) {
                        titleEl.textContent = `Новости за ${year} год`;
                    }

                    // КРИТИЧЕСКИ ВАЖНО: обновляем кнопку на "Скрыть"!
                    updateButtonTextToHide(showMoreBtn);
                } else {
                    newsContainer.innerHTML = '<p>Не удалось загрузить новости за этот год.</p>';
                    restoreButtonText(showMoreBtn);
                }
            })
            .catch(err => {
                console.error('Year change error:', err);
                newsContainer.innerHTML = '<p>Ошибка при загрузке.</p>';
                restoreButtonText(showMoreBtn);
            });
    }

    /**
     * Загрузка деталей конкретной новости
     */
    function loadNewsDetail(slug, deptSlug, addToHistory = true) {
        const url = `/ajax/news-detail/?slug=${encodeURIComponent(slug)}&department=${encodeURIComponent(deptSlug)}`;

        // Добавляем в историю, если нужно
        if (addToHistory) {
            const newState = {
                newsState: 'detail',
                department: deptSlug,
                slug: slug
            };
            window.history.pushState(newState, '', `${baseUrl}?department=${deptSlug}&news=${slug}`);
        }

        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.html) {
                    newsContainer.innerHTML = data.html;

                    // Извлекаем заголовок из загруженного контента
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = data.html;
                    const h2 = tempDiv.querySelector('h2');
                    const title = h2 ? h2.textContent.trim() : 'Новость';

                    if (titleEl) {
                        titleEl.textContent = title;
                    }

                    // Обновляем кнопку на "Назад"
                    updateButtonToBack();
                } else {
                    newsContainer.innerHTML = '<p>Не удалось загрузить новость.</p>';
                }
            })
            .catch(err => {
                console.error('News detail load error:', err);
                newsContainer.innerHTML = '<p>Ошибка загрузки новости.</p>';
            });
    }

    // ========================================
    // ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
    // ========================================

    /**
     * Восстановление начального списка новостей
     */
    function restoreNewsList() {
        newsContainer.innerHTML = initialContent;
        restoreButtonText(showMoreBtn);

        if (titleEl) {
            titleEl.textContent = initialTitle;
        }

        // Восстанавливаем базовый URL
        if (window.history.state?.newsState !== 'list') {
            window.history.replaceState({
                newsState: 'list',
                department: departmentSlug
            }, '', baseUrl);
        }
    }

    /**
     * Восстановление текста кнопки в начальное состояние
     */
    function restoreButtonText(btn) {
        btn.innerHTML = 'Все новости';
        const svgTemplate = document.getElementById('svg-show-all-template');

        if (svgTemplate && svgTemplate.firstElementChild) {
            const svgClone = svgTemplate.firstElementChild.cloneNode(true);
            svgClone.style.transform = 'scaleX(1)';
            btn.innerHTML = 'Все новости';
            btn.appendChild(svgClone);
        }

        btn.classList.remove('hide-news-btn', 'back-to-list-btn');
    }

    /**
     * Обновление кнопки для состояния "Скрыть"
     */
    function updateButtonTextToHide(btn) {
        btn.innerHTML = 'Скрыть';
        const svgTemplate = document.getElementById('svg-show-all-template');

        if (svgTemplate && svgTemplate.firstElementChild) {
            const svgClone = svgTemplate.firstElementChild.cloneNode(true);
            svgClone.style.transform = 'scaleX(-1)';
            btn.innerHTML = 'Скрыть';
            btn.appendChild(svgClone);
        }

        btn.classList.add('hide-news-btn');
        btn.classList.remove('back-to-list-btn');

        if (titleEl) {
            titleEl.textContent = 'Все новости';
        }
    }

    /**
     * Обновление кнопки для состояния "Назад"
     */
    function updateButtonToBack() {
        showMoreBtn.innerHTML = 'Назад';
        const svgTemplate = document.getElementById('svg-show-all-template');

        if (svgTemplate && svgTemplate.firstElementChild) {
            const svgClone = svgTemplate.firstElementChild.cloneNode(true);
            svgClone.style.transform = 'scaleX(-1)';
            showMoreBtn.innerHTML = 'Назад';
            showMoreBtn.appendChild(svgClone);
        }

        showMoreBtn.classList.add('back-to-list-btn');
        showMoreBtn.classList.remove('hide-news-btn');
    }

    /**
     * Обновление кнопки для состояния "по году"
     */
    function updateButtonTextForYear() {
        showMoreBtn.innerHTML = 'Все новости';
        const svgTemplate = document.getElementById('svg-show-all-template');

        if (svgTemplate && svgTemplate.firstElementChild) {
            const svgClone = svgTemplate.firstElementChild.cloneNode(true);
            svgClone.style.transform = 'scaleX(1)';
            showMoreBtn.innerHTML = 'Все новости';
            showMoreBtn.appendChild(svgClone);
        }

        showMoreBtn.classList.remove('hide-news-btn', 'back-to-list-btn');
    }

    /**
     * Привязка обработчиков к кнопкам годов
     */
    function attachYearHandlers(deptSlug) {
        const yearButtons = document.querySelectorAll('.year-btn[data-year]');

        yearButtons.forEach(btn => {
            const existingHandler = btn._clickHandler;
            if (existingHandler) {
                btn.removeEventListener('click', existingHandler);
            }

            const handler = function(e) {
                e.preventDefault();
                const year = this.dataset.year;
                loadNewsByYear(deptSlug, year, true);
            };

            btn._clickHandler = handler;
            btn.addEventListener('click', handler);
        });
    }
});