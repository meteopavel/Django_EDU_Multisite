from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('contacts/', views.contacts_view, name='contacts'),
    path('news/', views.news_list_view, name='news_list'),
    path('news/<slug:slug>/', views.news_detail_view, name='news_detail'),
]