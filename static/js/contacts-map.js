(function () {
    const mapContainer = document.getElementById('contacts__map');
    if (!mapContainer) return;
    const mapCenter = mapContainer.dataset.center;
    const balloonText = mapContainer.dataset.balloon || 'Офис';
    let centerCoords;
    try {
        centerCoords = JSON.parse(mapCenter);
    } catch (e) {
        console.error('Invalid map center coordinates:', mapCenter);
        return;
    }
    const script = document.createElement('script');
    script.src = 'https://api-maps.yandex.ru/2.1/?apikey=3b626eb6-01de-4406-a7ef-5c59c8621f96&lang=ru_RU';
    script.type = 'text/javascript';
    script.onload = function () {
        ymaps.ready(function () {
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
    };
    document.head.appendChild(script);
})();