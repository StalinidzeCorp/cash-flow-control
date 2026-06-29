# Cash Flow Control — Design Document

## 1. Цель
Веб-приложение для учёта движения денежных средств (ДДС) с управлением справочниками и фильтрацией.

## 2. Технологии
- Python 3.14, Django 6.0.6
- SQLite
- Django Templates (DTL) + Bootstrap 5 (CDN)
- Vanilla JS для связанных селектов

## 3. Структура проекта

```
cash-flow-control/
├── core/                    # проект Django (settings, urls, wsgi)
├── cashflow/                # приложение ДДС
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   ├── validators.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── registration/login.html
│   │   └── cashflow/
│   │       ├── record_list.html
│   │       ├── record_form.html
│   │       ├── record_confirm_delete.html
│   │       ├── directory_list.html
│   │       ├── directory_form.html
│   │       └── directory_confirm_delete.html
│   └── static/
│       └── cashflow/js/scripts.js
├── manage.py
├── pyproject.toml
└── uv.lock
```

## 4. Модели данных

### TimeStampedMixin (абстрактная база)
- `created_at` — DateTimeField(auto_now_add=True)

### NamedMixin (абстрактная, для справочников)
- `name` — CharField(max_length=100)
- `Meta: abstract = True`

### Status (TimeStampedMixin, NamedMixin)
- `name` — unique=True
- `Meta: ordering = ['name']`

### Type (TimeStampedMixin, NamedMixin)
- `name` — unique=True
- `Meta: ordering = ['name']`

### Category (TimeStampedMixin, NamedMixin)
- `name` — CharField(max_length=100)
- `type` — ForeignKey(Type, CASCADE, related_name='categories')
- `Meta: unique_together = ('name', 'type'), ordering = ['name']`

### Subcategory (TimeStampedMixin, NamedMixin)
- `name` — CharField(max_length=100)
- `category` — ForeignKey(Category, CASCADE, related_name='subcategories')
- `Meta: unique_together = ('name', 'category'), ordering = ['name']`

### CashFlowRecord (TimeStampedMixin)
- `date` — DateField(default=date.today)
- `status` — ForeignKey(Status, PROTECT)
- `type` — ForeignKey(Type, PROTECT)
- `category` — ForeignKey(Category, PROTECT)
- `subcategory` — ForeignKey(Subcategory, PROTECT)
- `amount` — DecimalField(max_digits=12, decimal_places=2)
- `comment` — TextField(blank=True, default='')
- `Meta: ordering = ['-date', '-created_at']`

## 5. Представления (CBV)

### Records
- `RecordListView` — ListView; фильтрация через GET (date_from, date_to, status, type, category, subcategory), все поля фильтра — точное совпадение (exact match), обработка через Q-объекты
- `RecordCreateView` — CreateView с кастомной формой (RecordForm)
- `RecordUpdateView` — UpdateView
- `RecordDeleteView` — DeleteView

### Directories (универсальные, через параметр модели)
- Универсальные view, принимают модель через mapping-словарь в urls.py: `{'status': Status, 'type': Type, 'category': Category, 'subcategory': Subcategory}`
- Один класс `DirectoryListView` — принимает model параметром, рендерит таблицу
- Один класс `DirectoryCreateView` — CreateView с авто-формой
- Один класс `DirectoryUpdateView` — UpdateView
- Один класс `DirectoryDeleteView` — DeleteView с проверкой FK-связей (защита PROTECT обрабатывается через try/except)

### API (JSON)
- `api_categories_by_type` — GET → возвращает JSON-список категорий для type_id
- `api_subcategories_by_category` — GET → возвращает JSON-список подкатегорий для category_id

## 6. Формы

### RecordForm (ModelForm)
- Все поля из CashFlowRecord
- `clean()`:
  - Проверяет, что category.type == type
  - Проверяет, что subcategory.category == category
  - Проверяет обязательность amount, type, category, subcategory

### DirectoryForm (ModelForm)
- Автоматическая ModelForm для любой модели справочника

## 7. Аутентификация
- LoginRequiredMixin на всех view
- Страница /accounts/login/ через стандартный django.contrib.auth.views.LoginView
- Выход через POST /accounts/logout/

## 8. Шаблоны
- **base.html**: Bootstrap 5, навбар (ссылки: Главная — `/`, Справочники — `/directories/status/`, Выйти — `/accounts/logout/`)
- **record_list.html**: таблица с записями, форма фильтра сверху, кнопка «Создать запись»
- **record_form.html**: форма с JS для связанных селектов, валидация ошибок
- **record_confirm_delete.html**: подтверждение удаления
- **directory_list.html**: таблица справочника + кнопка добавить, уникальный для каждой модели
- **directory_form.html**: простая форма для справочника
- **directory_confirm_delete.html**: подтверждение удаления справочника

## 9. JavaScript (scripts.js)
- Загрузка категорий при смене типа: fetch(/api/categories/?type_id=...)
- Загрузка подкатегорий при смене категории
- Предзагрузка значений при редактировании (вызов API в момент загрузки страницы для заполнения с учётом выбранного типа/категории)

## 10. Валидация
- **Клиент**: required на полях, JS-блокировка отправки при невыбранной категории/подкатегории
- **Сервер**: clean() формы + PROTECT при удалении справочников

## 11. URL-шаблоны

```
/                                    — RecordListView
/create/                             — RecordCreateView
/<pk>/edit/                          — RecordUpdateView
/<pk>/delete/                        — RecordDeleteView
/directories/<model>/                — DirectoryListView
/directories/<model>/create/         — DirectoryCreateView
/directories/<model>/<pk>/edit/      — DirectoryUpdateView
/directories/<model>/<pk>/delete/    — DirectoryDeleteView
/api/categories/                     — JSON по type_id
/api/subcategories/                  — JSON по category_id
```
