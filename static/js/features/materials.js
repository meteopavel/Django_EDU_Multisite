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
        const departmentSlug = group.dataset.department || '';

        cards.forEach(card => {
            const slug = card.dataset.materialSlug;
            const isExam = (slug === 'exameny');
            const loader = new DetailLoader({
                container: descContent,
                button: null,
                title: null,
                baseUrl: window.location.pathname,
                endpoint: isExam ? '/ajax/exam-info/' : '/ajax/material-description/',
                config: {
                    label: isExam ? 'информацию об экзаменах' : 'материал',
                    useHistory: false,
                    backText: 'Скрыть',
                    restoreText: '',
                    slugInPath: !isExam,  // ✅ Только материалы используют slug в пути
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
            card.addEventListener('click', function(e) {
                if (e.target.closest('a:not([data-material-slug])')) return;
                if (descBlock.style.display === 'block' && loader.currentSlug === slug) {
                    descBlock.style.display = 'none';
                    return;
                }
                sectionHeader?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                loader.load(isExam ? '' : slug, isExam ? { department: departmentSlug } : {}, false);
            });
        });
    });
}