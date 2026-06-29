from django.urls import path
from . import views

urlpatterns = [
    path('', views.RecordListView.as_view(), name='record_list'),
    path('create/', views.RecordCreateView.as_view(), name='record_create'),
    path('<int:pk>/edit/', views.RecordUpdateView.as_view(), name='record_edit'),
    path('<int:pk>/delete/', views.RecordDeleteView.as_view(), name='record_delete'),
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
