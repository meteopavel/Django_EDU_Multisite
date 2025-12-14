document.addEventListener('DOMContentLoaded', function () {
    const documentsSection = document.querySelector('#documents');
    const container = document.getElementById('documents-container');

    if (!documentsSection || !container) return;

    // Подгружаем при раскрытии (или сразу — как решите)
    //const departmentSlug = /* получите из data-department или из meta */;

    fetch(`/ajax/documents/?department=${encodeURIComponent(departmentSlug)}`)
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                container.innerHTML = data.html;
                container.style.display = 'block';
            }
        });
});