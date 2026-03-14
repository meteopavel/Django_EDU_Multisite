import { Accordion } from '../components/accordion.js';
import { fetchJSON, withErrorHandling, LOADING_HTML } from '../lib/ajax.js';


export function initEducation() {
    const groups = document.querySelectorAll('[data-accordion-group="education-accordion"]');
    if (!groups.length) return;
    groups.forEach(group => {
        new Accordion('[data-accordion-group="education-accordion"]', {
            onToggle: (item, isOpen) => {
                if (!isOpen) return;
                const content = item.querySelector('.accordion-content');
                const materialSlug = item.dataset.materialSlug;
                const isDocuments = item.dataset.documents === 'true';
                if (content.innerHTML.trim() !== LOADING_HTML && content.innerHTML.trim() !== '') {
                    return;
                }
                if (isDocuments) {
                    loadDocuments(content);
                } else if (materialSlug) {
                    loadMaterial(content, materialSlug);
                }
            }
        });
    });
}


async function loadDocuments(container) {
    container.innerHTML = LOADING_HTML;
    try {
        const data = await fetchJSON('/ajax/documents/');
        const { onSuccess } = withErrorHandling(container, 'документы');
        onSuccess(data, (html) => {
            container.innerHTML = html;
        });
    } catch (err) {
        const { onError } = withErrorHandling(container, 'документы');
        onError(err);
    }
}


async function loadMaterial(container, materialSlug) {
    container.innerHTML = LOADING_HTML;
    try {
        const data = await fetchJSON(`/ajax/material-description/${materialSlug}/`);
        const { onSuccess } = withErrorHandling(container, 'материал');
        onSuccess(data, (html) => {
            container.innerHTML = html;
        });
    } catch (err) {
        const { onError } = withErrorHandling(container, 'материал');
        onError(err);
    }
}