import { fetchJSON, withErrorHandling, LOADING_HTML } from '../lib/ajax.js';


export function initMaterials() {
    const groups = document.querySelectorAll('[data-accordion-group="material-cards"]');
    if (!groups.length) return;
    groups.forEach(group => {
        const cards = group.querySelectorAll('[data-material-slug]');
        const descBlock = group.querySelector('.material-description-block');
        const descContent = group.querySelector('.material-description-content')
        if (!descBlock || !descContent) return;
        let currentlyOpenSlug = null;
        const sectionHeader = group.closest('.section')?.querySelector('.section__header') ||
                              group.closest('.section') ||
                              group;
        cards.forEach(card => {
            card.addEventListener('click', function(e) {
                if (e.target.tagName === 'A' && !e.target.hasAttribute('data-material-slug')) {
                    return;
                }
                const materialSlug = this.dataset.materialSlug;
                if (currentlyOpenSlug === materialSlug) {
                    descBlock.style.display = 'none';
                    currentlyOpenSlug = null;
                    sectionHeader?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    return;
                }
                currentlyOpenSlug = materialSlug;
                descBlock.style.display = 'none';
                descContent.innerHTML = LOADING_HTML;
                loadMaterialDescription(
                    materialSlug,
                    descContent,
                    descBlock,
                    sectionHeader,
                    () => { currentlyOpenSlug = null; }
                );
            });
            const links = card.querySelectorAll('a[data-material-slug]');
            links.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    card.click();
                });
            });
        });
    });
}


async function loadMaterialDescription(slug, contentEl, blockEl, sectionHeader, onClose) {
    try {
        const data = await fetchJSON(`/ajax/material-description/${slug}/`);
        if (data.success && data.html) {
            contentEl.innerHTML = data.html;
            const closeButton = document.createElement('button');
            closeButton.className = 'material-close-button';
            closeButton.textContent = 'Скрыть';
            closeButton.type = 'button';
            closeButton.addEventListener('click', function() {
                blockEl.style.display = 'none';
                if (typeof onClose === 'function') onClose();
                sectionHeader?.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
            contentEl.appendChild(closeButton);
            blockEl.style.display = 'block';
            blockEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            const { onSuccess } = withErrorHandling(contentEl, 'материал');
            onSuccess(data, () => {});
            blockEl.style.display = 'block';
        }
    } catch (err) {
        const { onError } = withErrorHandling(contentEl, 'материал');
        onError(err);
        blockEl.style.display = 'block';
    }
}