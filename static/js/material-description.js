document.addEventListener('DOMContentLoaded', function () {
    const groups = document.querySelectorAll('[data-accordion-group="material-cards"]');
    groups.forEach(group => {
        const cards = group.querySelectorAll('[data-material-slug]');
        const descBlock = group.querySelector('.material-description-block');
        const descContent = group.querySelector('.material-description-content');

        if (!descBlock || !descContent) return;

        let currentlyOpenSlug = null;
        // ← Сохраняем не карточку, а родительскую секцию (или заголовок)
        const sectionHeader = group.closest('.section')?.querySelector('.section__header') ||
                              group.closest('.section') ||
                              group;

        cards.forEach(card => {
            card.addEventListener('click', function (e) {
                if (e.target.tagName === 'A' && !e.target.hasAttribute('data-material-slug')) {
                    return;
                }

                const materialSlug = this.dataset.materialSlug;

                // Если уже открыт — закрываем и скроллим к секции
                if (currentlyOpenSlug === materialSlug) {
                    descBlock.style.display = 'none';
                    currentlyOpenSlug = null;
                    sectionHeader?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    return;
                }

                currentlyOpenSlug = materialSlug;
                descBlock.style.display = 'none';
                descContent.innerHTML = '<p>Загрузка...</p>';

                fetch(`/ajax/material-description/${materialSlug}/`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            descContent.innerHTML = data.html;

                            const closeButton = document.createElement('button');
                            closeButton.className = 'material-close-button';
                            closeButton.textContent = 'Скрыть';
                            closeButton.type = 'button';
                            closeButton.addEventListener('click', function () {
                                descBlock.style.display = 'none';
                                currentlyOpenSlug = null;
                                sectionHeader?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                            });
                            descContent.appendChild(closeButton);

                            descBlock.style.display = 'block';
                            descBlock.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        } else {
                            descContent.innerHTML = '<p>Ошибка загрузки материала.</p>';
                            descBlock.style.display = 'block';
                            currentlyOpenSlug = null;
                        }
                    })
                    .catch(err => {
                        console.error('AJAX error:', err);
                        descContent.innerHTML = '<p>Не удалось загрузить материал.</p>';
                        descBlock.style.display = 'block';
                        currentlyOpenSlug = null;
                    });
            });

            const links = card.querySelectorAll('a[data-material-slug]');
            links.forEach(link => {
                link.addEventListener('click', function (e) {
                    e.preventDefault();
                    card.click();
                });
            });
        });
    });
});