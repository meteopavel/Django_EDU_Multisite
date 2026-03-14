import { initEducation } from './features/education.js';
import { initMaterials } from './features/materials.js';
import { initNews, initPartners } from './features/news-partners.js';
import { initMaps } from './features/maps.js';
import { initModal } from './components/modal.js';

document.addEventListener('DOMContentLoaded', () => {
    initModal();
    if (document.querySelector('[data-accordion-group="education-accordion"]')) {initEducation();}
    if (document.querySelector('[data-accordion-group="material-cards"]')) {initMaterials();}
    if (document.getElementById('news-content-container')) {initNews();}
    if (document.getElementById('partners-content-container')) {initPartners();}
    if (document.getElementById('contacts__map') || document.querySelector('.service-card-parking')) {initMaps();}
});