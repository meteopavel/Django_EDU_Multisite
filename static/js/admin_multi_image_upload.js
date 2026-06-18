window.addEventListener('load', function () {
    var $ = django.jQuery;

    var $inline = $('.inline-group').filter(function () {
        return $(this).find('input[type="file"]').length > 0;
    }).first();

    if (!$inline.length) return;

    var prefix = $inline.attr('id').replace('-group', '');
    var $origRow = $inline.find('.add-row');

    var $btn = $('<input type="file" multiple accept="image/*" style="display:none" id="id_multi_image_upload">');
    var $label = $('<a class="addlink" href="#">Добавить несколько фото</a>');

    $label.on('click', function (e) { e.preventDefault(); $btn.trigger('click'); });

    $btn.on('change', function () {
        var files = Array.from(this.files);
        if (!files.length) return;

        files.forEach(function (file, i) {
            if (i > 0) {
                $origRow.find('a').trigger('click');
            }
        });

        setTimeout(function () {
            var $rows = $inline.find('.dynamic-' + prefix + ':not(.empty-form)');
            var startIdx = $rows.length - files.length;
            files.forEach(function (file, i) {
                var $input = $rows.eq(startIdx + i).find('input[type="file"]');
                var dt = new DataTransfer();
                dt.items.add(file);
                $input[0].files = dt.files;
                $input.trigger('change');
            });
            $btn.val('');
        }, 150);
    });

    // Клонируем строку оригинальной кнопки — стили идентичны
    var $newRow = $origRow.clone();
    $newRow.find('a').replaceWith($btn).end().find('td').append($label);
    $origRow.after($newRow);

    // Скрываем оригинальную кнопку
    $origRow.hide();
});
