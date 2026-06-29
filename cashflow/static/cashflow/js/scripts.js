(function () {
    'use strict';

    var typeSelect = document.getElementById('id_type');
    var categorySelect = document.getElementById('id_category');
    var subcategorySelect = document.getElementById('id_subcategory');

    if (!typeSelect || !categorySelect || !subcategorySelect) return;

    function loadOptions(url, select, selectedValue) {
        fetch(url)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                select.innerHTML = '<option value="">---------</option>';
                data.forEach(function (item) {
                    var opt = document.createElement('option');
                    opt.value = item.id;
                    opt.textContent = item.name;
                    if (selectedValue && parseInt(selectedValue) === item.id) {
                        opt.selected = true;
                    }
                    select.appendChild(opt);
                });
            });
    }

    function onTypeChange() {
        var typeId = typeSelect.value;
        var selectedCategory = categorySelect.dataset.selected || '';
        if (typeId) {
            loadOptions('/api/categories/?type_id=' + typeId, categorySelect, selectedCategory);
        } else {
            categorySelect.innerHTML = '<option value="">---------</option>';
        }
        subcategorySelect.innerHTML = '<option value="">---------</option>';
    }

    function onCategoryChange() {
        var categoryId = categorySelect.value;
        var selectedSubcategory = subcategorySelect.dataset.selected || '';
        if (categoryId) {
            loadOptions('/api/subcategories/?category_id=' + categoryId, subcategorySelect, selectedSubcategory);
        } else {
            subcategorySelect.innerHTML = '<option value="">---------</option>';
        }
    }

    typeSelect.addEventListener('change', function () {
        delete categorySelect.dataset.selected;
        delete subcategorySelect.dataset.selected;
        onTypeChange();
    });

    categorySelect.addEventListener('change', function () {
        delete subcategorySelect.dataset.selected;
        onCategoryChange();
    });

    // On page load, if type is already selected (edit mode), load categories
    if (typeSelect.value) {
        var catVal = categorySelect.querySelector('option[selected]');
        if (catVal) categorySelect.dataset.selected = catVal.value;
        var subVal = subcategorySelect.querySelector('option[selected]');
        if (subVal) subcategorySelect.dataset.selected = subVal.value;
        onTypeChange();
    }

    // --- Client-side validation ---
    var form = document.getElementById('record-form');
    if (form) {
        form.addEventListener('submit', function (e) {
            var amount = document.querySelector('[name="amount"]');
            var type = document.querySelector('[name="type"]');
            var category = document.querySelector('[name="category"]');
            var subcategory = document.querySelector('[name="subcategory"]');

            if (!amount.value || parseFloat(amount.value) <= 0) {
                alert('Сумма должна быть положительным числом.');
                e.preventDefault();
                return;
            }
            if (!type.value) {
                alert('Выберите тип.');
                e.preventDefault();
                return;
            }
            if (!category.value) {
                alert('Выберите категорию.');
                e.preventDefault();
                return;
            }
            if (!subcategory.value) {
                alert('Выберите подкатегорию.');
                e.preventDefault();
                return;
            }
        });
    }
})();
