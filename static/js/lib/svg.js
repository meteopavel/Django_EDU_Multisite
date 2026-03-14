export function cloneButtonSVG(templateId, isFlipped = false) {
    const template = document.getElementById(templateId);
    if (!template || !template.firstElementChild) return null;
    const clone = template.firstElementChild.cloneNode(true);
    clone.style.transform = isFlipped ? 'scaleX(1)' : 'scaleX(-1)';
    return clone;
}


export function updateButton(button, text, isBack = false, svgTemplateId = 'svg-show-all-template') {
    if (!button) return;
    button.innerHTML = text + (isBack ? '\u00A0' : '');
    const svg = cloneButtonSVG(svgTemplateId, isBack);
    if (svg) button.appendChild(svg);
    button.classList.toggle('back-to-list-btn', isBack);
    button.classList.toggle('hide-news-btn', !isBack && text === 'Закрыть');
}