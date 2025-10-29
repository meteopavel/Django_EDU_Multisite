from django.urls import path
from . import views

urlpatterns = [
    path('', views.page_view, name='home'),
    path('<slug:slug>/', views.page_view, name='page'),
]