document.addEventListener('DOMContentLoaded', function () {
    const showMoreBtn = document.querySelector('.show-more-news');
    const newsContainer = document.getElementById('news-content-container');
    const titleEl = document.getElementById('news-section-title');
    const initialTitle = titleEl ? titleEl.textContent : 'Последние новости';

    if (!showMoreBtn || !newsContainer) return;

    const departmentSlug = showMoreBtn.dataset.department;
    if (!departmentSlug) {
        console.warn('Department slug not found on show-more button.');
        return;
    }

    const initialContent = newsContainer.innerHTML;

    // Клик по кнопке "Показать все / Скрыть / Назад"
    showMoreBtn.addEventListener('click', function(e) {
        e.preventDefault();

        if (showMoreBtn.classList.contains('back-to-list-btn')) {
            restoreNewsList();
            return;
        }

        if (newsContainer.innerHTML !== initialContent) {
            restoreNewsList();
            return;
        }

        updateButtonTextToHide(showMoreBtn);
        const url = `/ajax/all-news/?department=${encodeURIComponent(departmentSlug)}`;
        fetch(url)
            .then(response => {
                if (!response.ok) throw new Error('Network error');
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    newsContainer.innerHTML = data.html;
                    attachYearHandlers(departmentSlug);
                } else {
                    newsContainer.innerHTML = '<p>Ошибка загрузки новостей.</p>';
                }
            })
            .catch(err => {
                console.error('AJAX Error:', err);
                newsContainer.innerHTML = '<p>Ошибка загрузки.</p>';
            });
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

        loadNewsDetail(slug, departmentSlug);
    });

    // === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

    function restoreNewsList() {
        newsContainer.innerHTML = initialContent;
        restoreButtonText(showMoreBtn);
        if (titleEl) {
            titleEl.textContent = initialTitle;
        }
    }

    function restoreButtonText(btn) {
        btn.innerHTML = 'Показать все новости&nbsp;';
        const svgTemplate = document.getElementById('svg-show-all-template');
        if (svgTemplate && svgTemplate.firstElementChild) {
            const svgClone = svgTemplate.firstElementChild.cloneNode(true);
            svgClone.style.transform = 'scaleX(1)';
            btn.appendChild(svgClone);
        }
        btn.classList.remove('hide-news-btn', 'back-to-list-btn');
        if (titleEl) {
            titleEl.textContent = initialTitle;
        }
    }

    function updateButtonTextToHide(btn) {
        btn.innerHTML = 'Скрыть все новости&nbsp;';
        const svgTemplate = document.getElementById('svg-show-all-template');
        if (svgTemplate && svgTemplate.firstElementChild) {
            const svgClone = svgTemplate.firstElementChild.cloneNode(true);
            svgClone.style.transform = 'scaleX(-1)';
            btn.appendChild(svgClone);
        }
        btn.classList.add('hide-news-btn');
        if (titleEl) {
            titleEl.textContent = 'Все новости';
        }
    }

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
                const url = `/ajax/all-news/?department=${encodeURIComponent(deptSlug)}&year=${year}`;
                fetch(url)
                    .then(r => r.json())
                    .then(data => {
                        if (data.success) {
                            newsContainer.innerHTML = data.html;
                            attachYearHandlers(deptSlug);
                        } else {
                            newsContainer.innerHTML = '<p>Не удалось загрузить новости за этот год.</p>';
                        }
                    })
                    .catch(err => {
                        console.error('Year change error:', err);
                        newsContainer.innerHTML = '<p>Ошибка при загрузке.</p>';
                    });
            };
            btn._clickHandler = handler;
            btn.addEventListener('click', handler);
        });
    }

    function loadNewsDetail(slug, deptSlug) {
        const url = `/ajax/news-detail/?slug=${encodeURIComponent(slug)}&department=${encodeURIComponent(deptSlug)}`;
        fetch(url)
            .then(response => {
                if (!response.ok) throw new Error('Server returned ' + response.status);
                return response.json();
            })
            .then(data => {
                if (data.success && data.html) {
                    newsContainer.innerHTML = data.html;
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = data.html;
                    const h2 = tempDiv.querySelector('h2');
                    const title = h2 ? h2.textContent.trim() : 'Новость';

                    if (titleEl) {
                        titleEl.textContent = title;
                    }
                    // Обновляем кнопку на "Назад"
                    showMoreBtn.innerHTML = 'К списку новостей&nbsp';
                    showMoreBtn.classList.add('back-to-list-btn');
                    showMoreBtn.classList.remove('hide-news-btn');
                    const existingSvg = showMoreBtn.querySelector('svg');
                    if (existingSvg) existingSvg.remove();

                    // Добавляем новый SVG из шаблона
                    const svgTemplate = document.getElementById('svg-show-all-template');
                    if (svgTemplate && svgTemplate.firstElementChild) {
                        const svgClone = svgTemplate.firstElementChild.cloneNode(true);
                        // Например, можно оставить как есть, или сделать стрелку влево:
                        svgClone.style.transform = 'scaleX(-1)'; // ← как в "Скрыть все"
                        showMoreBtn.appendChild(svgClone);
                    }
                } else {
                    newsContainer.innerHTML = '<p>Не удалось загрузить новость.</p>';
                }
            })
            .catch(err => {
                console.error('News detail load error:', err);
                newsContainer.innerHTML = '<p>Ошибка загрузки новости.</p>';
            });
    }

    const modal = document.getElementById('image-modal');
    const modalImg = document.getElementById('modal-image');
    const modalCaption = document.getElementById('modal-caption');
    const modalClose = document.getElementById('modal-close');

    // Делегирование кликов по контейнеру новостей
    newsContainer.addEventListener('click', function(e) {
        const img = e.target.closest('img');
        if (!img) return;

        // Только для изображений внутри новости (можно уточнить селектор)
        const newsDetail = img.closest('.news-detail');
        if (!newsDetail) return;

        // Открываем модальное окно
        modal.style.display = 'block';
        modalImg.src = img.src;
        modalImg.alt = img.alt || '';
        modalCaption.textContent = img.alt || '';
    });

    // Закрыть по крестику
    modalClose.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    // Закрыть по клику вне изображения
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Закрыть по Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display === 'block') {
            modal.style.display = 'none';
        }
    });
});


