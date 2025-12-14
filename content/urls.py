from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('ajax/news-detail/', views.ajax_news_detail, name='ajax_news_detail'),
    path('ajax/all-news/', views.ajax_all_news, name='ajax_all_news'),
    path('ajax/service-description/<int:service_id>/', views.ajax_service_description, name='ajax_service_description'),
]