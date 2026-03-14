export function initMaps() {
    if (window.yaMapsInitialized) return;
    window.yaMapsInitialized = true;
    const contactsMap = document.getElementById('contacts__map');
    const serviceCards = document.querySelectorAll('.service-card-parking');
    if (!contactsMap && !serviceCards.length) return;
    const apiKey = window.APP_CONFIG?.YANDEX_MAPS_API_KEY || '';
    function initAllMaps() {
        initContactsMap(contactsMap);
        initServiceMaps(serviceCards);
    }
    const script = document.createElement('script');
    script.src = `https://api-maps.yandex.ru/2.1/?apikey=${apiKey}&lang=ru_RU`;
    script.type = 'text/javascript';
    script.onload = initAllMaps;
    document.head.appendChild(script);
}


function initContactsMap(contactsMap) {
    if (!contactsMap) return;
    const mapCenter = contactsMap.dataset.center;
    const balloonText = contactsMap.dataset.balloon || 'Офис';
    let centerCoords = [52.267482, 104.310026]; // fallback
    try {
        centerCoords = JSON.parse(mapCenter);
    } catch (e) {
        console.error('Invalid map center coordinates:', mapCenter);
    }
    ymaps.ready(function() {
        const myMap = new ymaps.Map('contacts__map', {
            center: centerCoords,
            zoom: 17,
            controls: ['smallMapDefaultSet']
        });
        const myPlacemark = new ymaps.Placemark(centerCoords, {
            balloonContent: balloonText
        });
        myMap.geoObjects.add(myPlacemark);
    });
}


function initServiceMaps(serviceCards) {
    if (!serviceCards.length) return;
    serviceCards.forEach((card, index) => {
        const mapId = `map-${index + 1}`;
        const mapContainer = card.querySelector(`#${mapId}`);
        if (!mapContainer) return;
        const coordsStr = card.dataset.coords;
        let coords = [52.267482, 104.310026]; // fallback
        try {
            coords = JSON.parse(coordsStr);
        } catch (e) {
            console.warn('Invalid coords:', coordsStr);
        }
        ymaps.ready(function() {
            const myMap = new ymaps.Map(mapId, {
                center: coords,
                zoom: 17,
                controls: ['smallMapDefaultSet']
            });
            const myPlacemark = new ymaps.Placemark(coords, {
                balloonContent: card.dataset.address || 'Автостоянка'
            });
            myMap.geoObjects.add(myPlacemark);
            myMap.events.add('click', function() {
                myPlacemark.balloon.open();
            });
        });
    });
}