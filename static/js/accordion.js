document.addEventListener('DOMContentLoaded', function () {
    const accordionGroups = document.querySelectorAll('[data-accordion-group]');

    accordionGroups.forEach(group => {
        const triggers = group.querySelectorAll('[data-accordion-trigger]');
        const contents = group.querySelectorAll('[data-accordion-content]');

        triggers.forEach(trigger => {
            trigger.addEventListener('click', function () {
                const item = this.closest('[data-accordion-item]');
                const content = item.querySelector('[data-accordion-content]');

                contents.forEach(c => {
                    if (c !== content) {
                        c.style.display = 'none';
                        c.closest('[data-accordion-item]').classList.remove('is-open');
                    }
                });

                if (content) {
                    if (content.style.display === 'block') {
                        content.style.display = 'none';
                        item.classList.remove('is-open');
                    } else {
                        content.style.display = 'block';
                        item.classList.add('is-open');
                    }
                }
            });
        });
    });
});