document.addEventListener('DOMContentLoaded', function () {
    const groups = document.querySelectorAll('[data-accordion-group="education-accordion"]');
    groups.forEach(group => {
        const items = group.querySelectorAll('.accordion-item');

        items.forEach(item => {
            const header = item.querySelector('.accordion-header');
            const content = item.querySelector('.accordion-content');
            const materialSlug = item.dataset.materialSlug;

            // Если нет materialSlug — это "Документы", не трогаем
            if (!materialSlug) return;

            header.addEventListener('click', function () {
                // Закрываем все открытые
                items.forEach(otherItem => {
                    if (otherItem !== item && otherItem.classList.contains('open')) {
                        otherItem.classList.remove('open');
                        otherItem.querySelector('.accordion-content').style.display = 'none';
                        otherItem.querySelector('.accordion-toggle').textContent = '+';
                    }
                });

                // Переключаем текущий
                if (item.classList.contains('open')) {
                    item.classList.remove('open');
                    content.style.display = 'none';
                    header.querySelector('.accordion-toggle').textContent = '+';
                } else {
                    item.classList.add('open');
                    content.style.display = 'block';
                    header.querySelector('.accordion-toggle').textContent = '−';

                    // Если контент ещё не загружен — загружаем
                    if (content.innerHTML.trim() === '<p>Загрузка...</p>') {
                        fetch(`/ajax/material-description/${materialSlug}/`)
                            .then(response => response.json())
                            .then(data => {
                                if (data.success) {
                                    content.innerHTML = data.html;
                                } else {
                                    content.innerHTML = '<p>Ошибка загрузки материала.</p>';
                                }
                            })
                            .catch(err => {
                                console.error('AJAX error:', err);
                                content.innerHTML = '<p>Не удалось загрузить материал.</p>';
                            });
                    }
                }
            });
        });
    });
});