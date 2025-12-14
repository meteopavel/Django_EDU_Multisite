document.addEventListener('DOMContentLoaded', function () {
    const ustkutGroup = document.querySelector('[data-accordion-group="ustkut-services"]');
    if (!ustkutGroup) return;

    const cards = ustkutGroup.querySelectorAll('.service-card-info_card');
    const descBlock = ustkutGroup.querySelector('.service-description-block');
    const descContent = ustkutGroup.querySelector('.service-description-content');

    cards.forEach(card => {
        card.addEventListener('click', function () {
            const serviceId = this.dataset.serviceId;
            const serviceName = this.dataset.serviceName;
            descBlock.style.display = 'none';
            descContent.innerHTML = '<p>Загрузка...</p>';
            fetch(`/ajax/service-description/${serviceId}/`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        descContent.innerHTML = data.html;
                        descBlock.style.display = 'block';
                        descBlock.scrollIntoView({ behavior: 'smooth' });
                    } else {
                        descContent.innerHTML = '<p>Ошибка загрузки описания.</p>';
                        descBlock.style.display = 'block';
                    }
                })
                .catch(err => {
                    console.error('AJAX error:', err);
                    descContent.innerHTML = '<p>Не удалось загрузить описание.</p>';
                    descBlock.style.display = 'block';
                });
        });
    });
});