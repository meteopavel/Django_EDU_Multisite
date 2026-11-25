/* Счётчик Яндекс.Метрики автошколы Иркутск (voa-irk.ru), №34367970 —
 * перенесён со старого сайта на Джумле. Подключается только для
 * department.slug == 'irkutsk' в base.html; параметры — как в штатном
 * снипете Метрики (webvisor, clickmap и т.д.). */
(function () {
    var counterId = 34367970;

    (function (m, e, t, r, i, k, a) {
        m[i] = m[i] || function () { (m[i].a = m[i].a || []).push(arguments); };
        m[i].l = 1 * new Date();
        for (var j = 0; j < document.scripts.length; j++) { if (document.scripts[j].src === r) { return; } }
        k = e.createElement(t), a = e.getElementsByTagName(t)[0], k.async = 1, k.src = r, a.parentNode.insertBefore(k, a);
    })(window, document, 'script', 'https://mc.yandex.ru/metrika/tag.js', 'ym');

    ym(counterId, 'init', {
        webvisor: true,
        clickmap: true,
        referrer: document.referrer,
        url: location.href,
        accurateTrackBounce: true,
        trackLinks: true
    });
})();
