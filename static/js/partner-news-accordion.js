document.addEventListener('DOMContentLoaded', function () {
    const showMoreBtn = document.querySelector('.show-all-partner-news-btn');
    const partnersContainer = document.getElementById('partners-content-container');
    const titleEl = document.querySelector('#partners .section__title');
    const initialTitle = titleEl ? titleEl.textContent : 'Наши партнёры';

    if (!showMoreBtn || !partnersContainer || !titleEl) return;

    const originalContent = partnersContainer.innerHTML;

    // Сохраняем departmentSlug (может не использоваться, но на всякий случай)
    const departmentSlug = showMoreBtn.dataset.department;

    // Клик по карточке партнёра
    partnersContainer.addEventListener('click', function(e) {
        const cardLink = e.target.closest('.partner-card-link');
        if (!cardLink) return;

        e.preventDefault();
        const slug = cardLink.dataset.slug;
        if (!slug) return;

        // Прокрутка к секции
        const partnersSection = document.getElementById('partners');
        if (partnersSection) {
            partnersSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        loadPartnerDetail(slug, departmentSlug);
    });

    // Клик по кнопке («Назад» или исходное состояние)
    showMoreBtn.addEventListener('click', function(e) {
        e.preventDefault();
        if (showMoreBtn.classList.contains('back-to-list-btn')) {
            restorePartnerList();
        }
        // В текущей реализации кнопка не делает ничего в исходном состоянии
        // (в отличие от новостей, где есть "Показать все")
    });

    function loadPartnerDetail(slug, deptSlug) {
        // Если партнёрские новости глобальные — deptSlug не нужен, но передаём для совместимости
        const url = `/ajax/news-detail/?slug=${encodeURIComponent(slug)}${deptSlug ? '&department=' + encodeURIComponent(deptSlug) : ''}`;

        fetch(url)
            .then(response => {
                if (!response.ok) throw new Error('Server returned ' + response.status);
                return response.json();
            })
            .then(data => {
                if (data.success && data.html) {
                    partnersContainer.innerHTML = data.html;

                    // Меняем заголовок
                    if (titleEl) {
                        const tempDiv = document.createElement('div');
                        tempDiv.innerHTML = data.html;
                        const h2 = tempDiv.querySelector('h2');
                        const title = h2 ? h2.textContent.trim() : 'Партнёр';
                        titleEl.textContent = title;
                    }

                    // Превращаем кнопку в "Назад"
                    showMoreBtn.innerHTML = 'К списку партнёров&nbsp;';
                    showMoreBtn.classList.add('back-to-list-btn');
                    showMoreBtn.classList.remove('hidden');

                    // Удаляем старый SVG
                    const existingSvg = showMoreBtn.querySelector('svg');
                    if (existingSvg) existingSvg.remove();

                    // Добавляем новый SVG (стрелка влево)
                    const svgTemplate = document.getElementById('svg-show-all-template');
                    if (svgTemplate && svgTemplate.firstElementChild) {
                        const svgClone = svgTemplate.firstElementChild.cloneNode(true);
                        svgClone.style.transform = 'scaleX(-1)';
                        showMoreBtn.appendChild(svgClone);
                    }
                } else {
                    partnersContainer.innerHTML = '<p>Не удалось загрузить информацию.</p>';
                }
            })
            .catch(err => {
                console.error('Partner detail load error:', err);
                partnersContainer.innerHTML = '<p>Ошибка загрузки.</p>';
            });
    }

    function restorePartnerList() {
        partnersContainer.innerHTML = originalContent;
        if (titleEl) {
            titleEl.textContent = initialTitle;
        }
        // Восстанавливаем кнопку (хотя сейчас она ничего не делает)
        showMoreBtn.innerHTML = '';
        showMoreBtn.classList.remove('back-to-list-btn');
        showMoreBtn.classList.add('hidden');
        const svg = showMoreBtn.querySelector('svg');
        if (svg) svg.remove();
    }
});