document.addEventListener('DOMContentLoaded', function () {
    const groups = document.querySelectorAll('[data-accordion-group="education-accordion"]');
    groups.forEach(group => {
        const items = group.querySelectorAll('.accordion-item');

        items.forEach(item => {
            const header = item.querySelector('.accordion-header');
            const content = item.querySelector('.accordion-content');
            const materialSlug = item.dataset.materialSlug;
            const isDocuments = item.dataset.documents === 'true';

            header.addEventListener('click', function () {
                // Закрываем все другие открытые пункты
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
                    return;
                }

                // Открываем текущий
                item.classList.add('open');
                content.style.display = 'block';
                header.querySelector('.accordion-toggle').textContent = '−';

                // Если контент ещё не загружен
                if (content.innerHTML.trim() === '<p>Загрузка...</p>') {
                    if (isDocuments) {
                        // Загружаем документы
                        fetch('/ajax/documents/')
                            .then(response => response.json())
                            .then(data => {
                                if (data.success) {
                                    content.innerHTML = data.html;
                                } else {
                                    content.innerHTML = '<p>Ошибка загрузки документов.</p>';
                                }
                            })
                            .catch(err => {
                                console.error('AJAX error (documents):', err);
                                content.innerHTML = '<p>Не удалось загрузить документы.</p>';
                            });
                    } else if (materialSlug) {
                        // Загружаем материал
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
                                console.error('AJAX error (material):', err);
                                content.innerHTML = '<p>Не удалось загрузить материал.</p>';
                            });
                    }
                }
            });
        });
    });
});