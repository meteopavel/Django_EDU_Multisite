import { DetailLoader } from '../components/detail-loader.js';


function createHideButton(onClick) {
    const btn = document.createElement('button');
    btn.className = 'material-close-button';
    btn.textContent = 'Скрыть';
    btn.type = 'button';
    btn.addEventListener('click', onClick);
    return btn;
}


export function initMaterials() {
    const groups = document.querySelectorAll('[data-accordion-group="material-cards"]');
    if (!groups.length) return;
    groups.forEach(group => {
        const cards = group.querySelectorAll('[data-material-slug]');
        const descBlock = group.querySelector('.material-description-block');
        const descContent = group.querySelector('.material-description-content');
        if (!descBlock || !descContent) return;
        const sectionHeader = group.closest('.section')?.querySelector('.section__header') || group;
        const materialLoader = new DetailLoader({
            container: descContent,
            button: null,
            title: null,
            baseUrl: window.location.pathname,
            endpoint: '/ajax/material-description/',
            config: {
                label: 'материал',
                useHistory: false,
                backText: 'Скрыть',
                restoreText: '',
                slugInPath: true,
                onLoaded: (container) => {
                    container.appendChild(createHideButton(() => {
                        descBlock.style.display = 'none';
                        sectionHeader?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }));
                    descBlock.style.display = 'block';
                    descBlock.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
        cards.forEach(card => {
            card.addEventListener('click', function(e) {
                if (e.target.closest('a') && !e.target.closest('a[data-material-slug]')) return;                const slug = this.dataset.materialSlug;
                if (descBlock.style.display === 'block' && materialLoader.currentSlug === slug) {
                    descBlock.style.display = 'none';
                    return;
                }
                sectionHeader?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                materialLoader.load(slug, {}, false);
            });
        });
    });
}