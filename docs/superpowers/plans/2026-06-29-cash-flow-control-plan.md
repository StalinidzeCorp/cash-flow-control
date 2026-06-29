# Cash Flow Control Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a web app for managing cash flow records with directory (status/type/category/subcategory) management, filtering, and chained select dependencies.

**Architecture:** Single Django app `cashflow` inside existing `core` project. CBVs for views, ModelForms for validation, DTL + Bootstrap 5 for UI, vanilla JS for dynamic select filtering.

**Tech Stack:** Python 3.14, Django 6.0.6, SQLite, Bootstrap 5 (CDN), DTL

---

### Task 1: Create cashflow app and register in settings

**Files:**
- Create: `cashflow/__init__.py`
- Create: `cashflow/apps.py`
- Modify: `core/settings.py`

- [ ] **Step 1: Create cashflow app directory**

```bash
mkdir -p cashflow/templates/cashflow cashflow/templates/registration cashflow/static/cashflow/js && touch cashflow/__init__.py
```

- [ ] **Step 2: Write apps.py**

```python
from django.apps import AppConfig


class CashflowConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cashflow'
```

- [ ] **Step 3: Register app in core/settings.py**

Add `'cashflow'` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cashflow',
]
```

- [ ] **Step 4: Verify app is detected**

Run: `uv run python manage.py check`
Expected: "System check identified no issues (0 silenced)."

---

### Task 2: Models (migrations)

**Files:**
- Create: `cashflow/models.py`

- [ ] **Step 1: Write models.py**

```python
from decimal import Decimal
from datetime import date

from django.db import models
from django.core.exceptions import ValidationError


class TimeStampedMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class NamedMixin(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Status(TimeStampedMixin, NamedMixin):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'statuses'


class Type(TimeStampedMixin, NamedMixin):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']


class Category(TimeStampedMixin, NamedMixin):
    type = models.ForeignKey(
        Type, on_delete=models.CASCADE, related_name='categories'
    )

    class Meta:
        ordering = ['name']
        unique_together = ('name', 'type')
        verbose_name_plural = 'categories'


class Subcategory(TimeStampedMixin, NamedMixin):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='subcategories'
    )

    class Meta:
        ordering = ['name']
        unique_together = ('name', 'category')
        verbose_name_plural = 'subcategories'


class CashFlowRecord(TimeStampedMixin):
    date = models.DateField(default=date.today)
    status = models.ForeignKey(
        Status, on_delete=models.PROTECT, verbose_name='status'
    )
    type = models.ForeignKey(
        Type, on_delete=models.PROTECT, verbose_name='type'
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, verbose_name='category'
    )
    subcategory = models.ForeignKey(
        Subcategory, on_delete=models.PROTECT, verbose_name='subcategory'
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name='amount'
    )
    comment = models.TextField(blank=True, default='', verbose_name='comment')

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'cash flow record'
```

- [ ] **Step 2: Create and apply migrations**

```bash
uv run python manage.py makemigrations cashflow && uv run python manage.py migrate
```

Expected: Migrations created and applied without errors.

---

### Task 3: Admin registration (for debugging convenience)

**Files:**
- Create: `cashflow/admin.py`

- [ ] **Step 1: Write admin.py**

```python
from django.contrib import admin
from .models import Status, Type, Category, Subcategory, CashFlowRecord


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    pass


@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')


@admin.register(CashFlowRecord)
class CashFlowRecordAdmin(admin.ModelAdmin):
    list_display = ('date', 'status', 'type', 'category', 'subcategory', 'amount')
    list_filter = ('status', 'type', 'category')
```

- [ ] **Step 2: Create superuser**

```bash
uv run python manage.py createsuperuser --noinput --username admin --email admin@example.com 2>/dev/null; uv run python manage.py shell -c "from django.contrib.auth.models import User; u=User.objects.get(username='admin'); u.set_password('admin'); u.save()"
```

---

### Task 4: Authentication setup

**Files:**
- Modify: `core/urls.py`
- Modify: `core/settings.py`
- Create: `cashflow/templates/registration/login.html`

- [ ] **Step 1: Add login/logout URLs to core/urls.py**

```python
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('cashflow.urls')),
]
```

- [ ] **Step 2: Add login redirect settings to core/settings.py**

```python
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
```

- [ ] **Step 3: Create login.html template**

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Вход — ДДС</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container vh-100 d-flex align-items-center justify-content-center">
        <div class="card shadow" style="width: 24rem;">
            <div class="card-body">
                <h3 class="card-title mb-4 text-center">Вход в систему</h3>
                <form method="post">
                    {% csrf_token %}
                    {{ form.as_p }}
                    <button type="submit" class="btn btn-primary w-100">Войти</button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
```

---

### Task 5: Base template and static files

**Files:**
- Create: `cashflow/templates/base.html`
- Create: `cashflow/static/cashflow/js/scripts.js`

- [ ] **Step 1: Write base.html**

```html
{% load static %}
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}ДДС{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
        <div class="container">
            <a class="navbar-brand" href="{% url 'record_list' %}">ДДС</a>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'record_list' %}">Главная</a>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">Справочники</a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{% url 'directory_list' model_name='status' %}">Статусы</a></li>
                            <li><a class="dropdown-item" href="{% url 'directory_list' model_name='type' %}">Типы</a></li>
                            <li><a class="dropdown-item" href="{% url 'directory_list' model_name='category' %}">Категории</a></li>
                            <li><a class="dropdown-item" href="{% url 'directory_list' model_name='subcategory' %}">Подкатегории</a></li>
                        </ul>
                    </li>
                </ul>
                <span class="navbar-text">
                    {{ user.username }} | <a class="text-white" href="{% url 'logout' %}">Выйти</a>
                </span>
            </div>
        </div>
    </nav>
    <main class="container">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show">{{ message }}</div>
            {% endfor %}
        {% endif %}
        {% block content %}{% endblock %}
    </main>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{% static 'cashflow/js/scripts.js' %}"></script>
</body>
</html>
```

- [ ] **Step 2: Create empty scripts.js placeholder**

```js
// Chained selects for record form — will be implemented in Task 9
```

---

### Task 6: Directory management (views, URLs, templates)

**Files:**
- Create: `cashflow/urls.py`
- Create: `cashflow/views.py`
- Create: `cashflow/templates/cashflow/directory_list.html`
- Create: `cashflow/templates/cashflow/directory_form.html`
- Create: `cashflow/templates/cashflow/directory_confirm_delete.html`

- [ ] **Step 1: Write views.py with all directory views**

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import ProtectedError
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect
from .models import Status, Type, Category, Subcategory, CashFlowRecord


MODEL_MAP = {
    'status': (Status, None),
    'type': (Type, None),
    'category': (Category, 'type'),
    'subcategory': (Subcategory, 'category'),
}


class DirectoryListView(LoginRequiredMixin, ListView):
    template_name = 'cashflow/directory_list.html'
    paginate_by = 50

    def get_model(self):
        return MODEL_MAP[self.kwargs['model_name']][0]

    def get_queryset(self):
        return self.get_model().objects.all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model_name'] = self.kwargs['model_name']
        ctx['parent_field'] = MODEL_MAP[self.kwargs['model_name']][1]
        return ctx


class DirectoryCreateView(LoginRequiredMixin, CreateView):
    template_name = 'cashflow/directory_form.html'

    def get_model(self):
        return MODEL_MAP[self.kwargs['model_name']][0]

    def get_form_class(self):
        from django.forms import ModelForm
        model = self.get_model()
        class F(ModelForm):
            class Meta:
                model = model
                fields = '__all__'
        return F

    def get_success_url(self):
        return reverse_lazy('directory_list', kwargs={'model_name': self.kwargs['model_name']})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model_name'] = self.kwargs['model_name']
        return ctx


class DirectoryUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'cashflow/directory_form.html'

    def get_model(self):
        return MODEL_MAP[self.kwargs['model_name']][0]

    def get_form_class(self):
        from django.forms import ModelForm
        model = self.get_model()
        class F(ModelForm):
            class Meta:
                model = model
                fields = '__all__'
        return F

    def get_object(self, queryset=None):
        return self.get_model().objects.get(pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy('directory_list', kwargs={'model_name': self.kwargs['model_name']})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model_name'] = self.kwargs['model_name']
        return ctx


class DirectoryDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'cashflow/directory_confirm_delete.html'

    def get_model(self):
        return MODEL_MAP[self.kwargs['model_name']][0]

    def get_object(self, queryset=None):
        return self.get_model().objects.get(pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy('directory_list', kwargs={'model_name': self.kwargs['model_name']})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model_name'] = self.kwargs['model_name']
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, 'Запись удалена.')
        except ProtectedError:
            messages.error(request, 'Невозможно удалить: запись используется в ДДС.')
        return redirect(self.get_success_url())
```

- [ ] **Step 2: Write urls.py**

```python
from django.urls import path
from . import views

urlpatterns = [
    path(
        'directories/<str:model_name>/',
        views.DirectoryListView.as_view(),
        name='directory_list',
    ),
    path(
        'directories/<str:model_name>/create/',
        views.DirectoryCreateView.as_view(),
        name='directory_create',
    ),
    path(
        'directories/<str:model_name>/<int:pk>/edit/',
        views.DirectoryUpdateView.as_view(),
        name='directory_edit',
    ),
    path(
        'directories/<str:model_name>/<int:pk>/delete/',
        views.DirectoryDeleteView.as_view(),
        name='directory_delete',
    ),
    path(
        'api/categories/',
        views.api_categories_by_type,
        name='api_categories',
    ),
    path(
        'api/subcategories/',
        views.api_subcategories_by_category,
        name='api_subcategories',
    ),
]
```

- [ ] **Step 3: Write directory_list.html**

```html
{% extends 'base.html' %}
{% block title %}{{ model_name|capfirst }} — Справочники{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
    <h2>{{ model_name|capfirst }}</h2>
    <a href="{% url 'directory_create' model_name=model_name %}" class="btn btn-primary">+ Добавить</a>
</div>

<table class="table table-striped">
    <thead>
        <tr>
            <th>#</th>
            <th>Название</th>
            {% if parent_field %}<th>{{ parent_field|capfirst }}</th>{% endif %}
            <th>Действия</th>
        </tr>
    </thead>
    <tbody>
        {% for obj in object_list %}
        <tr>
            <td>{{ obj.pk }}</td>
            <td>{{ obj.name }}</td>
            {% if parent_field %}
                <td>{{ obj|getattribute:parent_field }}</td>
            {% endif %}
            <td>
                <a href="{% url 'directory_edit' model_name=model_name pk=obj.pk %}" class="btn btn-sm btn-outline-secondary">Изменить</a>
                <a href="{% url 'directory_delete' model_name=model_name pk=obj.pk %}" class="btn btn-sm btn-outline-danger">Удалить</a>
            </td>
        </tr>
        {% empty %}
        <tr><td colspan="4">Нет записей.</td></tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

- [ ] **Step 4: Write directory_form.html**

```html
{% extends 'base.html' %}
{% block title %}{% if object %}Изменить{% else %}Создать{% endif %} {{ model_name|capfirst }}{% endblock %}
{% block content %}
<h2>{% if object %}Изменить{% else %}Создать{% endif %} {{ model_name|capfirst }}</h2>
<form method="post" class="mt-3" style="max-width: 400px;">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit" class="btn btn-success">Сохранить</button>
    <a href="{% url 'directory_list' model_name=model_name %}" class="btn btn-secondary">Отмена</a>
</form>
{% endblock %}
```

- [ ] **Step 5: Write directory_confirm_delete.html**

```html
{% extends 'base.html' %}
{% block title %}Удалить {{ object.name }}{% endblock %}
{% block content %}
<h2>Удалить «{{ object.name }}»?</h2>
<p>Это действие нельзя отменить.</p>
<form method="post">
    {% csrf_token %}
    <button type="submit" class="btn btn-danger">Удалить</button>
    <a href="{% url 'directory_list' model_name=model_name %}" class="btn btn-secondary">Отмена</a>
</form>
{% endblock %}
```

- [ ] **Step 6: Add getattribute template filter**

Before we can use `getattribute` in the template, we need a custom filter. Create `cashflow/templatetags/` directory with a filter:

```bash
mkdir -p cashflow/templatetags && touch cashflow/templatetags/__init__.py
```

Create `cashflow/templatetags/cashflow_extras.py`:

```python
from django import template

register = template.Library()


@register.filter
def getattribute(obj, attr):
    return getattr(obj, attr, '')
```

Update `directory_list.html` to load the tag:

```html
{% extends 'base.html' %}
{% load cashflow_extras %}
...
```

---

### Task 7: API endpoints for chained selects

**Files:**
- Modify: `cashflow/views.py` (add JSON views)

- [ ] **Step 1: Add api views to views.py**

```python
from django.http import JsonResponse
from .models import Category, Subcategory

def api_categories_by_type(request):
    type_id = request.GET.get('type_id')
    if not type_id:
        return JsonResponse([], safe=False)
    qs = Category.objects.filter(type_id=type_id).values('id', 'name')
    return JsonResponse(list(qs), safe=False)


def api_subcategories_by_category(request):
    category_id = request.GET.get('category_id')
    if not category_id:
        return JsonResponse([], safe=False)
    qs = Subcategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse(list(qs), safe=False)
```

- [ ] **Step 2: Test API manually**

```bash
curl http://localhost:8000/api/categories/?type_id=1
```

Expected: JSON array of categories for type_id=1 (or empty `[]` if none exist).

---

### Task 8: Record CRUD (forms, views, templates)

**Files:**
- Create: `cashflow/forms.py`
- Modify: `cashflow/views.py` (add record views)
- Modify: `cashflow/urls.py` (add record URL patterns)
- Create: `cashflow/templates/cashflow/record_list.html`
- Create: `cashflow/templates/cashflow/record_form.html`
- Create: `cashflow/templates/cashflow/record_confirm_delete.html`

- [ ] **Step 1: Write forms.py**

```python
from django import forms
from django.core.exceptions import ValidationError
from .models import CashFlowRecord


class RecordForm(forms.ModelForm):
    class Meta:
        model = CashFlowRecord
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'type': forms.Select(attrs={'class': 'form-select', 'id': 'id_type'}),
            'category': forms.Select(attrs={'class': 'form-select', 'id': 'id_category'}),
            'subcategory': forms.Select(attrs={'class': 'form-select', 'id': 'id_subcategory'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'required': True}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned = super().clean()
        type_obj = cleaned.get('type')
        category = cleaned.get('category')
        subcategory = cleaned.get('subcategory')

        if category and type_obj and category.type != type_obj:
            raise ValidationError(
                'Категория не относится к выбранному типу.'
            )

        if subcategory and category and subcategory.category != category:
            raise ValidationError(
                'Подкатегория не относится к выбранной категории.'
            )

        return cleaned
```

- [ ] **Step 2: Add record views to views.py**

```python
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import RecordForm
from .models import CashFlowRecord, Status, Type


class RecordListView(LoginRequiredMixin, ListView):
    model = CashFlowRecord
    template_name = 'cashflow/record_list.html'
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset().select_related('status', 'type', 'category', 'subcategory')
        params = self.request.GET

        date_from = params.get('date_from')
        date_to = params.get('date_to')
        status = params.get('status')
        type_obj = params.get('type')
        category = params.get('category')
        subcategory = params.get('subcategory')

        from django.db.models import Q
        filters = Q()
        if date_from:
            filters &= Q(date__gte=date_from)
        if date_to:
            filters &= Q(date__lte=date_to)
        if status:
            filters &= Q(status_id=status)
        if type_obj:
            filters &= Q(type_id=type_obj)
        if category:
            filters &= Q(category_id=category)
        if subcategory:
            filters &= Q(subcategory_id=subcategory)

        return qs.filter(filters)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['statuses'] = Status.objects.all()
        ctx['types'] = Type.objects.all()
        ctx['filter_params'] = self.request.GET
        return ctx


class RecordCreateView(LoginRequiredMixin, CreateView):
    model = CashFlowRecord
    form_class = RecordForm
    template_name = 'cashflow/record_form.html'
    success_url = reverse_lazy('record_list')


class RecordUpdateView(LoginRequiredMixin, UpdateView):
    model = CashFlowRecord
    form_class = RecordForm
    template_name = 'cashflow/record_form.html'
    success_url = reverse_lazy('record_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['is_update'] = True
        return ctx


class RecordDeleteView(LoginRequiredMixin, DeleteView):
    model = CashFlowRecord
    template_name = 'cashflow/record_confirm_delete.html'
    success_url = reverse_lazy('record_list')
```

- [ ] **Step 3: Add record URL patterns to urls.py**

```python
urlpatterns = [
    path('', views.RecordListView.as_view(), name='record_list'),
    path('create/', views.RecordCreateView.as_view(), name='record_create'),
    path('<int:pk>/edit/', views.RecordUpdateView.as_view(), name='record_edit'),
    path('<int:pk>/delete/', views.RecordDeleteView.as_view(), name='record_delete'),
    # ... directory and api patterns from Task 6
]
```

- [ ] **Step 4: Write record_list.html**

```html
{% extends 'base.html' %}
{% block title %}Главная — ДДС{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
    <h2>Записи ДДС</h2>
    <a href="{% url 'record_create' %}" class="btn btn-primary">+ Создать запись</a>
</div>

<form method="get" class="row g-2 mb-4 p-3 border rounded bg-light">
    <div class="col-md-2">
        <label class="form-label">Дата с</label>
        <input type="date" name="date_from" class="form-control" value="{{ filter_params.date_from }}">
    </div>
    <div class="col-md-2">
        <label class="form-label">Дата по</label>
        <input type="date" name="date_to" class="form-control" value="{{ filter_params.date_to }}">
    </div>
    <div class="col-md-2">
        <label class="form-label">Статус</label>
        <select name="status" class="form-select">
            <option value="">Все</option>
            {% for s in statuses %}
                <option value="{{ s.pk }}" {% if filter_params.status == s.pk|stringformat:"s" %}selected{% endif %}>{{ s.name }}</option>
            {% endfor %}
        </select>
    </div>
    <div class="col-md-2">
        <label class="form-label">Тип</label>
        <select name="type" class="form-select">
            <option value="">Все</option>
            {% for t in types %}
                <option value="{{ t.pk }}" {% if filter_params.type == t.pk|stringformat:"s" %}selected{% endif %}>{{ t.name }}</option>
            {% endfor %}
        </select>
    </div>
    <div class="col-md-2">
        <label class="form-label">Категория</label>
        <select name="category" class="form-select">
            <option value="">Все</option>
        </select>
    </div>
    <div class="col-md-2">
        <label class="form-label">Подкатегория</label>
        <select name="subcategory" class="form-select">
            <option value="">Все</option>
        </select>
    </div>
    <div class="col-12">
        <button type="submit" class="btn btn-success">Применить фильтры</button>
        <a href="{% url 'record_list' %}" class="btn btn-outline-secondary">Сбросить</a>
    </div>
</form>

<table class="table table-striped">
    <thead>
        <tr>
            <th>Дата</th>
            <th>Статус</th>
            <th>Тип</th>
            <th>Категория</th>
            <th>Подкатегория</th>
            <th>Сумма</th>
            <th>Комментарий</th>
            <th>Действия</th>
        </tr>
    </thead>
    <tbody>
        {% for record in object_list %}
        <tr>
            <td>{{ record.date|date:"d.m.Y" }}</td>
            <td>{{ record.status.name }}</td>
            <td>{{ record.type.name }}</td>
            <td>{{ record.category.name }}</td>
            <td>{{ record.subcategory.name }}</td>
            <td>{{ record.amount|floatformat:2 }} р.</td>
            <td>{{ record.comment|truncatewords:10 }}</td>
            <td>
                <a href="{% url 'record_edit' pk=record.pk %}" class="btn btn-sm btn-outline-secondary">Изменить</a>
                <a href="{% url 'record_delete' pk=record.pk %}" class="btn btn-sm btn-outline-danger">Удалить</a>
            </td>
        </tr>
        {% empty %}
        <tr><td colspan="8">Нет записей.</td></tr>
        {% endfor %}
    </tbody>
</table>

{% if page_obj.has_other_pages %}
<nav>
    <ul class="pagination">
        {% if page_obj.has_previous %}
            <li class="page-item"><a class="page-link" href="?page={{ page_obj.previous_page_number }}{% for key, value in filter_params.items %}&{{ key }}={{ value }}{% endfor %}">Назад</a></li>
        {% endif %}
        <li class="page-item active"><span class="page-link">{{ page_obj.number }}</span></li>
        {% if page_obj.has_next %}
            <li class="page-item"><a class="page-link" href="?page={{ page_obj.next_page_number }}{% for key, value in filter_params.items %}&{{ key }}={{ value }}{% endfor %}">Вперёд</a></li>
        {% endif %}
    </ul>
</nav>
{% endif %}
{% endblock %}
```

- [ ] **Step 5: Write record_form.html**

```html
{% extends 'base.html' %}
{% block title %}{% if is_update %}Изменить{% else %}Создать{% endif %} запись{% endblock %}
{% block content %}
<h2>{% if is_update %}Изменить{% else %}Создать{% endif %} запись</h2>
<form method="post" class="mt-3" style="max-width: 600px;" id="record-form">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit" class="btn btn-success">Сохранить</button>
    <a href="{% url 'record_list' %}" class="btn btn-secondary">Отмена</a>
</form>
{% endblock %}
```

- [ ] **Step 6: Write record_confirm_delete.html**

```html
{% extends 'base.html' %}
{% block title %}Удалить запись{% endblock %}
{% block content %}
<h2>Удалить запись от {{ object.date|date:"d.m.Y" }}?</h2>
<p>Тип: {{ object.type.name }}, Категория: {{ object.category.name }}, Сумма: {{ object.amount|floatformat:2 }} р.</p>
<p>Это действие нельзя отменить.</p>
<form method="post">
    {% csrf_token %}
    <button type="submit" class="btn btn-danger">Удалить</button>
    <a href="{% url 'record_list' %}" class="btn btn-secondary">Отмена</a>
</form>
{% endblock %}
```

---

### Task 9: JavaScript for chained selects

**Files:**
- Modify: `cashflow/static/cashflow/js/scripts.js`

- [ ] **Step 1: Write scripts.js**

```javascript
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
})();
```

---

### Task 10: Client-side validation

**Files:**
- Modify: `cashflow/static/cashflow/js/scripts.js`

- [ ] **Step 1: Add validation to scripts.js**

```javascript
// Add to the IIFE from Task 9
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
```

---

### Task 11: Verify full application works

- [ ] **Step 1: Run Django check**

```bash
uv run python manage.py check
```

Expected: No issues.

- [ ] **Step 2: Run migrations**

```bash
uv run python manage.py migrate
```

Expected: All migrations applied.

- [ ] **Step 3: Start dev server and manually test**

```bash
uv run python manage.py runserver
```

- Visit http://localhost:8000/ — should redirect to login
- Log in with admin/admin
- Create some directories (Status: Бизнес, Личное, Налог; Type: Пополнение, Списание; Category: Инфраструктура, Маркетинг; Subcategory: VPS, Proxy → Инфраструктура; Farpost, Avito → Маркетинг)
- Create a cash flow record with correct type→category→subcategory chain
- Test filtering by date, status, type
- Test edit and delete
- Test directory delete protection (try deleting a type that has records)
