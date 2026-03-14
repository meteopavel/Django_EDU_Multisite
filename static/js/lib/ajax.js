export const LOADING_HTML = '<p>Загрузка...</p>';


export function getErrorHTML(label = 'данные') {
    return `<p>Не удалось загрузить ${label}.</p>`;
}


export async function fetchJSON(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
    };
    const response = await fetch(url, { ...defaultOptions, ...options });
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
}


export function handleAJAXResponse(container, data, successCallback, label = 'данные') {
    if (data.success && typeof successCallback === 'function') {
        successCallback(data.html);
    } else {
        container.innerHTML = getErrorHTML(label);
        console.error(`API error (${label}):`, data);
    }
}


export function withErrorHandling(container, label = 'данные') {
    return {
        onSuccess: (data, render) => {
            handleAJAXResponse(container, data, render, label);
        },
        onError: (err) => {
            console.error(`AJAX error (${label}):`, err);
            container.innerHTML = getErrorHTML(label);
        }
    };
}


export async function fetchWithFeedback(container, url, options = {}, label = 'данные') {
    container.innerHTML = '<p>Загрузка...</p>';
    try {
        const data = await fetchJSON(url, options);

        if (data.success && data.html) {
            container.innerHTML = data.html;
            return { success: true, data };
        } else {
            container.innerHTML = `<p>Не удалось загрузить ${label}.</p>`;
            console.error(`API error (${label}):`, data);
            return { success: false, data };
        }
    } catch (err) {
        console.error(`AJAX error (${label}):`, err);
        container.innerHTML = `<p>Ошибка при загрузке ${label}.</p>`;
        return { success: false, error: err };
    }
}