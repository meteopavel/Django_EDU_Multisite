"""
URL-маршруты контентного приложения.

Модуль определяет:
- главную страницу подразделения;
- AJAX-эндпоинты новостей;
- AJAX-эндпоинты документов, материалов и экзаменов.
"""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('ajax/news-detail/', views.ajax_news_detail, name='ajax_news_detail'),
    path('ajax/all-news/', views.ajax_all_news, name='ajax_all_news'),
    path('ajax/documents/', views.ajax_documents, name='ajax_documents'),
    path('ajax/material-description/<slug:material_slug>/', views.ajax_material_description, name='ajax_service_description'),
    path('ajax/exam-info/', views.ajax_exam_info, name='ajax_exam_info'),
]
