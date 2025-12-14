document.addEventListener('DOMContentLoaded', function () {
    const serviceCards = document.querySelectorAll('.service-card-parking');
    if (!serviceCards.length) return;
    const script = document.createElement('script');
    script.src = 'https://api-maps.yandex.ru/2.1/?apikey=3b626eb6-01de-4406-a7ef-5c59c8621f96&lang=ru_RU';
    script.type = 'text/javascript';
    script.onload = initMaps;
    document.body.appendChild(script);
    function initMaps() {
        serviceCards.forEach((card, index) => {
            const mapId = `map-${index + 1}`;
            const mapContainer = card.querySelector(`#${mapId}`);
            if (!mapContainer) return;
            const coordsStr = card.dataset.coords;
            let coords = [52.267482, 104.310026];
            try {
                coords = JSON.parse(coordsStr);
            } catch (e) {
                console.warn('Invalid coords:', coordsStr);
            }
            ymaps.ready(function () {
                const myMap = new ymaps.Map(mapId, {
                    center: coords,
                    zoom: 17,
                    controls: ['smallMapDefaultSet']
                });
                const myPlacemark = new ymaps.Placemark(coords, {
                    balloonContent: card.dataset.address || 'Автостоянка'
                });
                myMap.geoObjects.add(myPlacemark);
                myMap.events.add('click', function () {
                    myPlacemark.balloon.open();
                });
            });
        });
    }
});